
import sys
import time
import glob
import serial
import threading


class WrongFirmware(Exception):

    def __init__(self):
        Exception.__init__(self, "Wrong Firmware")

class BoardNotConnected(Exception):

    def __init__(self):
        Exception.__init__(self, "Board Not Connected")

class Board(object):
    def __init__(self, parent=None, serial_name='COM4', baud_rate=115200):
        self.serial_name = serial_name
        self.baud_rate = baud_rate
        self.is_connected = False

        self.blanks = {
            "red":      [[9.339, 29.622, -17.074], 0],
            "yellow":   [[37.987, 41.024, -11.173], 0],
            "white":    [[12.433, -18.392, 32.659], 0],
            "orange":   [[31.513, -22.575, 29.164], 0]
        }

    def local_work(self):
        self.G0(self.blanks['red'][0])

    def connect(self):
        self.is_connected = False
        try:
            self.serial_port = serial.Serial(self.serial_name, self.baud_rate, timeout=100)
            if self.serial_port.isOpen():
                self.reset()
                version = str(self.serial_port.readline())
                if "Marlin 1.1.0-RC8" in version:
                    self.serial_port.timeout = 0.05
                    self.is_connected = True
                    self.hold(False)
                    self.G0([0,0,0])
                    
                else:
                    raise WrongFirmware()
            else:
                raise BoardNotConnected()
        except Exception as exception:
            self.serial_port = None
            raise exception

    def disconnect(self):
        if self.is_connected:
            try:
                if self.serial_port is not None:
                    self.is_connected = False
                    self.serial_port.close()
                    del self.serial_port
            except serial.SerialException:
                pass

    def hold(self, value):
        if self.is_connected:
            if value:
                self.send_command("M107 P0")
            else:
                self.send_command("M106 P0")

    def led(self, value):
        if self.is_connected:
            if value == 0:
                self.send_command("M107 P1")
            else:
                self.send_command("M106 P1 S{}".format(value))

    def auto_home(self):
        if self.is_connected:
            self.send_command("G28")
            self.reset_degree([-45, -45, -45])
            self.send_command("G0 F9000")
            self.send_command("G0 X0 Y0 Z0")

    def setFeed(self,value):
        self.send_command("G0 F{}".format(value))

    def reset_degree(self, degree):
        if self.is_connected:
            command = "G92 X{} Y{} Z{}".format(*degree)
            self.send_command(command)

    def send_command(self, data):
        if self.is_connected == True:
            self.serial_port.flushInput()
            self.serial_port.flushOutput()
            self.serial_port.write(str.encode(data + "\r\n"))
            time.sleep(0.01)

    def G0(self, degree):
        command = "G0 X{} Y{} Z{}".format(*degree)
        self.send_command(command)

    def get_blank(self,color):
        self.blanks[color][1]+=1
        return self.blanks[color][0]

    def get_number(self):
        red = self.blanks['red'][1]
        yellow = self.blanks['yellow'][1]
        white = self.blanks['white'][1]
        orange = self.blanks['orange'][1]
        return [red,yellow,white,orange]
    
    def pickup(self, up_degree, down_degree, color):
        self.G0(up_degree)
        self.hold(True)
        self.G0(down_degree)
        time.sleep(0.1)
        self.G0(up_degree)
        blank= self.get_blank(color)
        self.G0(blank)
        self.hold(False)
        time.sleep(1)

    def readline(self):
        return self.serial_port.readline().decode('utf-8')

    def reset(self):
        self.serial_port.flushInput()
        self.serial_port.flushOutput()
        self.serial_port.write(str.encode("\x18\r\n"))
        self.serial_port.readline()

    def get_ports():
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        else:
            raise EnvironmentError('Unsupported platform')
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result
