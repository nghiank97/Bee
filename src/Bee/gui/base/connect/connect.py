
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Bee.util import resources

class Connection(QWidget):

    def __init__(self,*args,**kwargs):
        super(Connection,self).__init__()

        self.connect = QPushButton()
        self.connect.setIcon(
            QIcon(resources.get_path_for_image("usb_connected_20px.png")))
        self.connect.setToolTip('Connect')  

        self.disconnect = QPushButton()
        self.disconnect.setIcon(
            QIcon(resources.get_path_for_image("usb_disconnected_20px.png")))
        self.disconnect.setToolTip('Disconnect')  

        self.play_auto = QPushButton()
        self.play_auto.setIcon(
            QIcon(resources.get_path_for_image("play_20px.png")))

        self.pause_auto = QPushButton()
        self.pause_auto.setIcon(
            QIcon(resources.get_path_for_image("pause_20px.png")))

        mode = ['Serial','Camera','Delta']
        self.select_mode = QComboBox()
        self.select_mode.addItems(mode)
        self.select_mode.setCurrentText('Serial')
        self.select_mode.currentIndexChanged.connect(self.show_auto)
        self.hide_auto(True)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.connect)
        hbox.addWidget(self.disconnect)
        hbox.addWidget(self.play_auto)
        hbox.addWidget(self.pause_auto)
        hbox.addStretch(1)
        hbox.addWidget(self.select_mode)

    def show_auto(self):
        if self.select_mode.currentText() == 'Delta':
            self.hide_auto(False)
        else:
            self.hide_auto(True)

    def hide_auto(self,value):
        self.play_auto.setHidden(value)
        self.pause_auto.setHidden(value)