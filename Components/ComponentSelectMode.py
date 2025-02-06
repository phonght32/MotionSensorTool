from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QRadioButton, QButtonGroup

from Components.ComponentAll import *
from Components.ComponentMag import *
from Utils.LoadConfigFile import *

MODE_IDX_ANALYZE_MAG = 0
MODE_IDX_ANALYZE_ALL = 1

class ComponentSelectMode(QWidget):
	def __init__(self):
		super().__init__()

		self.configModeData = LoadConfigFile()

		self.__currentModeIdx__ = MODE_IDX_ANALYZE_MAG


		# self.radiobutton_AnalyzeAccel = QRadioButton('Accel')
		# self.radiobutton_AnalyzeGyro = QRadioButton('Gyro')
		self.radiobutton_AnalyzeMag = QRadioButton('Mag')
		self.radiobutton_AnalyzeMag.setChecked(self.configModeData['showComponentAnalyzeMag']) 
		# self.radiobutton_AnalyzeBaro = QRadioButton('Baro')
		self.radiobutton_AnalyzeAll = QRadioButton('All')
		self.radiobutton_AnalyzeAll.setChecked(self.configModeData['showComponentAll']) 


		ComponentMagPlotter().setVisible(self.configModeData['showComponentAnalyzeMag'])
		ComponentMagAnalyze().setVisible(self.configModeData['showComponentAnalyzeMag'])
		ComponentAll().setVisible(self.configModeData['showComponentAll'])

		self.groupRadioButton = QButtonGroup(self)
		self.groupRadioButton.addButton(self.radiobutton_AnalyzeMag, MODE_IDX_ANALYZE_MAG)
		self.groupRadioButton.addButton(self.radiobutton_AnalyzeAll, MODE_IDX_ANALYZE_ALL)
		self.groupRadioButton.buttonClicked.connect(self.onChangeMode)

		layout = QHBoxLayout()
		layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
		# layout.addWidget(self.radiobutton_AnalyzeAccel)
		# layout.addWidget(self.radiobutton_AnalyzeGyro)
		layout.addWidget(self.radiobutton_AnalyzeMag)
		# layout.addWidget(self.radiobutton_Ancd LoadConfigFilecdalyzeBaro)
		layout.addWidget(self.radiobutton_AnalyzeAll)



		self.setLayout(layout)

	def onChangeMode(self, object):
		self.__currentModeIdx__ = self.groupRadioButton.id(object)

		if self.__currentModeIdx__ == MODE_IDX_ANALYZE_MAG:
			ComponentMagPlotter().setVisible(True)
			ComponentMagAnalyze().setVisible(True)
			ComponentAll().setVisible(False)
		elif self.__currentModeIdx__ == MODE_IDX_ANALYZE_ALL:
			ComponentMagPlotter().setVisible(False)
			ComponentMagAnalyze().setVisible(False)
			ComponentAll().setVisible(True)

