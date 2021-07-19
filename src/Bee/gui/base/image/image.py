

import cv2
import time
import numpy as np

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from Bee.util import profile, resources
from Bee.gui.style.spin import spin
from Bee.gui.style.slider import slider

class RotateImage(QWidget):
    def __init__(self, *args, **kwargs):
        super(RotateImage,self).__init__()
        self.create_camera_group()
        self.arrange_layout()

    def arrange_layout(self):
        hbox = QHBoxLayout(self)
        vbox = QVBoxLayout()
        vbox.addWidget(self.rotate_image)
        vbox.addWidget(self.right_image)
        vbox.addWidget(self.left_image)
        vbox.addWidget(self.clean_data)
        vbox.addStretch(1)
        vbox.setContentsMargins(0,0,0,0)
        hbox.addLayout(vbox)
        hbox.addWidget(self.local_text)

    def create_camera_group(self):

        self.rotate_image = QCheckBox("Rotate")
        self.right_image = QCheckBox("Right")
        self.left_image = QCheckBox("Left")

        # self.right_image.setChecked(True)
        # self.left_image.setChecked(True)        

        self.local_text = QTextBrowser()
        self.clean_data = QPushButton()
        self.clean_data.setIcon(
            QIcon(resources.get_path_for_image('trash_20px.png')))
        self.clean_data.clicked.connect(self.clean_local_data)

    def clean_local_data(self):
        self.local_text.clear()

class ImagePara(QWidget):
    def __init__(self, *args, **kwargs):
        super(ImagePara,self).__init__()

        self.para_capture = profile.get_capture()

        self.create_controller()
        self.arrange_layout()

    def arrange_layout(self):
        vbox = QVBoxLayout(self)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.reload_para)
        vbox.addLayout(hbox)
        vbox.addWidget(self.brightness)
        vbox.addWidget(self.contrast)
        vbox.addWidget(self.saturation)
        vbox.addWidget(self.exposure)
        vbox.setContentsMargins(0,0,0,0)

    def create_controller(self):

        self.reload_para = QPushButton()
        self.reload_para.setIcon(QIcon(resources.get_path_for_image("reload_20px.png")))
        self.reload_para.clicked.connect(self.reload_para_image)

        para_capture = profile.get_capture()
        self.brightness = slider.MSlider(
            name="Brightness", min=0, value=self.para_capture['brightness'], max=510)

        self.contrast = slider.MSlider(
            name="Contrast", min=0, value=self.para_capture['contrast'], max=255)

        self.saturation = slider.MSlider(
            name="Saturation", min=0, value=self.para_capture['saturation'], max=255)

        self.exposure = slider.MSlider(
            name="Exposure", min=1, value=self.para_capture['exposure'], max=64)

    def reload_para_image(self):
        self.brightness.setValue(self.para_capture['brightness'])
        self.contrast.setValue(self.para_capture['contrast'])
        self.saturation.setValue(self.para_capture['saturation'])
        self.exposure.setValue(self.para_capture['exposure'])

class ImageDetect(QWidget):

    def __init__(self,*args,**kwargs):
        super(ImageDetect,self).__init__()

        self.para_capture = profile.get_capture()
        self.create_widget()

        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.reload_para)
        vbox.addLayout(hbox)
        vbox.addWidget(self.thresh)
        vbox.addWidget(self.size_win)

        vbox.addWidget(self.min_center)
        vbox.addWidget(self.max_center)
        vbox.setContentsMargins(0,0,0,0)

    def create_widget(self):
        self.reload_para = QPushButton()
        self.reload_para.setIcon(QIcon(resources.get_path_for_image("reload_20px.png")))
        self.reload_para.clicked.connect(self.reload_para_image)

        self.thresh = slider.MSlider(
            name="Thresh", min=0, value=self.para_capture['thresh'], max=255)

        self.size_win = slider.MSlider(
            name="Size", min=0, value=self.para_capture['size'], max=10)

        self.min_center = spin.MSpin(text='Min',value=self.para_capture['min'])
        self.max_center = spin.MSpin(text='Max',value=self.para_capture['max'])
        self.min_center.spin.setFixedWidth(200)
        self.max_center.spin.setFixedWidth(200)
    
    def reload_para_image(self):
        self.thresh.setValue(self.para_capture['thresh'])
        self.size_win.setValue(self.para_capture['size'])
        self.min_center.setValue(self.para_capture['min'])
        self.max_center.setValue(self.para_capture['max'])

class LineImage(QWidget):

    def __init__(self,*args,**kwargs):
        super(LineImage,self).__init__()

        self.para_line = profile.get_control_line()
        self.create_widget()

        vbox = QVBoxLayout(self)
        
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.reload_para)
        vbox.addLayout(hbox)

        vbox.addWidget(self.top_line)
        vbox.addWidget(self.bottom_line)
        vbox.addWidget(self.start_pickup_line)
        vbox.setContentsMargins(0,0,0,0)

    def create_widget(self):
        self.reload_para = QPushButton()
        self.reload_para.setIcon(QIcon(resources.get_path_for_image("reload_20px.png")))
        self.reload_para.clicked.connect(self.reload_para_image)

        self.top_line = slider.MSlider(
            name="Top", min=0, value=self.para_line['top'], max=240)

        self.bottom_line = slider.MSlider(
            name="Bottom", min=0, value=self.para_line['bottom'], max=240)
        
        self.start_pickup_line = slider.MSlider(
            name="Pick up", min=0, value=self.para_line['start_pickup'], max=640)
    
    def reload_para_image(self):
        self.top_line.setValue(self.para_line['top'])
        self.bottom_line.setValue(self.para_line['bottom'])
        self.start_pickup_line.setValue(self.para_line['start_pickup'])


class ImageWidget(QWidget):
    def __init__(self,*args,**kwargs):
        super(ImageWidget, self).__init__()

        self.image_para = ImagePara()
        self.rotate_img = RotateImage()
        self.control_line = LineImage()
        self.detect_img = ImageDetect()

        self.save_img = QPushButton()
        self.save_img.setIcon(
            QIcon(resources.get_path_for_image('save_image_20px.png')))

        mode = ['original', 'gray', 'filter', 'thresh', 'contours', 'circle']
        self.select_mode_img = QComboBox()
        self.select_mode_img.addItems(mode)
        self.select_mode_img.setCurrentText('circle')

        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.save_img)
        hbox.addWidget(self.select_mode_img)

        vbox.addLayout(hbox)
        image_toolbox = QToolBox()

        vbox.addWidget(image_toolbox)
        image_toolbox.addItem(self.image_para, "Parameter")
        image_toolbox.addItem(self.detect_img, "Detect")
        image_toolbox.addItem(self.control_line, "Line")
        image_toolbox.addItem(self.rotate_img, "Rotate")

    def getRotate(self):
        return self.rotate_img.rotate_image.isChecked()

    def getHflip(self):
        return self.rotate_img.right_image.isChecked()

    def getVflip(self):
        return self.rotate_img.left_image.isChecked()

    def get_value_brightness(self):
        return self.image_para.brightness.value()

    def get_value_contrast(self):
        return self.image_para.contrast.value()

    def get_value_saturation(self):
        return self.image_para.saturation.value()

    def get_value_exposure(self):
        return self.image_para.exposure.value()

    def get_value_thresh(self):
        return self.detect_img.thresh.value()

    def get_value_size(self):
        size = self.detect_img.size_win.value()
        if size % 2 == 0:
            size += 1
        return size

    def get_value_mincenter(self):
        return self.detect_img.min_center.getValue()

    def get_value_maxcenter(self):
        return self.detect_img.max_center.getValue()

    def get_value_top_line(self):
        return self.control_line.top_line.value()

    def get_value_bottom_line(self):
        return self.control_line.bottom_line.value()

    def get_value_start_pickup(self):
        return self.control_line.start_pickup_line.value()

    def get_mode(self):
        return self.select_mode_img.currentText()

    def setLocal(self,list_local,list_color,list_detect_color):
        if len(list_local) != 0:
            self.rotate_img.local_text.append("<<")
            for local, color, detect_color in list(
                    zip(list_local, list_color, list_detect_color)):
                self.rotate_img.local_text.append(
                    str(local) + ' -> ' + str(color) + ' -> ' + str(detect_color))
            self.rotate_img.local_text.append("<<")


