import os

from binbuilder.dragdrop_table_widget import DragDropTableWidget
from binbuilder.block import Block, BlockSequence, DataType, Schema
from binbuilder.sequence_builder import SequenceBuilderDialog
from binbuilder.utils import truncate_string, errorDialog
from binbuilder.save_file import SavedSchema

from versionedobj import Serializer


from PyQt5 import QtWidgets, QtCore, QtGui


blocks1 = [
    Block(DataType.UINT_4B, "First Counter", 44),
    Block(DataType.UINT_4B, "Second Counter", 55),
    Block(DataType.DOUBLE, "THIRD,,::;;COUNTER", 55.5),
    Block(DataType.FLOAT, "fourth,  COUNTER", 55.5),
    Block(DataType.BYTES, "Auth. Token", b'ffff', 4),
    Block(DataType.BYTES, "AUTHKEY", b'ffffgggghhhhjjjj', 12)
]

blocks2 = [
    Block(DataType.UINT_4B, "First Counter", 44),
    Block(DataType.UINT_4B, "Second Counter", 55),
    Block(DataType.DOUBLE, "THIRD,,::;;COUNTER", 55.5),
    Block(DataType.FLOAT, "fourth,  COUNTER", 55.5),
    Block(DataType.BYTES, "Auth. Token", b'ffff', 4),
    Block(DataType.BYTES, "AUTHKEY", b'ffffgggghhhhjjjj', 12)
]

seq1 = BlockSequence("Seq 1", blocks1)
seq2 = BlockSequence("Seq 2", blocks2)


class MainWidget(QtWidgets.QDialog):
    def __init__(self, primaryScreen, mainWindow):
        super(MainWidget, self).__init__()
        self.main = mainWindow
        self.primary_screen = primaryScreen
        self.current_schema = Schema("Test schema", [seq1, seq2])

        self.sizeLabel = QtWidgets.QLabel()

        # Build button widgets for button layout
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.newButton = QtWidgets.QPushButton("Create new data item sequence")
        self.newButton.clicked.connect(self.newButtonClicked)
        self.buttonLayout.addWidget(self.newButton)

        # Build schema builder table widget
        self.table = DragDropTableWidget()
        self.table.setColumnCount(2)
        self.table.setWordWrap(False)
        self.table.setHorizontalHeaderLabels(['Name', 'Size'])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.onDoubleClick)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.addLayout(self.buttonLayout)
        self.mainLayout.addWidget(self.sizeLabel)
        self.mainLayout.addWidget(self.table)

        self.update()

    def saveSchema(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Select save file", "", "All Files (*)", options=options)
        if not filename:
            return

        saved_schema = SavedSchema()
        saved_schema.schema_data = self.current_schema
        serializer = Serializer()
        serializer.to_file(saved_schema, filename)

    def loadSchema(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select schema file to load", "", "All Files (*)", options=options)
        if not filename:
            return

        loaded_schema = SavedSchema()
        loaded_schema.schema_data = self.current_schema
        loaded_schema.schema_data.sequencelist = []

        serializer = Serializer()
        serializer.from_file(loaded_schema, filename)
        self.current_schema = loaded_schema.schema_data
        self.update()

    def newButtonClicked(self):
        new = BlockSequence(f"New sequence {len(self.current_schema.sequencelist)}")
        success = False

        while not success:
            dialog = SequenceBuilderDialog(self, new)
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.exec_()

            try:
                self.current_schema.add_sequence(new)
            except ValueError as e:
                errorDialog(self, message=str(e))
            else:
                success = True

        self.update()

    def reorder_schema_by_table(self):
        names = []
        for i in range(self.table.rowCount()):
            names.append(self.table.item(i, 0).text())

        self.current_schema.reorder_by_names(names)

    def addRow(self, sequence):
        nextFreeRow = self.table.rowCount()
        self.table.insertRow(nextFreeRow)

        item1 = QtWidgets.QTableWidgetItem(truncate_string(sequence.name))
        item2 = QtWidgets.QTableWidgetItem(str(sequence.size_bytes()))

        item2.setTextAlignment(QtCore.Qt.AlignVCenter)
        item2.setTextAlignment(QtCore.Qt.AlignHCenter)

        self.table.setItem(nextFreeRow, 0, item1)
        self.table.setItem(nextFreeRow, 1, item2)

    def populateTable(self):
        self.table.setRowCount(0)
        for seq in self.current_schema.sequencelist:
            self.addRow(seq)

    def update(self):
        self.populateTable()
        self.sizeLabel.setText(f"Total size: {self.current_schema.size_bytes()} bytes")
        self.reorder_schema_by_table()
        super(MainWidget, self).update()

    def onDoubleClick(self, signal):
        seq_name = self.table.item(signal.row(), 0).text()
        seq = self.current_schema.get_sequence_by_name(seq_name)
        dialog = SequenceBuilderDialog(self, seq)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.exec_()
        self.update()

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
