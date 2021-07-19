
import cv2
import time
import math
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Bee.engine.algorithms import cap

class CameraIsNull(Exception):
    def __init__(self):
        Exception.__init__(self, "The image is none")

class WrongCamera(Exception):

    def __init__(self):
        Exception.__init__(self, "Wrong Camera")

class CameraNotConnected(Exception):

    def __init__(self):
        Exception.__init__(self, "Camera Not Connected")

class InvalidVideo(Exception):

    def __init__(self):
        Exception.__init__(self, "Invalid Video")

class WrongDriver(Exception):

    def __init__(self):
        Exception.__init__(self, "Wrong Driver")

class InputOutputError(Exception):

    def __init__(self):
        Exception.__init__(self, "V4L2 Input/Output Error")

class Camera(object):
    height_bg = 720
    width_bg = 640

    def __init__(self, camera_id=0):
        self.camera_id = camera_id

        self.capture = None
        self.is_connected = False
        self.initialize()

    def initialize(self):
        self.thresh = 100
        self.brightness = 255
        self.contrast = 127
        self.saturation = 0
        self.exposure = 1
        self.rotate = True
        self.hflip = True
        self.vflip = False

    def connect(self):
        self.is_connected = False
        self.initialize()
        if self.capture is not None:
            self.capture.release()
        self.capture = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        time.sleep(0.2)
        if not self.capture.isOpened():
            time.sleep(1)
            self.capture.open(self.camera_id)
        if self.capture.isOpened():
            self.is_connected = True
        else:
            raise CameraNotConnected()

    def disconnect(self):
        tries = 0
        if self.is_connected:
            if self.capture is not None:
                if self.capture.isOpened():
                    self.is_connected = False
                    while tries < 10:
                        tries += 1
                        self.capture.release()

    def getBrightness(self,image):
        brightness = int((self.brightness - 0) * (255 - (-255)) / (510 - 0) + (-255)) 
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                max = 255
            else:
                shadow = 0
                max = 255 + brightness
            al_pha = (max - shadow) / 255
            ga_mma = shadow
            return cv2.addWeighted(image, al_pha, image, 0, ga_mma)
        else:
            return image

    def getContrast(self,image):
        copy_img = image.copy()
        contrast = int((self.contrast - 0) * (127 - (-127)) / (254 - 0) + (-127)) 
        if contrast != 0:
            Alpha = float(131 * (contrast + 127)) / \
                (127 * (131 - contrast))
            Gamma = 127 * (1 - Alpha)
            copy_img = cv2.addWeighted(copy_img, Alpha, image, 0, Gamma)
        return copy_img

    def getSaturation(self,image):
        copy_img = image.copy()
        hsv = cv2.cvtColor(copy_img, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] += self.saturation
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def getExposure(self,image):
        copy_img = image.copy()
        gamma_table = np.array(
            [((x/64)**self.exposure)*64 for x in range(256)]).astype("uint8")
        gamma_table = np.round(np.array(gamma_table)).astype(np.uint8)
        return cv2.LUT(copy_img, gamma_table)

    def capture_image(self):
        if self.is_connected:
            ret, image = self.capture.read()
            if ret:
                if self.rotate:
                    image = cv2.transpose(image)
                if self.hflip:
                    image = cv2.flip(image, 1)
                if self.vflip:
                    image = cv2.flip(image, 0)
                image = self.getBrightness(image)
                image = self.getContrast(image)
                image = self.getSaturation(image)
                image = self.getExposure(image)
                return image
            else:
                return None
        else:
            return None

    def set_rotate(self, value):
        self.rotate = value

    def set_hflip(self, value):
        self.hflip = value

    def set_vflip(self, value):
        self.vflip = value

    def get_ids():
        id_list = []
        for id in range(50):
            cap = cv2.VideoCapture(id,cv2.CAP_DSHOW)
            if cap.isOpened():
                id_list.append(str(id))
        cap.release()
        return id_list

    def create_black_background(image,w,h):
        if len(image.shape) == 3:
            x1, y1 = image.shape[:2]
            black_image = np.zeros((w,h, 3), dtype=np.uint8)
            x2, y2 = black_image.shape[:2]

            x3 = (x2 - x1) // 2
            y3 = (y2 - y1) // 2
            black_image[x3:x3 + x1, y3:y3 + y1] = image
        elif len(image.shape) == 2:
            x1, y1 = image.shape[:2]
            black_image = np.zeros((w,h), dtype=np.uint8)
            x2, y2 = black_image.shape[:2]

            x3 = (x2 - x1) // 2
            y3 = (y2 - y1) // 2
            black_image[x3:x3 + x1, y3:y3 + y1] = image
        return black_image

    def convert_cv_qt(cv_img,top_line=10,bottom_line=10,start_pickup=120):
        cv_img = Camera.create_black_background(cv_img,480,640)
        x,y =cv_img.shape[:2]
        # vertical
        cv2.line(cv_img, (y//2, x), (y//2, 0), (0, 0, 255), thickness=2)
        cv2.line(cv_img, (0, x // 2), (y, x // 2), (0, 0, 255), thickness=2)
        cv2.line(cv_img, (start_pickup, x), (start_pickup, 0), (0, 255, 255), thickness=2)

        add_background_img = Camera.create_black_background(cv_img,Camera.width_bg, Camera.height_bg)
                
        base_local = cap.RealLocal()

        cv2.putText(add_background_img, "{}:{}".format(*base_local.dir_es[:2]), (0,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(add_background_img, "{}:{}".format(*base_local.dir_s[:2]), (Camera.height_bg//2-25,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(add_background_img, "{}:{}".format(*base_local.dir_sw[:2]), (Camera.height_bg-125,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)        
        
        cv2.putText(add_background_img, "{}:{}".format(*base_local.dir_e[:2]), (0,Camera.width_bg//2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(add_background_img, "{}:{}".format(*base_local.dir_w[:2]), (Camera.height_bg-125,Camera.width_bg//2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        cv2.putText(add_background_img, "{}:{}".format(*base_local.dir_ne[:2]), (0,Camera.width_bg-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(add_background_img, "{}:{}".format(*base_local.dir_n[:2]), (Camera.height_bg//2-25,Camera.width_bg-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(add_background_img, "{}:{}".format(*base_local.dir_wn[:2]), (Camera.height_bg-125,Camera.width_bg-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)        
        
        rgb_image = cv2.cvtColor(add_background_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(
            rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(720, 640, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)