import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pyplot as plt


from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt
from Utils.Singleton import *

DISPLAY_INTERVAL = 30
LINE_WIDTH = 1


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


        self.linesRawAccelX, = self.pyplotFig2D_axes_accel.plot([], [], '-r', label='AccelX', lw=LINE_WIDTH)
        self.linesRawAccelY, = self.pyplotFig2D_axes_accel.plot([], [], '-g', label='AccelY', lw=LINE_WIDTH)
        self.linesRawAccelZ, = self.pyplotFig2D_axes_accel.plot([], [], '-b', label='AccelZ', lw=LINE_WIDTH)

        self.linesRawGyroX, = self.pyplotFig2D_axes_gyro.plot([], [], '-r', label='GyroX', lw=LINE_WIDTH)
        self.linesRawGyroY, = self.pyplotFig2D_axes_gyro.plot([], [], '-g', label='GyroY', lw=LINE_WIDTH)
        self.linesRawGyroZ, = self.pyplotFig2D_axes_gyro.plot([], [], '-b', label='GyroZ', lw=LINE_WIDTH)

        self.linesRawMagX, = self.pyplotFig2D_axes_mag.plot([], [], '-r', label='MagX', lw=LINE_WIDTH)
        self.linesRawMagY, = self.pyplotFig2D_axes_mag.plot([], [], '-g', label='MagY', lw=LINE_WIDTH)
        self.linesRawMagZ, = self.pyplotFig2D_axes_mag.plot([], [], '-b', label='MagZ', lw=LINE_WIDTH)


    def plotAllData(self, 
        Time=[], 
        RawData_AccelX=[], RawData_AccelY=[], RawData_AccelZ=[], 
        RawData_GyroX=[], RawData_GyroY=[], RawData_GyroZ=[], 
        RawData_MagX=[], RawData_MagY=[], RawData_MagZ=[]):

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

        self.linesRawGyroX.set_ydata(RawData_GyroX)
        self.linesRawGyroX.set_xdata(Time)
        self.linesRawGyroY.set_ydata(RawData_GyroY)
        self.linesRawGyroY.set_xdata(Time)
        self.linesRawGyroZ.set_ydata(RawData_GyroZ)
        self.linesRawGyroZ.set_xdata(Time)
        self.pyplotFig2D_axes_gyro.relim()
        self.pyplotFig2D_axes_gyro.autoscale_view()
        self.pyplotFig2D_axes_gyro.legend()

        self.linesRawAccelX.set_ydata(RawData_AccelX)
        self.linesRawAccelX.set_xdata(Time)
        self.linesRawAccelY.set_ydata(RawData_AccelY)
        self.linesRawAccelY.set_xdata(Time)
        self.linesRawAccelZ.set_ydata(RawData_AccelZ)
        self.linesRawAccelZ.set_xdata(Time)
        self.pyplotFig2D_axes_accel.relim()
        self.pyplotFig2D_axes_accel.autoscale_view()
        self.pyplotFig2D_axes_accel.legend()

        lim_max = Time[-1]
        if lim_max - DISPLAY_INTERVAL > 0:
            lim_min = lim_max - DISPLAY_INTERVAL
        else:
            lim_min = 0
        self.pyplotFig2D_axes_mag.set_xlim([lim_min, lim_max])

        self.__widget_Fig2D__.draw()
