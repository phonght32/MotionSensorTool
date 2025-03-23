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
        self.pyplotFig2D, (self.pyplotFig2D_axes_baro, self.pyplotFig2D_axes_accel, self.pyplotFig2D_axes_altitude) = plt.subplots(3, 1, sharex=True)

        # Configure axes of accel, gyro and mag
        self.__configFig2D_Data__()


        # Create lines
        self.linesBaro, = self.pyplotFig2D_axes_baro.plot([], [], '-r', label='Baro', lw=FIGURE_LINE_WIDTH)

        self.linesRawAccelX, = self.pyplotFig2D_axes_accel.plot([], [], '-r', label='AccelX', lw=FIGURE_LINE_WIDTH)
        self.linesRawAccelY, = self.pyplotFig2D_axes_accel.plot([], [], '-g', label='AccelY', lw=FIGURE_LINE_WIDTH)
        self.linesRawAccelZ, = self.pyplotFig2D_axes_accel.plot([], [], '-b', label='AccelZ', lw=FIGURE_LINE_WIDTH)

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
    
        self.pyplotFig2D_axes_accel.grid(True)
        self.pyplotFig2D_axes_accel.set_title("Accelerometer")

        self.pyplotFig2D_axes_altitude.grid(True)
        self.pyplotFig2D_axes_altitude.set_title("Altitude")

