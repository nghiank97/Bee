#!env python

import time
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from PyQt5.QtOpenGL import *
from Bee.gui.base.delta import delta
from Bee.util import resources
from Bee.gui.base.delta.read_stl import read_stl
from Bee.gui.style.spin import spin
from Bee.util import profile

class GLWidget(QGLWidget):
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(GLWidget, self).__init__()
        self.setMinimumSize(600, 600)
        self.delta_robot = delta.DeltaRobot()

        self.xRot = -2500
        self.yRot = 2000
        self.zRot = 0.0
        self.z_zoom = 35
        self.xTran = 0
        self.yTran = 0
        self.h = -0.4
        self.isDrawGrid = True
        self.bottel_cap = read_stl.loader(resources.get_path_for_stl('bottel_cap.stl'))
        self.real_local = []
        
    def setXRotation(self, angle):
        self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.updateGL()

    def setYRotation(self, angle):
        self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            # self.updateGL()

    def setZRotation(self, angle):
        self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.updateGL()

    def setXYTranslate(self, dx, dy):
        self.xTran += dx
        self.yTran -= dy
        self.updateGL()

    def setZoom(self, zoom):
        self.z_zoom = zoom
        self.updateGL()

    def updateJoint(self):
        self.updateGL()

    def initializeGL(self):
        lightPos = (5.0, 5.0, 10.0, 1.0)
        reflectance1 = (0.8, 0.1, 0.0, 1.0)
        reflectance2 = (0.0, 0.8, 0.2, 1.0)
        reflectance3 = (0.2, 0.2, 1.0, 1.0)

        ambientLight = [0.7, 0.7, 0.7, 1.0]
        diffuseLight = [0.7, 0.8, 0.8, 1.0]
        specularLight = [0.4, 0.4, 0.4, 1.0]
        positionLight = [20.0, 20.0, 20.0, 0.0]

        glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLight)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLight)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specularLight)
        glLightModelf(GL_LIGHT_MODEL_TWO_SIDE, 1.0)
        glLightfv(GL_LIGHT0, GL_POSITION, positionLight)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glEnable(GL_BLEND)
        glClearColor(178.0/255, 213.0/255, 214.0/255, 1.0)

    def drawBottelCap(self,local):
        glPushMatrix()
        glTranslatef(local[0], local[1], self.h)
        self.bottel_cap.draw()
        glPopMatrix()

    def drawGL(self):
        glPushMatrix()
        if self.isDrawGrid:
            self.drawGrid()
        if len(self.real_local)>0:
            for local in self.real_local:
                self.drawBottelCap(local)

        B = self.delta_robot.get_B_B()
        b = self.delta_robot.get_B_b()
        P = self.delta_robot.get_P_P()
        A = self.delta_robot.get_vector_B_A()

        position = self.delta_robot.Position
        base_P = P
        base_P[:, 0] += position
        base_P[:, 1] += position
        base_P[:, 2] += position

        color = [108.0/255, 108.0/255, 162.0/255]
        self.setupColor(color)

        glLineWidth(20)
        glColor3f(1,1,0)
        glBegin(GL_TRIANGLES)
        for i in range(3):
            glVertex3f(*P[:,i])
        glEnd()

        color = [255.0/255, 255.0/255, 255.0/255]
        self.setupColor(color)

        glColor3f(1,1,1)
        for i in [0,2]:
            glBegin(GL_LINES)
            glVertex3f(*B[:,i])
            glVertex3f(*A[:,i])
            glEnd()

            glBegin(GL_LINES)
            glVertex3f(*B[:,i])
            glVertex3f(*A[:,i])
            glEnd()
        
            glBegin(GL_LINES)
            glVertex3f(*P[:,i])
            glVertex3f(*A[:,i])
            glEnd()

        average = lambda array: np.array([sum(array[0]) / 3, sum(array[1]) / 3, sum(array[2]) / 3]).T
        cb_P = average(base_P)

        glBegin(GL_LINES)
        glVertex3f(0,0,0)
        glVertex3f(*cb_P)
        glEnd()

        color = [206.0/255, 207.0/255, 196.0/255]
        self.setupColor(color)

        glBegin(GL_LINES)
        glVertex3f(*cb_P)
        cb_P[2] -= 0.02
        glVertex3f(*cb_P)
        glEnd()

        color = [255.0/255, 0.0/255, 255.0/255]
        self.setupColor(color)
        glBegin(GL_TRIANGLES)
        for i in range(3):
            glVertex3f(*b[:,i])
        glEnd()

        color = [255.0/255, 255.0/255, 255.0/255]
        self.setupColor(color)

        glColor3f(1,1,1)
        for i in [1]:
            glBegin(GL_LINES)
            glVertex3f(*B[:,i])
            glVertex3f(*A[:,i])
            glEnd()

            glBegin(GL_LINES)
            glVertex3f(*B[:,i])
            glVertex3f(*A[:,i])
            glEnd()
        
            glBegin(GL_LINES)
            glVertex3f(*P[:,i])
            glVertex3f(*A[:,i])
            glEnd()

        glFlush()

        glPopMatrix()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glTranslate(0, 0, self.z_zoom)
        glTranslate(self.xTran, self.yTran, 0)
        glRotated(self.xRot/16.0, 1.0, 0.0, 0.0)
        glRotated(self.yRot/16.0, 0.0, 1.0, 0.0)
        glRotated(self.zRot/16.0, 0.0, 0.0, 1.0)
        glRotated(+90.0, 1.0, 0.0, 0.0)
        self.drawGL()
        glPopMatrix()


    def resizeGL(self, w, h):
        side = min(w, h)
        if side < 0:
            return
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(10.0, w / float(h), 1.0, 20000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslated(0.0, 0.0, -40.0)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def drawGrid(self):
        glPushMatrix()
        glLineWidth(2)
        color = [8.0/255, 108.0/255, 162.0/255]
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)
        step = 0.05
        num = 10
        for i in range(-num, num+1):
            glBegin(GL_LINES)
            glVertex3f(i*step, -num * step, self.h)
            glVertex3f(i*step, num*step, self.h)
            glVertex3f(-num * step, i*step, self.h)
            glVertex3f(num*step, i*step, self.h)
            glEnd()
        glPopMatrix()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + dy)
            self.setYRotation(self.yRot - dx)
        elif event.buttons() & Qt.RightButton:
            if (self.z_zoom + dy) < 35:
                self.setZoom(self.z_zoom + dy)
        elif event.buttons() & Qt.MidButton:
            self.setXYTranslate(dx/100, dx/100)
        self.lastPos = event.pos()

    def setupColor(self, color):
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)

    def xRotation(self):
        return self.xRot

    def yRotation(self):
        return self.yRot

    def zRotation(self):
        return self.zRot

    def normalizeAngle(self, angle):
        while (angle < 0):
            angle += 360 * 16
        while (angle > 360 * 16):
            angle -= 360 * 16

    def setDegree(self,degree):
        self.delta_robot.Degree = degree

    def setPosition(self,position):
        self.delta_robot.Position = position

class DeltaGL(QWidget):
    def __init__(self, *args, **kwargs):
        super(QWidget, self).__init__()

        para_error = profile.get_scale()

        self.widget_gl = GLWidget(self)
        self.error_width = spin.MSpin(text="EW",value=0)
        self.error_width.spin.setMaximum(10000)
        self.error_width.setValue(para_error['ew']*1000)

        self.error_height = spin.MSpin(text="EH",value=0)
        self.error_height.spin.setMaximum(10000)
        self.error_height.setValue(para_error['eh']*1000)

        self.delay_motor = spin.MSpin(text="D",value=0)
        self.delay_motor.spin.setMaximum(10000)
        self.delay_motor.setValue(para_error['delay_motor']*1000)

        self.load_error = QPushButton("LOAD")
        self.load_error.clicked.connect(self.upload_error)

        vbox_error = QVBoxLayout(self)
        vbox_error.addWidget(self.widget_gl)
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.error_width)
        hbox.addWidget(self.error_height)
        hbox.addWidget(self.delay_motor)
        hbox.addStretch(1)
        hbox.addWidget(self.load_error)

        vbox_error.addLayout(hbox)

    def upload_error(self):
        ew = round(self.error_width.getValue()/1000,3)
        eh = round(self.error_height.getValue()/1000,3)
        delay_motor = round(self.delay_motor.getValue()/1000,3)

        profile.set_error_width(ew)
        profile.set_error_height(eh)
        profile.set_error_delay_motor(delay_motor)
        QMessageBox.information(self," ","Updated")

    def get_error_width(self):
        return round(self.error_width.getValue()/1000,3)
    def get_error_height(self):
        return round(self.error_height.getValue()/1000,3)
    def get_delay_motor(self):
        return round(self.delay_motor.getValue()/1000,3)
    
    def upload_local_delta(self,real_local):
        self.widget_gl.real_local = real_local
        self.widget_gl.updateJoint()
    
    def upload_degree_delta(self,degree):
        self.widget_gl.delta_robot.Degree = degree
        self.widget_gl.updateJoint()
        
    def upload_position_delta(self,position):
        self.widget_gl.delta_robot.Position = position
        self.widget_gl.updateJoint()

    def reload_position_gl(self,degree_list):
        self.widget_gl.setDegree(degree_list)
        for position in self.widget_gl.delta_robot.get_point_on_line():
            self.widget_gl.updateGL()
            time.sleep(0.001)