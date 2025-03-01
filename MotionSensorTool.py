import sys, os, re

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QStatusBar, QRadioButton, QButtonGroup
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets


from Utils.LoadConfigFile import *
from GUI.Components.ComponentSerialControl import *
from GUI.Components.ComponentSerialPlotter import *
from GUI.Components.ComponentMag import *
from GUI.Components.ComponentConsole import *

from GUI.Widgets.WidgetSelectFile import *

MODE_IDX_SERIAL_PLOTTER = 0
MODE_IDX_ANALYZE_MAG = 1




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__runtime_TimeMagData__ = []
        self.__runtime_TimeAllData__ = []
        self.__runtime_RawAllData__ = np.empty((0,9), int)
        self.__runtime_RawMagData__ = np.empty((0,3), int)
        self.__runtime_TimeStartMs__ = 0

        self.__selectedFile_SerialPlotter__ = ''
        self.__selectedFile_MagAnalyze__ = ''

        self.configModeData = LoadConfigFile()

        if self.configModeData['enable_serial_plotter'] == 1:
            self.__currentModeIdx__ = MODE_IDX_SERIAL_PLOTTER
        elif self.configModeData['enable_mag_analyze'] == 1:
            self.__currentModeIdx__ = MODE_IDX_ANALYZE_MAG

        self.__componentSerialControl__ = ComponentSerialControl()
        self.__componentSerialPlotter__ = ComponentSerialPlotter()
        self.__componentMagPlotter__ = ComponentMagPlotter()
        self.__componentMagAnalyze__ = ComponentMagAnalyze()
        self.__widget_SelectFile__ = WidgetSelectFile(self.onLoadFile)


        self.__componentConsole__ = ComponentConsole(self)
        self.__componentConsole__.setFormatter(CustomeFormatter())

        self.__button_SerialControl_Save__ = QPushButton('Save')
        self.__button_SerialControl_Save__.setFixedWidth(DIMENSION_BUTTON_WIDTH)
        self.__button_SerialControl_Save__.clicked.connect(self.onClickSaveConsole)

        self.__button_SerialControl_Clear__ = QPushButton('Clear')
        self.__button_SerialControl_Clear__.setFixedWidth(DIMENSION_BUTTON_WIDTH)
        self.__button_SerialControl_Clear__.clicked.connect(self.onClickClearConsole)

        self.__layout_ControlButton__ = QHBoxLayout()
        self.__layout_ControlButton__.setContentsMargins(0,0,0,0)
        self.__layout_ControlButton__.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.__layout_ControlButton__.addWidget(self.__button_SerialControl_Clear__)
        self.__layout_ControlButton__.addWidget(self.__button_SerialControl_Save__)
        self.__widget_ControlButton__ = QWidget()
        self.__widget_ControlButton__.setLayout(self.__layout_ControlButton__)




        self.radiobutton_AnalyzeMag = QRadioButton('Magnetometer')
        self.radiobutton_AnalyzeMag.setChecked(self.configModeData['enable_mag_analyze']) 
        self.radiobutton_SerialPlotter = QRadioButton('Serial Plotter')
        self.radiobutton_SerialPlotter.setChecked(self.configModeData['enable_serial_plotter']) 


        self.__componentMagPlotter__.setVisible(self.configModeData['enable_mag_analyze'])
        self.__componentMagAnalyze__.setVisible(self.configModeData['enable_mag_analyze'])
        self.__componentSerialPlotter__.setVisible(self.configModeData['enable_serial_plotter'])


        self.groupRadioButton = QButtonGroup(self)
        self.groupRadioButton.addButton(self.radiobutton_SerialPlotter, MODE_IDX_SERIAL_PLOTTER)
        self.groupRadioButton.addButton(self.radiobutton_AnalyzeMag, MODE_IDX_ANALYZE_MAG)
        self.groupRadioButton.buttonClicked.connect(self.onChangeMode)

        self.groupRadioButtonLayout = QHBoxLayout()
        self.groupRadioButtonLayout.addWidget(self.radiobutton_SerialPlotter)
        self.groupRadioButtonLayout.addWidget(self.radiobutton_AnalyzeMag)
        self.__componentSelectMode__ = QWidget()
        self.__componentSelectMode__.setLayout(self.groupRadioButtonLayout)




        logging.getLogger().addHandler(self.__componentConsole__)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('matplotlib.font_manager').disabled = True


        leftPanelLayout = QVBoxLayout()
        leftPanelLayout.setContentsMargins(0, 0, 0, 0)
        leftPanelLayout.addWidget(self.__componentSerialControl__)
        leftPanelLayout.addWidget(self.__widget_SelectFile__)
        leftPanelLayout.addWidget(self.__componentMagAnalyze__)
        leftPanelLayout.addWidget(self.__componentConsole__.widget)
        leftPanelLayout.addWidget(self.__widget_ControlButton__)
        leftPanelWidget = QWidget()
        leftPanelWidget.setFixedWidth(480)
        leftPanelWidget.setLayout(leftPanelLayout)

        
        rightPannelLayout = QVBoxLayout()
        rightPannelLayout.addWidget(self.__componentSerialPlotter__)
        rightPannelLayout.addWidget(self.__componentMagPlotter__)
        rightPanelWidgets = QWidget()
        rightPanelWidgets.setLayout(rightPannelLayout)


        mainLayout = QHBoxLayout()
        mainLayout.addWidget(leftPanelWidget)
        mainLayout.addWidget(rightPanelWidgets)
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

        statusBar = QStatusBar()
        statusBar.addWidget(self.__componentSelectMode__)
        self.setStatusBar(statusBar)


        self.setWindowTitle("Motion Sensor Tool")
        self.setCentralWidget(mainWidget)

        # self.__componentSerialControl__.registerOnReceivedData(self.DrawData)
        self.__timerDrawData__ = QTimer(self)
        self.__timerDrawData__.timeout.connect(self.DrawData)
        self.__timerDrawData__.start(20)


    def onLoadFile(self, filePath):

        data = np.loadtxt(filePath, delimiter=',')
        num_samples = data.shape[0]

        Time = []
        currentTime = 0.0
        for idx in range(num_samples):
            Time.append(currentTime)
            currentTime += 0.1

        if self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG:
            self.__selectedFile_MagAnalyze__ = filePath
            self.__widget_SelectFile__.setSelectedFileName(os.path.basename(self.__selectedFile_MagAnalyze__))

            self.__runtime_RawMagData__ = np.empty((0,3), int)
            self.__runtime_TimeMagData__ = []
        
            if data.shape[1] == 3:
                self.savedTxt_RawMagData = data
                self.__componentMagAnalyze__.setRawData(data)
                ComponentMagPlotter().plotRawData(Time, data[:,0], data[:,1], data[:,2])
            else:
                print('Incorrect mag data format')

        elif self.__currentModeIdx__ == MODE_IDX_SERIAL_PLOTTER:
            self.__selectedFile_SerialPlotter__ = filePath
            self.__widget_SelectFile__.setSelectedFileName(os.path.basename(self.__selectedFile_SerialPlotter__))

            self.__runtime_RawAllData__ = np.empty((0,9), int)
            self.__runtime_TimeAllData__ = []

            if data.shape[1] == 9:
                self.saveTxt_RawAccelGyroMagData = data
                ComponentSerialPlotter().plotAllData(Time, 
                                                    data[:,0], data[:,1], data[:,2],
                                                    data[:,3], data[:,4], data[:,5],
                                                    data[:,6], data[:,7], data[:,8])
            else:
                print('Incorrect all data format')


        
    def onClickSaveConsole(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        fileName, fileType = dialog.getSaveFileName(self)
        if fileName:
            consoleData = self.__componentConsole__.getCurrentText()

            if '.txt' not in fileName:
                fileName += '.txt'
                
            with open(fileName, 'w') as output:
                output.write(consoleData)


    def onClickClearConsole(self):
        self.__componentConsole__.clear()

    def onChangeMode(self, object):
        self.__currentModeIdx__ = self.groupRadioButton.id(object)

        if self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG:
            ComponentMagPlotter().setVisible(True)
            ComponentMagAnalyze().setVisible(True)
            ComponentSerialPlotter().setVisible(False)
            self.__widget_SelectFile__.setSelectedFileName(os.path.basename(self.__selectedFile_MagAnalyze__))
        elif self.__currentModeIdx__ == MODE_IDX_SERIAL_PLOTTER:
            ComponentMagPlotter().setVisible(False)
            ComponentMagAnalyze().setVisible(False)
            ComponentSerialPlotter().setVisible(True)
            self.__widget_SelectFile__.setSelectedFileName(os.path.basename(self.__selectedFile_SerialPlotter__))

    def DrawData(self):
        if ComponentSerialControl().getConnectStatus() == True:
            listData = ComponentSerialControl().getSeriaData()
            for data in listData:
                splitData = np.array(data[1].split(','), dtype=int)
                if self.__currentModeIdx__ == MODE_IDX_SERIAL_PLOTTER and splitData.size == 9:
                    if len(self.__runtime_TimeAllData__) == 0:
                        self.__runtime_TimeAllData__.append(0)
                        self.__runtime_TimeStartMs__ = time.time()
                    else:
                        self.__runtime_TimeAllData__.append(float(data[0]-self.__runtime_TimeStartMs__))

                    self.__runtime_RawAllData__ = np.append(self.__runtime_RawAllData__, [[int(splitData[0]), int(splitData[1]), int(splitData[2]), 
                                                                    int(splitData[3]), int(splitData[4]), int(splitData[5]), 
                                                                    int(splitData[6]), int(splitData[7]), int(splitData[8])]], axis=0)
                elif self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG and splitData.size == 3:
                    if len(self.__runtime_TimeMagData__) == 0:
                        self.__runtime_TimeMagData__.append(0)
                        self.__runtime_TimeStartMs__ = time.time()
                    else:
                        self.__runtime_TimeMagData__.append(float(data[0]-self.__runtime_TimeStartMs__))

                    self.__runtime_RawMagData__ = np.append(self.__runtime_RawMagData__, [[int(splitData[0]), int(splitData[1]), int(splitData[2])]], axis=0)


                self.__componentConsole__.logInfo(data[1])

            if self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG and self.__runtime_TimeMagData__ != []:
                self.__componentMagAnalyze__.setRawData(self.__runtime_RawMagData__)
                ComponentMagPlotter().plotRawData(self.__runtime_TimeMagData__, self.__runtime_RawMagData__[:,0], self.__runtime_RawMagData__[:,1], self.__runtime_RawMagData__[:,2])
            elif self.__currentModeIdx__ == MODE_IDX_SERIAL_PLOTTER and self.__runtime_TimeAllData__ != []:
                ComponentSerialPlotter().plotAllData(self.__runtime_TimeAllData__, 
                    self.__runtime_RawAllData__[:,0], self.__runtime_RawAllData__[:,1], self.__runtime_RawAllData__[:,2],
                    self.__runtime_RawAllData__[:,3], self.__runtime_RawAllData__[:,4], self.__runtime_RawAllData__[:,5],
                    self.__runtime_RawAllData__[:,6], self.__runtime_RawAllData__[:,7], self.__runtime_RawAllData__[:,8])




app = QApplication(sys.argv)

window = MainWindow()
window.showMaximized()
sys.exit(app.exec())