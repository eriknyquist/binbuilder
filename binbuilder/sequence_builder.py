from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore, QtGui

from binbuilder.saved_sequence_browser import add_saved_sequence
from binbuilder.dragdrop_table_widget import DragDropTableWidget
from binbuilder.block_builder import BlockBuilderDialog
from binbuilder.utils import truncate_string, ScrollableTextDisplay, errorDialog, ICON_PATH
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

        self.nameLayout = QtWidgets.QHBoxLayout()
        self.nameInput = QtWidgets.QLineEdit()
        self.nameLabel = QtWidgets.QLabel()
        self.nameLabel.setText("Sequence name: ")
        self.nameInput.setText(sequence.name)
        self.nameLayout.addWidget(self.nameLabel)
        self.nameLayout.addWidget(self.nameInput)

        self.newButton = QtWidgets.QPushButton("Add new item")
        self.newButton.clicked.connect(self.newButtonClicked)
        self.buttonLayout.addWidget(self.newButton)

        self.editButton = QtWidgets.QPushButton("Edit selected")
        self.editButton.clicked.connect(self.editButtonClicked)
        self.buttonLayout.addWidget(self.editButton)

        self.removeButton = QtWidgets.QPushButton("Delete selected")
        self.removeButton.clicked.connect(self.removeButtonClicked)
        self.buttonLayout.addWidget(self.removeButton)

        self.saveButton = QtWidgets.QPushButton("Save sequence")
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.buttonLayout.addWidget(self.saveButton)

        self.cCodeButton = QtWidgets.QPushButton("C code")
        self.cCodeButton.clicked.connect(self.cCodeButtonClicked)
        self.buttonLayout.addWidget(self.cCodeButton)

        self.structFmtButton = QtWidgets.QPushButton("python format string")
        self.structFmtButton.clicked.connect(self.structFmtButtonClicked)
        self.buttonLayout.addWidget(self.structFmtButton)


        # Build table
        self.table = DragDropTableWidget()
        self.table.setColumnCount(4)
        self.table.setWordWrap(False)
        self.table.setHorizontalHeaderLabels(['Name', 'Type', 'Size', 'Value'])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.onDoubleClick)
        self.tableLayout.addWidget(self.table)

        self.mainLayout.addLayout(self.nameLayout)
        self.mainLayout.addLayout(self.buttonLayout)
        self.mainLayout.addWidget(self.sizeLabel)
        self.mainLayout.addLayout(self.tableLayout)

        self.setWindowTitle(f"Data item sequence '{self.sequence.name}'")
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))

        self.update()

    def removeButtonClicked(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            errorDialog(self, message="No data item is selected")
            return

        block_name = self.table.item(rows[0].row(), 0).text()
        self.sequence.remove_block_by_name(block_name)
        self.update()

    def editButtonClicked(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            errorDialog(self, message="No data item is selected")
            return

        self.editItemByRow(rows[0].row())
        self.update()

    def closeEvent(self, event):
        self.sequence.set_name(self.nameInput.text())

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
        writer = CodeWriter()
        dialog = ScrollableTextDisplay(f"python struct format string for '{self.sequence.name}'",
                                       writer.generate_pystruct_fmtstring(self.sequence))
        dialog.exec_()

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
        new = Block(name=f"Block {len(self.sequence.blocklist)}")
        success = False

        while not success:
            dialog = BlockBuilderDialog(self, new)
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.exec_()

            try:
                self.sequence.add_block(new)
            except ValueError as e:
                errorDialog(self, message=str(e))
            else:
                success = True

        self.update()

    def saveButtonClicked(self):
        self.sequence.set_name(self.nameInput.text())
        self.reorder_sequence_by_table()
        saved_sequence = self.sequence.copy()
        success = add_saved_sequence(saved_sequence)
        if not success:
            errorDialog(self, message="You already have a saved sequence with this name")

    def update(self):
        self.populateTable()
        self.sizeLabel.setText(f"Total size: {self.sequence.size_bytes()} bytes")
        self.reorder_sequence_by_table()
        super(SequenceBuilderDialog, self).update()

    def editItemByRow(self, row):
        block_name = self.table.item(row, 0).text()
        block = self.sequence.get_block_by_name(block_name)
        dialog = BlockBuilderDialog(self, block)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.exec_()

    def onDoubleClick(self, signal):
        self.editItemByRow(signal.row())
        self.update()
