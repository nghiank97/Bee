

import cv2
import numpy as np

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from Bee.gui.style.lineedit import lineedit

class CoordinateForm(QWidget):
    def __init__(self, *args, **kwargs):
        super(CoordinateForm,self).__init__()
        
        self.init_gui()
        self.arrange_layout()

    def init_gui(self):

        self.real_widght = lineedit.MLineEdit(text='Real Widght (m)',value=100,number=0)
        self.real_height = lineedit.MLineEdit(text='Real Widght (m)',value=100,number=0)

        self.widght_image = lineedit.MLineEdit(text='Widght Image (px))',value=100,number=0)
        self.height_image = lineedit.MLineEdit(text='Widght Image (px)',value=100,number=0)
        
        self.image_la = QLabel()

    def arrange_layout(self):
        hbox = QHBoxLayout(self)

        vbox_para = QVBoxLayout()
        vbox_para.addWidget(self.real_widght)
        vbox_para.addWidget(self.real_height)
        vbox_para.addStretch(1)
        vbox_para.addWidget(self.widght_image)
        vbox_para.addWidget(self.height_image)

        vbox_image = QVBoxLayout()
        vbox_image.addWidget(self.image_la)

        hbox.addLayout(vbox_para)
        hbox.addLayout(vbox_image)