import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pyplot as plt


from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit
from PyQt6.QtCore import Qt

from Utils.Singleton import *


DISPLAY_INTERVAL = 15

@singleton
class ComponentMagPlotter(QWidget):
    def __init__(self):
        super().__init__()

        self.pyplotFig2D = plt.figure()
        self.pyplotFig2D_axes = self.pyplotFig2D.add_subplot(111)
        self.pyplotFig2D_axes.grid(True)

        self.pyplotFig3D = plt.figure()
        self.pyplotFig3D_Axes_RawData = self.pyplotFig3D.add_subplot(121, projection='3d')
        self.pyplotFig3D_Axes_RawData.grid(True)
        self.pyplotFig3D_Axes_RawData.set_xlabel('MagX')
        self.pyplotFig3D_Axes_RawData.set_ylabel('MagY')
        self.pyplotFig3D_Axes_RawData.set_zlabel('MagZ')

        self.pyplotFig3D_Axes_CalibData = self.pyplotFig3D.add_subplot(122, projection='3d')
        self.pyplotFig3D_Axes_CalibData.grid(True)
        self.pyplotFig3D_Axes_CalibData.set_xlabel('MagX')
        self.pyplotFig3D_Axes_CalibData.set_ylabel('MagY')
        self.pyplotFig3D_Axes_CalibData.set_zlabel('MagZ')

        self.widgetFig2D = FigureCanvasQTAgg(self.pyplotFig2D)
        self.widgetFig3D = FigureCanvasQTAgg(self.pyplotFig3D)
        self.widgetToolbar = NavigationToolbar2QT(self.widgetFig2D, self)

        layout = QVBoxLayout()
        layout.addWidget(self.widgetToolbar)
        layout.addWidget(self.widgetFig2D)
        layout.addWidget(self.widgetFig3D)

        self.setLayout(layout)

        self.CntDisplay3D = 0



    def runtimePlotMagData(self, Time=[], RawData_MagX=[], RawData_MagY=[], RawData_MagZ=[]):

        self.pyplotFig2D_axes.cla()
        self.pyplotFig2D_axes.plot(Time, RawData_MagX, label='MagX')
        self.pyplotFig2D_axes.plot(Time, RawData_MagY, label='MagY')
        self.pyplotFig2D_axes.plot(Time, RawData_MagZ, label='MagZ')
        self.pyplotFig2D_axes.grid(True)
        self.pyplotFig2D_axes.legend()

        lim_max = Time[-1]
        if lim_max - DISPLAY_INTERVAL > 0:
            lim_min = lim_max - DISPLAY_INTERVAL
        else:
            lim_min = 0
        self.pyplotFig2D_axes.set_xlim([lim_min, lim_max])
        self.widgetFig2D.draw()

        self.CntDisplay3D += 1
        if self.CntDisplay3D == 10:
            self.CntDisplay3D = 0

            self.pyplotFig3D_Axes_RawData.cla()
            self.pyplotFig3D_Axes_RawData.scatter(RawData_MagX, RawData_MagY, RawData_MagZ)
            self.pyplotFig3D_Axes_RawData.grid(True)
            self.pyplotFig3D_Axes_RawData.set_xlabel('MagX')
            self.pyplotFig3D_Axes_RawData.set_ylabel('MagY')
            self.pyplotFig3D_Axes_RawData.set_zlabel('MagZ')
            plt.draw()

    def plotMagData(self, Time=[], RawData_MagX=[], RawData_MagY=[], RawData_MagZ=[]):

        self.pyplotFig2D_axes.cla()
        self.pyplotFig2D_axes.plot(Time, RawData_MagX, label='MagX')
        self.pyplotFig2D_axes.plot(Time, RawData_MagY, label='MagY')
        self.pyplotFig2D_axes.plot(Time, RawData_MagZ, label='MagZ')
        self.pyplotFig2D_axes.grid(True)
        self.pyplotFig2D_axes.legend()

        lim_max = Time[-1]
        if lim_max - DISPLAY_INTERVAL > 0:
            lim_min = lim_max - DISPLAY_INTERVAL
        else:
            lim_min = 0
        self.pyplotFig2D_axes.set_xlim([lim_min, lim_max])
        self.widgetFig2D.draw()

        self.pyplotFig3D_Axes_RawData.cla()
        self.pyplotFig3D_Axes_RawData.scatter(RawData_MagX, RawData_MagY, RawData_MagZ)
        self.pyplotFig3D_Axes_RawData.grid(True)
        self.pyplotFig3D_Axes_RawData.set_xlabel('MagX')
        self.pyplotFig3D_Axes_RawData.set_ylabel('MagY')
        self.pyplotFig3D_Axes_RawData.set_zlabel('MagZ')
        plt.draw()

@singleton
class ComponentMagAnalyze(QWidget):
    def __init__(self):
        super().__init__()

        self.__current_NormOfGravity__ = '1024'

        self.__label_NormOfGravity__ = QLabel('Norm of Magnetic or Gravity:')

        self.__input_NormOfMagnetic__ = QLineEdit(self.__current_NormOfGravity__)
        self.__input_NormOfMagnetic__.setFixedWidth(100)
        self.__input_NormOfMagnetic__.textChanged.connect(self.onChangeNormOfMagnetic)
        
        self.__widget_NormOfMagnetic_Layout__ = QHBoxLayout()
        self.__widget_NormOfMagnetic_Layout__.addWidget(self.__label_NormOfGravity__)
        self.__widget_NormOfMagnetic_Layout__.addWidget(self.__input_NormOfMagnetic__)
        self.__widget_NormOfMagnetic__ = QWidget()
        self.__widget_NormOfMagnetic__.setLayout(self.__widget_NormOfMagnetic_Layout__)



        layout = QVBoxLayout()
        layout.addWidget(self.__widget_NormOfMagnetic__)


        self.setLayout(layout)

    def onChangeNormOfMagnetic(self, text):
        self.__current_NormOfGravity__ = text








