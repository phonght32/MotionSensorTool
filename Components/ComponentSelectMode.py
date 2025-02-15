from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QRadioButton, QButtonGroup

from Components.ComponentSerialControl import *
from Components.ComponentSerialPlotter import *
from Components.ComponentMag import *
from Utils.LoadConfigFile import *


MODE_IDX_SERIAL_PLOTTER = 0
MODE_IDX_ANALYZE_MAG = 1

class ComponentSelectMode(QWidget):
	def __init__(self):
		super().__init__()

		self.configModeData = LoadConfigFile()

		self.__currentModeIdx__ = MODE_IDX_ANALYZE_MAG


		self.radiobutton_AnalyzeMag = QRadioButton('Magnetometer')
		self.radiobutton_AnalyzeMag.setChecked(self.configModeData['enable_mag_analyze']) 
		self.radiobutton_SerialPlotter = QRadioButton('Serial Plotter')
		self.radiobutton_SerialPlotter.setChecked(self.configModeData['enable_serial_plotter']) 


		ComponentMagPlotter().setVisible(self.configModeData['enable_mag_analyze'])
		ComponentMagAnalyze().setVisible(self.configModeData['enable_mag_analyze'])
		ComponentSerialPlotter().setVisible(self.configModeData['enable_serial_plotter'])
		ComponentSerialControl().setVisible(self.configModeData['enable_serial_plotter'])


		self.groupRadioButton = QButtonGroup(self)
		self.groupRadioButton.addButton(self.radiobutton_SerialPlotter, MODE_IDX_SERIAL_PLOTTER)
		self.groupRadioButton.addButton(self.radiobutton_AnalyzeMag, MODE_IDX_ANALYZE_MAG)
		self.groupRadioButton.buttonClicked.connect(self.onChangeMode)

		layout = QHBoxLayout()
		layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
		layout.addWidget(self.radiobutton_SerialPlotter)
		layout.addWidget(self.radiobutton_AnalyzeMag)



		self.setLayout(layout)

	def onChangeMode(self, object):
		self.__currentModeIdx__ = self.groupRadioButton.id(object)

		if self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG:
			ComponentMagPlotter().setVisible(True)
			ComponentMagAnalyze().setVisible(True)
			ComponentSerialControl().setVisible(False)
			ComponentSerialPlotter().setVisible(False)
		elif self.__currentModeIdx__ == MODE_IDX_SERIAL_PLOTTER:
			ComponentMagPlotter().setVisible(False)
			ComponentMagAnalyze().setVisible(False)
			ComponentSerialControl().setVisible(True)
			ComponentSerialPlotter().setVisible(True)

