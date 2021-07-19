
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Bee.util import resources
from Bee.engine.driver import camera

from Bee.gui.base.delta import delta
from Bee.gui.base.delta import delta_gl
from Bee.gui.base.image import image
from Bee.gui.base.connect import connect
from Bee.gui.base.controller import controller
from Bee.gui.base.preferences import preferences
from Bee.gui.style.label import label
from Bee.gui.style.led import led

class NumberCap(QWidget):
    def __init__(self,*args,**kwargs):
        super(NumberCap, self).__init__()
        self.init_gui()

    def init_gui(self):

        self.red_number = label.MLabel(text="Red",value=0)
        self.yellow_number = label.MLabel(text="Yellow",value=0)
        self.white_number = label.MLabel(text="White",value=0)
        self.orange_number = label.MLabel(text="Orange",value=0)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.red_number)
        hbox.addWidget(self.yellow_number)
        hbox.addWidget(self.white_number)
        hbox.addWidget(self.orange_number)

    def setValue(self,list_number_cap):
        self.red_number.setValue(list_number_cap[0])
        self.yellow_number.setValue(list_number_cap[1])
        self.white_number.setValue(list_number_cap[2])
        self.orange_number.setValue(list_number_cap[3])

class Container(QWidget):
    def __init__(self,*args,**kwargs):
        super(Container, self).__init__()

        self.init_gui()
        self.create_stacked()

    def init_gui(self):
        
        self.connected = connect.Connection()
        self.connected.select_mode.activated.connect(self.switch_mode)

        self.camera_image = QLabel()
        self.camera_image.setPixmap(QPixmap(resources.get_path_for_image('black.png')))

        self.led_threading = led.MLed()
        self.number_cap = NumberCap()

        self.stackedLayout = QStackedLayout()
        
        self.serial_page = QWidget()
        self.controller = controller.Controller()
        serial_hbox = QHBoxLayout()
        serial_hbox.addWidget(self.controller)
        self.serial_page.setLayout(serial_hbox)
        self.stackedLayout.addWidget(self.serial_page)

        self.image_page = QWidget()
        self.edit_image = image.ImageWidget()
        image_hbox = QHBoxLayout()
        image_hbox.addWidget(self.edit_image)
        self.image_page.setLayout(image_hbox)
        self.stackedLayout.addWidget(self.image_page)

        self.delta_page = QWidget()
        self.delta_gl = delta_gl.DeltaGL()
        delta_hbox = QHBoxLayout()
        delta_hbox.addWidget(self.delta_gl)
        self.delta_page.setLayout(delta_hbox)
        self.stackedLayout.addWidget(self.delta_page)

    def create_stacked(self):
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.connected)
        hbox = QHBoxLayout()
        hbox.addLayout(self.stackedLayout)

        group_camera = QGroupBox()
        vbox_image = QVBoxLayout()
        hbox_led = QHBoxLayout()
        hbox_led.addWidget(self.led_threading)
        hbox_led.addWidget(self.number_cap)
        vbox_image.addLayout(hbox_led)
        vbox_image.addWidget(self.camera_image)
        group_camera.setLayout(vbox_image)

        hbox.addWidget(group_camera)
        vbox.addLayout(hbox)

    def switch_mode(self):
        self.stackedLayout.setCurrentIndex(self.connected.select_mode.currentIndex())

    def setImage(self,image,t,b,s):
        qt_img = camera.Camera.convert_cv_qt(image,t,b,s)
        self.camera_image.setPixmap(qt_img)

    def setLed(self,value):
        self.led_threading.setValue(value)

class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow, self).__init__()
        self.init_title()
        self.create_actions()
        self.container = Container()
        self.setCentralWidget(self.container)
        self.delta_form = None
        self.device_form = None

    def init_title(self):
        self.setWindowTitle("Bee")
        self.setWindowIcon(
            QIcon(resources.get_path_for_image("Bee.ico")))

    def create_actions(self):
        menubar = self.menuBar()
        self.file = menubar.addMenu("File")

        self.save = QAction(
            QIcon(resources.get_path_for_image("save_20px.png")), "Save", self)
        self.quit = QAction(
            QIcon(resources.get_path_for_image("quit_20px.png")), "Quit", self)
        self.quit.triggered.connect(self.close)

        self.file.addAction(self.save)
        self.file.addAction(self.quit)

        self.setting = menubar.addMenu("Setting")
        self.device = QAction(
            QIcon(resources.get_path_for_image("settings_20px.png")), "Device", self)
        self.delta = QAction(
            QIcon(resources.get_path_for_image("bee_20px.png")), "Delta", self)
        self.grbl = QAction(
            QIcon(resources.get_path_for_image("firmware_20px.png")), "Marlin", self)
        self.get_real_para = QAction(
            QIcon(resources.get_path_for_image("coordinate_system_20px.png")), "Parameter", self)

        self.setting.addAction(self.device)
        self.setting.addAction(self.delta)
        self.setting.addAction(self.grbl)
        self.setting.addAction(self.get_real_para)

        self.delta.triggered.connect(self.create_form_setting_delta)
        self.device.triggered.connect(self.create_form_device)

    def create_form_setting_delta(self):
        self.delta_form = delta.DeltaForm()
        self.delta_form.show()

    def create_form_device(self):
        self.device_form = preferences.Prefrences()
        self.device_form.show()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()

class Base(MainWindow):
    __wid = 1300
    __hei = 900

    def __init__(self,*args,**kwargs):
        super(Base,self).__init__()
        self.initGui()

    def initGui(self):
        pos_x = (QDesktopWidget().screenGeometry().width() - self.__wid) // 2
        pos_y = (QDesktopWidget().screenGeometry().height() - self.__hei) // 2
        self.setGeometry(pos_x, pos_y, self.__wid, self.__hei)
