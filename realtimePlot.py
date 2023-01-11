import time
from collections import deque
import numpy as np


import pyqtgraph as pg
import pyqtgraph.exporters


class Float2:
    x = 0.0
    y = 0.0

    def __init__(self, history_size=1000):
        self.x_history = deque([], history_size)
        self.y_history = deque([], history_size)

    def set_data(self, x, y):
        self.x = x
        self.y = y
        self.x_history.append(self.x)
        self.y_history.append(self.y)

    def clear(self):
        self.x = 0.0
        self.y = 0.0
        self.x_history.clear()
        self.y_history.clear()


class Float3:
    x = 0.0
    y = 0.0
    z = 0.0

    def __init__(self, history_size=1000):
        self.x_history = deque([], history_size)
        self.y_history = deque([], history_size)
        self.z_history = deque([], history_size)

    def set_data(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.x_history.append(self.x)
        self.y_history.append(self.y)
        self.z_history.append(self.z)

    def clear(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.x_history.clear()
        self.y_history.clear()
        self.z_history.clear()


class ScatterPlot(pg.PlotWidget):
    def __init__(self, xlabel_text=None, ylabel_text=None, xlabel_unit=None, ylabel_unit=None, history_size=1000, **kargs):
        super().__init__(**kargs)
        # self.setXRange(0, 200)
        # self.setYRange(0, 3)
        self.setLabel(axis='bottom', text=xlabel_text, units=xlabel_unit)
        self.setLabel(axis='left', text=ylabel_text, units=ylabel_unit)
        self.showGrid(x=True, y=True, alpha=0.5)

        self.update_enable = True
        self.data = Float2(history_size)
        self.time_last_frame = 0

    def update(self, x, y):
        self.data.set_data(x, y)
        if self.update_enable:
            time_now = time.time()
            if time_now - self.time_last_frame > 0.03:
                self.time_last_frame = time_now

                t1 = time.time()
                self.clear()
                scatter = pg.ScatterPlotItem(pxMode=True)
                # scatter_colors = []
                # for i in range(len(X)): scatter_colors.append((255, 255, 255, int(i / len(X) * 255)))
                scatter.setData(
                    x=self.data.x_history, y=self.data.y_history, pen=None, symbol='x', brush='w')
                self.addItem(scatter)
                t2 = time.time()
                # print(t2-t1)

    def set_update_enable(self, status):
        self.update_enable = status

    def reset(self):
        self.clear()
        self.data.clear()


class LinePlot(pg.PlotWidget):
    def __init__(self, xlabel_text=None, ylabel_text=None, xlabel_unit=None, ylabel_unit=None, history_size=1000, **kargs):
        super().__init__(**kargs)
        # self.setXRange(0, 200)
        # self.setYRange(0, 3)
        self.setLabel(axis='bottom', text=xlabel_text, units=xlabel_unit)
        self.setLabel(axis='left', text=ylabel_text, units=ylabel_unit)
        self.showGrid(x=True, y=True, alpha=0.5)

        self.update_enable = True
        self.data = Float2(history_size)
        self.time_last_frame = 0

    def update(self, x, y):
        self.data.set_data(x, y)
        if self.update_enable:
            time_now = time.time()
            if time_now - self.time_last_frame > 0.03:
                self.time_last_frame = time_now

                t1 = time.time()
                self.clear()
                self.plot(x=self.data.x_history, y=self.data.y_history)
                t2 = time.time()
                # print(t2-t1)

    def set_update_enable(self, enable):
        self.update_enable = enable

    def reset(self):
        self.clear()
        self.data.clear()


class ScatterPlot2Y(pg.PlotWidget):
    def __init__(self, xlabel_text=None, xlabel_unit=None, ylabel1_text=None, ylabel1_unit=None, ylabel2_text=None, ylabel2_unit=None, show_y='y1', history_size=1000, **kargs):
        super().__init__(**kargs)

        self.ylabel1_text = ylabel1_text
        self.ylabel1_unit = ylabel1_unit
        self.ylabel2_text = ylabel2_text
        self.ylabel2_unit = ylabel2_unit
        self.show_y = 'y1'

        self.setLabel(axis='bottom', text=xlabel_text, units=xlabel_unit)
        if show_y == 'y1':
            self.setLabel(axis='left', text=ylabel1_text, units=ylabel1_unit)
        elif show_y == 'y2':
            self.setLabel(axis='left', text=ylabel2_text, units=ylabel2_unit)
        self.showGrid(x=True, y=True, alpha=0.5)

        self.update_enable = True
        self.data = Float3(history_size)
        self.time_last_frame = 0

    def refresh(self):
        self.clear()
        scatter = pg.ScatterPlotItem(pxMode=True)
        # scatter_colors = []
        # for i in range(len(X)): scatter_colors.append((255, 255, 255, int(i / len(X) * 255)))
        if self.show_y == 'y1':
            scatter.setData(
                x=self.data.x_history, y=self.data.y_history, pen=None, symbol='x', brush='w')
        elif self.show_y == 'y2':
            scatter.setData(
                x=self.data.x_history, y=self.data.z_history, pen=None, symbol='x', brush='w')
        self.addItem(scatter)

    def update(self, x, y1, y2):
        self.data.set_data(x, y1, y2)
        if self.update_enable:
            time_now = time.time()
            if time_now - self.time_last_frame > 0.03:
                self.time_last_frame = time_now

                t1 = time.time()
                self.refresh()
                t2 = time.time()
                # print(t2-t1)

    def set_update_enable(self, status):
        self.update_enable = status

    def set_show_y(self, show_y):
        if show_y == 'y1':
            self.show_y = show_y
            self.setLabel(axis='left', text=self.ylabel1_text,
                          units=self.ylabel1_unit)
        elif show_y == 'y2':
            self.show_y = show_y
            self.setLabel(axis='left', text=self.ylabel2_text,
                          units=self.ylabel2_unit)
        self.refresh()

    def reset(self):
        self.clear()
        self.data.clear()
        self.refresh()

    def export(self, path):
        pg.exporters.ImageExporter(self.plotItem).export(path)


class LinePlot2Y(pg.PlotWidget):
    def __init__(self, xlabel_text=None, xlabel_unit=None, ylabel1_text=None, ylabel1_unit=None, ylabel2_text=None, ylabel2_unit=None, show_y='y1', history_size=1000, **kargs):
        super().__init__(**kargs)

        self.ylabel1_text = ylabel1_text
        self.ylabel1_unit = ylabel1_unit
        self.ylabel2_text = ylabel2_text
        self.ylabel2_unit = ylabel2_unit
        self.show_y = 'y1'

        self.setLabel(axis='bottom', text=xlabel_text, units=xlabel_unit)
        if show_y == 'y1':
            self.setLabel(axis='left', text=ylabel1_text, units=ylabel1_unit)
        elif show_y == 'y2':
            self.setLabel(axis='left', text=ylabel2_text, units=ylabel2_unit)
        self.showGrid(x=True, y=True, alpha=0.5)

        self.update_enable = True
        self.data = Float3(history_size)
        self.time_last_frame = 0

    def refresh(self):
        self.clear()
        if self.show_y == 'y1':
            self.plot(x=self.data.x_history, y=self.data.y_history)
        elif self.show_y == 'y2':
            self.plot(x=self.data.x_history, y=self.data.z_history)

    def update(self, x, y1, y2):
        self.data.set_data(x, y1, y2)
        if self.update_enable:
            time_now = time.time()
            if time_now - self.time_last_frame > 0.03:
                self.time_last_frame = time_now
                t1 = time.time()
                self.refresh()
                t2 = time.time()
                # print(t2-t1)

    def set_update_enable(self, status):
        self.update_enable = status

    def set_show_y(self, show_y):
        if show_y == 'y1':
            self.show_y = show_y
            self.setLabel(axis='left', text=self.ylabel1_text,
                          units=self.ylabel1_unit)
        elif show_y == 'y2':
            self.show_y = show_y
            self.setLabel(axis='left', text=self.ylabel2_text,
                          units=self.ylabel2_unit)

        self.refresh()

    def reset(self):
        self.clear()
        self.data.clear()
        self.refresh()

    def export(self, path):
        pg.exporters.ImageExporter(self.plotItem).export(path)
