import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pyplot as plt


from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt
from Utils.Singleton import *

from GUI.Config.Config_Widget import *

@singleton
class ComponentAltitudePlotter(QWidget):
    def __init__(self):
        super().__init__()

        # Create figure and axes. All axes share horizontal axis.
        self.pyplotFig2D, (self.pyplotFig2D_axes_baro, self.pyplotFig2D_axes_altitude) = plt.subplots(2, 1, sharex=True)

        # Configure axes of accel, gyro and mag
        self.__configFig2D_Data__()

        # Create lines
        self.linesBaro, = self.pyplotFig2D_axes_baro.plot([], [], '-r', label='Baro', lw=FIGURE_LINE_WIDTH)
        self.linesAltitude, = self.pyplotFig2D_axes_altitude.plot([], [], '-r', label='Altitude', lw=FIGURE_LINE_WIDTH)

        # Configure Qt canvas and toolbar
        self.__widget_Fig2D__ = FigureCanvasQTAgg(self.pyplotFig2D)
        self.__widget_Toolbar__ = NavigationToolbar2QT(self.__widget_Fig2D__, self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__widget_Toolbar__)
        layout.addWidget(self.__widget_Fig2D__)
        self.setLayout(layout)

    def __configFig2D_Data__(self):
        self.pyplotFig2D_axes_baro.grid(True)
        self.pyplotFig2D_axes_baro.set_title("Barometer")

        self.pyplotFig2D_axes_altitude.grid(True)
        self.pyplotFig2D_axes_altitude.set_title("Altitude")

    # Type of "ImuData" is np.array
    def plot(self, ImuData):
        # Mapping data
        Time = ImuData[:,0]
        Baro = ImuData[:,1]
        Altitude = ImuData[:,2]

        self.linesBaro.set_ydata(Baro)
        self.linesBaro.set_xdata(Time)
        self.pyplotFig2D_axes_baro.relim()
        self.pyplotFig2D_axes_baro.autoscale_view()
        self.pyplotFig2D_axes_baro.legend()

        self.linesAltitude.set_ydata(Altitude)
        self.linesAltitude.set_xdata(Time)
        self.pyplotFig2D_axes_altitude.relim()
        self.pyplotFig2D_axes_altitude.autoscale_view()
        self.pyplotFig2D_axes_altitude.legend()

        lim_max = Time[-1]
        if lim_max - FIGURE_DISPLAY_INTERVAL > 0:
            lim_min = lim_max - FIGURE_DISPLAY_INTERVAL
        else:
            lim_min = 0
        self.pyplotFig2D_axes_baro.set_xlim([float(lim_min), float(lim_max+FIGURE_DISPLAY_EXTENDED_DURRATION)])

        self.__widget_Fig2D__.draw()

    def clear(self):
        # Clear content
        self.pyplotFig2D_axes_baro.cla()
        self.pyplotFig2D_axes_altitude.cla()

        # Re-configure settings
        self.__configFig2D_Data__()

        # Update figure
        self.__widget_Fig2D__.draw()

