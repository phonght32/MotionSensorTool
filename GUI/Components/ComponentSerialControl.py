from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QGridLayout, QPushButton, QLineEdit, QPlainTextEdit, QFileDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6 import QtTest
from GUI.Config.Config_Widget import *
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

List_DataBits = [
    '7',
    '8'
]

List_DataBits_Value = [
    7,
    8
]

List_Parity = [
    'None',
    'Odd',
    'Even'
]

List_Parity_Value = [
    0,
    1,
    2
]

List_StopBits = [
    '1',
    '2'
]

List_StopBits_Value = [
    1,
    1
]

UNHANDLED_KEYS = [Qt.Key.Key_Backspace, Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up,
                  Qt.Key.Key_Down]

@singleton
class ComponentSerialControl(QWidget):
    def __init__(self):
        super().__init__()

        self.__current_ListComPort__ = []
        self.__current_SelectedDeviceIdx__ = 0
        self.__current_SelectedDeviceName__ = ''
        self.__current_SerialPort__ = None
        self.__current_SerialPortOpened__ = False

        self.__current_BaudrateIdx__ = 5
        self.__current_DataBitsIdx__ = 1
        self.__current_ParityIdx__ = 0
        self.__current_StopBitsIdx__ = 0

        self.__current_ListSerialData__ = []

        self.__callback_GetData__ = None

        self.__label_ComPort__ = QLabel('COM')
        self.__label_ComPort__.setFixedWidth(DIMENSION_LABEL_WIDTH)

        self.__combobox_ComPort__ = QComboBox()
        self.__combobox_ComPort__.setFixedWidth(DIMENSION_COMBOBOX_WIDTH)
        self.__combobox_ComPort__.currentTextChanged.connect(self.onChangeComport)

        self.__button_Connect__ = QPushButton('Connect')
        self.__button_Connect__.setFixedWidth(DIMENSION_BUTTON_WIDTH)
        self.__button_Connect__.clicked.connect(self.onClickConnect)


        self.__label_Baudrate = QLabel('Baud rates')
        self.__label_Baudrate.setFixedWidth(DIMENSION_LABEL_WIDTH)

        self.__combobox_Baudrates__ = QComboBox()
        self.__combobox_Baudrates__.setFixedWidth(DIMENSION_COMBOBOX_WIDTH)
        self.__combobox_Baudrates__.addItems(ListBaudrate)
        self.__combobox_Baudrates__.setCurrentIndex(self.__current_BaudrateIdx__)
        self.__combobox_Baudrates__.currentIndexChanged.connect(self.onChangeBaudrates)

        self.__label_DataBits__ = QLabel('Data bits')
        self.__label_DataBits__.setFixedWidth(DIMENSION_LABEL_WIDTH)

        self.__combobox_DataBits__ = QComboBox()
        self.__combobox_DataBits__.setFixedWidth(DIMENSION_COMBOBOX_WIDTH)
        self.__combobox_DataBits__.addItems(List_DataBits)
        self.__combobox_DataBits__.setCurrentIndex(self.__current_DataBitsIdx__)
        self.__combobox_DataBits__.currentIndexChanged.connect(self.onChangeDataBits)

        self.__label_Parity__ = QLabel('Parity')
        self.__label_Parity__.setFixedWidth(DIMENSION_LABEL_WIDTH)

        self.__combobox_Parity__ = QComboBox()
        self.__combobox_Parity__.setFixedWidth(DIMENSION_COMBOBOX_WIDTH)
        self.__combobox_Parity__.addItems(List_Parity)
        self.__combobox_Parity__.setCurrentIndex(self.__current_ParityIdx__)
        self.__combobox_Parity__.currentIndexChanged.connect(self.onChangeParity)

        self.__label_StopBits__ = QLabel('Stop bits')
        self.__label_StopBits__.setFixedWidth(DIMENSION_LABEL_WIDTH)

        self.__combobox_StopBits__ = QComboBox()
        self.__combobox_StopBits__.setFixedWidth(DIMENSION_COMBOBOX_WIDTH)
        self.__combobox_StopBits__.addItems(List_StopBits)
        self.__combobox_StopBits__.setCurrentIndex(self.__current_StopBitsIdx__)
        self.__combobox_StopBits__.currentIndexChanged.connect(self.onChangeStopBits)

        

        self.__serialSetting_layout__ = QGridLayout()
        self.__serialSetting_layout__.setAlignment(Qt.AlignmentFlag.AlignTop)

        currentRowIdx = 0
        self.__serialSetting_layout__.addWidget(self.__label_ComPort__, currentRowIdx, 1)
        self.__serialSetting_layout__.addWidget(self.__combobox_ComPort__, currentRowIdx, 2)
        self.__serialSetting_layout__.addWidget(self.__button_Connect__, currentRowIdx, 3)

        currentRowIdx += 1
        self.__serialSetting_layout__.addWidget(self.__label_Baudrate, currentRowIdx, 1)
        self.__serialSetting_layout__.addWidget(self.__combobox_Baudrates__, currentRowIdx, 2)
        
        currentRowIdx += 1
        self.__serialSetting_layout__.addWidget(self.__label_DataBits__, currentRowIdx, 1)
        self.__serialSetting_layout__.addWidget(self.__combobox_DataBits__, currentRowIdx, 2)

        currentRowIdx += 1
        self.__serialSetting_layout__.addWidget(self.__label_Parity__, currentRowIdx, 1)
        self.__serialSetting_layout__.addWidget(self.__combobox_Parity__, currentRowIdx, 2)

        currentRowIdx += 1
        self.__serialSetting_layout__.addWidget(self.__label_StopBits__, currentRowIdx, 1)
        self.__serialSetting_layout__.addWidget(self.__combobox_StopBits__, currentRowIdx, 2)

        self.__serialSetting_widget__ = QWidget()
        self.__serialSetting_widget__.setLayout(self.__serialSetting_layout__)


        layout = QVBoxLayout()
        layout.addWidget(self.__serialSetting_widget__)
        self.setLayout(layout)

        scanTimer = QTimer(self)
        scanTimer.timeout.connect(self.searchDevCP210x)
        scanTimer.start(500)

    


    def searchDevCP210x(self):
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
        self.__current_BaudrateIdx__ = idx

    def onChangeDataBits(self, idx):
        self.__current_DataBitsIdx__ = idx

    def onChangeParity(self, idx):
        self.__current_ParityIdx__ = idx

    def onChangeStopBits(self, idx):
        self.__current_StopBitsIdx__ = idx

    def onClickConnect(self):
        if self.__current_SerialPortOpened__ == False:
            if self.__current_SelectedDeviceName__ != '':
                self.__current_SerialPort__ = serial.Serial(self.__current_SelectedDeviceName__, 
                                                            ListBaudrateValue[self.__current_BaudrateIdx__], 
                                                            timeout=0.001, 
                                                            xonxoff=False)
                self.__button_Connect__.setText('Disconnect')
                self.__current_SerialPortOpened__ = True
                self.__timerGetData__ = QTimer(self)
                self.__timerGetData__.timeout.connect(self.TaskGetData)
                self.__timerGetData__.start(1)
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
        index = 0
        while self.__current_SerialPort__.in_waiting > 0:
            
            timestamp = time.time()
            index += 1
            string_data = self.__current_SerialPort__.readline().decode('utf-8')

            self.__current_ListSerialData__.append([timestamp, string_data])

        if index > 1:
            for i in range(index):
                self.__current_ListSerialData__[i][0] -= (index - i - 1)*0.05


    def getSeriaData(self):
        listData = []
        while len(self.__current_ListSerialData__) > 0:
            data = self.__current_ListSerialData__[0]
            listData.append(data)
            self.__current_ListSerialData__.pop(0)


        return listData

    def getConnectStatus(self):
        if self.__current_SerialPort__ != None:
            return self.__current_SerialPort__.isOpen()
        else:
            return False




    




