import sys, os, re

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QStatusBar, QRadioButton, QButtonGroup
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets


from Utils.LoadConfigFile import *
from GUI.Components.ComponentSerialControl import *
from GUI.Components.ComponentImuData import *
from GUI.Components.ComponentMag import *
from GUI.Components.ComponentConsole import *

from GUI.Widgets.WidgetSelectFile import *

MODE_IDX_SERIAL_PLOTTER = 0
MODE_IDX_ANALYZE_MAG = 1




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Numpy array contains IMU data and timestamp: [timestamp, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z]
        self.__runtime_ImuData__ = np.empty((0,10), int)

        # Numpy array contains saved IMU data from .txt file
        self.__savedTxt_ImuData__ = np.empty((0,10), int)

        # Numpy array contains magnetometer data and timestamp: [timestamp, mag_x, mag_y, mag_z]
        self.__runtime_MagData__ = np.empty((0,4), int)

        # Numpy array contains saved mag data from .txt file
        self.__savedTxt_MagData__ = np.empty((0,4), int)

        # Time point when start monitor data
        self.__runtime_TimeStartMs__ = 0

        # Current selected files
        self.__selectedFile_SerialPlotter__ = ''
        self.__selectedFile_MagAnalyze__ = ''

        self.__configModeData__ = LoadConfigFile()

        # Get current mode display [IMU data, magnetometer]
        if self.__configModeData__['enable_imu_data_analyze'] == 1:
            self.__currentModeIdx__ = MODE_IDX_SERIAL_PLOTTER
        elif self.__configModeData__['enable_mag_analyze'] == 1:
            self.__currentModeIdx__ = MODE_IDX_ANALYZE_MAG

        # Create component serial control 
        self.__componentSerialControl__ = ComponentSerialControl()

        # Create component IMU data
        self.__componentImuData__ = ComponentImuData()
        self.__componentImuData__.setVisible(self.__configModeData__['enable_imu_data_analyze'])

        # Create component mag plotter
        self.__componentMagPlotter__ = ComponentMagPlotter()
        self.__componentMagPlotter__.setVisible(self.__configModeData__['enable_mag_analyze'])
        
        # Create component mag analyzer
        self.__componentMagAnalyze__ = ComponentMagAnalyze()
        self.__componentMagAnalyze__.setVisible(self.__configModeData__['enable_mag_analyze'])
        
        # Create component select file
        self.__widget_SelectFile__ = WidgetSelectFile(self.onLoadFile)
        
        # Create component console
        self.__componentConsole__ = ComponentConsole(self)
        self.__componentConsole__.setFormatter(CustomeFormatter())

        
        # Create radio button for mode selection
        self.__radiobutton_AnalyzeMag__ = QRadioButton('Magnetometer')
        self.__radiobutton_AnalyzeMag__.setChecked(self.__configModeData__['enable_mag_analyze']) 
        self.__radiobutton_ImuData__ = QRadioButton('IMU data')
        self.__radiobutton_ImuData__.setChecked(self.__configModeData__['enable_imu_data_analyze']) 

        self.__groupRadioButton_SelectMode__ = QButtonGroup(self)
        self.__groupRadioButton_SelectMode__.addButton(self.__radiobutton_ImuData__, MODE_IDX_SERIAL_PLOTTER)
        self.__groupRadioButton_SelectMode__.addButton(self.__radiobutton_AnalyzeMag__, MODE_IDX_ANALYZE_MAG)
        self.__groupRadioButton_SelectMode__.buttonClicked.connect(self.onChangeMode)

        self.__groupRadioButton_SelectMode_Layout__ = QHBoxLayout()
        self.__groupRadioButton_SelectMode_Layout__.addWidget(self.__radiobutton_ImuData__)
        self.__groupRadioButton_SelectMode_Layout__.addWidget(self.__radiobutton_AnalyzeMag__)
        self.__groupRadioButton_SelectMode_Widget__ = QWidget()
        self.__groupRadioButton_SelectMode_Widget__.setLayout(self.__groupRadioButton_SelectMode_Layout__)


        # Handle logging module
        logging.getLogger().addHandler(self.__componentConsole__)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('matplotlib.font_manager').disabled = True


        # Create left panel
        leftPanelLayout = QVBoxLayout()
        leftPanelLayout.setContentsMargins(0, 0, 0, 0)
        leftPanelLayout.addWidget(self.__componentSerialControl__)
        leftPanelLayout.addWidget(self.__widget_SelectFile__)
        leftPanelLayout.addWidget(self.__componentMagAnalyze__)
        leftPanelLayout.addWidget(self.__componentConsole__.widget)
        leftPanelWidget = QWidget()
        leftPanelWidget.setFixedWidth(480)
        leftPanelWidget.setLayout(leftPanelLayout)

        # Create right panel
        rightPannelLayout = QVBoxLayout()
        rightPannelLayout.addWidget(self.__componentImuData__)
        rightPannelLayout.addWidget(self.__componentMagPlotter__)
        rightPanelWidgets = QWidget()
        rightPanelWidgets.setLayout(rightPannelLayout)

        # Create main window
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(leftPanelWidget)
        mainLayout.addWidget(rightPanelWidgets)
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

        # Create status bar
        statusBar = QStatusBar()
        statusBar.addWidget(self.__groupRadioButton_SelectMode_Widget__)
        self.setStatusBar(statusBar)


        self.setWindowTitle("Motion Sensor Tool")
        self.setCentralWidget(mainWidget)

        # Create timer to get data from serial
        self.__timerDrawData__ = QTimer(self)
        self.__timerDrawData__.timeout.connect(self.DrawData)
        self.__timerDrawData__.start(20)

    def onChangeMode(self, object):
        self.__currentModeIdx__ = self.__groupRadioButton_SelectMode__.id(object)

        if self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG:
            ComponentMagPlotter().setVisible(True)
            ComponentMagAnalyze().setVisible(True)
            ComponentImuData().setVisible(False)
            self.__widget_SelectFile__.setSelectedFileName(os.path.basename(self.__selectedFile_MagAnalyze__))
        elif self.__currentModeIdx__ == MODE_IDX_SERIAL_PLOTTER:
            ComponentMagPlotter().setVisible(False)
            ComponentMagAnalyze().setVisible(False)
            ComponentImuData().setVisible(True)
            self.__widget_SelectFile__.setSelectedFileName(os.path.basename(self.__selectedFile_SerialPlotter__))


    
    def onLoadFile(self, filePath):
        data = np.loadtxt(filePath, delimiter=',')

        num_samples = data.shape[0]

        Time = np.empty((num_samples,1), float)
        currentTime = 0.0

        for idx in range(num_samples):
            Time[idx] = currentTime
            currentTime += 0.1

        if self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG:
            self.__selectedFile_MagAnalyze__ = filePath
            self.__widget_SelectFile__.setSelectedFileName(os.path.basename(self.__selectedFile_MagAnalyze__))

            self.__runtime_MagData__ = np.empty((0,4), int)
        
            if data.shape[1] == 3:
                self.__savedTxt_MagData__ = np.concatenate((Time, data), axis=1)
                self.__componentMagAnalyze__.setRawData(data)
                ComponentMagPlotter().plot(self.__savedTxt_MagData__)
            else:
                print('Incorrect mag data format')

        elif self.__currentModeIdx__ == MODE_IDX_SERIAL_PLOTTER:
            self.__selectedFile_SerialPlotter__ = filePath
            self.__widget_SelectFile__.setSelectedFileName(os.path.basename(self.__selectedFile_SerialPlotter__))

            self.__runtime_ImuData__ = np.empty((0,10), int)

            if data.shape[1] == 9:
                self.__savedTxt_ImuData__ = np.concatenate((Time, data), axis=1)
                ComponentImuData().plot(self.__savedTxt_ImuData__)
            else:
                print('Incorrect all data format')


    def DrawData(self):
        if ComponentSerialControl().getConnectStatus() == True:
            listData = ComponentSerialControl().getSeriaData()
            for data in listData:
                splitData = np.array(data[1].split(','), dtype=int)
                if self.__currentModeIdx__ == MODE_IDX_SERIAL_PLOTTER and splitData.size == 9:
                    if len(self.__runtime_ImuData__) == 0:
                        self.__runtime_TimeStartMs__ = time.time()
                        timestamp = 0.0
                    else:
                        timestamp = float(data[0]-self.__runtime_TimeStartMs__)

                    self.__runtime_ImuData__ = np.append(self.__runtime_ImuData__, [[timestamp,
                                                                    int(splitData[0]), int(splitData[1]), int(splitData[2]), 
                                                                    int(splitData[3]), int(splitData[4]), int(splitData[5]), 
                                                                    int(splitData[6]), int(splitData[7]), int(splitData[8])]], axis=0)
                elif self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG and splitData.size == 3:
                    if len(self.__runtime_MagData__) == 0:
                        self.__runtime_TimeStartMs__ = time.time()
                        timestamp = 0.0
                    else:
                        timestamp = float(data[0]-self.__runtime_TimeStartMs__)

                    self.__runtime_MagData__ = np.append(self.__runtime_MagData__, [[timestamp, int(splitData[0]), int(splitData[1]), int(splitData[2])]], axis=0)


                self.__componentConsole__.logInfo(data[1])

            if self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG:
                self.__componentMagAnalyze__.setRawData(self.__runtime_MagData__[:,[1,2,3]])
                ComponentMagPlotter().plot(self.__runtime_MagData__)
            elif self.__currentModeIdx__ == MODE_IDX_SERIAL_PLOTTER:
                ComponentImuData().plot(self.__runtime_ImuData__)




app = QApplication(sys.argv)

window = MainWindow()
window.showMaximized()
sys.exit(app.exec())