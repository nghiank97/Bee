
from PyQt5.QtCore import center
import cv2
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

from Bee.util import profile
from Bee.util import resources

class MKnn:

    def __init__(self,*args,**kwargs):

        path = resources.get_path_for_data("data_color.csv")
        dataset = pd.read_csv(path)
        self.data_train = dataset[['blue','green','red']]
        self.target_train = dataset['label']

        self.clf = KNeighborsClassifier(n_neighbors=kwargs['neighbors'])
        self.clf.fit(self.data_train,self.target_train)

    def predict(self,test):
        if type(test) == list:
            return self.clf.predict(np.array([test]))[0]
        return self.clf.predict(test)[0]

class RealLocal:
    def __init__(self,*args,**kwargs):

        para_scale = profile.get_scale()

        self.h = para_scale["h"]
        self.rh = para_scale["rh"]
        self.rw = para_scale["rw"]

        self.local_top_point()

    def local_top_point(self):
        self.center = np.array([0,0,self.h])
        self.dir_n = np.array([-self.rh/2, 0, self.h])
        self.dir_s = np.array([self.rh/2, 0, self.h])
        self.dir_e = np.array([0, -self.rw/2, self.h])
        self.dir_w = np.array([0, self.rw/2, self.h])

        self.dir_ne = np.array([-self.rh/2,-self.rw/2,self.h])
        self.dir_es = np.array([self.rh/2,-self.rw/2,self.h])

        self.dir_sw = np.array([self.rh/2,self.rw/2,self.h])
        self.dir_wn = np.array([-self.rh/2,self.rw/2,self.h])

    def get_real_local(self,image_size,local_img,ew,eh,dm):

        self.ih = image_size[0]
        self.iw = image_size[1]

        cvt_rh = self.rh*self.ih/480
        cvt_rw = self.rw*self.iw/640

        del_col_img = self.ih/2-local_img[1]
        del_row_img = local_img[0]-self.iw/2

        scale_col_img = del_col_img/(self.ih/2)
        scale_row_img = del_row_img/(self.iw/2)

        real_col_local = scale_col_img*(cvt_rh/2)+eh
        real_row_local = scale_row_img*(cvt_rw/2)+ew-dm

        return np.round(np.array([real_col_local,real_row_local,self.h]).T,3)

class CapImage:

    def __init__(self, error=3, *args, **kwargs):
        self.original_image = kwargs['image'].copy()
        self.image = kwargs['image'].copy()
        self.thresh = kwargs['thresh']
        self.size = kwargs['size']
        self.max = kwargs['max']
        self.min = kwargs['min']
        self.start_pickup =  kwargs['start_pickup']
        self.error_center = error
        self.model_predict = MKnn(neighbors=5)

        self.ew= kwargs['ew']
        self.eh= kwargs['eh']
        self.delay_motor=kwargs['delay_motor']
        
        self.cvt_real_local = RealLocal()
        self.detect_cap()

    def get_gray_image(self):
        image = self.image.copy()
        self.gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def get_filter_image(self):
        size_win = (self.size, self.size)
        self.filter_image = cv2.GaussianBlur(self.gray_image, size_win, 2)

    def get_thresh_image(self):
        _, self.thresh_image = cv2.threshold(
            self.filter_image, self.thresh, 255, cv2.THRESH_BINARY)

    def get_contures_image(self):
        self.contours, _ = cv2.findContours(
            self.thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.contours_image = self.original_image.copy()
        self.contours_image = cv2.drawContours(
            self.contours_image, self.contours, -1, (0, 255, 0), 2)

    def average_cap(self,centers,radius,error=10):

        x,y,w,h = self.get_square(centers,radius)
        square = self.original_image[x:y,w:h]
        width, height = square.shape[:2]
        mask = np.zeros((width, height, 3), square.dtype)
        cv2.circle(mask, (int(width / 2), int(height / 2)),int(radius)-error, (255, 255, 255), -1)
        self.bitwiseAnd = cv2.bitwise_and(square, mask)
        data = []
        for i in range(3):
            channel = self.bitwiseAnd[:, :, i]
            color = channel[np.nonzero(channel)].mean()
            data.append(int(color))
        return data

    def get_square(self,center,radius):
        radius = int(radius)
        start_point_row = int(center[0]) - radius
        start_point_column = int(center[1])-radius
        return start_point_column,start_point_column+2*radius,start_point_row,start_point_row+2*radius

    def bottel_cap(self):
        self.circle_image = self.original_image.copy()
        image_size=self.circle_image.shape[:2]
        self.number_cap = 0
        self.local = []
        self.bgr_color = []
        self.detect_color = []
        self.radius = []
        self.real_local = []
        if len(self.contours) > 0:
            for contour in self.contours:
                centers, radius = cv2.minEnclosingCircle(contour)
                if centers[0]<radius or centers[1]<radius or centers[0]>=self.start_pickup:
                    continue
            
                if self.min <= radius <= self.max:
                    self.radius.append(int(radius))
                    self.local.append([int(centers[0]), int(centers[1])])

                    self.bgr_color.append(
                        self.average_cap(centers,radius))
                        
                    self.detect_color.append(
                        self.model_predict.predict(self.bgr_color[-1]))
                    self.number_cap += 1

                    cv2.circle(self.circle_image, (int(centers[0]), int(
                        centers[1])), int(radius)-self.error_center, (255, 0, 0), 2)
                    
                    cv2.putText(self.circle_image, "{:.3f}:{}".format(radius, str(self.detect_color[-1])), (int(
                        centers[0]), int(centers[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                    real_local = self.cvt_real_local.get_real_local(image_size,centers,self.ew,self.eh,self.delay_motor)
                    self.real_local.append(real_local)
                    
                    cv2.putText(self.circle_image, "{}:{}:{}".format(*real_local), (int(
                        centers[0])+20, int(centers[1])+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    
    def detect_cap(self):
        self.get_gray_image()
        self.get_filter_image()
        self.get_thresh_image()
        self.get_contures_image()
        self.bottel_cap()