
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MLed(QLabel):
    color_on  = """
        QWidget {
            border: 2px solid blue;
            border-radius: 25px;
            background-color: blue
            }
        """

    color_off  = """
        QWidget {
            border: 2px solid red;
            border-radius: 25px;
            background-color: red
            }
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = 0
        self.setFixedSize(50, 50)
        self.setStyleSheet(self.color_off)

    def setValue(self,value):
        self.value = value
        if self.value ==1:
            self.setStyleSheet(self.color_on)
        else:
            self.setStyleSheet(self.color_off)

          
