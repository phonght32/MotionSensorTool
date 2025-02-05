from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtCore import Qt

# Only needed for access to command line arguments
import sys, os, re


from Utils.LoadConfigFile import *
from Components.ComponentSelectMode import *
from Components.ComponentSerial import *
from Components.ComponentAll import *
from Components.ComponentAnalyzeMag import *




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
        self.componentAll = ComponentAll()
        self.componentAnalyzeMag = ComponentAnalyzeMag()
        self.componentSelectMode = ComponentSelectMode()

        # self.componentAll.setVisible(self.configModeData['showComponentAll'])
        # self.componentAnalyzeMag.setVisible(self.configModeData['showComponentAnalyzeMag'])

        leftPanelLayout = QVBoxLayout()
        leftPanelLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        leftPanelLayout.addWidget(self.componentSerial)
        leftPanelLayout.addWidget(self.componentSelectMode)
        leftPanelWidget = QWidget()
        leftPanelWidget.setLayout(leftPanelLayout)

        
        rightPannelLayout = QVBoxLayout()
        rightPannelLayout.addWidget(self.componentAll)
        rightPannelLayout.addWidget(self.componentAnalyzeMag, 1)
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

        self.TimeStartMs = time.time()

    def DrawData(self, timestamp, binary_string):
        splitData = re.findall("[+-]?[0-9]+",str(binary_string))

        if splitData != []:
            if len(splitData) == 3:
                self.Time.append(float(timestamp-self.TimeStartMs))
                self.RawData_MagX.append(int(splitData[0]))
                self.RawData_MagY.append(int(splitData[1]))
                self.RawData_MagZ.append(int(splitData[2]))

                self.componentAnalyzeMag.plotMagData(self.Time, self.RawData_MagX, self.RawData_MagY, self.RawData_MagZ)
            

        else:
            print('IGNORE DATA')




app = QApplication(sys.argv)

window = MainWindow()
window.showMaximized()
sys.exit(app.exec())