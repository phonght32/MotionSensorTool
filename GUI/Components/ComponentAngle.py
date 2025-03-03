import numpy as np
from scipy import linalg
import matplotlib

matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from Utils.Singleton import *
from GUI.Config.Config_Widget import *

class ComponentAnglePlotter(QWidget):
    def __init__(self):
        super().__init__()

        self.pyplotFig2D = plt.figure()

        self.pyplotFig2D_axes = self.pyplotFig2D.add_subplot(111)
        self.pyplotFig2D_axes.grid(True)
        self.pyplotFig2D_axes.set_title("Angle")

        self.widgetFig2D = FigureCanvasQTAgg(self.pyplotFig2D)
        self.widgetToolbar = NavigationToolbar2QT(self.widgetFig2D, self)


        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.widgetToolbar)
        layout.addWidget(self.widgetFig2D)
        self.setLayout(layout)

    def plot(self, AngleData):
        Time = AngleData[:,0]
        Roll = AngleData[:,1]
        Pitch = AngleData[:,2]
        Yaw = AngleData[:,3]


        self.pyplotFig2D_axes.cla()
        self.pyplotFig2D_axes.plot(Time, Roll, label='Roll', lw=FIGURE_LINE_WIDTH)
        self.pyplotFig2D_axes.plot(Time, Pitch, label='Pitch', lw=FIGURE_LINE_WIDTH)
        self.pyplotFig2D_axes.plot(Time, Yaw, label='Yaw', lw=FIGURE_LINE_WIDTH)
        self.pyplotFig2D_axes.grid(True)
        self.pyplotFig2D_axes.legend()
        self.pyplotFig2D_axes.set_title("Raw data")

        lim_max = Time[-1]
        if lim_max - FIGURE_DISPLAY_INTERVAL > 0:
            lim_min = lim_max - FIGURE_DISPLAY_INTERVAL
        else:
            lim_min = 0
        self.pyplotFig2D_axes.set_xlim([float(lim_min), float(lim_max+FIGURE_DISPLAY_EXTENDED_DURRATION)])
        self.widgetFig2D.draw()