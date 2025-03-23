import sys
import os
import re
import json

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QStatusBar, QRadioButton, QButtonGroup
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets


from Utils.HandleFile import *
from GUI.Components.ComponentSerialControl import *
from GUI.Components.ComponentImuData import *
from GUI.Components.ComponentMag import *
from GUI.Components.ComponentConsole import *
from GUI.Components.ComponentAngle import *

from GUI.Widgets.WidgetSelectFile import *

MODE_IDX_IMU_DATA_ANALYZER = 0
MODE_IDX_MAG_ANALYZER = 1
MODE_IDX_ANGLE_ANALYZER = 2


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Numpy array contains IMU data and timestamp: [timestamp, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z]
        self.__runtime_ImuData__ = np.empty((0, 10), float)

        # Numpy array contains saved IMU data from .txt file
        self.__savedTxt_ImuData__ = np.empty((0, 10), float)

        # Numpy array contains magnetometer data and timestamp: [timestamp, mag_x, mag_y, mag_z]
        self.__runtime_MagData__ = np.empty((0, 4), float)

        # Numpy array contains saved mag data from .txt file
        self.__savedTxt_MagData__ = np.empty((0, 4), float)

        # Numpy array contains angle data and timestamp: [timestamp, roll, pitch, yaw]
        self.__runtime_AngleData__ = np.empty((0, 4), float)

        # Numpy array contains saved angle data from .txt file
        self.__savedTxt_AngleData__ = np.empty((0, 4), float)

        # Time point when start monitor data
        self.__runtime_TimeStartMs__ = 0

        # Current selected files
        self.__selectedFile_ImuDataAnalyzer__ = ''
        self.__selectedFile_MagAnalyzer__ = ''
        self.__selectedFile_AngleAnalyzer__ = ''

        self.__configModeData__ = LoadConfigFile(FILE_CONFIG_WINDOW)

        # Get current mode display [IMU data, magnetometer]
        if self.__configModeData__['enable_imu_data_analyzer'] == 1:
            self.__currentModeIdx__ = MODE_IDX_IMU_DATA_ANALYZER
        elif self.__configModeData__['enable_mag_analyzer'] == 1:
            self.__currentModeIdx__ = MODE_IDX_MAG_ANALYZER
        elif self.__configModeData__['enable_angle_analyzer'] == 1:
            self.__currentModeIdx__ = MODE_IDX_ANGLE_ANALYZER

        # Create component serial control
        self.__componentSerialControl__ = ComponentSerialControl()

        # Create component IMU data
        self.__componentImuData__ = ComponentImuDataPlotter()
        self.__componentImuData__.setVisible(
            self.__configModeData__['enable_imu_data_analyzer'])

        # Create component mag plotter
        self.__componentMagPlotter__ = ComponentMagPlotter()
        self.__componentMagPlotter__.setVisible(
            self.__configModeData__['enable_mag_analyzer'])

        # Create component mag analyzer
        self.__componentMagAnalyze__ = ComponentMagAnalyze()
        self.__componentMagAnalyze__.setVisible(
            self.__configModeData__['enable_mag_analyzer'])

        # Create component angle analyzer
        self.__componentAnglePlotter__ = ComponentAnglePlotter()
        self.__componentAnglePlotter__.setVisible(
            self.__configModeData__['enable_angle_analyzer'])

        # Create button clear plotter
        self.__button_Plotter_Clear__ = QPushButton('Clear')
        self.__button_Plotter_Clear__.setFixedWidth(DIMENSION_BUTTON_WIDTH)
        self.__button_Plotter_Clear__.clicked.connect(self.onClickClearPlotter)

        # Create component select file
        self.__widget_SelectFile__ = WidgetSelectFile(self.onLoadFile)

        # Create component console
        self.__componentConsole__ = ComponentConsole(self)
        self.__componentConsole__.setFormatter(CustomeFormatter())

        # Create radio button for mode selection
        self.__radiobutton_AnalyzeMag__ = QRadioButton('Magnetometer')
        self.__radiobutton_AnalyzeMag__.setChecked(
            self.__configModeData__['enable_mag_analyzer'])
        self.__radiobutton_ImuData__ = QRadioButton('IMU data')
        self.__radiobutton_ImuData__.setChecked(
            self.__configModeData__['enable_imu_data_analyzer'])
        self.__radiobutton_AngleAnalyzer__ = QRadioButton('Angle')
        self.__radiobutton_AngleAnalyzer__.setChecked(
            self.__configModeData__['enable_angle_analyzer'])

        self.__groupRadioButton_SelectMode__ = QButtonGroup(self)
        self.__groupRadioButton_SelectMode__.addButton(
            self.__radiobutton_ImuData__, MODE_IDX_IMU_DATA_ANALYZER)
        self.__groupRadioButton_SelectMode__.addButton(
            self.__radiobutton_AnalyzeMag__, MODE_IDX_MAG_ANALYZER)
        self.__groupRadioButton_SelectMode__.addButton(
            self.__radiobutton_AngleAnalyzer__, MODE_IDX_ANGLE_ANALYZER)
        self.__groupRadioButton_SelectMode__.buttonClicked.connect(
            self.onChangeMode)

        self.__groupRadioButton_SelectMode_Layout__ = QHBoxLayout()
        self.__groupRadioButton_SelectMode_Layout__.addWidget(
            self.__radiobutton_ImuData__)
        self.__groupRadioButton_SelectMode_Layout__.addWidget(
            self.__radiobutton_AnalyzeMag__)
        self.__groupRadioButton_SelectMode_Layout__.addWidget(
            self.__radiobutton_AngleAnalyzer__)
        self.__groupRadioButton_SelectMode_Widget__ = QWidget()
        self.__groupRadioButton_SelectMode_Widget__.setLayout(
            self.__groupRadioButton_SelectMode_Layout__)

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
        rightPannelLayout.addWidget(self.__componentAnglePlotter__)
        rightPannelLayout.addWidget(
            self.__button_Plotter_Clear__, alignment=Qt.AlignmentFlag.AlignRight)
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
        self.__timerDrawData__.start(1)

    def onChangeMode(self, object):
        self.__currentModeIdx__ = self.__groupRadioButton_SelectMode__.id(
            object)

        if self.__currentModeIdx__ == MODE_IDX_MAG_ANALYZER:
            # Hide/Unhide widgets
            self.__componentMagPlotter__.setVisible(True)
            self.__componentMagAnalyze__.setVisible(True)
            self.__componentImuData__.setVisible(False)
            self.__componentAnglePlotter__.setVisible(False)

            # Update selected file name
            self.__widget_SelectFile__.setSelectedFileName(
                os.path.basename(self.__selectedFile_MagAnalyzer__))

            # Save current config
            self.saveCurrentConfig()

        elif self.__currentModeIdx__ == MODE_IDX_IMU_DATA_ANALYZER:
            # Hide/Unhide widgets
            self.__componentMagPlotter__.setVisible(False)
            self.__componentMagAnalyze__.setVisible(False)
            self.__componentImuData__.setVisible(True)
            self.__componentAnglePlotter__.setVisible(False)

            # Update selected file name
            self.__widget_SelectFile__.setSelectedFileName(
                os.path.basename(self.__selectedFile_ImuDataAnalyzer__))

            # Save current config
            self.saveCurrentConfig()

        elif self.__currentModeIdx__ == MODE_IDX_ANGLE_ANALYZER:
            # Hide/Unhide widgets
            self.__componentMagPlotter__.setVisible(False)
            self.__componentMagAnalyze__.setVisible(False)
            self.__componentImuData__.setVisible(False)
            self.__componentAnglePlotter__.setVisible(True)

            # Update selected file name
            self.__widget_SelectFile__.setSelectedFileName(
                os.path.basename(self.__selectedFile_AngleAnalyzer__))

            # Save current config
            self.saveCurrentConfig()

    def onClickClearPlotter(self):
        # Clear plotter of magnetometer
        if self.__currentModeIdx__ == MODE_IDX_MAG_ANALYZER:
            self.__runtime_MagData__ = np.empty((0, 4), float)
            self.__componentMagPlotter__.clear()

        # Clear plotter of imu data
        elif self.__currentModeIdx__ == MODE_IDX_IMU_DATA_ANALYZER:
            self.__runtime_ImuData__ = np.empty((0, 10), float)
            self.__componentImuData__.clear()

        # Clear plotter of angle
        elif self.__currentModeIdx__ == MODE_IDX_ANGLE_ANALYZER:
            self.__runtime_AngleData__ = np.empty((0, 4), float)
            self.__componentAnglePlotter__.clear()

    def saveCurrentConfig(self):
        data = {"enable_mag_analyzer": 0,
                "enable_imu_data_analyzer": 0,
                "enable_angle_analyzer": 0}

        if self.__currentModeIdx__ == MODE_IDX_MAG_ANALYZER:
            data["enable_mag_analyzer"] = 1
        elif self.__currentModeIdx__ == MODE_IDX_IMU_DATA_ANALYZER:
            data["enable_imu_data_analyzer"] = 1
        elif self.__currentModeIdx__ == MODE_IDX_ANGLE_ANALYZER:
            data["enable_angle_analyzer"] = 1

        jsonString = json.dumps(data)
        SaveConfigFile(FILE_CONFIG_WINDOW, jsonString)

    # When load data from .txt file, runtime data of current selected mode will be cleared.

    def onLoadFile(self, filePath):
        # Data is seperated by ','
        data = np.loadtxt(filePath, delimiter=',')

        # Create array that contains timestamp. Assume that sample was recorded every 20ms
        num_samples = data.shape[0]

        Time = np.empty((num_samples, 1), float)
        currentTime = 0.0

        for idx in range(num_samples):
            Time[idx] = currentTime
            currentTime += 0.02

        # Display data for mode IMU Data analyzer
        if self.__currentModeIdx__ == MODE_IDX_IMU_DATA_ANALYZER:
            if data.shape[1] == 9:
                self.__selectedFile_ImuDataAnalyzer__ = filePath
                self.__widget_SelectFile__.setSelectedFileName(
                    os.path.basename(filePath))

                self.__runtime_ImuData__ = np.empty((0, 10), float)
                self.__savedTxt_ImuData__ = np.concatenate(
                    (Time, data), axis=1)
                self.__componentImuData__.plot(self.__savedTxt_ImuData__)
            else:
                print('Incorrect all data format')

        # Display data for mode Mag analyzer
        elif self.__currentModeIdx__ == MODE_IDX_MAG_ANALYZER:
            if data.shape[1] == 3:
                self.__selectedFile_MagAnalyzer__ = filePath
                self.__widget_SelectFile__.setSelectedFileName(
                    os.path.basename(filePath))

                self.__runtime_MagData__ = np.empty((0, 4), float)
                self.__savedTxt_MagData__ = np.concatenate(
                    (Time, data), axis=1)
                self.__componentMagAnalyze__.setRawData(data)
                self.__componentMagPlotter__.plot(self.__savedTxt_MagData__)
            else:
                print('Incorrect mag data format')

        # Display data for mode angle analyzer
        elif self.__currentModeIdx__ == MODE_IDX_ANGLE_ANALYZER:
            if data.shape[1] == 3:
                self.__selectedFile_AngleAnalyzer__ = filePath
                self.__widget_SelectFile__.setSelectedFileName(
                    os.path.basename(filePath))

                self.__runtime_AngleData__ = np.empty((0, 4), float)
                self.__savedTxt_AngleData__ = np.concatenate(
                    (Time, data), axis=1)
                self.__componentAnglePlotter__.plot(
                    self.__savedTxt_AngleData__)
            else:
                print('Incorrect angle data format')

    def DrawData(self):
        # Only draw data when serial is connecting
        if self.__componentSerialControl__.getConnectStatus() == True:
            listData = self.__componentSerialControl__.getSeriaData()
            for data in listData:
                # Log data to console
                self.__componentConsole__.logInfo(data[1])

                # Read data to np array
                # splitData = np.array(data[1].split(','), dtype=float)
                try:
                    f = [float(x) for x in re.split('[,;]', data[1])]
                    splitData = np.array(f)

                    # Draw IMU data
                    if self.__currentModeIdx__ == MODE_IDX_IMU_DATA_ANALYZER and splitData.size == 9:
                        # If no runtime data before, start draw data from origin. Else, calculate time offset from now to origin
                        if len(self.__runtime_ImuData__) == 0:
                            self.__runtime_TimeStartMs__ = time.time()
                            timestamp = 0.0
                        else:
                            timestamp = float(
                                data[0]-self.__runtime_TimeStartMs__)

                        self.__runtime_ImuData__ = np.append(self.__runtime_ImuData__,
                                                             [[timestamp,
                                                               float(splitData[0]), float(
                                                                   splitData[1]), float(splitData[2]),
                                                               float(splitData[3]), float(
                                                                   splitData[4]), float(splitData[5]),
                                                               float(splitData[6]), float(splitData[7]), float(splitData[8])]],
                                                             axis=0)

                    # Draw mag data
                    elif self.__currentModeIdx__ == MODE_IDX_MAG_ANALYZER and splitData.size == 3:
                        # If no runtime data before, start draw data from origin. Else, calculate time offset from now to origin
                        if len(self.__runtime_MagData__) == 0:
                            self.__runtime_TimeStartMs__ = time.time()
                            timestamp = 0.0
                        else:
                            timestamp = float(
                                data[0]-self.__runtime_TimeStartMs__)

                        self.__runtime_MagData__ = np.append(self.__runtime_MagData__, [[timestamp, float(
                            splitData[0]), float(splitData[1]), float(splitData[2])]], axis=0)

                    # Draw angle data
                    elif self.__currentModeIdx__ == MODE_IDX_ANGLE_ANALYZER and splitData.size == 3:
                        # If no runtime data before, start draw data from origin. Else, calculate time offset from now to origin
                        if len(self.__runtime_AngleData__) == 0:
                            self.__runtime_TimeStartMs__ = time.time()
                            timestamp = 0.0
                        else:
                            timestamp = float(
                                data[0]-self.__runtime_TimeStartMs__)

                        self.__runtime_AngleData__ = np.append(self.__runtime_AngleData__, [
                                                               [timestamp, float(splitData[0]), float(splitData[1]), float(splitData[2])]], axis=0)
                except:
                    print('Errors')

            if self.__currentModeIdx__ == MODE_IDX_MAG_ANALYZER:
                # Set raw data which necessary for calculate calibrated data
                if self.__runtime_MagData__.shape[0] != 0:
                    self.__componentMagAnalyze__.setRawData(
                        self.__runtime_MagData__[:, [1, 2, 3]])
                    self.__componentMagPlotter__.plot(self.__runtime_MagData__)

            elif self.__currentModeIdx__ == MODE_IDX_IMU_DATA_ANALYZER:
                if self.__runtime_ImuData__.shape[0] != 0:
                    self.__componentImuData__.plot(self.__runtime_ImuData__)

            elif self.__currentModeIdx__ == MODE_IDX_ANGLE_ANALYZER:
                if self.__runtime_AngleData__.shape[0] != 0:
                    self.__componentAnglePlotter__.plot(
                        self.__runtime_AngleData__)


app = QApplication(sys.argv)

window = MainWindow()
window.showMaximized()
sys.exit(app.exec())
