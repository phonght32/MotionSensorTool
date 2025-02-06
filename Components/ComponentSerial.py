from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QGridLayout, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6 import QtTest
from Dimension.Dimension import *
from Utils.Singleton import *

import time
import serial
import serial.tools.list_ports as prtlst

ListBaudrate = [
    '4800',
    '9600',
    '19200',
    '38400',
    '57600',
    '115200',
    '460800',
    '912600'
]

ListBaudrateValue = [
    4800,
    9600,
    19200,
    38400,
    57600,
    115200,
    460800,
    912600
]

@singleton
class ComponentSerial(QWidget):
    def __init__(self):
        super().__init__()

        self.__current_ListComPort__ = []
        self.__current_SelectedDeviceIdx__ = 0
        self.__current_SelectedDeviceName__ = ''
        self.__current_SerialPort__ = None
        self.__current_SerialPortOpened__ = False

        self.__current_SelectedBaudrateIdx__ = 5

        self.__callback_GetData__ = None

        # Create widgets for select COM Port 
        self.__label_ComPort__ = QLabel('COM')
        self.__label_ComPort__.setFixedWidth(DIMENSION_LABEL_WIDTH)

        self.__combobox_ComPort__ = QComboBox()
        self.__combobox_ComPort__.setFixedWidth(DIMENSION_COMBOBOX_WIDTH)
        self.__combobox_ComPort__.currentTextChanged.connect(self.onChangeComport)

        self.__button_Connect__ = QPushButton('Connect')
        self.__button_Connect__.setFixedWidth(DIMENSION_BUTTON_WIDTH)
        self.__button_Connect__.clicked.connect(self.onClickConnect)


        #Create widgets for select baudrate
        self.__label_Baudrate = QLabel('Baud rates')
        self.__label_Baudrate.setFixedWidth(DIMENSION_LABEL_WIDTH)

        self.__combobox_Baudrates__ = QComboBox()
        self.__combobox_Baudrates__.setFixedWidth(DIMENSION_COMBOBOX_WIDTH)
        self.__combobox_Baudrates__.addItems(ListBaudrate)
        self.__combobox_Baudrates__.setCurrentText(ListBaudrate[self.__current_SelectedBaudrateIdx__])
        self.__combobox_Baudrates__.currentIndexChanged.connect(self.onChangeBaudrates)



        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        currentRowIdx = 0
        layout.addWidget(self.__label_ComPort__, currentRowIdx, 1)
        layout.addWidget(self.__combobox_ComPort__, currentRowIdx, 2)
        layout.addWidget(self.__button_Connect__, currentRowIdx, 3)

        currentRowIdx += 1
        layout.addWidget(self.__label_Baudrate, currentRowIdx, 1)
        layout.addWidget(self.__combobox_Baudrates__, currentRowIdx, 2)

        self.setLayout(layout)

        scanTimer = QTimer(self)
        scanTimer.timeout.connect(self.SearchDevCP210x)
        scanTimer.start(1000)

        self.num_read = 0

    def createButtonControl(self):

        self.__buttonAnalyzeData__ = QPushButton('Start')
        self.__buttonAnalyzeData__.setFixedWidth(DIMENSION_BUTTON_WIDTH)

        self.__buttonControlLayout__ = QHBoxLayout()
        self.__buttonControlLayout__.addWidget(self.__buttonAnalyzeData__)
        self.__buttonControlLayout__.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.__buttonControlWidget__ = QWidget()
        self.__buttonControlWidget__.setLayout(self.__buttonControlLayout__)

        return self.__buttonControlWidget__


    def SearchDevCP210x(self):
        COMs=[]
        pts= prtlst.comports()

        for pt in pts:
            if 'USB' in pt[1]: #check 'USB' string in device description
                COMs.append(pt[0])

        self.__combobox_ComPort__.clear()
        self.__combobox_ComPort__.addItems(COMs)

        if self.__current_SerialPortOpened__ == True:
            if self.__current_SelectedDeviceName__ not in COMs:
                self.__current_SerialPort__.close()
                self.__button_Connect__.setText('Connect')
                self.__current_SerialPortOpened__ = False
                self.__timerGetData__.stop()
                print('Device is disconnected')

    def onChangeComport(self, idx):
        self.__current_SelectedDeviceIdx__ = idx
        self.__current_SelectedDeviceName__ = self.__combobox_ComPort__.currentText()

    def onChangeBaudrates(self, idx):
        self.__current_SelectedBaudrateIdx__ = idx



    def onClickConnect(self):
        if self.__current_SerialPortOpened__ == False:
            if self.__current_SelectedDeviceName__ != '':
                self.__current_SerialPort__ = serial.Serial(self.__current_SelectedDeviceName__, ListBaudrateValue[self.__current_SelectedBaudrateIdx__], timeout=0.001, xonxoff=False)
                self.__button_Connect__.setText('Disconnect')
                self.__current_SerialPortOpened__ = True
                self.__timerGetData__ = QTimer(self)
                self.__timerGetData__.timeout.connect(self.TaskGetData)
                self.__timerGetData__.start(100)
                print('Connect to {}'.format(self.__current_SelectedDeviceName__))

            else:
                print('Please insert device')

        else:
            self.__current_SerialPort__.close()
            self.__button_Connect__.setText('Connect')
            self.__current_SerialPortOpened__ = False
            self.__timerGetData__.stop()
            print('Disconnect to {}'.format(self.__current_SelectedDeviceName__))

    def TaskGetData(self):
        if self.__callback_GetData__ != None:
            timestamp = time.time()
            binary_string = self.__current_SerialPort__.readline()
            self.__callback_GetData__(timestamp, binary_string)

            # binary_string = self.__current_SerialPort__.read()
            # print('{} {}'.format(self.num_read, binary_string))
            

    def registerCallbackAnalyze(self, callback):
        self.__callback_GetData__ = callback


    




