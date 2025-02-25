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

        self.pyplotFig2D, (self.pyplotFig2D_axes_accel, self.pyplotFig2D_axes_gyro, self.pyplotFig2D_axes_mag) = plt.subplots(3, 1, sharex=True)

        # self.pyplotFig2D = plt.figure()

        # self.pyplotFig2D_axes_accel = self.pyplotFig2D.add_subplot(311)
        self.pyplotFig2D_axes_accel.grid(True)
        self.pyplotFig2D_axes_accel.set_title("Accelerometer")

        # self.pyplotFig2D_axes_gyro = self.pyplotFig2D.add_subplot(312, sharex=self.pyplotFig2D_axes_accel)
        self.pyplotFig2D_axes_gyro.grid(True)
        self.pyplotFig2D_axes_gyro.set_title("Gyroscope")

        # self.pyplotFig2D_axes_mag = self.pyplotFig2D.add_subplot(313, sharex=self.pyplotFig2D_axes_accel)
        self.pyplotFig2D_axes_mag.grid(True)
        self.pyplotFig2D_axes_mag.set_title("Magnetometer")

        self.__widget_Fig2D__ = FigureCanvasQTAgg(self.pyplotFig2D)
        self.__widget_Toolbar__ = NavigationToolbar2QT(self.__widget_Fig2D__, self)

        layout = QVBoxLayout()
        
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__widget_Toolbar__)
        layout.addWidget(self.__widget_Fig2D__)


        self.setLayout(layout)

        self.linesRawMagX, = self.pyplotFig2D_axes_mag.plot([], [], '-r', label='MagX')
        self.linesRawMagY, = self.pyplotFig2D_axes_mag.plot([], [], '-g', label='MagY')
        self.linesRawMagZ, = self.pyplotFig2D_axes_mag.plot([], [], '-b', label='MagZ')


    def plotMagData(self, Time=[], RawData_MagX=[], RawData_MagY=[], RawData_MagZ=[]):
        self.pyplotFig2D_axes_mag.set_title("Magnetometer")


        self.linesRawMagX.set_ydata(RawData_MagX)
        self.linesRawMagX.set_xdata(Time)
        self.linesRawMagY.set_ydata(RawData_MagY)
        self.linesRawMagY.set_xdata(Time)
        self.linesRawMagZ.set_ydata(RawData_MagZ)
        self.linesRawMagZ.set_xdata(Time)
        self.pyplotFig2D_axes_mag.relim()
        self.pyplotFig2D_axes_mag.autoscale_view()
        self.pyplotFig2D_axes_mag.legend()

        lim_max = Time[-1]
        if lim_max - DISPLAY_INTERVAL > 0:
            lim_min = lim_max - DISPLAY_INTERVAL
        else:
            lim_min = 0
        self.pyplotFig2D_axes_mag.set_xlim([lim_min, lim_max])

        self.__widget_Fig2D__.draw()

