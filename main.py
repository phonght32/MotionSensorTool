from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtCore import Qt

# Only needed for access to command line arguments
import sys, os, re


from Utils.LoadConfigFile import *
from Components.ComponentSelectMode import *
from Components.ComponentSelectFile import *
from Components.ComponentSerial import *
from Components.ComponentAll import *
from Components.ComponentMag import *




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.Time = []
        self.RawData_MagX = []
        self.RawData_MagY = []
        self.RawData_MagZ = []
        self.TimeStartMs = 0

        self.configModeData = LoadConfigFile()

        self.componentSerial = ComponentSerial()
        self.componentSelectMode = ComponentSelectMode()
        self.componentSelectFile = ComponentSelectFile()
        self.componentAll = ComponentAll()
        self.componentMagPlotter = ComponentMagPlotter()
        self.componentMagAnalyze = ComponentMagAnalyze()



        leftPanelLayout = QVBoxLayout()
        leftPanelLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        leftPanelLayout.addWidget(self.componentSerial)
        leftPanelLayout.addWidget(self.componentSelectMode)
        leftPanelLayout.addWidget(self.componentSelectFile)
        leftPanelLayout.addWidget(self.componentMagAnalyze)
        leftPanelWidget = QWidget()
        leftPanelWidget.setFixedWidth(450)
        leftPanelWidget.setLayout(leftPanelLayout)

        
        rightPannelLayout = QVBoxLayout()
        rightPannelLayout.addWidget(self.componentAll)
        rightPannelLayout.addWidget(self.componentMagPlotter, 1)
        rightPanelWidgets = QWidget()
        rightPanelWidgets.setLayout(rightPannelLayout)


        myLayout = QHBoxLayout()
        myLayout.addWidget(leftPanelWidget)
        myLayout.addWidget(rightPanelWidgets)
        myWidget = QWidget()
        myWidget.setLayout(myLayout)


        self.setWindowTitle("Motion Sensor Tool")
        self.setCentralWidget(myWidget)

        self.componentSerial.registerCallbackAnalyze(self.DrawData)
        self.componentSelectFile.registerCallbackLoadFile(self.callbackLoadFile)

        self.TimeStartMs = time.time()

    def callbackLoadFile(self, file_content):
        list_data = file_content.splitlines()
        Time = []
        RawData_MagX = []
        RawData_MagY = []
        RawData_MagZ = []

        currentTime = 0.0

        for lineData in list_data:
            splitData = re.findall("[+-]?[0-9]+",str(lineData))
            
            Time.append(currentTime)
            currentTime += 0.1
            RawData_MagX.append(int(splitData[0]))
            RawData_MagY.append(int(splitData[1]))
            RawData_MagZ.append(int(splitData[2]))

        self.componentMagPlotter.plotMagData(Time, RawData_MagX, RawData_MagY, RawData_MagZ)

        # print(file_content)

    def DrawData(self, timestamp, binary_string):
        splitData = re.findall("[+-]?[0-9]+",str(binary_string))

        if splitData != []:
            if len(splitData) == 3:
                self.Time.append(float(timestamp-self.TimeStartMs))
                self.RawData_MagX.append(int(splitData[0]))
                self.RawData_MagY.append(int(splitData[1]))
                self.RawData_MagZ.append(int(splitData[2]))
                self.componentMagPlotter.runtimePlotMagData(self.Time, self.RawData_MagX, self.RawData_MagY, self.RawData_MagZ)
        else:
            print('IGNORE DATA')





app = QApplication(sys.argv)

window = MainWindow()
window.showMaximized()
sys.exit(app.exec())