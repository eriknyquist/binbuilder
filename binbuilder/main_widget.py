import os

from binbuilder.block import Block, BlockSequence, DataType
from binbuilder.sequence_builder import SequenceBuilderDialog

from PyQt5 import QtWidgets, QtCore, QtGui


class MainWidget(QtWidgets.QDialog):
    def __init__(self, primaryScreen, mainWindow):
        super(MainWidget, self).__init__()
        self.main = mainWindow
        self.primary_screen = primaryScreen

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.newButton = QtWidgets.QPushButton("Create new data item sequence")
        self.newButton.clicked.connect(self.newButtonClicked)
        self.buttonLayout.addWidget(self.newButton)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.addLayout(self.buttonLayout)

    def newButtonClicked(self):
        blocks = [
            Block(DataType.UINT_4B, "First Counter", 44),
            Block(DataType.UINT_4B, "Second Counter", 55),
            Block(DataType.DOUBLE, "THIRD,,::;;COUNTER", 55.5),
            Block(DataType.FLOAT, "fourth,  COUNTER", 55.5),
            Block(DataType.BYTES, "Auth. Token", b'ffff', 4),
            Block(DataType.BYTES, "AUTHKEY", b'ffffgggghhhhjjjj', 12)
        ]

        seq = BlockSequence("test sequence", blocks)

        dialog = SequenceBuilderDialog(self, seq)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.exec_()

    def warningBeforeQuit(self):
        return yesNoDialog(self, "Are you sure?", "Are you sure you want to quit?")

    def quit(self):
        if self.warningBeforeQuit():
            QtWidgets.qApp.quit()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.quit()

    def sizeHint(self):
        return QtCore.QSize(800, 600)
