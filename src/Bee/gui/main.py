
import sys
from Bee.gui import main
from PyQt5.QtWidgets import QApplication
from Bee.gui import threading

def run():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    my_app = threading.App()
    my_app.show()
    app.exec_()