from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import Qt

from Utils.Singleton import *
from Dimension.Dimension import *

import os

class WidgetSelectFile(QWidget):
	def __init__(self, onLoadFile=None):
		super().__init__()

		self.__callbackLoadFile__ = onLoadFile
		self.__current_FileContent__ = ''

		self.__current_SelectedFilePath__ = 'None'

		self.__label_FilePath__ = QLabel('File:')
		self.__label_FilePath__.setFixedWidth(DIMENSION_LABEL_WIDTH)

		self.__label_SelectedFilePath__ = QLabel(self.__current_SelectedFilePath__)
		self.__label_SelectedFilePath__.setFixedWidth(DIMENSION_COMBOBOX_WIDTH)

		self.__button_LoadFile__ = QPushButton('Load')
		self.__button_LoadFile__.setFixedWidth(DIMENSION_BUTTON_WIDTH)
		self.__button_LoadFile__.clicked.connect(self.onLoadFile)


		layout = QGridLayout()
		layout.addWidget(self.__label_FilePath__, 0, 1)
		layout.addWidget(self.__label_SelectedFilePath__, 0, 2)
		layout.addWidget(self.__button_LoadFile__, 0, 3)
        # layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(layout)



	def onLoadFile(self):
		dialog = QFileDialog(self)
		dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
		if dialog.exec():
			filePath, = dialog.selectedFiles()
			if filePath:

				self.__current_SelectedFilePath__ = filePath
				self.__label_SelectedFilePath__.setText(os.path.basename(self.__current_SelectedFilePath__))

				if self.__callbackLoadFile__:
					self.__callbackLoadFile__(self.__current_SelectedFilePath__)

