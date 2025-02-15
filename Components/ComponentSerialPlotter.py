import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pyplot as plt


from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt
from Utils.Singleton import *

DISPLAY_INTERVAL = 15


@singleton
class ComponentSerialPlotter(QWidget):
    def __init__(self):
        super().__init__()

        self.pyplotFig2D = plt.figure()

        self.pyplotFig2D_axes_accel = self.pyplotFig2D.add_subplot(311)
        self.pyplotFig2D_axes_accel.grid(True)

        self.pyplotFig2D_axes_gyro = self.pyplotFig2D.add_subplot(312, sharex=self.pyplotFig2D_axes_accel)
        self.pyplotFig2D_axes_gyro.grid(True)

        self.pyplotFig2D_axes_mag = self.pyplotFig2D.add_subplot(313, sharex=self.pyplotFig2D_axes_accel)
        self.pyplotFig2D_axes_mag.grid(True)

        self.__widget_Fig2D__ = FigureCanvasQTAgg(self.pyplotFig2D)
        self.__widget_Toolbar__ = NavigationToolbar2QT(self.__widget_Fig2D__, self)

        layout = QVBoxLayout()
        layout.addWidget(self.__widget_Toolbar__)
        layout.addWidget(self.__widget_Fig2D__)


        self.setLayout(layout)


    def plotMagData(self, Time=[], RawData_MagX=[], RawData_MagY=[], RawData_MagZ=[]):
        self.pyplotFig2D_axes_mag.cla()
        self.pyplotFig2D_axes_mag.plot(Time, RawData_MagX, label='MagX')
        self.pyplotFig2D_axes_mag.plot(Time, RawData_MagY, label='MagY')
        self.pyplotFig2D_axes_mag.plot(Time, RawData_MagZ, label='MagZ')
        self.pyplotFig2D_axes_mag.grid(True)
        self.pyplotFig2D_axes_mag.legend()

        lim_max = Time[-1]
        if lim_max - DISPLAY_INTERVAL > 0:
            lim_min = lim_max - DISPLAY_INTERVAL
        else:
            lim_min = 0
        self.pyplotFig2D_axes_mag.set_xlim([lim_min, lim_max])
        self.__widget_Fig2D__.draw()