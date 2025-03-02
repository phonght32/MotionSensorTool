import logging
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPlainTextEdit, QVBoxLayout, QPushButton, QHBoxLayout
from Utils.Singleton import *

from GUI.Config.Config_Widget import *


class CustomeFormatter(logging.Formatter):
	FORMATS = {
		logging.ERROR: ("%(message)s", QtGui.QColor('red')),
		logging.DEBUG: ("%(message)s", QtGui.QColor('blue')),
		logging.INFO: ("%(message)s", QtGui.QColor('grey')),
		logging.WARNING: ("%(message)s", QtGui.QColor('orange')),
	}

	def format(self, record):
		last_fmt = self._style._fmt
		opt = CustomeFormatter.FORMATS.get(record.levelno)
		if opt:
			fmt, color = opt
			self._style._fmt = \
			"<font font-family: \"Time New Roman\" color=\"{}\" size=\"2\">\
				<pre tab-size: 8;>{}</pre>\
			</font>".format(QtGui.QColor(color).name(), fmt)

		res = logging.Formatter.format(self, record)
		self._style._fmt = last_fmt
		return res


@singleton
class ComponentConsole(logging.Handler):
	def __init__(self, parent):
		super().__init__()

		# Init callback function 
		self.__callback_onSave__ = None 
		self.__callback_onClear__ = None

		# Create button save
		self.__button_SerialControl_Save__ = QPushButton('Save')
		self.__button_SerialControl_Save__.setFixedWidth(DIMENSION_BUTTON_WIDTH)
		self.__button_SerialControl_Save__.clicked.connect(self.onClickSaveConsole)

		# Create button clear
		self.__button_SerialControl_Clear__ = QPushButton('Clear')
		self.__button_SerialControl_Clear__.setFixedWidth(DIMENSION_BUTTON_WIDTH)
		self.__button_SerialControl_Clear__.clicked.connect(self.onClickClearConsole)

		# Combine buttons in a row
		self.__layout_ControlButton__ = QHBoxLayout()
		self.__layout_ControlButton__.setContentsMargins(0,0,0,0)
		self.__layout_ControlButton__.setAlignment(Qt.AlignmentFlag.AlignRight)
		self.__layout_ControlButton__.addWidget(self.__button_SerialControl_Clear__)
		self.__layout_ControlButton__.addWidget(self.__button_SerialControl_Save__)
		self.__widget_ControlButton__ = QWidget()
		self.__widget_ControlButton__.setLayout(self.__layout_ControlButton__)


		# Create console from QPlainTextEdit
		self.__console__ = QPlainTextEdit(parent)
		self.__console__.setReadOnly(True)

		__layout__ = QVBoxLayout()
		__layout__.addWidget(self.__console__)
		__layout__.addWidget(self.__widget_ControlButton__)

		self.widget = QWidget()
		self.widget.setLayout(__layout__)

	def registerOnSave(self, onSave):
		self.__callback_onSave__ = onSave

	def registerOnClear(self, onClear):
		self.__callback_onClear__ = onClear

	def onClickSaveConsole(self):
		if self.__callback_onSave__ != None:
			self.__callback_onSave__()

	def onClickClearConsole(self):
		if self.__callback_onClear__ != None:
			self.__callback_onClear__()

	def emit(self, record):
		msg = self.format(record)
		self.__console__.appendHtml(msg)
		scrollbar = self.__console__.verticalScrollBar()
		scrollbar.setValue(scrollbar.maximum())

	def clear(self):
		self.__console__.clear()

	def getCurrentText(self):
		return self.__console__.toPlainText()

	def logDebug(self, *arg):
		logging.debug(*arg)

	def logInfo(self, *arg):
		logging.info(*arg)