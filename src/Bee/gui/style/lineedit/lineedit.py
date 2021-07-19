
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MLineEdit(QWidget):

    def __init__(self,number = 3, *args, **kwargs):
        super(MLineEdit, self).__init__()
        self.text_la = kwargs['text']
        self.value = kwargs['value']
        self.number = number
        self.initGui()

    def initGui(self):
        layout = QHBoxLayout(self)
        self.lable = QLabel(self.text_la)

        required_number = QDoubleValidator()
        number_string = "{:."+str(self.number)+"f}"
        self.line_edit = QLineEdit(number_string.format(self.value))
        self.line_edit.textChanged.connect(self.change_value)
        self.line_edit.setFixedWidth(60)
        self.line_edit.setAlignment(Qt.AlignRight)
        self.line_edit.setValidator(required_number)

        layout.addWidget(self.lable)
        layout.addWidget(self.line_edit)

    def change_value(self):
        self.value = round(float(self.line_edit.text()),3)
    
    def setValue(self,value):
        self.value = value
        number_string = "{:."+str(self.number)+"f}"
        self.line_edit.setText(number_string.format(self.value))
    
    def getValue(self):
        return self.value
