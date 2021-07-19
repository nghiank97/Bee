
import pandas as pd
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Bee.util import resources

class NotResponed(Exception):
    def __init__(self):
        Exception.__init__(self, "Not responed")

class Grbl(QWidget):
    wid = 500
    hei = 500

    def __init__(self,data_setting_split,*args, **kwargs):
        super().__init__(*args, **kwargs)
        pos_x = int((QDesktopWidget().screenGeometry().width() - self.wid) / 2)
        pos_y = int((QDesktopWidget().screenGeometry().height() - self.hei) / 2)

        self.setWindowTitle('Prefrences')
        self.setGeometry(pos_x, pos_y, self.wid, self.hei)

        self.data_split = [self.split_setting(data) for data in data_setting_split]
        self.row = len(self.data_split)
        self.save_file_setting_grbl(data_setting_split)
        self.command_setting = []

        self.initGui()
        self.add_setting()
        self.fixed_setting()

        vbox = QVBoxLayout()
        vbox.addWidget(self.table_setting) 

        hbox = QHBoxLayout()
        hbox.addWidget(self.cancel_grbl)
        hbox.addWidget(self.save_grbl)

        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def split_setting(self,data):
        try:
            x = data.split(" (")
            y = x[0].split("=")
            if len(x) == 1:
                y[1].strip('\r\n')
                y.append("None")
            else:
                y.append(x[1].strip(')\r\n'))
            return y
        except:
            raise NotResponed()
    
    def initGui(self):
        self.table_setting = QTableWidget()
        self.table_setting.setRowCount(self.row)
        self.table_setting.setColumnCount(3)
        self.table_setting.setHorizontalHeaderLabels(["Setting","Value","Description"])
        self.table_setting.verticalHeader().setVisible(False)

        self.cancel_grbl = QPushButton("CANCEL")
        self.save_grbl = QPushButton("SAVE")
        self.save_grbl.clicked.connect(self.save_setting)
        self.cancel_grbl.clicked.connect(self.close)

    def add_setting(self):
        for idx, val in enumerate(self.data_split):
            self.table_setting.setItem(idx,0, QTableWidgetItem(val[0]))
            self.table_setting.setItem(idx,1, QTableWidgetItem(val[1]))
            self.table_setting.setItem(idx,2, QTableWidgetItem(val[2]))
        self.table_setting.itemChanged.connect(self.change_setting)
        self.pass_value = [self.table_setting.item(i,1).text() for i in range(self.row)]

    def change_setting(self):
        self.real_value = [self.table_setting.item(i,1).text() for i in range(self.row)]
        self.command_setting = [self.table_setting.item(i,0).text()+"="+self.real_value[i] for i in range(self.row) if self.pass_value[i] != self.real_value[i]]

    def fixed_setting(self):
        header = self.table_setting.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def save_setting(self):
        self.close()

    def save_file_setting_grbl(self,data):
        with open(resources.get_path_for_grbl("grbl.txt"),"w+") as grbl_file:
            for elm in data:
                grbl_file.write(elm[:-1])

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:  
            self.close()
        if (key == Qt.Key_Return):
            pass