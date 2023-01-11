import csv
import datetime
import os
import sys
import time

import serial
from PyQt6 import uic
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QVBoxLayout, QFileDialog
from serial.tools import list_ports

from realtimePlot import *
from stertch_protocol import *


class StretchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/stretchWindow.ui", self)  # load the ui file

        # Data cache initialzation
        self.cache = Cache()

        # Serial prot initialzation
        self.serial_arduino = serial.Serial()
        self.serial_psoc = serial.Serial()

        # Graph initialization
        self.plot1 = ScatterPlot2Y(xlabel_text='Elongation (mm)', xlabel_unit=None,
                                   ylabel1_text='R', ylabel1_unit='Ohm',
                                   ylabel2_text='R/R0', ylabel2_unit=None,
                                   show_y='y1',
                                   history_size=2500,
                                   title='Resistance-Elongation')

        self.plot2 = LinePlot2Y(xlabel_text='Time', xlabel_unit='s',
                                ylabel1_text='R', ylabel1_unit='Ohm',
                                ylabel2_text='R/R0', ylabel2_unit=None,
                                show_y='y1',
                                history_size=2500,
                                title='Resistance-Time')
        self.plot_area1.setLayout(QVBoxLayout())
        self.plot_area1.layout().addWidget(self.plot1)
        self.plot_area2.setLayout(QVBoxLayout())
        self.plot_area2.layout().addWidget(self.plot2)

        # Button configuration
        self.pushButton_connect.clicked.connect(self.onclick_connect)
        self.pushButton_refresh.clicked.connect(self.onclick_refresh)
        self.pushButton_launch.clicked.connect(self.onclick_launch)
        self.pushButton_stop.clicked.connect(self.onclick_stop)
        self.pushButton_save.clicked.connect(self.onclick_save)
        self.pushButton_pause.clicked.connect(self.onclick_pause)
        self.pushButton_clear_text.clicked.connect(self.textBrowser_data.clear)
        self.pushButton_clear_graph.clicked.connect(
            lambda: [self.plot1.reset(), self.plot2.reset()])

        # Check box configuration
        self.checkBox_graph1.stateChanged.connect(
            lambda state: [self.plot_area1.hide(), self.plot1.set_update_enable(False)] if state == 0 else [self.plot_area1.show(), self.plot1.set_update_enable(True)])
        self.checkBox_graph2.stateChanged.connect(
            lambda state: [self.plot_area2.hide(), self.plot2.set_update_enable(False)] if state == 0 else [self.plot_area2.show(), self.plot2.set_update_enable(True)])

        # Radion button configuration
        self.radioButton_RS_abs.toggled.connect(
            lambda checked: self.plot1.set_show_y('y1') if checked else None)
        self.radioButton_RS_rel.toggled.connect(
            lambda checked: self.plot1.set_show_y('y2') if checked else None)
        self.radioButton_RT_abs.toggled.connect(
            lambda checked: self.plot2.set_show_y('y1') if checked else None)
        self.radioButton_RT_rel.toggled.connect(
            lambda checked: self.plot2.set_show_y('y2') if checked else None)

        # ComboBox configuration
        self.comboBox_comports_arduino.addItems(
            [i.device for i in list(list_ports.comports())])
        self.comboBox_comports_psoc.addItems(
            [i.device for i in list(list_ports.comports())])

        self.body_left.setEnabled(False)

    def onclick_connect(self):

        if self.pushButton_connect.text() == 'Connect':
            self.serial_arduino = None
            self.serial_psoc = None
            psoc_connected = False
            arduino_connected = False
            try:
                self.serial_arduino = serial.Serial(port=self.comboBox_comports_arduino.currentText(),
                                                    baudrate=115200,
                                                    timeout=None)
            except Exception as e:
                QMessageBox.warning(self, 'Warning',
                                    'Arduino connection failed!\n' + str(e),
                                    QMessageBox.StandardButton.Ok,
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, 'Information',
                                        'Arduino connection successful!',
                                        QMessageBox.StandardButton.Ok,
                                        QMessageBox.StandardButton.Ok)
                arduino_connected = True

            try:
                self.serial_psoc = serial.Serial(port=self.comboBox_comports_psoc.currentText(),
                                                 baudrate=115200,
                                                 timeout=None)

            except Exception as e:
                QMessageBox.warning(self, 'Warning',
                                    'PSoC connection failed!\n' + str(e),
                                    QMessageBox.StandardButton.Ok,
                                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, 'Information',
                                        'PSOC connection successful!',
                                        QMessageBox.StandardButton.Ok,
                                        QMessageBox.StandardButton.Ok)
                psoc_connected = True

            if psoc_connected and arduino_connected:
                self.pushButton_connect.setText('Disconnect')
                self.body_left.setEnabled(True)

        elif self.pushButton_connect.text() == 'Disconnect':
            self.pushButton_connect.setText('Connect')
            self.body_left.setEnabled(False)
            self.serial_arduino = None
            self.serial_psoc = None

            QMessageBox.information(self, 'Information', 'Disconnected!', QMessageBox.StandardButton.Ok,
                                    QMessageBox.StandardButton.Ok)

    def onclick_refresh(self):
        self.comboBox_comports_arduino.clear()
        self.comboBox_comports_psoc.clear()
        self.comboBox_comports_arduino.addItems(
            [i.device for i in list(list_ports.comports())])
        self.comboBox_comports_psoc.addItems(
            [i.device for i in list(list_ports.comports())])

    def onclick_launch(self):
        sample_length = self.spinBox_sample_length.value()  # in um
        max_strain = self.doubleSpinBox_max_strain.value() / 100
        stretch_length = sample_length * max_strain
        stretch_speed = self.spinBox_speed.value()  # in um/s
        cycles = self.spinBox_cycles.value()
        self.serial_arduino.write(bytes(str(ARDUINO_TELEGRAM_PARAMETER_SETTING_REQUEST(
            stretch_length=stretch_length, stretch_speed=stretch_speed, cycles=cycles)), 'UTF-8'))

        sample_rate = self.spinBox_sample_rate.value()
        downsample = self.spinBox_downsample.value()
        gain_channel = self.comboBox_gain.currentIndex()
        current_source_channel = self.comboBox_current_source.currentIndex() - 1
        self.serial_psoc.write(bytes(str(PSOC_TELEGRAM_SET_PARAMETER_REQUEST(
            sample_rate, downsample, gain_channel, current_source_channel)), 'UTF-8'))

        self.cache = Cache()

        self.cache.test_parameter = {'sample_length': sample_length,
                                     'max_strain': max_strain,
                                     'stretch_speed': stretch_speed,
                                     'cycles': cycles,
                                     'sample_rate': sample_rate,
                                     'downsample': downsample,
                                     'gain': self.comboBox_gain.currentText(),
                                     'current_source': self.comboBox_current_source.currentText()
                                     }

        self.plot1.reset()
        self.plot2.reset()

        self.receive_data_thread = DataReceiver(
            self.serial_arduino, self.serial_psoc)
        self.receive_data_thread.update_textBroswer.connect(
            lambda data: self.textBrowser_data.append(data))
        self.receive_data_thread.update_cache.connect(
            lambda data: self.cache.append(data))
        self.receive_data_thread.update_plot1.connect(self.plot1.update)
        self.receive_data_thread.update_plot2.connect(self.plot2.update)
        self.receive_data_thread.test_finished.connect(
            self.test_stopped_callback)

        self.receive_data_thread.start()
        self.test_started_callback()

        self.serial_psoc.write(str(PSOC_TELEGRAM_DATA_SUBSCRIPTION_REQUEST(
            PSOC_DATA_SUBSCRIPTION)).encode(encoding='UTF-8'))
        self.serial_arduino.write(ARDUINO_TELEGRAM_LAUNCH_TEST_REQUEST)

    def onclick_pause(self):
        if self.pushButton_pause.text() == 'Pause':
            self.pushButton_pause.setText('Continue')
            self.serial_arduino.write(str(ARDUINO_TELEGRAM_PROGRESS_CONTROL_REQUEST(
                ARDUINO_TEST_PAUSE)).encode(encoding='UTF-8'))
        elif self.pushButton_pause.text() == 'Continue':
            self.pushButton_pause.setText('Pause')
            self.serial_arduino.write(str(ARDUINO_TELEGRAM_PROGRESS_CONTROL_REQUEST(
                ARDUINO_TEST_START)).encode(encoding='UTF-8'))

    def onclick_stop(self):
        self.receive_data_thread.stop()
        self.serial_arduino.write(str(ARDUINO_TELEGRAM_PROGRESS_CONTROL_REQUEST(
            ARDUINO_TEST_STOP)).encode(encoding='UTF-8'))
        self.serial_psoc.write(str(PSOC_TELEGRAM_DATA_SUBSCRIPTION_REQUEST(
            PSOC_DATA_UNSUBSCRIPTION)).encode(encoding='UTF-8'))
        self.textBrowser_data.append(
            '---------------------Test terminated by user!---------------------')
        self.test_stopped_callback()

    def onclick_save(self):
        try:
            root = QFileDialog.getExistingDirectory(
                self, caption='Save File', directory=os.path.join('./report'))
            if root:
                now = datetime.datetime.now().strftime('%Y%m%d_%H_%M_%S')
                test_parameter = '_'.join(
                    f'{k}={v}' for k, v in self.cache.test_parameter.items())
                folder_name = now + '_' + test_parameter
                dictionary = os.path.join(root, folder_name)
                os.mkdir(dictionary)

                self.plot1.export(path=os.path.join(
                    dictionary, self.plot1.getPlotItem().titleLabel.text + '.png'))
                self.plot2.export(path=os.path.join(
                    dictionary, self.plot2.getPlotItem().titleLabel.text + '.png'))
                self.cache.save(os.path.join(dictionary, 'data.csv'))
                self.textBrowser_data.append(
                    f'Save successfully!\nResult is saved to: {dictionary}')

        except Exception as e:
            self.textBrowser_data.append(
                f'Save failed!\n{e}')

    def test_started_callback(self):
        self.groupBox_test_configuration.setEnabled(False)
        self.pushButton_launch.setEnabled(False)
        self.pushButton_pause.setEnabled(True)
        self.pushButton_save.setEnabled(False)

    def test_stopped_callback(self):
        self.groupBox_test_configuration.setEnabled(True)
        self.pushButton_launch.setEnabled(True)
        self.pushButton_pause.setEnabled(False)
        self.pushButton_save.setEnabled(True)

    def test_finished_callback(self):
        self.serial_arduino.write(str(ARDUINO_TELEGRAM_PROGRESS_CONTROL_REQUEST(
            ARDUINO_TEST_STOP)).encode(encoding='UTF-8'))
        self.serial_psoc.write(str(PSOC_TELEGRAM_DATA_SUBSCRIPTION_REQUEST(
            PSOC_DATA_UNSUBSCRIPTION)).encode(encoding='UTF-8'))
        self.groupBox_test_configuration.setEnabled(True)
        self.pushButton_launch.setEnabled(True)
        self.pushButton_pause.setEnabled(False)
        self.pushButton_save.setEnabled(True)

    def closeEvent(self, event):
        try:
            self.serial_arduino.write(str(ARDUINO_TELEGRAM_PROGRESS_CONTROL_REQUEST(
                ARDUINO_TEST_STOP)).encode(encoding='UTF-8'))
            self.serial_psoc.write(str(PSOC_TELEGRAM_DATA_SUBSCRIPTION_REQUEST(
                PSOC_DATA_UNSUBSCRIPTION)).encode(encoding='UTF-8'))
        except:
            pass


class DataReceiver(QThread):
    update_textBroswer = pyqtSignal(str)
    update_cache = pyqtSignal(list)

    update_plot1 = pyqtSignal(float, float, float)
    update_plot2 = pyqtSignal(float, float, float)

    test_finished = pyqtSignal()

    def __init__(self, serial_setup, serial_psoc):
        super().__init__()
        self.serial_setup = serial_setup
        self.serial_psoc = serial_psoc
        self.enable = False

    def run(self):
        self.enable = True
        self.exec()

    def exec(self):
        self.serial_psoc.reset_input_buffer()
        self.serial_setup.reset_input_buffer()
        self.serial_psoc.read_until(expected=serial.LF)

        timestamp_start = time.time()
        init_resistance = None
        while self.enable:
            if self.serial_setup.in_waiting:

                msg = self.serial_setup.read_until(
                    expected=serial.LF).decode('UTF-8').strip().split(',')
                if msg[0] == ARDUINO_TELEGRAM_TYPE_LAUNCH_TEST_RESPONSE and msg[1] == ARDUINO_TEST_STOP:
                    self.update_textBroswer.emit(
                        '---------------------Test finished!---------------------')
                    self.test_finished.emit()
                    break

            if self.serial_psoc.in_waiting:
                raw_data = self.serial_psoc.read_until(
                    expected=serial.LF).decode('UTF-8')
                # print(raw_data)
                try:
                    timestamp, step, elongation, resistance, v_4pm, v_force, v_position, gain_channel, current_source_channel = self.parse_psoc_data(
                        raw_data)
                    if init_resistance == None:
                        init_resistance = resistance
                    self.update_textBroswer.emit(
                        f'timestamp: {timestamp:<12} step: {step:<12} ΔLength:{elongation:<12} resistance: {resistance:<12} v_4pm: {v_4pm:<12} v_force: {v_force:<12} v_position: {v_position:<12} gain_channel: {gain_channel:<12} current_source_channel: {current_source_channel:<12}')
                    self.update_cache.emit([timestamp, elongation, resistance])
                    self.update_plot1.emit(
                        elongation, resistance, resistance/init_resistance)
                    self.update_plot2.emit(
                        time.time() - timestamp_start, resistance, resistance/init_resistance)
                except:
                    continue

    def stop(self):
        self.enable = False

    def parse_psoc_data(self, raw_data):
        raw_data_list = raw_data.strip().split(',')
        telegram_type = int(raw_data_list[0])
        timestep = int(raw_data_list[1])
        step = int(raw_data_list[2])
        length_change = float(raw_data_list[3])
        resistance = int(raw_data_list[4])
        v_4pm = float(raw_data_list[5])
        v_force = float(raw_data_list[6])
        v_position = float(raw_data_list[7])
        gain_channel = int(raw_data_list[8])
        current_source_channel = int(raw_data_list[9])
        return timestep, step, length_change, resistance, v_4pm, v_force, v_position, gain_channel, current_source_channel


class Cache:
    def __init__(self):
        self.test_parameter = {}
        self.data = []

    def append(self, new_data):
        self.data.append(new_data)

    def save(self, path):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            f.write(','.join(f'{k}={v}' for k,
                    v in self.test_parameter.items()))
            f.write('\n')
            f.write('timestamp,elongation,R_sample')
            f.write('\n')
            writer = csv.writer(f, delimiter=',')
            writer.writerows(self.data)
            # for line in self.data:
            #     f.write(line)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StretchWindow()
    window.show()
    sys.exit(app.exec())
