import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pyplot as plt


from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt
from Utils.Singleton import *

from GUI.Config.Config_Widget import *


@singleton
class ComponentImuDataPlotter(QWidget):
    def __init__(self):
        super().__init__()

        # Create figure and axes. All axes share horizontal axis.
        self.pyplotFig2D, (self.pyplotFig2D_axes_accel, self.pyplotFig2D_axes_gyro, self.pyplotFig2D_axes_mag) = plt.subplots(3, 1, sharex=True)


        # Configure axes of accel, gyro and mag
        self.pyplotFig2D_axes_accel.grid(True)
        self.pyplotFig2D_axes_accel.set_title("Accelerometer")

        self.pyplotFig2D_axes_gyro.grid(True)
        self.pyplotFig2D_axes_gyro.set_title("Gyroscope")

        self.pyplotFig2D_axes_mag.grid(True)
        self.pyplotFig2D_axes_mag.set_title("Magnetometer")

        # Create lines
        self.linesRawAccelX, = self.pyplotFig2D_axes_accel.plot([], [], '-r', label='AccelX', lw=FIGURE_LINE_WIDTH)
        self.linesRawAccelY, = self.pyplotFig2D_axes_accel.plot([], [], '-g', label='AccelY', lw=FIGURE_LINE_WIDTH)
        self.linesRawAccelZ, = self.pyplotFig2D_axes_accel.plot([], [], '-b', label='AccelZ', lw=FIGURE_LINE_WIDTH)

        self.linesRawGyroX, = self.pyplotFig2D_axes_gyro.plot([], [], '-r', label='GyroX', lw=FIGURE_LINE_WIDTH)
        self.linesRawGyroY, = self.pyplotFig2D_axes_gyro.plot([], [], '-g', label='GyroY', lw=FIGURE_LINE_WIDTH)
        self.linesRawGyroZ, = self.pyplotFig2D_axes_gyro.plot([], [], '-b', label='GyroZ', lw=FIGURE_LINE_WIDTH)

        self.linesRawMagX, = self.pyplotFig2D_axes_mag.plot([], [], '-r', label='MagX', lw=FIGURE_LINE_WIDTH)
        self.linesRawMagY, = self.pyplotFig2D_axes_mag.plot([], [], '-g', label='MagY', lw=FIGURE_LINE_WIDTH)
        self.linesRawMagZ, = self.pyplotFig2D_axes_mag.plot([], [], '-b', label='MagZ', lw=FIGURE_LINE_WIDTH)


        # Configure Qt canvas and toolbar
        self.__widget_Fig2D__ = FigureCanvasQTAgg(self.pyplotFig2D)
        self.__widget_Toolbar__ = NavigationToolbar2QT(self.__widget_Fig2D__, self)


        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__widget_Toolbar__)
        layout.addWidget(self.__widget_Fig2D__)
        self.setLayout(layout)

    # Type of "ImuData" is np.array
    def plot(self, ImuData):
        # Mapping data
        Time = ImuData[:,0]
        AccelX = ImuData[:,1]
        AccelY = ImuData[:,2]
        AccelZ = ImuData[:,3]
        GyroX = ImuData[:,4]
        GyroY = ImuData[:,5]
        GyroZ = ImuData[:,6]
        MagX = ImuData[:,7]
        MagY = ImuData[:,8]
        MagZ = ImuData[:,9]

        self.linesRawAccelX.set_ydata(AccelX)
        self.linesRawAccelX.set_xdata(Time)
        self.linesRawAccelY.set_ydata(AccelY)
        self.linesRawAccelY.set_xdata(Time)
        self.linesRawAccelZ.set_ydata(AccelZ)
        self.linesRawAccelZ.set_xdata(Time)
        self.pyplotFig2D_axes_accel.relim()
        self.pyplotFig2D_axes_accel.autoscale_view()
        self.pyplotFig2D_axes_accel.legend()

        self.linesRawGyroX.set_ydata(GyroX)
        self.linesRawGyroX.set_xdata(Time)
        self.linesRawGyroY.set_ydata(GyroY)
        self.linesRawGyroY.set_xdata(Time)
        self.linesRawGyroZ.set_ydata(GyroZ)
        self.linesRawGyroZ.set_xdata(Time)
        self.pyplotFig2D_axes_gyro.relim()
        self.pyplotFig2D_axes_gyro.autoscale_view()
        self.pyplotFig2D_axes_gyro.legend()

        self.linesRawMagX.set_ydata(MagX)
        self.linesRawMagX.set_xdata(Time)
        self.linesRawMagY.set_ydata(MagY)
        self.linesRawMagY.set_xdata(Time)
        self.linesRawMagZ.set_ydata(MagZ)
        self.linesRawMagZ.set_xdata(Time)
        self.pyplotFig2D_axes_mag.relim()
        self.pyplotFig2D_axes_mag.autoscale_view()
        self.pyplotFig2D_axes_mag.legend()

        self.pyplotFig2D_axes_mag.set_title("Magnetometer")

        lim_max = Time[-1]
        if lim_max - FIGURE_DISPLAY_INTERVAL > 0:
            lim_min = lim_max - FIGURE_DISPLAY_INTERVAL
        else:
            lim_min = 0
        self.pyplotFig2D_axes_mag.set_xlim([lim_min, lim_max+FIGURE_DISPLAY_EXTENDED_DURRATION])

        self.__widget_Fig2D__.draw()
