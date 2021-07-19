
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MSlider(QWidget):

    def __init__(self,*args,**kwargs):
        super(QWidget, self).__init__()

        self.min_value = QLabel(str(kwargs['min']))
        self.max_value = QLabel(str(kwargs['max']))
        self.value_la = QLabel(str(kwargs['value']))
        self.title = QLabel(kwargs['name'])
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFixedWidth(300)
        self.slider.setRange(kwargs['min'],kwargs['max'])
        self.slider.setValue(kwargs['value'])
        self.slider.valueChanged.connect(self.value_changed)

        hbox = QHBoxLayout(self)

        right_hbox = QVBoxLayout()
        up_hbox = QHBoxLayout()
        up_hbox.addWidget(self.min_value)
        up_hbox.addWidget(self.value_la)
        up_hbox.addWidget(self.max_value)
        right_hbox.addLayout(up_hbox)
        right_hbox.addWidget(self.slider)

        hbox.addWidget(self.title)
        hbox.addLayout(right_hbox)

    def value_changed(self,value):
        self.value_la.setText(str(value))

    def value(self):
        return self.slider.value()

    def setValue(self,value):
        self.slider.setValue(int(value))