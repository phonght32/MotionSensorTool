from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import Qt

from Utils.Singleton import *
from Dimension.Dimension import *

import os

@singleton
class ComponentSelectFile(QWidget):
	def __init__(self):
		super().__init__()

		self.__callbackLoadFile__ = None
		self.__current_FileContent__ = ''

		self.__current_SelectedFilePath__ = 'None'

		self.__label_FilePath__ = QLabel('File:')
		self.__label_FilePath__.setFixedWidth(DIMENSION_LABEL_WIDTH)

		self.__label_SelectedFilePath__ = QLabel(self.__current_SelectedFilePath__)
		self.__label_SelectedFilePath__.setFixedWidth(DIMENSION_COMBOBOX_WIDTH)

		self.__button_LoadFile__ = QPushButton('Load')
		self.__button_LoadFile__.clicked.connect(self.onLoadFile)


		layout = QHBoxLayout()
		layout.addWidget(self.__label_FilePath__)
		layout.addWidget(self.__label_SelectedFilePath__)
		layout.addWidget(self.__button_LoadFile__)

		self.setLayout(layout)


	def onLoadFile(self):
		dialog = QFileDialog(self)
		dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
		if dialog.exec():
			filePath, = dialog.selectedFiles()
			if filePath:
				self.__current_FileContent__ = ''
				with open(filePath, 'r') as file:
					self.__current_FileContent__ = file.read()

					if self.__callbackLoadFile__:
						self.__callbackLoadFile__(self.__current_FileContent__)

	def registerCallbackLoadFile(self, callback):
		self.__callbackLoadFile__ = callback
