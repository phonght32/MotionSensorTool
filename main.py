from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QStatusBar
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets

import sys, os, re


from Utils.LoadConfigFile import *
from Components.ComponentSelectMode import *
from Components.ComponentSerialControl import *
from Components.ComponentSerialPlotter import *
from Components.ComponentMag import *




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.time = []
        self.rawMagData = np.empty((0,3), int)
        self.timeStartMs = 0

        self.configModeData = LoadConfigFile()

        
        self.componentSelectMode = ComponentSelectMode()
        self.componentSerialControl = ComponentSerialControl()
        self.componentSerialPlotter = ComponentSerialPlotter()
        self.componentMagPlotter = ComponentMagPlotter()
        self.componentMagAnalyze = ComponentMagAnalyze()


        leftPanelLayout = QVBoxLayout()
        leftPanelLayout.setContentsMargins(0, 0, 0, 0)
        leftPanelLayout.addWidget(self.componentSerialControl)
        leftPanelLayout.addWidget(self.componentMagAnalyze)
        leftPanelWidget = QWidget()
        leftPanelWidget.setFixedWidth(550)
        leftPanelWidget.setLayout(leftPanelLayout)

        
        rightPannelLayout = QVBoxLayout()
        rightPannelLayout.addWidget(self.componentSerialPlotter)
        rightPannelLayout.addWidget(self.componentMagPlotter)
        rightPanelWidgets = QWidget()
        rightPanelWidgets.setLayout(rightPannelLayout)


        mainLayout = QHBoxLayout()
        mainLayout.addWidget(leftPanelWidget)
        mainLayout.addWidget(rightPanelWidgets)
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

        statusBar = QStatusBar()
        statusBar.addWidget(self.componentSelectMode)
        self.setStatusBar(statusBar)


        self.setWindowTitle("Motion Sensor Tool")
        self.setCentralWidget(mainWidget)

        self.componentSerialControl.registerOnReceivedData(self.DrawData)

        self.timeStartMs = time.time()

    

    def DrawData(self, timestamp, binary_string):
        splitData = np.array(binary_string.split(','), dtype=int)
        if splitData.size == 9:
            self.time.append(float(timestamp-self.timeStartMs))

            self.rawMagData = np.append(self.rawMagData, [[int(splitData[6]), int(splitData[7]), int(splitData[8])]], axis=0)

            ComponentSerialPlotter().plotMagData(self.time, self.rawMagData[:,0], self.rawMagData[:,1], self.rawMagData[:,2])


app = QApplication(sys.argv)

window = MainWindow()
window.showMaximized()
sys.exit(app.exec())