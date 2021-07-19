
import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Bee.util import profile
from Bee.util import resources
from Bee.gui.style.spin import spin
from Bee.gui.base.delta import delta
from Bee.gui.style.lineedit import lineedit

class Command(QWidget):
    def __init__(self,*args,**kwargs):
        super(Command, self).__init__()

        self.command = QLineEdit("")
        self.send_command = QPushButton()
        self.send_command.setIcon(
            QIcon(resources.get_path_for_image('email_send_20px.png')))
        self.clean_command = QPushButton()
        self.clean_command.setIcon(
            QIcon(resources.get_path_for_image('broom_20px.png')))
        self.clean_command.clicked.connect(self.clean_text_command)

        self.receivers_data = QTextBrowser()

        self.path = QLineEdit()
        self.load_path = QPushButton()
        self.load_path.setIcon(
            QIcon(resources.get_path_for_image('folder_20px.png')))
        self.load_path.clicked.connect(self.get_path)
        self.send_file = QPushButton()
        self.send_file.setIcon(
            QIcon(resources.get_path_for_image('send_file_20px.png')))

        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout()
        hbox.addWidget(self.path)
        hbox.addWidget(self.load_path)
        hbox.addWidget(self.send_file)
        vbox.addLayout(hbox)

        vbox.addWidget(self.receivers_data)

        hbox = QHBoxLayout()
        hbox.addWidget(self.command)
        hbox.addWidget(self.send_command)
        hbox.addWidget(self.clean_command)
        vbox.addLayout(hbox)

    def put_data_received(self,data):
        self.receivers_data.append("<<"+data)

    def put_data_transmit(self,data):
        self.receivers_data.append(">>"+data)

    def setEnabled(self,status):
        self.receivers_box.setEnabled(status)

    def clean_text_command(self):
        if self.command.text() != "":
            self.command.setText("")
        self.receivers_data.clear()

    def get_path(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Open file', "C:/", "Gcode (*.gcode)")[0]
        self.path.setText(fname)

class ActiveState(QWidget):

    def __init__(self,text="Active State : ",value = False):
        super(ActiveState, self).__init__()
        self.state = value
        self.status_la = QLabel("")
        self.status_la.setAlignment(Qt.AlignCenter)
        self.load_state()

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.status_la)

    def get_value(self):
        return self.state 

    def setValue(self, value):
        self.state = value
        self.load_state()

    def load_state(self):
        if (self.state == True):
            self.status_la.setText("Active State : Run")
            self.status_la.setStyleSheet("background-color:blue")
        else:
            self.status_la.setText("Active State : Idel")
            self.status_la.setStyleSheet("background-color:red")

class StatusMachine(QWidget):
    def __init__(self,*args,**kwargs):
        super(StatusMachine, self).__init__()

        self.degree = np.array([0,0,0]).T
        self.position = np.array([0,0,0]).T

        layout = QHBoxLayout(self)
        self.state_group = QGroupBox()

        self.status = ActiveState()
        self.gcode_text = QLineEdit()

        self.machine_position = QLabel("Position")
        self.machine_position.setAlignment(Qt.AlignCenter)
        self.machine_angle = QLabel("Angle")
        self.machine_angle.setAlignment(Qt.AlignCenter)

        self.position_x = QLineEdit('{:.3f}'.format(self.position[0]))
        self.position_y = QLineEdit('{:.3f}'.format(self.position[1]))
        self.position_z = QLineEdit('{:.3f}'.format(self.position[2]))

        self.degree_x = QLineEdit('{:.3f}'.format(self.degree[0]))
        self.degree_y = QLineEdit('{:.3f}'.format(self.degree[1]))
        self.degree_z = QLineEdit('{:.3f}'.format(self.degree[2]))

        required_number = QDoubleValidator()
        self.position_x.setValidator(required_number)
        self.position_y.setValidator(required_number)
        self.position_z.setValidator(required_number)

        self.degree_x.setValidator(required_number)
        self.degree_y.setValidator(required_number)
        self.degree_z.setValidator(required_number)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        vbox_left_left = QVBoxLayout()
        vbox_left_left.addWidget(self.machine_position)
        vbox_left_left.addWidget(self.position_x)
        vbox_left_left.addWidget(self.position_y)
        vbox_left_left.addWidget(self.position_z)

        vbox_left_right = QVBoxLayout()
        vbox_left_right.addWidget(self.machine_angle)
        vbox_left_right.addWidget(self.degree_x)
        vbox_left_right.addWidget(self.degree_y)
        vbox_left_right.addWidget(self.degree_z)

        hbox.addLayout(vbox_left_left)
        hbox.addLayout(vbox_left_right)

        vbox.addLayout(hbox)
        vbox.addWidget(self.status)
        vbox.addWidget(self.gcode_text)

        self.state_group.setLayout(vbox)
        layout.addWidget(self.state_group)
        layout.setContentsMargins(5,5,5,5)

    def setDegree(self,degree):
        self.degree = degree
        self.degree_x.setText('{:.3f}'.format(self.degree[0]))
        self.degree_y.setText('{:.3f}'.format(self.degree[1]))
        self.degree_z.setText('{:.3f}'.format(self.degree[2]))

    def setPosition(self,position):
        self.position = position
        self.position_x.setText('{:.3f}'.format(self.position[0]))
        self.position_y.setText('{:.3f}'.format(self.position[1]))
        self.position_z.setText('{:.3f}'.format(self.position[2]))

    def getDegree(self):
        self.degree[0] = float(self.degree_x.text())
        self.degree[1] = float(self.degree_y.text())
        self.degree[2] = float(self.degree_z.text())
        return self.degree

    def getPosition(self):
        self.position[0] = float(self.position_x.text())
        self.position[1] = float(self.position_y.text())
        self.position[2] = float(self.position_z.text())
        return self.position

    def setState(self,value):
        self.status.setValue(value)

class LedSlider(QWidget):
    def __init__(self,*args,**kwargs):
        super(LedSlider, self).__init__()

        self.led_la = QLabel("Led")
        self.value_la = QLabel("000")
        self.slider = QSlider(Qt.Vertical)
        self.slider.setRange(0,255)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.value_changed)
        
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.value_la)
        vbox.addWidget(self.slider)
        vbox.addWidget(self.led_la)

    def value_changed(self,value):
        self.value_la.setText("{0:03d}".format(value))

    def value(self):
        return self.slider.value()

    def setValue(self,value):
        self.slider.setValue(int(value))

class Job(QWidget):
    def __init__(self,*args,**kwargs):
        super(Job, self).__init__()

        self.scale = 10
        self.feed_motor = 5000
        self.initGui()

    def initGui(self):

        self.inc_position_x = QPushButton("x+")
        self.des_position_x = QPushButton("x-")
        self.inc_position_y = QPushButton("y+")
        self.des_position_y = QPushButton("y-")

        self.home_position = QPushButton()
        self.home_position.setIcon(
            QIcon(resources.get_path_for_image('home_20px.png')))

        self.inc_position_z = QPushButton("z+")
        self.des_position_z = QPushButton("z-")

        self.inc_position_z.setFixedWidth(40)
        self.des_position_z.setFixedWidth(40)
        self.inc_position_x.setFixedWidth(40)
        self.des_position_x.setFixedWidth(40)
        self.inc_position_y.setFixedWidth(40)
        self.des_position_y.setFixedWidth(40)

        self.step_size = spin.MSpin(text="Step (mm)",value=10)
        self.step_size.spin.valueChanged.connect(self.upload_step)
        self.feed_size = spin.MSpin(text="Feed",value=9000)
        self.feed_size.spin.valueChanged.connect(self.upload_feed)
        self.feed_size.spin.setMaximum(10000)
        self.feed_size.setValue(9000)
        
        self.valve = QCheckBox("Valve")
        self.led = LedSlider()

        layout = QHBoxLayout(self)
        hbox = QHBoxLayout()
        self.job_group = QGroupBox()

        grid = QGridLayout()
        grid.addWidget(self.inc_position_x,0,1)
        grid.addWidget(self.des_position_x,2,1)

        grid.addWidget(self.inc_position_y,1,0)
        grid.addWidget(self.home_position,1,1)       
        grid.addWidget(self.des_position_y,1,2)

        grid.addWidget(self.inc_position_z,0,3)
        grid.addWidget(self.des_position_z,2,3)

        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addWidget(self.step_size)
        vbox.addWidget(self.feed_size)
        vbox.addWidget(self.valve)

        hbox.addLayout(vbox)
        hbox.addWidget(self.led)

        self.job_group.setLayout(hbox)
        layout.addWidget(self.job_group)

    def upload_step(self,value):
        self.scale = value

    def upload_feed(self,value):
        self.feed_motor = self.feed_size.getValue()

    def getValve(self):
        return self.valve.isChecked()

    def getLed(self):
        return self.led.value()

class Controller(QWidget):
    SCALE = 1000
    def __init__(self,*args,**kwargs):
        super(Controller, self).__init__()

        self.job = Job()
        self.receivers = Command()
        self.display = StatusMachine()

        delta_para = profile.get_para_delta()
        self.delta_robot = delta.DeltaRobot(**delta_para)
        self.display.setPosition(self.delta_robot.Position)
        self.display.setDegree(self.delta_robot.Degree)
        self.setGcode(self.delta_robot.Degree)

        hbox = QHBoxLayout(self)
        controller_toolbox = QToolBox()

        delta_widget = QWidget()
        vbox = QVBoxLayout()

        hbox_local = QHBoxLayout()
        hbox_local.addWidget(self.job)

        vbox.addLayout(hbox_local)
        vbox.addWidget(self.display)
        delta_widget.setLayout(vbox)
        
        controller_toolbox.addItem(delta_widget, "Delta")
        controller_toolbox.addItem(self.receivers, "Serial")
    
        hbox.addWidget(controller_toolbox)

        self.job.inc_position_z.clicked.connect(self.inc_position_z)
        self.job.des_position_z.clicked.connect(self.des_position_z)
        self.job.inc_position_y.clicked.connect(self.inc_position_y)
        self.job.des_position_y.clicked.connect(self.des_position_y)
        self.job.inc_position_x.clicked.connect(self.inc_position_x)
        self.job.des_position_x.clicked.connect(self.des_position_x)
        self.job.home_position.clicked.connect(self.home_degree)

    def reload_position(self):
        try:
            real_degree = self.display.getDegree()
            self.delta_robot.Degree = np.array(real_degree).T
            position = self.delta_robot.Position
            self.display.setPosition(position)
            self.setGcode(self.delta_robot.Degree)
        except delta.InvalidValue as e:
            QMessageBox.warning(self,"",str(e))

    def reload_degree(self):
        try:
            real_position = self.display.getPosition()
            self.delta_robot.Position = real_position
            degree = self.delta_robot.Degree
            self.display.setDegree(degree)
            self.setGcode(self.delta_robot.Degree)
        except delta.InvalidValue as e:
            QMessageBox.warning(self,"",str(e))

    def inc_position_z(self):
        scale = self.job.scale
        value = self.display.getPosition()
        value[2]+=scale/self.SCALE
        self.display.setPosition(value)
        self.reload_degree()

    def des_position_z(self):
        scale = self.job.scale
        value = self.display.getPosition()
        value[2]-=scale/self.SCALE
        self.display.setPosition(value)
        self.reload_degree()

    def inc_position_y(self):
        scale = self.job.scale
        value = self.display.getPosition()
        value[1]+=scale/self.SCALE
        self.display.setPosition(value)
        self.reload_degree()

    def des_position_y(self):
        scale = self.job.scale
        value = self.display.getPosition()
        value[1]-=scale/self.SCALE
        self.display.setPosition(value)
        self.reload_degree()

    def inc_position_x(self):
        scale = self.job.scale
        value = self.display.getPosition()
        value[0]+=scale/self.SCALE
        self.display.setPosition(value)
        self.reload_degree()
        
    def des_position_x(self):
        scale = self.job.scale
        value = self.display.getPosition()
        value[0]-=scale/self.SCALE
        self.display.setPosition(value)
        self.reload_degree()

    def upload_value_position(self,position):
        self.display.setDegree(position)
        self.reload_degree()

    def upload_value_degree(self,degree):
        self.display.setDegree(degree)
        self.reload_position()

    def home_degree(self):
        self.display.setDegree(degree=[0,0,0])
        self.reload_position()

    def show_data_received(self,data):
        self.receivers.put_data_received(data)

    def show_data_trasmit(self,data):
        self.receivers.put_data_transmit(data)

    def setStatus(self,value):
        self.display.setState(value)

    def getText(self):
        return self.receivers.command.text()

    def setText(self,text):
        return self.receivers.command.setText(text)
    
    def setGcode(self,degree):
        command = 'G0 X{} Y{} Z{}'.format(*degree)
        self.display.gcode_text.clear()
        self.display.gcode_text.setText(command)