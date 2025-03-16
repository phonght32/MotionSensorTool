import numpy as np
from scipy import linalg
import matplotlib

matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pyplot as plt
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from Utils.Singleton import *
from GUI.Config.Config_Widget import *

class ComponentAnglePlotter(QWidget):
    def __init__(self):
        super().__init__()

        # Create figure 2D
        self.pyplotFig2D = plt.figure()

        # Add subplot for drawing angle
        self.pyplotFig2D_axes = self.pyplotFig2D.add_subplot(111)
        self.pyplotFig2D_axes.grid(True)
        self.pyplotFig2D_axes.set_title("Angle")

        # Create instance for Canvas and Toolbar
        self.widgetFig2D = FigureCanvasQTAgg(self.pyplotFig2D)
        self.widgetToolbar = NavigationToolbar2QT(self.widgetFig2D, self)

        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.widgetToolbar)
        layout.addWidget(self.widgetFig2D)
        self.setLayout(layout)

    # plot function
    def plot(self, AngleData):
        # Get data
        Time = AngleData[:,0]
        Roll = AngleData[:,1]
        Pitch = AngleData[:,2]
        Yaw = AngleData[:,3]

        # Draw data and configure figure
        self.pyplotFig2D_axes.cla()
        self.pyplotFig2D_axes.plot(Time, Roll, label='Roll', lw=FIGURE_LINE_WIDTH)
        self.pyplotFig2D_axes.plot(Time, Pitch, label='Pitch', lw=FIGURE_LINE_WIDTH)
        self.pyplotFig2D_axes.plot(Time, Yaw, label='Yaw', lw=FIGURE_LINE_WIDTH)
        self.pyplotFig2D_axes.grid(True)
        self.pyplotFig2D_axes.legend()
        self.pyplotFig2D_axes.set_title("Angle")
        
        # Configure x axis: value show every 5 and there are 5 seperated members
        self.pyplotFig2D_axes.xaxis.set_major_locator(MultipleLocator(5))
        self.pyplotFig2D_axes.xaxis.set_minor_locator(AutoMinorLocator(5))

        # Configure y axis: value show every 10 and there are 5 seperated members
        self.pyplotFig2D_axes.yaxis.set_major_locator(MultipleLocator(10))
        self.pyplotFig2D_axes.yaxis.set_minor_locator(AutoMinorLocator(5))

        # Display latest [FIGURE_DISPLAY_INTERVAL]s data
        lim_max = Time[-1]
        if lim_max - FIGURE_DISPLAY_INTERVAL > 0:
            lim_min = lim_max - FIGURE_DISPLAY_INTERVAL
        else:
            lim_min = 0
        self.pyplotFig2D_axes.set_xlim([float(lim_min), float(lim_max+FIGURE_DISPLAY_EXTENDED_DURRATION)])

        # Update figure
        self.widgetFig2D.draw()

    def clear(self):
        self.pyplotFig2D_axes.cla()
        self.widgetFig2D.draw()
