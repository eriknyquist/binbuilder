import sys
import os

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore, QtGui


if getattr(sys, 'frozen', False):
    SOURCE_DIR = os.path.dirname(sys.executable)
else:
    SOURCE_DIR = os.path.dirname(__file__)

IMAGE_DIR = os.path.join(SOURCE_DIR, 'images')
ICON_PATH = os.path.join(IMAGE_DIR, 'icon.png')


def truncate_string(s, max_len=24):
    if len(s) > max_len:
        return s[:max_len - 4] + " ..."

    return s


class ScrollableTextDisplay(QtWidgets.QDialog):
    def __init__(self, title, text, monospace=True):
        super(ScrollableTextDisplay, self).__init__()

        mainLayout = QtWidgets.QVBoxLayout(self)

        self.text_browser = QtWidgets.QTextBrowser()
        self.text_browser.append(text)

        if monospace:
            font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
            self.text_browser.setFont(font)

        mainLayout.addWidget(self.text_browser)

        self.setLayout(mainLayout)
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))

    def sizeHint(self):
        return QtCore.QSize(600, 400)


def errorDialog(parent, heading="Error", message="Unrecoverable error occurred"):
    msg = QtWidgets.QMessageBox(parent)
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(heading)
    msg.setInformativeText(message)
    msg.setWindowTitle("Error")
    msg.setWindowIcon(QtGui.QIcon(ICON_PATH))
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()

