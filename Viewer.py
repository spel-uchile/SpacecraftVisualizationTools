# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 02:47:18 2020

@author: EO
"""
import sys
from PyQt5.Qt import *
from PyQt5 import QtWidgets
from PyQt5 import QtCore
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
from forms.main_screen_ui import Ui_MainWindow
from pyvista.utilities import translate


class Viewer(GeoDef, QtWidgets.QMainWindow):

    def __init__(self, parent=None, show=True):
        self.time_speed = 1
        self.earth_av = 7.2921150*360.0*1e-5/(2*np.pi)
        self.run_flag = False
        self.pause_flag = False
        self.stop_flag = False
        self.thread = None
        self.countTime = 0
        self.screen = None
        self.simulation_index = -1

        QMainWindow.__init__(self, parent)
        self.window = Ui_MainWindow()
        self.window.setupUi(self)

        # Set-up signals and slots
        # self.window.actionGeneratePlot.triggered.connect(self.plot_slot)
        # self.window.control_spinbox.valueChanged.connect(self.window.control_slider.setValue)
        # self.window.control_slider.valueChanged.connect(self.window.control_spinbox.setValue)


        #########################################

        vlayout = QVBoxLayout()
        self.window.view_frame.setLayout(vlayout)

        self.vtk_widget = pv.QtInteractor(self.window.view_frame, shape=(1, 2))
        self.vtk_widget.set_background([0.25, 0.25, 0.25])
        vlayout.addWidget(self.vtk_widget)

        GeoDef.__init__(self, self.vtk_widget)

        self.add_bar()
        self.add_i_frame_attitude()

        # --------------------------------------------------------------------------------------------------------------
        # simple menu to functions
        main_menu = self.menuBar()
        # --------------------------------------------------------------------------------------------------------------
        # File option
        self.window.actionLoadCsv.triggered.connect(self.load_csv_file)
        # --------------------------------------------------------------------------------------------------------------
        # Path Orbit option
        # aries_action = QAction('Add vector to Vernal Equinox', self)

        # orb_menu.addAction(orbit_action)
        # orb_menu.addAction(cad_action)
        # orb_menu.addAction(aries_action)
        # --------------------------------------------------------------------------------------------------------------
        # Attitude
        # AttMenu         = main_menu.addMenu('Attitude')
        # sat_action      = QAction('Add satellite', self)
        # frame_action    = QAction('Add Body reference frame', self)

        # sat_action.triggered.connect(self.add_spacecraft_2_attitude)
        # frame_action.triggered.connect(self.add_b_frame_attitude)
        # AttMenu.addAction(sat_action)
        # AttMenu.addAction(frame_action)
        # --------------------------------------------------------------------------------------------------------------
        # Simulation option
        # sim_menu = main_menu.addMenu('Simulation')
        # run_action = QAction('Run', self)
        # pause_action = QAction('Pause', self)
        # stop_action = QAction('Stop', self)

        self.window.actionRun.triggered.connect(self.run_simulation)
        self.window.actionPause.triggered.connect(self.pause_simulation)
        self.window.actionStop.triggered.connect(self.stop_simulation)

        # sim_menu.addAction(run_action)
        # sim_menu.addAction(pause_action)
        # sim_menu.addAction(stop_action)
        # --------------------------------------------------------------------------------------------------------------
        self.window.actionGeneratePlot.triggered.connect(self.add_graph2d)
        # --------------------------------------------------------------------------------------------------------------

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
            data_log = read_data(filename)
            self.datalog = DataHandler(data_log)
            self.datalog.create_variable()

            # Add actors to orbit view
            self.add_orbit()
            self.add_spacecraft_2_orbit()
            self.add_aries_arrow()

            # Add actors to attitude view
            self.add_spacecraft_2_attitude()
            self.add_b_frame_attitude(show_nadir=True)

            print('Data log created')
        else:
            print('Could not create data log')

    def run_simulation(self):
        self.run_flag = True
        self.stop_flag = False
        self.pause_flag = False
        self.run_orbit_3d()
        print('Running...')

    def pause_simulation(self):
        self.pause_flag = True
        self.run_flag = False
        print('Paused...')

    def stop_simulation(self):
        self.stop_flag = True
        if self.thread:
            self.thread.join()
            self.thread = None
        self.update_meshes(0)
        self.reset_time()

    def reset_time(self):
        self.countTime = 0
        self.simulation_index = 1

    def update_time(self):
        self.countTime += self.datalog.stepTime

    def update_meshes(self, index):
        # Update Earth
        self.sphere.rotate_z(10)

        if index == 0:
            print('Reseting')

        # Update Orbit
        tr_vector = self.datalog.sat_pos_i[index, :] - self.datalog.sat_pos_i[index - 1, :] if index != 0 \
            else  self.datalog.sat_pos_i[0, :] - self.spacecraft_in_orbit.center_of_mass()
        self.spacecraft_in_orbit.translate(tr_vector)

        # Update Attitude
        self.update_attitude(index)

        # Update widget
        self.vtk_widget.update()

    def rotate_th(self):
        self.vtk_widget.subplot(0, 0)
        self.reset_time()
        while not self.stop_flag and self.countTime < self.datalog.endTime:
            self.update_meshes(self.simulation_index)
            time.sleep(self.datalog.stepTime / self.time_speed)

            # Update time
            self.update_time()
            self.simulation_index += 1

            while self.pause_flag:
                if self.stop_flag:
                    return
                elif self.run_flag:
                    self.pause_flag = False
                else:
                    time.sleep(1)

    def run_orbit_3d(self):
        if self.thread is None:
            self.thread = Thread(target=self.rotate_th, daemon=True)
            self.thread.start()

    def sim_speed(self, value):
        self.time_speed = value
        return

    def update_attitude(self, n):
        quaternion_tn = Quaternion(self.datalog.q_t_i2b[n, :]).unit
        inv_quaternion = self.quaternion_t0.inverse
        d_quaternion = quaternion_tn*inv_quaternion

        KMatrix = d_quaternion.transformation_matrix
        self.body_x.transform(KMatrix)
        self.body_y.transform(KMatrix)
        self.body_z.transform(KMatrix)
        self.spacecraft_in_attitude.transform(KMatrix)
        # q0 = self.quaternion_t0
        # prev_vector = self.prev_vector
        self.quaternion_t0 = quaternion_tn
        # self.prev_vector = d_quaternion.rotate(self.prev_vector)
        # print('vector:', self.prev_vector)
        # print('z pointing: ', quaternion_tn.rotate([0,0,1]))
        # print('------------------------')

        #nadir
        if self.show_nadir:
            nadir_tn_i = self.datalog.sat_pos_i[n, :]
            nadir_tn_i = - nadir_tn_i / np.linalg.norm(nadir_tn_i)
            # nadir_tn_b = quaternion_tn.rotate(nadir_tn_i)
            # nadir_tn_b = self.datalog.nadir_t_b[n, :]
            tar_v = nadir_tn_i
            print(tar_v)

            vec = np.cross(self.nadir_0, tar_v)
            ang = np.arccos(np.dot(self.nadir_0, tar_v))
            self.body_nadir.transform(Quaternion(axis=vec, angle=ang).transformation_matrix)
            self.nadir_0 = tar_v

            # ct_v = self.datalog.control_torque[n, :]
            # ct_v = ct_v/ np.linalg.norm(ct_v)
            # tar_v = ct_v
            #
            # vec = np.cross(self.ct0, tar_v)
            # ang = np.arccos(np.dot(self.ct0, tar_v))
            # self.body_control_torque.transform(Quaternion(axis=vec, angle=ang).transformation_matrix)
            # self.ct0 = tar_v
            # translate(self.control_torque, [0,0,0], self.datalog.control_torque[n, :])



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Viewer()
    window.show()
    sys.exit(app.exec_())