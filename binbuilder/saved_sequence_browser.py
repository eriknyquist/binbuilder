import os

from versionedobj import VersionedObject, CustomValue, Serializer
from binbuilder.block import BlockSequence
from binbuilder.utils import truncate_string

from PyQt5 import QtCore, QtGui, QtWidgets


SAVE_FILE_PATH = os.path.join(os.path.expanduser('~'), ".binbuilder_saved_sequences")


class SequenceList(CustomValue):
    def __init__(self, *args, **kwargs):
        super(SequenceList, self).__init__(*args, **kwargs)

        self.sequences = []

    def to_dict(self):
        return [s.to_dict() for s in self.sequences]

    def from_dict(self, attrs):
        new_sequences = []
        for d in attrs:
            new_sequences.append(BlockSequence.from_dict(d))

        self.sequences = new_sequences


class SavedSequenceList(VersionedObject):
    version = "1.0"
    sequences = SequenceList()


saved_sequence_list = SavedSequenceList()
serializer = Serializer()


def save_sequences(self):
    serializer.to_file(saved_sequence_list, SAVE_FILE_PATH)


def load_sequences(self):
    if os.path.isfile(SAVE_FILE_PATH):
        serializer.from_file(saved_sequence_list, SAVE_FILE_PATH)


def add_saved_sequence(seq):
    for s in saved_sequence_list.sequences.sequences:
        if s.name == seq.name:
            return False

    saved_sequence_list.sequences.sequences.append(seq)
    return True


class SavedSequenceBrowserDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(SavedSequenceBrowserDialog, self).__init__(*args, **kwargs)


        self.table = QtWidgets.QTableWidget()
        self.table.setDragEnabled(False)
        self.table.setAcceptDrops(False)
        self.table.viewport().setAcceptDrops(False)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.table.setColumnCount(2)
        self.table.setWordWrap(False)
        self.table.setHorizontalHeaderLabels(['Sequence name', 'Sequence size'])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.addWidget(self.table)

        self.update()

    def addRow(self, sequence):
        nextFreeRow = self.table.rowCount()
        self.table.insertRow(nextFreeRow)

        item1 = QtWidgets.QTableWidgetItem(truncate_string(sequence.name))
        item2 = QtWidgets.QTableWidgetItem(str(sequence.size_bytes()))

        item2.setTextAlignment(QtCore.Qt.AlignVCenter)
        item2.setTextAlignment(QtCore.Qt.AlignHCenter)

        item1.setBackground(QtGui.QColor(*sequence.color))
        item2.setBackground(QtGui.QColor(*sequence.color))

        self.table.setItem(nextFreeRow, 0, item1)
        self.table.setItem(nextFreeRow, 1, item2)

    def populateTable(self):
        self.table.setRowCount(0)
        for seq in saved_sequence_list.sequences.sequences:
            self.addRow(seq)

    def update(self):
        self.populateTable()
        super(SavedSequenceBrowserDialog, self).update()

