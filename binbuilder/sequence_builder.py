from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore, QtGui

from binbuilder.dragdrop_table_widget import DragDropTableWidget
from binbuilder.utils import truncate_string


class SequenceBuilderDialog(QtWidgets.QDialog):
    def __init__(self, parent, sequence):
        super(SequenceBuilderDialog, self).__init__(parent)

        self.parent = parent
        self.sequence = sequence
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        self.buttonLayout = QtWidgets.QHBoxLayout()

        self.newButton = QtWidgets.QPushButton("Add new data item")
        self.newButton.clicked.connect(self.newButtonClicked)
        self.buttonLayout.addWidget(self.newButton)

        self.saveButton = QtWidgets.QPushButton("Save sequence")
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.buttonLayout.addWidget(self.saveButton)

        # Build table
        self.table = DragDropTableWidget()
        self.table.setColumnCount(4)
        self.table.setWordWrap(False)
        self.table.setHorizontalHeaderLabels(['Name', 'Type', 'Size', 'Value'])

        self.mainLayout.addLayout(self.buttonLayout)
        self.mainLayout.addWidget(self.table)
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Data item sequence editor")
        #self.setWindowIcon(QtGui.QIcon(ICON_PATH))

        self.update()

    def addRow(self, block):
        nextFreeRow = self.table.rowCount()
        self.table.insertRow(nextFreeRow)

        item1 = QtWidgets.QTableWidgetItem(truncate_string(block.name))
        item2 = QtWidgets.QTableWidgetItem(block.typeinfo.name)
        item3 = QtWidgets.QTableWidgetItem(f"{block.size_bytes():,}")
        item4 = QtWidgets.QTableWidgetItem(truncate_string(block.value_string()))

        item3.setTextAlignment(Qt.AlignHCenter)

        self.table.setItem(nextFreeRow, 0, item1)
        self.table.setItem(nextFreeRow, 1, item2)
        self.table.setItem(nextFreeRow, 2, item3)
        self.table.setItem(nextFreeRow, 3, item4)

    def populateTable(self):
        self.table.setRowCount(0)
        for block in self.sequence.blocklist:
            print(block.size_bytes())
            self.addRow(block)

    def newButtonClicked(self):
        pass

    def saveButtonClicked(self):
        pass

    def update(self):
        self.populateTable()
        self.table.resizeColumnsToContents()
        super(SequenceBuilderDialog, self).update()

    def onDoubleClick(self, signal):
        item = store_items[signal.row()]
        self.buyItem(item)

    def sizeHint(self):
        return QtCore.QSize(800, 400)
