from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore, QtGui

from binbuilder.dragdrop_table_widget import DragDropTableWidget
from binbuilder.block_builder import BlockBuilderDialog
from binbuilder.utils import truncate_string, ScrollableTextDisplay
from binbuilder.block import Block, CodeWriter


class SequenceBuilderDialog(QtWidgets.QDialog):
    def __init__(self, parent, sequence):
        super(SequenceBuilderDialog, self).__init__(parent)

        self.parent = parent
        self.sequence = sequence
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.tableLayout = QtWidgets.QHBoxLayout()

        self.sizeLabel = QtWidgets.QLabel()

        self.newButton = QtWidgets.QPushButton("Add new data item")
        self.newButton.clicked.connect(self.newButtonClicked)
        self.buttonLayout.addWidget(self.newButton)

        self.saveButton = QtWidgets.QPushButton("Save sequence")
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.buttonLayout.addWidget(self.saveButton)

        self.cCodeButton = QtWidgets.QPushButton("C code")
        self.cCodeButton.clicked.connect(self.cCodeButtonClicked)
        self.buttonLayout.addWidget(self.cCodeButton)

        self.structFmtButton = QtWidgets.QPushButton("python 'struct' format string")
        self.structFmtButton.clicked.connect(self.structFmtButtonClicked)
        self.buttonLayout.addWidget(self.structFmtButton)


        # Build table
        self.table = DragDropTableWidget()
        self.table.setColumnCount(4)
        self.table.setWordWrap(False)
        self.table.setHorizontalHeaderLabels(['Name', 'Type', 'Size', 'Value'])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        #self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.onDoubleClick)
        self.tableLayout.addWidget(self.table)

        self.mainLayout.addWidget(self.sizeLabel)
        self.mainLayout.addLayout(self.buttonLayout)
        self.mainLayout.addLayout(self.tableLayout)

        self.setWindowTitle(f"Data item sequence '{self.sequence.name}'")
        #self.setWindowIcon(QtGui.QIcon(ICON_PATH))

        self.update()

    def reorder_sequence_by_table(self):
        names = []
        for i in range(self.table.rowCount()):
            names.append(self.table.item(i, 0).text())

        self.sequence.reorder_by_names(names)

    def cCodeButtonClicked(self):
        self.reorder_sequence_by_table()
        writer = CodeWriter()

        dialog = ScrollableTextDisplay(f"C code for '{self.sequence.name}'",
                                       writer.generate_c_string(self.sequence))
        dialog.exec_()

    def structFmtButtonClicked(self):
        self.reorder_sequence_by_table()

    def addRow(self, block):
        nextFreeRow = self.table.rowCount()
        self.table.insertRow(nextFreeRow)

        item1 = QtWidgets.QTableWidgetItem(truncate_string(block.name))
        item2 = QtWidgets.QTableWidgetItem(block.typeinfo.name)
        item3 = QtWidgets.QTableWidgetItem(f"{block.size_bytes():,}")
        item4 = QtWidgets.QTableWidgetItem(truncate_string(block.value_string()))

        item3.setTextAlignment(Qt.AlignHCenter)
        item3.setTextAlignment(Qt.AlignVCenter)

        self.table.setItem(nextFreeRow, 0, item1)
        self.table.setItem(nextFreeRow, 1, item2)
        self.table.setItem(nextFreeRow, 2, item3)
        self.table.setItem(nextFreeRow, 3, item4)

    def populateTable(self):
        self.table.setRowCount(0)
        for block in self.sequence.blocklist:
            self.addRow(block)

    def newButtonClicked(self):
        dialog = BlockBuilderDialog(self, Block())
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.exec_()

    def saveButtonClicked(self):
        pass

    def update(self):
        self.populateTable()
        self.sizeLabel.setText(f"Total size: {self.sequence.size_bytes()} bytes")
        super(SequenceBuilderDialog, self).update()

    def onDoubleClick(self, signal):
        block_name = self.table.item(signal.row(), 0).text()
        block = self.sequence.get_block_by_name(block_name)
        dialog = BlockBuilderDialog(self, block)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.exec_()
        self.reorder_sequence_by_table()
        self.update()
