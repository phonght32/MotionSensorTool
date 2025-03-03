import sys, os, re, json

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QStatusBar, QRadioButton, QButtonGroup
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets


from Utils.HandleFile import *
from GUI.Components.ComponentSerialControl import *
from GUI.Components.ComponentImuData import *
from GUI.Components.ComponentMag import *
from GUI.Components.ComponentConsole import *

from GUI.Widgets.WidgetSelectFile import *

MODE_IDX_IMU_DATA = 0
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

        self.__configModeData__ = LoadConfigFile(FILE_CONFIG_WINDOW)

        # Get current mode display [IMU data, magnetometer]
        if self.__configModeData__['enable_imu_data_analyze'] == 1:
            self.__currentModeIdx__ = MODE_IDX_IMU_DATA
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
        self.__groupRadioButton_SelectMode__.addButton(self.__radiobutton_ImuData__, MODE_IDX_IMU_DATA)
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
            # Hide/Unhide widgets
            self.__componentMagPlotter__.setVisible(True)
            self.__componentMagAnalyze__.setVisible(True)
            self.__componentImuData__.setVisible(False)

            # Update selected file name
            self.__widget_SelectFile__.setSelectedFileName(os.path.basename(self.__selectedFile_MagAnalyze__))

            # Save current config
            self.saveCurrentConfig()

        elif self.__currentModeIdx__ == MODE_IDX_IMU_DATA:
            # Hide/Unhide widgets
            self.__componentMagPlotter__.setVisible(False)
            self.__componentMagAnalyze__.setVisible(False)
            self.__componentImuData__.setVisible(True)

            # Update selected file name
            self.__widget_SelectFile__.setSelectedFileName(os.path.basename(self.__selectedFile_SerialPlotter__))

            # Save current config
            self.saveCurrentConfig()

    def saveCurrentConfig(self):
        data = {
                "enable_mag_analyze": 0,
                "enable_imu_data_analyze": 0
                }

        if self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG:
            data["enable_mag_analyze"] = 1
        elif self.__currentModeIdx__ == MODE_IDX_IMU_DATA:
            data["enable_imu_data_analyze"] = 1


        jsonString = json.dumps(data)
        SaveConfigFile(FILE_CONFIG_WINDOW, jsonString)



    # When load data from .txt file, runtime data of current selected mode will be cleared.
    def onLoadFile(self, filePath):
        # Data is seperated by ','
        data = np.loadtxt(filePath, delimiter=',')

        # Create array that contains timestamp. Assume that sample was recorded every 20ms
        num_samples = data.shape[0]

        Time = np.empty((num_samples,1), float)
        currentTime = 0.0

        for idx in range(num_samples):
            Time[idx] = currentTime
            currentTime += 0.02

        # Display data for mode Mag analyzer
        if self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG:
            self.__selectedFile_MagAnalyze__ = filePath

            self.__runtime_MagData__ = np.empty((0,4), int)
        
            if data.shape[1] == 3:
                self.__savedTxt_MagData__ = np.concatenate((Time, data), axis=1)
                self.__componentMagAnalyze__.setRawData(data)
                self.__componentMagPlotter__.plot(self.__savedTxt_MagData__)
            else:
                print('Incorrect mag data format')

        # Display data for mode IMU Data analyzer
        elif self.__currentModeIdx__ == MODE_IDX_IMU_DATA:
            self.__selectedFile_SerialPlotter__ = filePath
            
            self.__runtime_ImuData__ = np.empty((0,10), int)

            if data.shape[1] == 9:
                self.__savedTxt_ImuData__ = np.concatenate((Time, data), axis=1)
                self.ComponentImuData.plot(self.__savedTxt_ImuData__)
            else:
                print('Incorrect all data format')

        self.__widget_SelectFile__.setSelectedFileName(os.path.basename(filePath))


    def DrawData(self):
        # Only draw data when serial is connecting
        if self.__componentSerialControl__.getConnectStatus() == True:
            listData = self.__componentSerialControl__.getSeriaData()
            for data in listData:
                # Log data to console
                self.__componentConsole__.logInfo(data[1])

                # Read data to np array
                splitData = np.array(data[1].split(','), dtype=int)

                # Draw IMU data
                if self.__currentModeIdx__ == MODE_IDX_IMU_DATA and splitData.size == 9:
                    # If no runtime data before, start draw data from origin. Else, calculate time offset from now to origin
                    if len(self.__runtime_ImuData__) == 0:
                        self.__runtime_TimeStartMs__ = time.time()
                        timestamp = 0.0
                    else:
                        timestamp = float(data[0]-self.__runtime_TimeStartMs__)

                    self.__runtime_ImuData__ = np.append(self.__runtime_ImuData__, [[timestamp,
                                                                    int(splitData[0]), int(splitData[1]), int(splitData[2]), 
                                                                    int(splitData[3]), int(splitData[4]), int(splitData[5]), 
                                                                    int(splitData[6]), int(splitData[7]), int(splitData[8])]], axis=0)
                
                # Draw mag data
                elif self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG and splitData.size == 3:
                    # If no runtime data before, start draw data from origin. Else, calculate time offset from now to origin
                    if len(self.__runtime_MagData__) == 0:
                        self.__runtime_TimeStartMs__ = time.time()
                        timestamp = 0.0
                    else:
                        timestamp = float(data[0]-self.__runtime_TimeStartMs__)

                    self.__runtime_MagData__ = np.append(self.__runtime_MagData__, [[timestamp, int(splitData[0]), int(splitData[1]), int(splitData[2])]], axis=0)


            if self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG:
                # Set raw data which necessary for calculate calibrated data
                self.__componentMagAnalyze__.setRawData(self.__runtime_MagData__[:,[1,2,3]])

                self.__componentMagPlotter__.plot(self.__runtime_MagData__)


            elif self.__currentModeIdx__ == MODE_IDX_IMU_DATA:
                self.__componentImuData__.plot(self.__runtime_ImuData__)




app = QApplication(sys.argv)

window = MainWindow()
window.showMaximized()
sys.exit(app.exec())