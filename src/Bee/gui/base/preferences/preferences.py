

import sys
import time 

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Bee.util import profile
from Bee.util import resources
from Bee.engine.driver import camera
from Bee.engine.driver import board

class BaseForm(QWidget):
    wid = 250
    hei = 300

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pos_x = int((QDesktopWidget().screenGeometry().width() - self.wid) / 2)
        pos_y = int((QDesktopWidget().screenGeometry().height() - self.hei) / 2)

        self.setWindowTitle('Prefrences')
        self.setGeometry(pos_x, pos_y, self.wid, self.hei)
        self.setWindowIcon(QIcon(resources.get_path_for_image("settings_20px.png")))

        self.init_gui()

    def init_gui(self):
        setup_grid = QGridLayout(self)

        self.camera_la = QLabel("Camera ID")
        self.camera_cb = QComboBox()

        self.port_la = QLabel("Serial name")
        self.port_cb = QComboBox()

        self.baud_la = QLabel("Baud")
        bauds = ['1200', '2400', '4800', '9600',
                 '19200', '38400', '57600', '115200','230400','250000','500000']
        self.baud_cb = QComboBox()
        self.baud_cb.addItems(bauds)
        self.baud_cb.setCurrentText('250000')
        self.baud_cb.view().setSelectionMode(2)

        self.process_la = QProgressBar()
        self.process_la.setValue(0)
        self.upload_bt = QPushButton("UPLOAD")
        self.upload_bt.setEnabled(False)

        self.cancel_bt = QPushButton("CANCEL")
        self.save_bt = QPushButton("SAVE")

        setup_grid.addWidget(self.camera_la, 0, 0)
        setup_grid.addWidget(self.port_la, 1, 0)
        setup_grid.addWidget(self.baud_la, 2, 0)

        setup_grid.addWidget(self.camera_cb, 0, 1)
        setup_grid.addWidget(self.port_cb, 1, 1)
        setup_grid.addWidget(self.baud_cb, 2, 1)

        setup_grid.addWidget(self.upload_bt, 3, 0)
        setup_grid.addWidget(self.process_la, 3, 1)

        setup_grid.addWidget(self.cancel_bt, 4, 0)
        setup_grid.addWidget(self.save_bt, 4, 1)

        self.setLayout(setup_grid)

class Prefrences(BaseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.get_device()
        self.save_camera_id()
        self.save_portname()
        self.save_baudrate()

        self.save_bt.clicked.connect(self.save_device)
        self.cancel_bt.clicked.connect(self.cancel_device)
        # self.upload_bt.clicked.connect(self.on_upload_firmware)

        self.camera_cb.currentTextChanged.connect(self.save_camera_id)
        self.port_cb.currentTextChanged.connect(self.save_portname)
        self.baud_cb.currentTextChanged.connect(self.save_baudrate)

    def save_camera_id(self):
        camera_id = self.camera_cb.currentText()
        profile.set_camera_id(int(camera_id))

    def save_portname(self):
        port_name = self.port_cb.currentText()
        profile.set_portname(port_name)

    def save_baudrate(self):
        baudrate = self.baud_cb.currentText()
        profile.set_baudrate(int(baudrate))

    def cancel_device(self):
        self.save_camera_id()
        self.save_portname()
        self.save_baudrate()
        self.close()

    def save_device(self):
        self.save_camera_id()
        self.save_portname()
        self.save_baudrate()
        QMessageBox.about(self, "Info", "Saved")
        self.close()

    def get_device(self):
        port_list = board.Board.get_ports()
        self.port_cb.addItems(port_list)
        self.port_cb.setCurrentText(port_list[-1])
        
        cammera_list = camera.Camera.get_ids()
        self.camera_cb.addItems(cammera_list)
        self.camera_cb.setCurrentText(cammera_list[-1])

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()