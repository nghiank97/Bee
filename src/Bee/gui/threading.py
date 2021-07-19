
import cv2
import time
import numpy as np

import threading
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Bee.util import profile, resources

from Bee.engine.driver import camera
from Bee.engine.driver import board
from Bee.engine.algorithms import cap

from Bee.gui.base import base
from Bee.gui.base.grbl import grbl
from Bee.gui.base.image.coordinate import coordinate

class DataReceiver(QThread):
    signal_data = pyqtSignal(str)

    def __init__(self, connect):
        super().__init__()
        self.connect = connect

    def run(self):
        while self.connect.is_connected:
            data_receiver = self.connect.readline()
            self.signal_data.emit(data_receiver)
            time.sleep(0.1)

    def stop(self):
        self.connect.is_connected = False
        self.connect.close()

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, connect):
        super().__init__()
        self.connect_camera = connect

    def run(self):
        while self.connect_camera.is_connected:
            cv_img = self.connect_camera.capture_image()
            self.change_pixmap_signal.emit(cv_img)
            time.sleep(0.1)
            
    def pause(self):
        self.connect_camera.is_connected = False

    def stop(self):
        self.connect_camera.is_connected = False
        self.connect_camera.disconnect()

class PickUp(QThread):
    signal_process = pyqtSignal(bool)
    number_color = pyqtSignal(list)

    real_degree = pyqtSignal(np.ndarray)
    def __init__(self, serial,local,color,delta):
        super().__init__()
        self.connect = serial
        self.local = local
        self.color = color
        self.delta = delta
        self.is_connected = True
        self.is_process = False

    def run(self):
        while(self.is_connected):
            if len(self.local) != 0:
                self.is_process = True
                for center,color in zip(self.local,self.color):

                    center[2] = center[2]+0.02
                    self.delta.Position = center
                    up_degree = self.delta.Degree

                    center[2] = center[2]-0.04
                    self.delta.Position = center
                    down_degree = self.delta.Degree

                    #self.connect.pickup(up_degree,down_degree,color)

                    self.connect.G0(up_degree)
                    self.real_degree.emit(up_degree)

                    self.connect.hold(True)
                    self.connect.G0(down_degree)
                    self.real_degree.emit(down_degree)
                    
                    time.sleep(0.1)
                    self.connect.G0(up_degree)
                    self.real_degree.emit(up_degree)

                    blank= self.connect.get_blank(color)
                    self.connect.G0(blank)
                    self.real_degree.emit(np.array(blank))
                    self.connect.hold(False)
                    time.sleep(1)

                self.local = []
                self.color = []
                self.is_process = False
            self.signal_process.emit(self.is_process)
            self.number_color.emit(self.connect.get_number())
            time.sleep(0.1)

    def stop(self):
        self.is_connected = False
        self.is_process = False

class App(base.Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial = None
        self.camera = None
        self.thread_pickup = None
        self.grbl_status = False
        self.grbl_data = []

        self.h_img = 480
        self.w_img = 680

        self.container.connected.connect.clicked.connect(self.connect_device)
        self.container.connected.disconnect.clicked.connect(self.disconnect_device)

        self.container.controller.job.inc_position_z.clicked.connect(self.put_serial)
        self.container.controller.job.des_position_z.clicked.connect(self.put_serial)
        self.container.controller.job.inc_position_y.clicked.connect(self.put_serial)
        self.container.controller.job.des_position_y.clicked.connect(self.put_serial)
        self.container.controller.job.inc_position_x.clicked.connect(self.put_serial)
        self.container.controller.job.des_position_x.clicked.connect(self.put_serial)
        self.container.controller.job.home_position.clicked.connect(self.auto_home)

        self.container.controller.job.valve.stateChanged.connect(self.set_hold_valve)
        self.container.controller.job.led.slider.valueChanged.connect(self.set_led)

        self.container.connected.play_auto.clicked.connect(self.pick_up_bottelcap)
        self.container.connected.pause_auto.clicked.connect(self.pause_pick_up_bottelcap)

        self.container.edit_image.save_img.clicked.connect(self.save_ori_image)

        self.container.controller.receivers.send_command.clicked.connect(self.send_command_serial)
        self.grbl.triggered.connect(self.create_form_grbl)
        self.get_real_para.triggered.connect(self.create_form_coordinate)

    def save_ori_image(self):
        cv2.imwrite(resources.get_path_cv2("image.png"),self.roi_img)
        QMessageBox.information(self," ","saved")

    def move_home(self):
        self.serial.G0([0,0,0])

    def get_data_setting_grbl(self, data_receiver):
        self.grbl_data.append(data_receiver)
        if data_receiver == 'ok\r\n':
            self.grbl_status = False
            self.grbl_data = self.grbl_data[:-1]
            try:
                self.grbl_form = grbl.Grbl(self.grbl_data)
                self.grbl_form.save_grbl.clicked.connect(self.load_para_grbl)
                self.grbl_form.show()
            except grbl.NotResponed as e:
                QMessageBox.warning(self,"","Not responed")

    def load_para_grbl(self):
        if len(self.grbl_form.command_setting) != 0:
            for command in self.grbl_form.command_setting:
                self.container.controller.show_data_trasmit(command)
                self.serial.send_command(command)
                time.sleep(0.05)
        QMessageBox.information(self,"","Saved")
                
    def create_form_grbl(self):
        if self.serial != None:
            if self.serial.is_connected:
                self.grbl_status = True
                self.container.controller.show_data_trasmit("$$")
                self.serial.send_command("$$")
        else:
            QMessageBox.warning(self,"","Don't connect port")

    def set_led(self):
        value_led = self.container.controller.job.led.value()
        self.serial.led(value_led)

    def set_hold_valve(self):
        self.serial.hold(self.container.controller.job.valve.isChecked())

    def set_enabled(self,state):
        self.container.controller.setEnabled(state)
        self.container.connected.select_mode.setEnabled(state)

    def openning_device(self):
        try:
            port = profile.get_port_name()
            baud = profile.get_baudrate()
            id = profile.get_camera_id()
            self.serial = board.Board(serial_name=port,baud_rate=baud)
            self.camera = camera.Camera(camera_id=id)
            self.serial.connect()
            self.camera.connect()
            
            self.thread_serial = DataReceiver(connect=self.serial)
            self.thread_serial.signal_data.connect(self.show_receiver)
            self.thread_serial.start()

            self.thread_camera = VideoThread(connect=self.camera)
            self.thread_camera.change_pixmap_signal.connect(self.show_image)
            self.thread_camera.start()

            QMessageBox.information(self," ", "Connected")
            self.set_enabled(True)
            self.container.controller.setStatus(True)
            self.serial.send_command("\r\n")

        except board.BoardNotConnected:
            QMessageBox.warning(self, " ", "Error : port or camera")
        except Exception as exception:
            QMessageBox.warning(self, " ", "Error : " +str(exception))

    def connect_device(self):
        if self.serial == None:
            self.openning_device()
        elif self.serial.is_connected == True:
            QMessageBox.information(self, " ", "Connect")
        elif self.serial.is_connected == False:
            self.openning_device()

        
    def disconnect_device(self):
        if self.serial != None:
            if self.serial.is_connected == True:
                self.serial.disconnect()
                QMessageBox.information(self, " ", "Disconnected")
            if self.camera.is_connected == True:
                self.camera.disconnect()
            self.container.controller.setStatus(False)
        self.set_enabled(False)

    def auto_home(self):
        self.serial.auto_home()

    def put_serial(self):
        data = self.container.controller.delta_robot.Degree
        command = "G0 X{:.3f} Y{:.3f} Z{:.3f}".format(*data)
        self.serial.send_command(command)
        self.container.controller.show_data_trasmit(command)

    def send_command_serial(self):
        text = self.container.controller.getText()
        if text != "":
            self.serial.send_command(text)
            self.container.controller.show_data_trasmit(text)
            self.container.controller.setText("")

    @pyqtSlot(str)
    def show_receiver(self, data_receiver):
        if data_receiver != "":
            if self.grbl_status == True:
                self.get_data_setting_grbl(data_receiver)
            self.container.controller.show_data_received(data_receiver)

    def display_image(self,top_value,bottom_value,start_pickup):
        if self.container.edit_image.get_mode() == 'original':
            self.container.setImage(self.cap_image.original_image,top_value,bottom_value,start_pickup)
        elif self.container.edit_image.get_mode() == 'gray':
            self.container.setImage(self.cap_image.gray_image,top_value,bottom_value,start_pickup)
        elif self.container.edit_image.get_mode() == 'filter':
            self.container.setImage(self.cap_image.filter_image,top_value,bottom_value,start_pickup)
        elif self.container.edit_image.get_mode() == 'thresh':
            self.container.setImage(self.cap_image.thresh_image,top_value,bottom_value,start_pickup)
        elif self.container.edit_image.get_mode() == 'contours':
            self.container.setImage(self.cap_image.contours_image,top_value,bottom_value,start_pickup)
        elif self.container.edit_image.get_mode() == 'circle':
            self.container.setImage(self.cap_image.circle_image,top_value,bottom_value,start_pickup)

    @pyqtSlot(np.ndarray)
    def show_image(self, cv_img):
        try:
            top_value = self.container.edit_image.get_value_top_line()
            bottom_value = self.container.edit_image.get_value_bottom_line()
            start_pickup = self.container.edit_image.get_value_start_pickup()

            self.camera.set_rotate(self.container.edit_image.getRotate())
            self.camera.set_hflip(self.container.edit_image.getHflip())
            self.camera.set_vflip(self.container.edit_image.getVflip())
            self.camera.brightness = self.container.edit_image.get_value_brightness()
            self.camera.contrast = self.container.edit_image.get_value_contrast()
            self.camera.saturation = self.container.edit_image.get_value_saturation()
            self.camera.exposure = self.container.edit_image.get_value_exposure()

            self.roi_img= cv_img[top_value:self.h_img-bottom_value,0:self.w_img]
            para_dict = {
                'image': self.roi_img.copy(),
                'thresh': self.container.edit_image.get_value_thresh(),
                'size': self.container.edit_image.get_value_size(),
                'max': self.container.edit_image.get_value_maxcenter(),
                'min': self.container.edit_image.get_value_mincenter(),
                'start_pickup':start_pickup,
                'ew': self.container.delta_gl.get_error_width(),
                'eh': self.container.delta_gl.get_error_height(),
                'delay_motor': self.container.delta_gl.get_delay_motor(),
            }

            self.cap_image = cap.CapImage(**para_dict)
            self.display_image(top_value,bottom_value,start_pickup)
            self.show_reallocal()
        except camera.CameraNotConnected as e:
            QMessageBox.warning(self,"Camera",str(e)+"Try again ! ")

    @pyqtSlot(list)
    def load_number_cap(self,list_number_cap):
        self.container.number_cap.setValue(list_number_cap)

    @pyqtSlot(bool)
    def load_process(self,process):
        if self.thread_pickup.is_process == False:
            self.thread_pickup.local = self.cap_image.real_local
            self.thread_pickup.color = self.cap_image.detect_color

    @pyqtSlot(np.ndarray)
    def upload_delta_gl(self,real_degree):
        self.container.delta_gl.reload_position_gl(real_degree)

    def create_thread_pick_up_bottelcap(self):
        if (self.serial != None) & (self.camera != None):
            self.thread_pickup = PickUp(
                serial= self.serial,
                local= self.cap_image.real_local,
                color= self.cap_image.detect_color,
                delta= self.container.controller.delta_robot
            )
            self.thread_pickup.signal_process.connect(self.load_process)
            self.thread_pickup.number_color.connect(self.load_number_cap)
            self.thread_pickup.real_degree.connect(self.upload_delta_gl)
            self.thread_pickup.start()
            QMessageBox.information(self,"","Auto pick")
            self.container.setLed(1)
            self.serial.local_work()
            self.container.delta_gl.reload_position_gl(np.array(self.serial.blanks['red'][0]))
        else:
            QMessageBox.warning(self,"","Don't connect")

    def pick_up_bottelcap(self):
        if self.thread_pickup == None:
            self.create_thread_pick_up_bottelcap()
        elif self.thread_pickup.is_connected == True:
            QMessageBox.warning(self,"","Connected")
        else:
            self.create_thread_pick_up_bottelcap()
    
    def pause_pick_up_bottelcap(self):
        if self.thread_pickup == None:
            QMessageBox.information(self," ","Disauto")
        elif self.thread_pickup.is_connected == True:
            self.thread_pickup.stop()
            self.container.setLed(0)
            QMessageBox.information(self," ","Disauto")

    def show_reallocal(self):
        self.container.edit_image.setLocal(self.cap_image.local,self.cap_image.bgr_color,self.cap_image.detect_color)

    def create_form_coordinate(self):
        if (self.camera == None):
            QMessageBox.warning(self,"","Camera don't connect")
            return
        if (self.camera.is_connected == False):
            QMessageBox.warning(self,"","Camera don't connect")
            return
        else:
            self.coordinate_form = coordinate.CoordinateForm()
            self.coordinate_form.show()

    def closeEvent(self, event):
        if self.serial != None:
            if self.serial.is_connected == True:
                self.serial.disconnect()
            if self.camera.is_connected == True:
                self.camera.disconnect()
        if self.device_form != None:
            self.device_form.close()
        if self.delta_form != None:
            self.delta_form.close()