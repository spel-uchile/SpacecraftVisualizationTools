# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 02:47:18 2020

@author: EO
"""
import sys
from PyQt5 import Qt
from PyQt5.QtWidgets import QFileDialog
from threading import Thread
import time
import numpy as np
import pyvista as pv
from ElementsDefinition import GeoDef
import pandas as pd
from Graphics import MainGraph
from datalogcsv import DataHandler
from pyquaternion import Quaternion


class Viewer(GeoDef, Qt.QMainWindow):

    def __init__(self, parent=None, show=True):
        self.time_speed = 1
        self.earth_av = 7.2921150*360.0*1e-5/(2*np.pi)
        self.run_flag = False
        self.pause_flag = False
        self.stop_flag = False
        self.thread = None
        self.countTime = 0
        self.screen = None

        Qt.QMainWindow.__init__(self, parent)
        # create the frame
        self.frame = Qt.QFrame()
        vlayout = Qt.QVBoxLayout()

        # add the pyvista interactor object
        self.vtk_widget = pv.QtInteractor(self.frame, shape=(1, 2))
        self.vtk_widget.set_background([0.25, 0.25, 0.25])
        self.vtk_widget.setFixedWidth(1000)
        self.vtk_widget.setFixedHeight(500)
        vlayout.addWidget(self.vtk_widget)
        GeoDef.__init__(self, self.vtk_widget)

        self.frame.setLayout(vlayout)
        self.setCentralWidget(self.frame)

        self.add_bar()
        self.add_i_frame_attitude()

        # --------------------------------------------------------------------------------------------------------------
        # simple menu to functions
        main_menu = self.menuBar()
        # --------------------------------------------------------------------------------------------------------------
        # File option
        fileMenu = main_menu.addMenu('File')
        loadcsvData = Qt.QAction('Load csv data', self)
        exitButton = Qt.QAction('Exit', self)

        exitButton.setShortcut('Ctrl+Q')
        loadcsvData.triggered.connect(self.load_csv_file)
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(loadcsvData)
        fileMenu.addAction(exitButton)
        # --------------------------------------------------------------------------------------------------------------
        # Path Orbit option
        orb_menu = main_menu.addMenu('Orbit')
        # orbit_action    = Qt.QAction('Show Orbit', self)
        # cad_action      = Qt.QAction('Add satellite', self)
        aries_action = Qt.QAction('Add vector to Vernal Equinox', self)

        # orbit_action.triggered.connect(self.add_orbit)
        # cad_action.triggered.connect(self.add_spacecraft_2_orbit)
        aries_action.triggered.connect(self.add_aries_arrow)

        # orb_menu.addAction(orbit_action)
        # orb_menu.addAction(cad_action)
        orb_menu.addAction(aries_action)
        # --------------------------------------------------------------------------------------------------------------
        # Attitude
        # AttMenu         = main_menu.addMenu('Attitude')
        # sat_action      = Qt.QAction('Add satellite', self)
        # frame_action    = Qt.QAction('Add Body reference frame', self)
        #
        # sat_action.triggered.connect(self.add_spacecraft_2_attitude)
        # frame_action.triggered.connect(self.add_b_frame_attitude)
        # AttMenu.addAction(sat_action)
        # AttMenu.addAction(frame_action)
        # --------------------------------------------------------------------------------------------------------------
        # Simulation option
        sim_menu = main_menu.addMenu('Simulation')
        run_action = Qt.QAction('Run', self)
        pause_action = Qt.QAction('Pause', self)
        stop_action = Qt.QAction('Stop', self)

        run_action.triggered.connect(self.run_simulation)
        pause_action.triggered.connect(self.pause_simulation)
        stop_action.triggered.connect(self.stop_simulation)

        sim_menu.addAction(run_action)
        sim_menu.addAction(pause_action)
        sim_menu.addAction(stop_action)
        # --------------------------------------------------------------------------------------------------------------
        graph2d_menu = main_menu.addMenu('Data')
        plot_action = Qt.QAction('Generate graph', self)

        plot_action.triggered.connect(self.add_graph2d)

        graph2d_menu.addAction(plot_action)
        # --------------------------------------------------------------------------------------------------------------

        if show:
            self.show()

    def add_graph2d(self):
        self.screen = MainGraph(self.datalog)
        self.screen.win.show()

    def load_csv_file(self):
        def read_data(file_path):
            df = pd.read_csv(file_path, delimiter=',')
            sim_data = df
            return sim_data

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Select CSV data file", "", "CSV Files (*.csv)",
                                                  options=options)
        if filename:
            dataLog = read_data(filename)
            self.datalog = DataHandler(dataLog)
            self.datalog.create_variable()

            # Add actors to orbit view
            self.add_orbit()
            self.add_spacecraft_2_orbit()
            self.add_aries_arrow()

            # Add actors to attitude view
            self.add_spacecraft_2_attitude()
            self.add_b_frame_attitude()

            print('Data log created')
        else:
            print('Could not create data log')

    def run_simulation(self):
        self.run_flag = True
        self.run_orbit_3d()
        print('Running...')

    def pause_simulation(self):
        self.pause_flag = True
        self.run_flag = False
        print('Paused...')

    def stop_simulation(self):
        return

    def reset_time(self):
        self.countTime = 0

    def update_time(self):
        self.countTime += self.datalog.stepTime

    def update_meshes(self, index):
        # Update Earth
        self.sphere.rotate_z(10)

        # Update Orbit
        self.current_pos = self.datalog.sat_pos_i[index, :] - self.datalog.sat_pos_i[index - 1, :]
        self.spacecraft_in_orbit.translate(self.current_pos)

        # Update Attitude
        self.update_attitude(index)

        # Update widget
        self.vtk_widget.update()

    def rotate_th(self):
        self.vtk_widget.subplot(0, 0)
        i = 1
        self.reset_time()
        while self.countTime < self.datalog.endTime:

            while self.pause_flag:
                if self.run_flag:
                    self.pause_flag = False

            self.update_meshes(i)
            time.sleep(self.datalog.stepTime / self.time_speed)

            # Update time
            self.update_time()
            i += 1

    def run_orbit_3d(self):
        if self.thread is None:
            self.thread = Thread(target=self.rotate_th, daemon=True)
            self.thread.start()

    def sim_speed(self, value):
        self.time_speed = value
        return

    def update_attitude(self, i):
        quaternion_ti = Quaternion(self.datalog.q_t_i2b[i, :])
        inv_quaternion = self.quaternion_t0.inverse
        d_quaternion = inv_quaternion*quaternion_ti
        KMatrix = d_quaternion.transformation_matrix
        self.body_x.transform(KMatrix)
        self.body_y.transform(KMatrix)
        self.body_z.transform(KMatrix)
        self.spacecraft_in_attitude.transform(KMatrix)
        self.quaternion_t0 = quaternion_ti


if __name__ == '__main__':
    app = Qt.QApplication(sys.argv)
    window = Viewer()
    sys.exit(app.exec_())