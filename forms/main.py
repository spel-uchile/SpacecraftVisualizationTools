# -*- coding: utf-8 -*-

import sys

from PyQt5.Qt import *
from PyQt5 import QtWidgets
from PyQt5 import QtCore

from main_screen_ui import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # Set-up window
        QtWidgets.QMainWindow.__init__(self)
        self.window = Ui_MainWindow()
        self.window.setupUi(self)
        
        # Set-up signals and slots
        self.window.actionRun.triggered.connect(self.start_slot)
        self.window.actionPause.triggered.connect(self.pause_slot)
        self.window.actionStop.triggered.connect(self.stop_slot)
        self.window.actionLoadCsv.triggered.connect(self.load_slot)
        self.window.actionGeneratePlot.triggered.connect(self.plot_slot)
        self.window.control_spinbox.valueChanged.connect(self.window.control_slider.setValue)
        self.window.control_slider.valueChanged.connect(self.window.control_spinbox.setValue)
        
    def start_slot(self):
        print("START")
        
    def pause_slot(self):
        print("PAUSE")
        
    def stop_slot(self):
        print("STOP")
        
    def load_slot(self):
        print("LOAD CSV")
        
    def plot_slot(self):
        print("PLOT SLOT")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(app.exec_())
