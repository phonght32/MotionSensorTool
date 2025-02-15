from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import Qt

from Utils.Singleton import *
from Dimension.Dimension import *

import os

class WidgetSelectFile(QWidget):
	def __init__(self, onLoadFile=None):
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
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.__label_FilePath__)
		layout.addWidget(self.__label_SelectedFilePath__)
		layout.addWidget(self.__button_LoadFile__)

		self.setLayout(layout)


		self.__callbackLoadFile__ = onLoadFile


	def onLoadFile(self):
		dialog = QFileDialog(self)
		dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
		if dialog.exec():
			filePath, = dialog.selectedFiles()
			if filePath:

				self.__current_SelectedFilePath__ = filePath
				self.__label_SelectedFilePath__.setText(os.path.basename(self.__current_SelectedFilePath__))

				# with open(filePath, 'r') as file:
				# 	self.__current_FileContent__ = file.read()

				if self.__callbackLoadFile__:
					self.__callbackLoadFile__(self.__current_SelectedFilePath__)

