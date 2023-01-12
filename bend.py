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
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from pathlib import Path
from realtimePlot import *
from bend_protocol import *

didyoucheck = 0
contacts = 1

class BendWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("C:/Users/Messknecht/OneDrive - tu-braunschweig.de/Desktop/Bend_aktuell/final_modified/ui/bendWindow.ui", self)  # load the ui file

        # Data cache initialzation
        self.cache = Cache()
        self.savew = Savebynumber()
        self.contexplain = ContactExplain()

        # Serial prot initialzation
        self.serial_arduino = serial.Serial()
        self.serial_psoc = serial.Serial()

        # Graph initialization
        self.plot1 = ScatterPlot2Y(xlabel_text='Step', xlabel_unit=None,
                                   ylabel1_text='R', ylabel1_unit='Ohm',
                                   ylabel2_text='R/R0', ylabel2_unit=None,
                                   show_y='y1',
                                   history_size=2500,
                                   title='R_longitudinal-Step')

        self.plot2 = LinePlot2Y(xlabel_text='Time', xlabel_unit='s',
                                ylabel1_text='R', ylabel1_unit='Ohm',
                                ylabel2_text='R/R0', ylabel2_unit=None,
                                show_y='y1',
                                history_size=2500,
                                title='R_longitudinal-Time')

        self.plot3 = ScatterPlot2Y(xlabel_text='Step', xlabel_unit=None,
                                   ylabel1_text='R', ylabel1_unit='Ohm',
                                   ylabel2_text='R/R0', ylabel2_unit=None,
                                   show_y='y1',
                                   history_size=2500,
                                   title='R_lateral-Step')

        self.plot4 = LinePlot2Y(xlabel_text='Time', xlabel_unit='s',
                                ylabel1_text='R', ylabel1_unit='Ohm',
                                ylabel2_text='R/R0', ylabel2_unit=None,
                                show_y='y1',
                                history_size=2500,
                                title='R_lateral-Time')

        self.plot_area1.setLayout(QVBoxLayout())
        self.plot_area1.layout().addWidget(self.plot1)
        self.plot_area2.setLayout(QVBoxLayout())
        self.plot_area2.layout().addWidget(self.plot2)
        self.plot_area3.setLayout(QVBoxLayout())
        self.plot_area3.layout().addWidget(self.plot3)
        self.plot_area4.setLayout(QVBoxLayout())
        self.plot_area4.layout().addWidget(self.plot4)


        # Button configuration
        self.pushButton_connect.clicked.connect(self.onclick_connect)
        self.pushButton_contacts.clicked.connect(self.explaincontacts)
        self.pushButton_refresh.clicked.connect(self.onclick_refresh)
        self.pushButton_launch.clicked.connect(self.onclick_launch)
        self.pushButton_stop.clicked.connect(self.onclick_stop)
        self.pushButton_spchange.clicked.connect(self.toggle_saveWindow)
        self.pushButton_save.clicked.connect(self.onclick_save)
        self.pushButton_pause.clicked.connect(self.onclick_pause)
        self.pushButton_clear_text.clicked.connect(self.textBrowser_data.clear)
        self.pushButton_clear_graph.clicked.connect(
            lambda: [self.plot1.reset(), self.plot2.reset(), self.plot3.reset(), self.plot4.reset()])

        # Check box configuration
        self.checkBox_graph1.stateChanged.connect(
            lambda state: [self.plot_area1.hide(), self.plot1.set_update_enable(False)] if state == 0 else [self.plot_area1.show(), self.plot1.set_update_enable(True)])
        self.checkBox_graph2.stateChanged.connect(
            lambda state: [self.plot_area2.hide(), self.plot2.set_update_enable(False)] if state == 0 else [self.plot_area2.show(), self.plot2.set_update_enable(True)])
        self.checkBox_graph3.stateChanged.connect(
            lambda state: [self.plot_area3.hide(), self.plot3.set_update_enable(False)] if state == 0 else [self.plot_area3.show(), self.plot3.set_update_enable(True)])
        self.checkBox_graph4.stateChanged.connect(
            lambda state: [self.plot_area4.hide(), self.plot4.set_update_enable(False)] if state == 0 else [self.plot_area4.show(), self.plot4.set_update_enable(True)])

        # Radion button configuration
        self.radioButton_RS_long_abs.toggled.connect(
            lambda checked: self.plot1.set_show_y('y1') if checked else None)
        self.radioButton_RS_long_rel.toggled.connect(
            lambda checked: self.plot1.set_show_y('y2') if checked else None)
        self.radioButton_RT_long_abs.toggled.connect(
            lambda checked: self.plot2.set_show_y('y1') if checked else None)
        self.radioButton_RT_long_rel.toggled.connect(
            lambda checked: self.plot2.set_show_y('y2') if checked else None)
        self.radioButton_RS_lat_abs.toggled.connect(
            lambda checked: self.plot3.set_show_y('y1') if checked else None)
        self.radioButton_RS_lat_rel.toggled.connect(
            lambda checked: self.plot3.set_show_y('y2') if checked else None)
        self.radioButton_RT_lat_abs.toggled.connect(
            lambda checked: self.plot4.set_show_y('y1') if checked else None)
        self.radioButton_RT_lat_rel.toggled.connect(
            lambda checked: self.plot4.set_show_y('y2') if checked else None)

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
        global contacts
        bending_direction = self.comboBox_direction.currentIndex()
        bending_speed = self.spinBox_speed.value()  # in r/min
        cycles = self.spinBox_cycles.value()
        steps = self.spinBox_steps.value()
        contacts = self.spinBox_contacts.value()
        self.serial_arduino.write(bytes(str(ARDUINO_TELEGRAM_SET_PARAMETER_REQUEST(
            bending_direction=bending_direction, bending_speed=bending_speed, cycles=cycles, steps=steps)), 'UTF-8'))

        sample_rate = self.spinBox_sample_rate.value()
        downsample = self.spinBox_downsample.value()
        reference_channel = self.comboBox_reference.currentIndex() - 1
        self.serial_psoc.write(bytes(str(PSOC_TELEGRAM_SET_PARAMETER_REQUEST(
            sample_rate=sample_rate, downsample=downsample, reference_channel=reference_channel)), 'UTF-8'))

        self.cache = Cache()

        self.cache.test_parameter = {'bending_direction': bending_direction,
                                     'bending_speed': bending_speed,
                                     'cycles': cycles,
                                     'steps': steps,
                                     'contacts': contacts,
                                     'sample_rate': sample_rate,
                                     'downsample': downsample,
                                     'reference': self.comboBox_reference.currentText(), }

        self.plot1.reset()
        self.plot2.reset()
        self.plot3.reset()
        self.plot4.reset()

        self.receive_data_thread = DataReceiver(
            self.serial_arduino, self.serial_psoc)
        self.receive_data_thread.update_textBroswer.connect(
            lambda data: self.textBrowser_data.append(data))
        self.receive_data_thread.update_cache.connect(
            lambda data: self.cache.append(data))
        self.receive_data_thread.update_plot1.connect(self.plot1.update)
        self.receive_data_thread.update_plot2.connect(self.plot2.update)
        self.receive_data_thread.update_plot3.connect(self.plot3.update)
        self.receive_data_thread.update_plot4.connect(self.plot4.update)
        self.receive_data_thread.test_finished.connect(
            self.test_stopped_callback)

        self.receive_data_thread.start()
        self.test_started_callback()

        self.serial_psoc.write(str(PSOC_TELEGRAM_DATA_SUBSCRIPTION_REQUEST(PSOC_DATA_SUBSCRIPTION)).encode(encoding='UTF-8'))
        self.serial_arduino.write(ARDUINO_TELEGRAM_LAUNCH_TEST_REQUEST)

    def onclick_pause(self):
        if self.pushButton_pause.text() == 'Pause':
            self.pushButton_pause.setText('Continue')
            self.serial_arduino.write(str(ARDUINO_TELEGRAM_PROGRESS_CONTROL_REQUEST(ARDUINO_TEST_PAUSE)).encode(encoding='UTF-8'))
            # self.serial_psoc.write(PSOC_TELEGRAM_DATA_UNSUBSCRIPTION_REQUEST)
        elif self.pushButton_pause.text() == 'Continue':
            self.pushButton_pause.setText('Pause')
            self.serial_arduino.write(str(ARDUINO_TELEGRAM_PROGRESS_CONTROL_REQUEST(ARDUINO_TEST_START)).encode(encoding='UTF-8'))
            # self.serial_psoc.write(PSOC_TELEGRAM_DATA_SUBSCRIPTION_REQUEST)

    def onclick_stop(self):
        self.receive_data_thread.stop()
        self.serial_arduino.write(str(ARDUINO_TELEGRAM_PROGRESS_CONTROL_REQUEST(ARDUINO_TEST_STOP)).encode(encoding='UTF-8'))
        self.serial_psoc.write(str(PSOC_TELEGRAM_DATA_SUBSCRIPTION_REQUEST(PSOC_DATA_UNSUBSCRIPTION)).encode(encoding='UTF-8'))
        self.textBrowser_data.append(
            '---------------------Test terminated by user!---------------------')
        self.test_stopped_callback()

    def onclick_save(self):
        global didyoucheck
        if didyoucheck == 0:
            self.toggle_saveWindow()
        else:
            didyoucheck=0
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
                    self.plot3.export(path=os.path.join(
                        dictionary, self.plot3.getPlotItem().titleLabel.text + '.png'))
                    self.plot4.export(path=os.path.join(
                        dictionary, self.plot4.getPlotItem().titleLabel.text + '.png'))
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
        self.serial_arduino.write(str(ARDUINO_TELEGRAM_PROGRESS_CONTROL_REQUEST(ARDUINO_TEST_STOP)).encode(encoding='UTF-8'))
        self.serial_psoc.write(str(PSOC_TELEGRAM_DATA_SUBSCRIPTION_REQUEST(PSOC_DATA_UNSUBSCRIPTION)).encode(encoding='UTF-8'))
        self.groupBox_test_configuration.setEnabled(True)
        self.pushButton_launch.setEnabled(True)
        self.pushButton_pause.setEnabled(False)
        self.pushButton_save.setEnabled(True)

    def toggle_saveWindow(self):
        print(self.savew.sample_parameter)
        if self.savew.isVisible():
            self.savew.hide()

        else:
            self.savew.show()

    def explaincontacts(self, checked):
        if self.contexplain.isVisible():
            self.contexplain.hide()

        else:
            self.contexplain.show()

    def closeEvent(self, event):
        try:
            self.serial_arduino.write(str(ARDUINO_TELEGRAM_PROGRESS_CONTROL_REQUEST(ARDUINO_TEST_STOP)).encode(encoding='UTF-8'))
            self.serial_psoc.write(str(PSOC_TELEGRAM_DATA_SUBSCRIPTION_REQUEST(PSOC_DATA_UNSUBSCRIPTION)).encode(encoding='UTF-8'))
        except:
            pass


class DataReceiver(QThread):
    update_textBroswer = pyqtSignal(str)
    update_cache = pyqtSignal(list)

    update_plot1 = pyqtSignal(float, float, float)
    update_plot2 = pyqtSignal(float, float, float)
    update_plot3 = pyqtSignal(float, float, float)
    update_plot4 = pyqtSignal(float, float, float)

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
        init_R_longitudinal = None
        init_R_lateral = None
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
                    timestamp, step, R_longitudinal, R_lateral, V_longitudinal, V_lateral, V_reference, reference_channel = self.parse_psoc_data(
                        raw_data)
                    if init_R_longitudinal == None:
                        init_R_longitudinal = R_longitudinal
                    if init_R_lateral == None:
                        init_R_lateral = R_lateral

                    self.update_textBroswer.emit(
                        f'timestamp: {timestamp:<7} step: {step:<5} R_longitudinal: {R_longitudinal:<12} R_longitudinal: {R_lateral:<12} V_longitudinal: {V_longitudinal:<12} V_lateral: {V_lateral:<12} V_reference: {V_reference:<12} reference_channel: {reference_channel:<5}')
                    self.update_cache.emit([timestamp, step, R_longitudinal, R_lateral])
                    self.update_plot1.emit(
                        step, R_longitudinal, R_longitudinal/init_R_longitudinal)
                    self.update_plot2.emit(
                        time.time() - timestamp_start, R_longitudinal, R_longitudinal/init_R_longitudinal)
                    self.update_plot3.emit(
                        step, R_lateral, R_lateral/init_R_lateral)
                    self.update_plot4.emit(
                        time.time() - timestamp_start, R_lateral, R_lateral/init_R_lateral)
                except Exception as e:
                    print(e)
                    continue

    def stop(self):
        self.enable = False

    def parse_psoc_data(self, raw_data):
        raw_data_list = raw_data.strip().split(',')
        # print(raw_data_list)
        telegram_type = raw_data_list[0]
        timestamp = int(raw_data_list[1])
        step = int(raw_data_list[2])
        R_longitudinal = int(raw_data_list[3])
        R_lateral = int(raw_data_list[4])
        V_longitudinal = float(raw_data_list[5])
        V_lateral = float(raw_data_list[6])
        V_reference = float(raw_data_list[7])
        reference_channel = int(raw_data_list[8])
        return timestamp, step, R_longitudinal, R_lateral, V_longitudinal, V_lateral, V_reference, reference_channel


class Savebynumber(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("C:/Users/Messknecht/OneDrive - tu-braunschweig.de/Desktop/Bend_aktuell/final_modified/ui/saveform.ui",self)
        #self.load_ui()
        self.sample_parameter= {}

        #Button configuration
        self.pushButton_Save.clicked.connect(self.onclick_newsave)

    def load_ui(self):
        loader = QUiLoader()
        path = "C:/Users/Messknecht/OneDrive - tu-braunschweig.de/Desktop/Bend_aktuell/final_modified/ui/saveform.ui"
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()

    def onclick_newsave(self):
        global didyoucheck
        project = self.spinBox_Project.value()
        design = self.spinBox_Design.value()
        sample = self.spinBox_Sample.value()
        material = self.spinBox_Material.value()
        characteristics = self.spinBox_Characteristics.value()
        orientation = self.spinBox_Orientation.value()
        a_Parameter = self.spinBox_APara.value()
        b_Parameter = self.spinBox_BPara.value()
        f_Parameter = self.spinBox_FPara.value()
        g_Parameter = self.spinBox_GPara.value()
        self.sample_parameter = {'Project': project,
                                     'Design': design,
                                     'Sample': sample,
                                     'Material': material,
                                     'Print Characteristics': characteristics,
                                     'Orientation': orientation,
                                     'A-Parameter': a_Parameter,
                                     'B_Parameter': b_Parameter,
                                     'C_Parameter': f_Parameter,
                                     'D_Parameter': g_Parameter,}
        print(self.sample_parameter)
        didyoucheck = 1
    
class ContactExplain(QWidget):
    def __init__(self):
        super().__init__()
        self.load_ui()

    def load_ui(self):
        loader = QUiLoader()
        path = "C:/Users/Messknecht/OneDrive - tu-braunschweig.de/Desktop/Bend_aktuell/final_modified/ui/contactexplain.ui"
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()   


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
            f.write('timestamp,step,R_longitudianl,R_lateral')
            f.write('\n')
            writer = csv.writer(f, delimiter=',')
            writer.writerows(self.data)
            # for line in self.data:
            #     f.write(line)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BendWindow()
    window.show()
    sys.exit(app.exec())
