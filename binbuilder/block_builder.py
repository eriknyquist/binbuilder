from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore, QtGui

from binbuilder.dragdrop_table_widget import DragDropTableWidget
from binbuilder.utils import truncate_string, ICON_PATH
from binbuilder.block import DataType, DATATYPES


type_name_map = {DATATYPES[code].name: code for code in DATATYPES}


def clean_bin_str(s):
    return ''.join([i.strip() for i in s.split()])

def bin_str_len(s):
    return int(len(clean_bin_str(s)) / 2)


class BlockBuilderDialog(QtWidgets.QDialog):
    def __init__(self, parent, block):
        super(BlockBuilderDialog, self).__init__(parent)

        self.old_type = None
        self.parent = parent
        self.block = block
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        self.hex_validator = QtGui.QRegExpValidator(QtCore.QRegExp("([0-9A-Fa-f]{2}[ \t]*)+"))
        self.decimal_validator = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]+"))
        self.float_validator = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]+(\\.?[0-9]+)?"))

        self.type_is_bytes = block.typeinfo.datatype == DataType.BYTES

        self.nameLayout = QtWidgets.QHBoxLayout()
        self.nameInput = QtWidgets.QLineEdit()
        self.nameLabel = QtWidgets.QLabel()
        self.nameLabel.setText("Name: ")
        self.nameInput.setText(block.name)
        self.nameLayout.addWidget(self.nameLabel)
        self.nameLayout.addWidget(self.nameInput)

        self.sizeLabel = QtWidgets.QLabel(self)

        self.valueLayout = QtWidgets.QHBoxLayout()
        self.valueInput = QtWidgets.QLineEdit()
        self.valueInput.textChanged.connect(self.value_input_changed)
        self.valueLabel = QtWidgets.QLabel()
        self.valueLabel.setText("Value: ")
        self.valueInput.setText(block.value_string())
        self.valueLayout.addWidget(self.valueLabel)
        self.valueLayout.addWidget(self.valueInput)

        self.set_size_label(block.typeinfo.name)

        self.typeLayout = QtWidgets.QHBoxLayout()
        self.typeCombo = QtWidgets.QComboBox()
        self.typeCombo.addItems(type_name_map.keys())
        self.typeLabel = QtWidgets.QLabel(self)
        self.typeLabel.setText("Data type: ")
        self.typeCombo.setCurrentText(block.typeinfo.name)
        self.typeCombo.currentTextChanged.connect(self.datatype_changed)
        self.set_value_validator_for_type(block.typeinfo.name)
        self.typeLayout.addWidget(self.typeLabel)
        self.typeLayout.addWidget(self.typeCombo)

        self.mainLayout.addLayout(self.nameLayout)
        self.mainLayout.addLayout(self.typeLayout)
        self.mainLayout.addLayout(self.valueLayout)
        self.mainLayout.addWidget(self.sizeLabel)

        self.setWindowTitle(f"Data block editor")
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))

        self.update()

    def closeEvent(self, event):
        self.block.set_name(self.nameInput.text())
        self.block.set_type(type_name_map[self.typeCombo.currentText()])
        self.block.set_value_string(self.valueInput.text())

    def value_input_changed(self, value):
        if self.type_is_bytes:
            size = bin_str_len(value)
            self.sizeLabel.setText(f"Size: {size}")

    def set_size_label(self, typename):
        datatype = type_name_map[typename]
        if datatype == DataType.BYTES:
            size = bin_str_len(self.valueInput.text())
        else:
            size = DATATYPES[datatype].size_bytes

        self.sizeLabel.setText(f"Size: {size}")

    def set_value_validator_for_type(self, typename):
        datatype = type_name_map[typename]
        if DataType.BYTES == datatype:
            self.valueInput.setValidator(self.hex_validator)
        elif datatype in [DataType.FLOAT, DataType.DOUBLE]:
            self.valueInput.setValidator(self.float_validator)
        else:
            self.valueInput.setValidator(self.decimal_validator)

    def datatype_changed(self, typename):
        new_type = type_name_map[typename]

        self.set_value_validator_for_type(typename)
        self.set_size_label(typename)
        self.type_is_bytes = new_type == DataType.BYTES

        if self.old_type != new_type:
            self.valueInput.setText('')

        self.old_type = new_type

