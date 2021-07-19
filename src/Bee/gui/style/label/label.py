
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MLabel(QWidget):

    def __init__(self, *args, **kwargs):
        super(MLabel, self).__init__()
        self.text_la = kwargs['text']
        self.value = kwargs['value']
        self.initGui()

    def initGui(self):
        self.lable = QLabel(self.text_la)
        self.lable.setAlignment(Qt.AlignCenter)
        self.number_cap = QLabel(str(self.value))
        self.number_cap.setAlignment(Qt.AlignCenter)

        hbox = QVBoxLayout(self)
        hbox.addWidget(self.lable)
        hbox.addWidget(self.number_cap)
    
    def setValue(self,value):
        self.value = value
        self.number_cap.setText(str(self.value))
