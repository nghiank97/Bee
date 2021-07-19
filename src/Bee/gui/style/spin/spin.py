
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MSpin(QWidget):

    def __init__(self,*args,**kwargs):
        super(QWidget, self).__init__()

        self.title = QLabel(kwargs['text'])
        self.spin = QSpinBox()
        self.spin.setValue(kwargs['value'])
        
        self.spin.valueChanged.connect(self.reload_value)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.title)
        hbox.addWidget(self.spin)

    def reload_value(self,value):
        self.setValue(value)

    def getValue(self):
        return self.spin.value()

    def setValue(self,value):
        self.spin.setValue(int(value))