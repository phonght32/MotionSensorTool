import logging
from PyQt6 import QtGui
from PyQt6.QtWidgets import QWidget, QPlainTextEdit
from Utils.Singleton import *


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
		self.widget = QPlainTextEdit(parent)
		self.widget.setReadOnly(True)

	def emit(self, record):
		msg = self.format(record)
		self.widget.appendHtml(msg)
		scrollbar = self.widget.verticalScrollBar()
		scrollbar.setValue(scrollbar.maximum())

	def clear(self):
		self.widget.clear()

	def getCurrentText(self):
		return self.widget.toPlainText()

	def logDebug(self, *arg):
		logging.debug(*arg)

	def logInfo(self, *arg):
		logging.info(*arg)