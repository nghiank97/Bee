
import numpy as np
from math import *

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets

from Bee.util import resources
from Bee.util import profile
from Bee.gui.style.spin import spin
from Bee.gui.base.controller import controller
from Bee.gui.style.lineedit import lineedit
from Bee.gui.style.slider import slider

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class InvalidValue(Exception):
    def __init__(self):
        Exception.__init__(self, "Not real solution")

class DeltaRobot:
    def __init__(self, sb=0.31, sp=0.065, L=0.118, l=0.33, h=0.04, *args, **kwargs):
        self.__sb = sb
        self.__sp = sp
        self.__L = L
        self.__l = l
        self.__h = h
        self.load_base_dis()

        self.__pass_degree = np.array([0,0,0]).T
        self.__angle = np.array([0,0,0]).T
        self.__degree = np.array([0,0,0]).T
        self.__pass_position = self.get_position(self.__degree)
        self.__position = self.__pass_position
        self.Degree = np.array([0,0,0]).T

    def load_base_dis(self):
        self.__wb = np.sqrt(3) * self.__sb / 6
        self.__ub = np.sqrt(3) * self.__sb / 3
        self.__wp = np.sqrt(3) * self.__sp / 6
        self.__up = np.sqrt(3) * self.__sp / 3

        self.__a = self.__wb - self.__up
        self.__b = self.__sp / 2 - np.sqrt(3) * self.__wb / 2
        self.__c = self.__wp - self.__wb / 2

    @property
    def Angle(self):
        return np.round(self.__angle,3)

    @Angle.setter
    def Angle(self, angle):
        self.__angle = angle
        self.__position = self.get_position(angle)

    @property
    def Degree(self):
        self.__degree = self.__angle*180/np.pi
        return np.round(self.__degree,3)

    @Degree.setter
    def Degree(self, degree):
        self.__pass_degree = self.__degree
        self.__degree = degree
        self.__angle = self.__degree/180 * np.pi
        self.__pass_position = self.__position
        self.__position = self.get_position(self.__angle)

    @property
    def Position(self):
        return np.round(self.__position,3)

    @Position.setter
    def Position(self, position):
        self.__position = position
        self.__angle = self.get_angle(position)

    @property
    def PassPosition(self):
        return np.round(self.__pass_position,3)

    @staticmethod
    def square_resolution(a, b, c):
        deltal = b ** 2 - 4 * a * c
        if deltal < 0:
            raise InvalidValue()
        x1 = (-b - sqrt(deltal)) / (2 * a)
        x2 = (-b + sqrt(deltal)) / (2 * a)
        return x1, x2

    def get_B_B(self):
        B_B_1 = [0, -self.__wb, 0]
        B_B_2 = [sqrt(3) * self.__wb / 2, self.__wb / 2, 0]
        B_B_3 = [-sqrt(3) * self.__wb / 2, self.__wb / 2, 0]
        return np.array([B_B_1, B_B_2, B_B_3]).T

    def get_B_b(self):
        B_b_1 = [self.__sb / 2, -self.__wb, 0]
        B_b_2 = [0, self.__ub, 0]
        B_b_3 = [-self.__sb / 2, -self.__wb, 0]
        return np.array([B_b_1, B_b_2, B_b_3]).T

    def get_P_P(self):
        P_P_1 = [0, -self.__up, 0]
        P_P_2 = [self.__sp / 2, self.__wp, 0]
        P_P_3 = [-self.__sp / 2, self.__wp, 0]
        return np.array([P_P_1, P_P_2, P_P_3]).T

    def get_angle(self, position):
        x, y, z = position[0], position[1], position[2]
        dis = x ** 2 + y ** 2 + z ** 2

        E1 = 2 * self.__L * (y + self.__a)
        F1 = 2 * z * self.__L
        G1 = dis + self.__a ** 2 + self.__L ** 2 + 2 * y * self.__a - self.__l ** 2

        E2 = -self.__L * (sqrt(3) * (x + self.__b) + y + self.__c)
        F2 = 2 * z * self.__L
        G2 = dis + self.__b ** 2 + self.__c ** 2 + self.__L ** 2 + \
             2 * (x * self.__b + y * self.__c) - self.__l ** 2

        E3 = self.__L * (sqrt(3) * (x - self.__b) - y - self.__c)
        F3 = 2 * z * self.__L
        G3 = dis + self.__b ** 2 + self.__c ** 2 + self.__L ** 2 + \
             2 * (-x * self.__b + y * self.__c) - self.__l ** 2

        T1_1, T1_2 = self.square_resolution(G1 - E1, 2 * F1, G1 + E1)
        T2_1, T2_2 = self.square_resolution(G2 - E2, 2 * F2, G2 + E2)
        T3_1, T3_2 = self.square_resolution(G3 - E3, 2 * F3, G3 + E3)

        phi_1_1 = 2 * np.arctan(T1_1)
        phi_2_1 = 2 * np.arctan(T2_1)
        phi_3_1 = 2 * np.arctan(T3_1)

        # phi_1_2 = 2 * np.arctan(T1_2)
        # phi_2_2 = 2 * np.arctan(T2_2)
        # phi_3_2 = 2 * np.arctan(T3_2)

        # return np.round(np.array([phi_1_2, phi_2_2, phi_3_2]).T,3)
        return np.round(np.array([phi_1_1, phi_2_1, phi_3_1]).T,3)

    def get_center(point1,point2):
        return [(point1[i]/2+point2[i]/2) for i in range(3)]

    def check_samelist(list1,list2):
        for i in range(3):
            if list1[i]!=list2[i]:
                return False
        return True

    def get_point_on_line(self,step=10):
        point1 = self.PassPosition.tolist()
        point2 = self.Position.tolist()
        if DeltaRobot.check_samelist(point1,point2):
            return point1
        result = [point1,point2]
        result.sort()
        if result[0] == point1:
            list_inc = True
        else:
            list_inc = False
        n = step//2-1
        for i in range(n+1):
            for j in range(len(result)-1):
                result.append(DeltaRobot.get_center(result[j],result[j+1]))
            result.sort()
        if list_inc==True:
            return result
        else:
            return result[::-1]

    def get_position(self, angle):
        phi_1, phi_2, phi_3 = angle[0], angle[1], angle[2]
        Av1 = [0, -self.__wb - self.__L *
               cos(phi_1) + self.__up, -self.__L * sin(phi_1)]
        Av2 = [sqrt(3) * (self.__wb + self.__L * cos(phi_2)) / 2 - self.__sp / 2,
               (self.__wb + self.__L * cos(phi_2)) / 2 - self.__wp,
               -self.__L * sin(phi_2)]
        Av3 = [-sqrt(3) * (self.__wb + self.__L * cos(phi_3)) / 2 + self.__sp / 2,
               (self.__wb + self.__L * cos(phi_3)) / 2 - self.__wp,
               -self.__L * sin(phi_3)]

        x1, y1, z1 = Av1[0], Av1[1], Av1[2]
        x2, y2, z2 = Av2[0], Av2[1], Av2[2]
        x3, y3, z3 = Av3[0], Av3[1], Av3[2]

        w1 = self.__l ** 2 - (x1 ** 2 + y1 ** 2 + z1 ** 2)
        w2 = self.__l ** 2 - (x2 ** 2 + y2 ** 2 + z2 ** 2)
        w3 = self.__l ** 2 - (x3 ** 2 + y3 ** 2 + z3 ** 2)

        d = 4 * (x1 - x2) * (y2 - y3) - 4 * (x2 - x3) * (y1 - y2)

        a1 = -4 * ((z1 - z2) * (y2 - y3) - (y1 - y2) * (z2 - z3)) / d
        b1 = (-2 * (y2 - y3) * (w1 - w2) + 2 * (y1 - y2) * (w2 - w3)) / d

        a2 = -4 * ((x1 - x2) * (z2 - z3) - (z1 - z2) * (x2 - x3)) / d
        b2 = (-2 * (x1 - x2) * (w2 - w3) + 2 * (x2 - x3) * (w1 - w2)) / d

        i = a1 ** 2 + a2 ** 2 + 1
        j = 2 * a1 * b1 + 2 * a2 * b2 - 2 * a1 * x3 - 2 * a2 * y3 - 2 * z3
        k = b1 ** 2 + b2 ** 2 - 2 * b1 * x3 - 2 * b2 * y3 - w3
        z, h = self.square_resolution(i, j, k)
        x = a1 * z + b1
        y = a2 * z + b2
        return np.round(np.array([x, y, z]).T,3)

    def get_vector_B_L(self):
        phi_1, phi_2, phi_3 = self.__angle
        L_1 = [0, -self.__L * cos(phi_1), -self.__L * sin(phi_1)]
        L_2 = [sqrt(3) * self.__L * cos(phi_2) / 2, self.__L *
               cos(phi_2) / 2, -self.__L * sin(phi_2)]
        L_3 = [-sqrt(3) * self.__L * cos(phi_3) / 2, self.__L *
               cos(phi_3) / 2, -self.__L * sin(phi_3)]
        return np.array([L_1, L_2, L_3]).T

    def get_vector_B_A(self):
        phi_1, phi_2, phi_3 = self.__angle
        A_1 = [0, -self.__wb - self.__L * cos(phi_1), -self.__L * sin(phi_1)]
        A_2 = [sqrt(3) * (self.__wb + self.__L * cos(phi_2)) / 2,
               (self.__wb + self.__L * cos(phi_2)) / 2, -self.__L * sin(phi_2)]
        A_3 = [-sqrt(3) * (self.__wb + self.__L * cos(phi_3)) / 2,
               (self.__wb + self.__L * cos(phi_3)) / 2, -self.__L * sin(phi_3)]
        return np.array([A_1, A_2, A_3]).T

    # def get_vector_B_A_v(self):
    #     phi_1, phi_2, phi_3 = self.__angle
    #     Av1 = [0, -self.__wb - self.__L *
    #            cos(phi_1) + self.__up, -self.__L * sin(phi_1)]
    #     Av2 = [sqrt(3) * (self.__wb + self.__L * cos(phi_2)) / 2 - self.__sp / 2,
    #            (self.__wb + self.__L * cos(phi_2)) / 2 - self.__wp,
    #            -self.__L * sin(phi_2)]
    #     Av3 = [-sqrt(3) * (self.__wb + self.__L * cos(phi_3)) / 2 + self.__sp / 2,
    #            (self.__wb + self.__L * cos(phi_3)) / 2 - self.__wp,
    #            -self.__L * sin(phi_3)]
    #     return np.array([Av1, Av2, Av3]).T

class DegreeCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111)

    def plot(self, *args, **kwargs):
        self.axes.plot(*args, **kwargs)
        self.axes.grid(color = 'green', linestyle = '--', linewidth = 1)
        self.canvas.draw()

    def scatter(self, *args, **kwargs):
        self.axes.scatter(*args, **kwargs)
        self.axes.grid(color = 'green', linestyle = '--', linewidth = 1)
        self.canvas.draw()  

class SlideShowDelta(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111)

    def scatter(self, *args, **kwargs):
        self.axes.scatter(*args, **kwargs)
        self.canvas.draw()

    def plot(self, *args, **kwargs):
        self.axes.plot(*args, **kwargs)
        self.canvas.draw()

class DeltaPlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111, projection='3d')

    def scatter(self, *args, **kwargs):
        self.axes.scatter(*args, **kwargs)
        self.canvas.draw()

    def plot(self, *args, **kwargs):
        self.axes.plot(*args, **kwargs)
        self.canvas.draw()

class ParaDelta(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sb = lineedit.MLineEdit(text="SB (m)",value=0)
        self.sp = lineedit.MLineEdit(text="SP (m)",value=0)
        self.L = lineedit.MLineEdit(text="L (m)",value=0)
        self.l = lineedit.MLineEdit(text="l (m)",value=0)
        self.h = lineedit.MLineEdit(text="h (m)",value=0)
        self.upload = QPushButton(text="UPLOAD")
        self.upload.clicked.connect(self.setDeltaPara)
        self.load_delta_para()

        hbox = QHBoxLayout(self)
        self.para_box = QGroupBox()
        vbox = QVBoxLayout()
        vbox.addWidget(self.sb)
        vbox.addWidget(self.sp)
        vbox.addWidget(self.L)
        vbox.addWidget(self.l)
        vbox.addWidget(self.h)
        vbox.addWidget(self.upload)
        self.para_box.setLayout(vbox)
        hbox.addWidget(self.para_box)

    def load_delta_para(self):
        delta_para = profile.get_para_delta()
        self.sb.setValue(delta_para['sb'])
        self.sp.setValue(delta_para['sp'])
        self.L.setValue(delta_para['L'])
        self.l.setValue(delta_para['l'])
        self.h.setValue(delta_para['h'])

    def getDeltaPara(self):
        value = {
            "sb": self.sb.getValue(),
            "sp": self.sp.getValue(),
            "L": self.L.getValue(),
            "l": self.l.getValue(),
            "h": self.h.getValue()
        }
        return value

    def setDeltaPara(self):
        value = {
            "sb": self.sb.getValue(),
            "sp": self.sp.getValue(),
            "L": self.L.getValue(),
            "l": self.l.getValue(),
            "h": self.h.getValue()
        }
        profile.set_para_delta(value)
        QMessageBox.about(self, "Save", str(value))

class CalculatorDelta(QWidget):
    def __init__(self, *args, **kwargs):
        super(CalculatorDelta,self).__init__()

        self.local_la = QLabel("Position")
        self.local_la.setAlignment(Qt.AlignCenter)
        self.degree_la = QLabel("Degree")
        self.degree_la.setAlignment(Qt.AlignCenter)

        self.local_x = QLineEdit("0.000")
        self.local_y = QLineEdit("0.000")
        self.local_z = QLineEdit("0.000")
        self.degree_x = QLineEdit("0.000")
        self.degree_y = QLineEdit("0.000")
        self.degree_z = QLineEdit("0.000")

        required_number = QDoubleValidator()
        self.local_x.setValidator(required_number)
        self.local_y.setValidator(required_number)
        self.local_z.setValidator(required_number)
        self.degree_x.setValidator(required_number)
        self.degree_y.setValidator(required_number)
        self.degree_z.setValidator(required_number)

        self.local2_degree = QPushButton()
        self.local2_degree.setIcon(
            QIcon(resources.get_path_for_image('right_20px.png')))
        self.degree2_local = QPushButton()
        self.degree2_local.setIcon(
            QIcon(resources.get_path_for_image('left_20px.png')))

        vbox = QVBoxLayout(self)
        self.calculator_box = QGroupBox()
        hbox = QHBoxLayout()
        left_vbox = QVBoxLayout()
        left_vbox.addWidget(self.local_la)
        left_vbox.addWidget(self.local_x)
        left_vbox.addWidget(self.local_y)
        left_vbox.addWidget(self.local_z)
        left_vbox.addWidget(self.local2_degree)
        hbox.addLayout(left_vbox)

        right_vbox = QVBoxLayout()
        right_vbox.addWidget(self.degree_la)
        right_vbox.addWidget(self.degree_x)
        right_vbox.addWidget(self.degree_y)
        right_vbox.addWidget(self.degree_z)
        right_vbox.addWidget(self.degree2_local)
        hbox.addLayout(right_vbox)
        self.calculator_box.setLayout(hbox)
        vbox.addWidget(self.calculator_box)

    def get_position(self):
        local_x = float(self.local_x.text())
        local_y = float(self.local_y.text())
        local_z = float(self.local_z.text())
        return np.array([local_x,local_y,local_z]).T

    def get_degree(self):
        degree_x = float(self.degree_x.text())
        degree_y = float(self.degree_y.text())
        degree_z = float(self.degree_z.text())
        return np.array([degree_x,degree_y,degree_z]).T

    def set_position(self,position):
        self.local_x.setText("{:.3f}".format(position[0]))
        self.local_y.setText("{:.3f}".format(position[1]))
        self.local_z.setText("{:.3f}".format(position[2]))

    def set_degree(self,degree):
        self.degree_x.setText("{:.3f}".format(degree[0]))
        self.degree_y.setText("{:.3f}".format(degree[1]))
        self.degree_z.setText("{:.3f}".format(degree[2]))

class PlotDelta(QWidget):
    def __init__(self, *args, **kwargs):
        super(PlotDelta,self).__init__()

        hbox = QHBoxLayout(self)
        self.plot_box = QGroupBox()
        vbox = QVBoxLayout()
        self.plot_delta = DeltaPlotCanvas(width=5, height=5)
        self.plot_degree_delta = DegreeCanvas(width=5, height=5)
        self.plot_slideshow_delta = SlideShowDelta(width=5, height=5)

        hbox_delta = QHBoxLayout()
        hbox_delta.addWidget(self.plot_delta.canvas)
        hbox_delta.addWidget(self.plot_slideshow_delta.canvas)

        vbox.addLayout(hbox_delta)
        vbox.addWidget(self.plot_degree_delta.canvas)
        self.plot_box.setLayout(vbox)
        hbox.addWidget(self.plot_box)

class GcodeDelta(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.gcode_box = QGroupBox()
        self.gcode_text = QTextBrowser()

        self.clear_gcode = QPushButton()
        self.clear_gcode.setIcon(QIcon(resources.get_path_for_image("broom_20px.png")))
        self.clear_gcode.clicked.connect(self.clear_text)

        self.save_gcode_bt = QPushButton()
        self.save_gcode_bt.setIcon(QIcon(resources.get_path_for_image("save_20px.png")))
        self.namefile = QLineEdit()
        self.namefile.setText("process.gcode")
        
        layout = QHBoxLayout(self)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.namefile)
        hbox.addWidget(self.save_gcode_bt)
        hbox.addWidget(self.clear_gcode)

        vbox.addLayout(hbox)
        vbox.addWidget(self.gcode_text)
        self.gcode_box.setLayout(vbox)
        layout.addWidget(self.gcode_box)

    def clear_text(self):
        self.gcode_text.clear()

    def set_text(self,gcode):
        self.gcode_text.append(gcode)

class Move(QWidget):
    def __init__(self,*args,**kwargs):
        super(Move, self).__init__()

        self.scale = 10
        self.feed_motor = 500
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

        hbox = QHBoxLayout(self)
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

        self.job_group.setLayout(vbox)
        hbox.addWidget(self.job_group)

    def upload_step(self,value):
        self.scale = value

class DeltaForm(QWidget):
    __wid = 1300
    __hei = 900
    SCALE = 1000
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        delta_para = profile.get_para_delta()
        self.delta_robot = DeltaRobot(**delta_para)
        self.angle_delta_robot = []

        self.initGui()
        
        self.controller.inc_position_z.clicked.connect(self.inc_position_z)
        self.controller.des_position_z.clicked.connect(self.des_position_z)
        self.controller.inc_position_y.clicked.connect(self.inc_position_y)
        self.controller.des_position_y.clicked.connect(self.des_position_y)
        self.controller.inc_position_x.clicked.connect(self.inc_position_x)
        self.controller.des_position_x.clicked.connect(self.des_position_x)
        self.controller.home_position.clicked.connect(self.home_degree)

        self.calcu_delta.degree2_local.clicked.connect(self.reload_position)
        self.calcu_delta.local2_degree.clicked.connect(self.reload_degree)
        self.reload_position()

    def plot_position_deltal(self):
        self.plot_delta.plot_delta.axes.clear()
        self.plot_delta.plot_delta.axes.set_title('Delta Robot 3D')
        self.plot_delta.plot_delta.axes.set_xlim(-0.2, 0.2)
        self.plot_delta.plot_delta.axes.set_ylim(-0.2, 0.2)
        self.plot_delta.plot_delta.axes.set_zlim(-0.4, 0.1)

        B = self.delta_robot.get_B_B()
        b = self.delta_robot.get_B_b()
        P = self.delta_robot.get_P_P()
        A = self.delta_robot.get_vector_B_A()

        position = self.delta_robot.Position
        base_P = P
        base_P[:, 0] += position
        base_P[:, 1] += position
        base_P[:, 2] += position

        self.plot_delta.plot_delta.scatter(B[0], B[1], B[2], color='g')
        self.plot_delta.plot_delta.scatter(b[0], b[1], b[2], color='r')
        base_move = np.c_[b, b[:, 0]]
        self.plot_delta.plot_delta.plot(base_move[0], base_move[1], base_move[2], color='b',linewidth=3.0)
        self.plot_delta.plot_delta.scatter(P[0], P[1], P[2], color='g')
        self.plot_delta.plot_delta.scatter(base_P[0], base_P[1], base_P[2], color='g')
        move = np.c_[P, P[:, 0]]
        self.plot_delta.plot_delta.plot(move[0], move[1], move[2], color='g',linewidth=3.0)
        self.plot_delta.plot_delta.scatter(A[0], A[1], A[2], s=20)

        average = lambda array: np.array([sum(array[0]) / 3, sum(array[1]) / 3, sum(array[2]) / 3]).T
        cb_P = average(base_P)
        self.plot_delta.plot_delta.scatter(cb_P[0], cb_P[1], cb_P[2], s=20,color='#fcc11e')
        self.plot_delta.plot_delta.scatter(cb_P[0], cb_P[1], cb_P[2]-0.02, s=20,color='#fcc11e')
        self.plot_delta.plot_delta.plot([cb_P[0], cb_P[0]], [cb_P[1], cb_P[1]], [cb_P[2], cb_P[2]-0.02],color='#fcc11e')

        for i in range(3):
            self.plot_delta.plot_delta.plot([B[0][i], A[0][i]], [B[1][i], A[1][i]], [B[2][i], A[2][i]], color='g')

        for i in range(3):
            self.plot_delta.plot_delta.plot([A[0][i], base_P[0][i]], [A[1][i], base_P[1][i]], [A[2][i], base_P[2][i]], color='b')

        self.plot_delta.plot_delta.scatter([0], [0], [0], color='g')
        self.plot_delta.plot_delta.plot([0, position[0]], [0, position[1]], [0, position[2]], color='r')
        self.plot_delta.plot_delta.canvas.draw()

        self.plot_delta.plot_degree_delta.axes.clear()
        self.plot_delta.plot_degree_delta.axes.set_title('Degree Delta Robot')
        self.plot_delta.plot_degree_delta.axes.set_xlim(0,10)
        self.plot_delta.plot_degree_delta.axes.set_ylim(-90, 90)
        self.angle_delta_robot.append(self.delta_robot.Degree)
        angle_x = [item[0] for item in self.angle_delta_robot]
        angle_y = [item[1] for item in self.angle_delta_robot]
        angle_z = [item[2] for item in self.angle_delta_robot]
        index = [x/10 for x in range(0,len(angle_x))]
        self.plot_delta.plot_degree_delta.plot(index,angle_x,label='Degree X')
        self.plot_delta.plot_degree_delta.plot(index,angle_y,label='Degree Y')
        self.plot_delta.plot_degree_delta.plot(index,angle_z,label='Degree Z')
        
        self.plot_delta.plot_degree_delta.fig.legend()
        self.plot_delta.plot_degree_delta.canvas.draw()

        self.plot_delta.plot_slideshow_delta.axes.clear()
        self.plot_delta.plot_slideshow_delta.axes.set_title('SlidesShow Delta Robot')
        self.plot_delta.plot_slideshow_delta.axes.set_xlim(-0.25, 0.25)
        self.plot_delta.plot_slideshow_delta.axes.set_ylim(-0.25, 0.25)
        
        self.plot_delta.plot_slideshow_delta.scatter(b[0], b[1],color='r')
        self.plot_delta.plot_slideshow_delta.plot(np.insert(b[0], 3, b[0][0], axis=0), np.insert(b[1], 3, b[1][0], axis=0),color='b')

        self.plot_delta.plot_slideshow_delta.scatter(B[0], B[1],color='g')
        for i in range(3):
            self.plot_delta.plot_slideshow_delta.plot([A[0][i], B[0][i]], [A[1][i], B[1][i]], color='g')

        self.plot_delta.plot_slideshow_delta.scatter(base_P[0], base_P[1],color='b')
        for i in range(3):
            self.plot_delta.plot_slideshow_delta.plot([A[0][i], base_P[0][i]], [A[1][i], base_P[1][i]], color='b')

        self.plot_delta.plot_slideshow_delta.scatter(A[0], A[1])
        
        self.plot_delta.plot_slideshow_delta.scatter(move[0], move[1], color='g')
        self.plot_delta.plot_slideshow_delta.plot(np.insert(move[0], 3, move[0][0], axis=0), np.insert(move[1], 3, move[1][0], axis=0),color='g')
    
        self.plot_delta.plot_slideshow_delta.scatter(cb_P[0], cb_P[1], color='#fcc11e')
        self.plot_delta.plot_slideshow_delta.plot([0, position[0]], [0, position[1]], color='r')

        self.plot_delta.plot_slideshow_delta.canvas.draw()

    def put_gcode(self):
        command = "G0 X{:.3f} Y{:.3f} Z{:.3f}".format(self.delta_robot.Degree[0],self.delta_robot.Degree[1],self.delta_robot.Degree[2])
        self.gcode_delta.set_text(command)

    def reload_position(self):
        real_degree = self.calcu_delta.get_degree()
        self.delta_robot.Degree = real_degree
        position = self.delta_robot.Position
        self.calcu_delta.set_position(position)
        self.plot_position_deltal()
        self.put_gcode()

    def reload_degree(self):
        try:
            real_position = self.calcu_delta.get_position()
            self.delta_robot.Position = real_position
            degree = self.delta_robot.Degree
            self.calcu_delta.set_degree(degree)
            self.plot_position_deltal()
            self.put_gcode()
        except InvalidValue as e:
            QMessageBox.warning(self,"",str(e))

    def initGui(self):

        self.setWindowTitle('DELTA')
        self.setWindowIcon(QIcon(resources.get_path_for_image("Bee_32px.png")))
        pos_x = (QDesktopWidget().screenGeometry().width() - self.__wid) // 2
        pos_y = (QDesktopWidget().screenGeometry().height() - self.__hei) // 2
        self.setGeometry(pos_x, pos_y, self.__wid, self.__hei)
        self.setWindowIcon(QIcon(resources.get_path_for_image("bee_20px.png")))

        self.para_delta = ParaDelta()
        self.para_delta.upload.clicked.connect(self.load_para)
        self.calcu_delta = CalculatorDelta()
        self.plot_delta = PlotDelta()
        self.gcode_delta = GcodeDelta()
        self.controller = Move()

        layout = QHBoxLayout(self)

        vbox_para = QVBoxLayout()

        hbox = QHBoxLayout()
        hbox.addWidget(self.para_delta)

        vbox = QVBoxLayout()
        vbox.addWidget(self.controller)
        vbox.addWidget(self.calcu_delta)
        hbox.addLayout(vbox)
        vbox_para.addLayout(hbox)
        vbox_para.addWidget(self.gcode_delta)

        layout.addLayout(vbox_para)
        layout.addWidget(self.plot_delta)

    def load_para(self):
        para = self.para_delta.getDeltaPara()
        self.delta_robot = DeltaRobot(**para)
        self.reload_position()

    def inc_position_z(self):
        scale = self.controller.scale
        value = self.calcu_delta.get_position()
        value[2]+=scale/self.SCALE
        self.calcu_delta.set_position(value)
        self.reload_degree()

    def des_position_z(self):
        scale = self.controller.scale
        value = self.calcu_delta.get_position()
        value[2]-=scale/self.SCALE
        self.calcu_delta.set_position(value)
        self.reload_degree()

    def inc_position_y(self):
        scale = self.controller.scale
        value = self.calcu_delta.get_position()
        value[1]+=scale/self.SCALE
        self.calcu_delta.set_position(value)
        self.reload_degree()

    def des_position_y(self):
        scale = self.controller.scale
        value = self.calcu_delta.get_position()
        value[1]-=scale/self.SCALE
        self.calcu_delta.set_position(value)
        self.reload_degree()

    def inc_position_x(self):
        scale = self.controller.scale
        value = self.calcu_delta.get_position()
        value[0]+=scale/self.SCALE
        self.calcu_delta.set_position(value)
        self.reload_degree()

    def des_position_x(self):
        scale = self.controller.scale
        value = self.calcu_delta.get_position()
        value[0]-=scale/self.SCALE
        self.calcu_delta.set_position(value)
        self.reload_degree()

    def home_degree(self):
        self.calcu_delta.set_degree(degree=[0,0,0])
        self.reload_position()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()