import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure


from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt
from Utils.Singleton import *


RawData_Time = [0,1,2,3,4]

RawData_AccelX = [10,1,20,3,40]
RawData_AccelY = [8,2,3,3,7]
RawData_AccelZ = [3,1,2,3,4]

RawData_GyroX = [10,1,20,3,40]
RawData_GyroY = [8,2,3,3,7]
RawData_GyroZ = [3,1,2,3,4]

RawData_MagX = [10,1,20,3,40]
RawData_MagY = [8,2,3,3,7]
RawData_MagZ = [3,1,2,3,100]

RawData_Roll = [0,0,0,0,0]
RawData_Pitch = [0,0,0,0,0]
RawData_Yaw = [0,0,0,0,0]


class PlotterLineChart(FigureCanvasQTAgg):
    def __init__(self, parent = None, width=10, height=10, dpi=100):
        figLineChart = Figure(dpi=dpi)


        self.DrawAccel = figLineChart.add_subplot(4,1,1)
        self.DrawAccel.plot(RawData_Time, RawData_AccelX, label='AccelX')
        self.DrawAccel.plot(RawData_Time, RawData_AccelY, label='AccelY')
        self.DrawAccel.plot(RawData_Time, RawData_AccelZ, label='AccelZ')
        self.DrawAccel.grid(True)
        self.DrawAccel.legend()

        self.DrawGyro = figLineChart.add_subplot(4,1,2,sharex=self.DrawAccel)
        self.DrawGyro.plot(RawData_Time, RawData_GyroX, label='GyroX')
        self.DrawGyro.plot(RawData_Time, RawData_GyroY, label='GyroY')
        self.DrawGyro.plot(RawData_Time, RawData_GyroZ, label='GyroZ')
        self.DrawGyro.grid(True)
        self.DrawGyro.legend()

        self.DrawMag = figLineChart.add_subplot(4,1,3,sharex=self.DrawAccel)
        self.DrawMag.plot(RawData_Time, RawData_MagX, label='MagX')
        self.DrawMag.plot(RawData_Time, RawData_MagY, label='MagY')
        self.DrawMag.plot(RawData_Time, RawData_MagZ, label='MagZ')
        self.DrawMag.grid(True)
        self.DrawMag.legend()

        self.DrawAngle = figLineChart.add_subplot(4,1,4,sharex=self.DrawAccel)
        self.DrawAngle.plot(RawData_Time, RawData_Roll, label='Roll')
        self.DrawAngle.plot(RawData_Time, RawData_Pitch, label='Pitch')
        self.DrawAngle.plot(RawData_Time, RawData_Yaw, label='Yaw')
        self.DrawAngle.grid(True)
        self.DrawAngle.legend()




        super().__init__(figLineChart)

@singleton
class ComponentAll(QWidget):
    def __init__(self):
        super().__init__()

        self.__figLineChart__ = PlotterLineChart()
        self.__toolbar__ = NavigationToolbar2QT(self.__figLineChart__, self)

        layout = QVBoxLayout()
        layout.addWidget(self.__toolbar__)
        layout.addWidget(self.__figLineChart__)


        self.setLayout(layout)

    # def setVisible(self, visible):
    #     self.setVisible(visible)



