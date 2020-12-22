# -*- coding: utf-8 -*-
"""
@author: Elias Obreque
@Date: 11/13/2020 9:25 PM
els.obrq@gmail.com
"""
import sys
from PyQt5.Qt import *
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog
from threading import Thread
import time
import numpy as np
from pyvistaqt import QtInteractor
from GeometricElements import GeometricElements
import pandas as pd
from Graphics import MainGraph
from DataHandler import DataHandler
from pyquaternion import Quaternion
from forms.main_screen_2 import Ui_MainWindow
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime

twopi = 2.0 * np.pi
deg2rad = np.pi / 180.0
rad2deg = 1 / deg2rad


class Viewer(GeometricElements, QtWidgets.QMainWindow):

    def __init__(self, datalog=None, parent=None, show=True):
        self.time_speed = 1
        self.earth_av = 7.2921150 * 360.0 * 1e-5 / (2 * np.pi)
        self.init_sideral = 0
        self.current_sideral = 0
        self.vector_point = np.zeros(3)
        self.datalog_flag = False
        self.show_ref_vector_point = False
        self.run_flag = False
        self.pause_flag = False
        self.stop_flag = False
        self.gs_flag = False
        self.thread = None
        self.countTime = 0
        self.last_index = 0
        self.max_index = 0
        self.screen = None
        self.simulation_index = -1
        self.q_t_i2b = None
        self.spacecraft_pos_i = None
        self.datalog = datalog
        self.data_handler = None
        QMainWindow.__init__(self, parent)
        self.window = Ui_MainWindow()
        self.window.setupUi(self)
        self.quaternion_t0 = None

        # Set-up signals and slots
        # self.window.actionGeneratePlot.triggered.connect(self.plot_slot)
        # self.window.control_spinbox.valueChanged.connect(self.window.control_slider.setValue)
        # self.window.control_slider.valueChanged.connect(self.window.control_spinbox.setValue)

        #########################################

        vlayout = QVBoxLayout()
        self.window.view_frame.setLayout(vlayout)

        self.vtk_widget = QtInteractor(self.window.view_frame, shape=(1, 2))
        self.vtk_widget.set_background([0.25, 0.25, 0.25])
        vlayout.addWidget(self.vtk_widget)

        self.preview_plot_widget = QtWidgets.QVBoxLayout(self.window.PlotWidget)
        self.canvas_ = FigureCanvas(Figure(figsize=(5, 3)))
        self.preview_plot_widget.addWidget(self.canvas_)
        self.plot_canvas = self.canvas_.figure.subplots()
        self.plot_canvas.grid()
        self.plot_canvas.set_xlabel('Time [s]')

        GeometricElements.__init__(self, self.vtk_widget)
        self.add_bar()
        self.add_i_frame_attitude()
        self.add_gs_item()

        # --------------------------------------------------------------------------------------------------------------
        # simple menu to functions
        main_menu = self.menuBar()
        # --------------------------------------------------------------------------------------------------------------
        # File option
        self.window.actionLoadCsv.triggered.connect(self.load_csv_file)
        if datalog is not None:
            self.load_csv_file()
        # --------------------------------------------------------------------------------------------------------------

        self.window.actionRun.triggered.connect(self.run_simulation)
        self.window.actionPause.triggered.connect(self.pause_simulation)
        self.window.actionStop.triggered.connect(self.stop_simulation)
        self.window.actionAddGS.triggered.connect(self.add_gs_item)

        # sim_menu.addAction(run_action)
        # sim_menu.addAction(pause_action)
        # sim_menu.addAction(stop_action)
        # --------------------------------------------------------------------------------------------------------------
        self.window.actionGeneratePlot.triggered.connect(self.add_graph2d)
        self.window.PlotSelectedData.clicked.connect(self.plot_selected_data)
        self.window.listWidget.clicked.connect(self.preview_plot_data)
        # --------------------------------------------------------------------------------------------------------------

    def add_item_to_list(self):
        _translate = QtCore.QCoreApplication.translate
        for elem in self.data_handler.auxiliary_datalog_keys:
            item = QtWidgets.QListWidgetItem()
            item.setCheckState(QtCore.Qt.Unchecked)
            item.setText(_translate("MainWindow", elem))
            self.window.listWidget.addItem(item)

        flat_basic_list = [item for sublist in self.data_handler.basic_datalog_keys[1:] for item in sublist]
        for elem in flat_basic_list:
            item = QtWidgets.QListWidgetItem()
            item.setCheckState(QtCore.Qt.Unchecked)
            item.setText(_translate("MainWindow", elem))
            self.window.listWidget.addItem(item)
        return

    def add_graph2d(self):
        self.screen = MainGraph(self.data_handler)
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
            if self.datalog is not None:
                self.window.listWidget.clear()
            self.datalog = read_data(filename)
            self.datalog_flag = True
            print('Data log loaded')
        else:
            print('Could not load data log')

        if self.datalog_flag:
            self.data_handler = DataHandler(self.datalog)
            self.data_handler.create_variable()

            # Add actors to orbit view
            self.spacecraft_pos_i = np.array([self.data_handler.basic_datalog[self.data_handler.basic_datalog_keys[2][0]],
                                              self.data_handler.basic_datalog[self.data_handler.basic_datalog_keys[2][1]],
                                              self.data_handler.basic_datalog[
                                                  self.data_handler.basic_datalog_keys[2][2]]]).transpose()
            self.max_index = len(self.spacecraft_pos_i)
            self.add_orbit(self.spacecraft_pos_i)
            # self.add_aries_arrow()

            # Add actors to attitude view
            self.q_t_i2b = np.array([self.data_handler.basic_datalog[self.data_handler.basic_datalog_keys[4][0]],
                                     self.data_handler.basic_datalog[self.data_handler.basic_datalog_keys[4][1]],
                                     self.data_handler.basic_datalog[self.data_handler.basic_datalog_keys[4][2]],
                                     self.data_handler.basic_datalog[
                                         self.data_handler.basic_datalog_keys[4][3]]]).transpose()

            self.add_spacecraft_2_orbit(self.spacecraft_pos_i[0, :], self.q_t_i2b)
            self.add_spacecraft_2_attitude(self.q_t_i2b)
            init_time = self.data_handler.auxiliary_datalog['Date time'][0]
            datetime_array = datetime.strptime(init_time, '%Y-%m-%d %H:%M:%S')
            init_jd = self.jday(datetime_array.year, datetime_array.month, datetime_array.day,
                                datetime_array.hour, datetime_array.minute, datetime_array.second)
            self.init_sideral = rad2deg * self.gstime(init_jd)
            self.sphere.rotate_z(self.init_sideral)
            if self.gs_flag:
                self.update_gs_location(rad2deg * self.gstime(init_jd))
            self.vector_point = np.array([self.data_handler.auxiliary_datalog['Vector_tar_i(X) [-]'][0],
                                          self.data_handler.auxiliary_datalog['Vector_tar_i(Y) [-]'][0],
                                          self.data_handler.auxiliary_datalog['Vector_tar_i(Z) [-]'][0]])
            if np.linalg.norm(self.vector_point) != 0:
                self.show_ref_vector_point = True
                self.add_vector_line_in_orbit(self.spacecraft_pos_i[0, :], self.vector_point)
            self.add_b_frame_attitude(show_ref_vector_point=self.show_ref_vector_point,
                                      vector_point=self.vector_point)
            self.add_item_to_list()

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
        self.countTime = self.data_handler.stepTime * self.simulation_index

    def update_meshes(self, index):
        if index == 0:
            print('Resetting')
            self.sphere.rotate_z(-self.current_sideral)
            tr_vector = self.spacecraft_pos_i[0, :] - np.array([0, 0, 34/2])

            self.spacecraft_model_2_orbit.translate(-self.spacecraft_model_2_orbit.center_of_mass())
            self.update_attitude(index, self.spacecraft_model_2_attitude, self.spacecraft_model_2_orbit)
            self.spacecraft_model_2_orbit.translate(self.spacecraft_model_2_orbit.center_of_mass())
            if self.show_ref_vector_point:
                self.update_vector_line(self.spacecraft_pos_i[index, :], self.vector_point)

            self.spacecraft_model_2_orbit.translate(tr_vector)
            self.body_x_i.translate(tr_vector)
            self.body_y_i.translate(tr_vector)
            self.body_z_i.translate(tr_vector)
        else:
            # Update Earth
            sideral = self.earth_av * self.data_handler.stepTime * int(self.time_speed)
            self.current_sideral += sideral
            self.sphere.rotate_z(sideral)
            if self.gs_flag:
                self.update_gs_location(sideral)

            # Update Orbit
            tr_vector = self.spacecraft_pos_i[index, :] - self.spacecraft_pos_i[self.last_index, :]
            self.spacecraft_model_2_orbit.translate(-self.spacecraft_pos_i[self.last_index, :])
            self.update_attitude(index, self.spacecraft_model_2_attitude, self.spacecraft_model_2_orbit)
            self.spacecraft_model_2_orbit.translate(self.spacecraft_pos_i[self.last_index, :])
            if self.show_ref_vector_point:
                self.update_vector_line(self.spacecraft_pos_i[index, :], self.vector_point)
            self.spacecraft_model_2_orbit.translate(tr_vector)
            self.body_x_i.translate(tr_vector)
            self.body_y_i.translate(tr_vector)
            self.body_z_i.translate(tr_vector)
        # Update widget
        self.vtk_widget.update()
        self.last_index = index

    def rotate_th(self):
        self.vtk_widget.subplot(0, 0)
        self.reset_time()
        while not self.stop_flag and self.countTime < self.data_handler.endTime:
            self.update_meshes(self.simulation_index)
            # time.sleep(self.data_handler.stepTime / self.time_speed)
            time.sleep(self.data_handler.stepTime)
            # Update time
            self.simulation_index += 1 * int(self.time_speed)
            self.update_time()

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

    def update_vector_line(self, center_point, vector_point):
        self.vtk_widget.subplot(0, 0)
        new_points = np.array([center_point, center_point + 2e7 * vector_point])
        self.vector_line_from_sc.points = new_points
        cells = np.full((len(new_points) - 1, 3), 2, dtype=np.int)
        cells[:, 1] = np.arange(0, len(new_points) - 1, dtype=np.int)
        cells[:, 2] = np.arange(1, len(new_points), dtype=np.int)
        self.vector_line_from_sc.lines = cells

    def update_gs_location(self, sideral):
        self.tar_pos_eci.rotate_z(sideral)
        return

    def update_attitude(self, n, sc_model1, sc_model2=None):
        quaternion_tn = Quaternion(self.q_t_i2b[n, :]).unit
        inv_quaternion = self.quaternion_t0.inverse
        d_quaternion = quaternion_tn * inv_quaternion

        k_matrix = d_quaternion.transformation_matrix
        self.body_x.transform(k_matrix)
        self.body_y.transform(k_matrix)
        self.body_z.transform(k_matrix)
        sc_model1.transform(k_matrix)
        if sc_model2 is not None:
            sc_model2.transform(k_matrix)
        self.quaternion_t0 = quaternion_tn

        if self.show_ref_vector_point:
            curr_vector_point = np.array([self.data_handler.auxiliary_datalog['Vector_tar_i(X) [-]'][n],
                                          self.data_handler.auxiliary_datalog['Vector_tar_i(Y) [-]'][n],
                                          self.data_handler.auxiliary_datalog['Vector_tar_i(Z) [-]'][n]])

            vec = np.cross(self.vector_point, curr_vector_point)
            arg = np.dot(self.vector_point, curr_vector_point)
            if arg > 1.0:
                arg = 1.0
            elif arg < -1.0:
                arg = -1.0

            ang = np.arccos(arg)
            if np.linalg.norm(vec) == 0:
                vec = np.array([0, 0, 1])
            self.body_ref_point.transform(Quaternion(axis=vec, angle=ang).transformation_matrix)
            self.vector_point = curr_vector_point

    def preview_plot_data(self):
        self.plot_canvas.cla()
        is_data = False
        self.plot_canvas.grid()
        self.plot_canvas.set_xlabel('Time [s]')
        flat_basic_list = [item for sublist in self.data_handler.basic_datalog_keys[1:] for item in sublist]
        len_aux_keys = len(self.data_handler.auxiliary_datalog_keys)
        for index in range(self.window.listWidget.count()):
            if self.window.listWidget.item(index).checkState() == Qt.Checked:
                if index < len_aux_keys:
                    elem = self.data_handler.auxiliary_datalog_keys[index]
                    self.plot_canvas.plot(self.data_handler.basic_datalog['time[sec]'],
                                          self.data_handler.auxiliary_datalog[elem], label=elem)
                else:
                    elem = flat_basic_list[index - len_aux_keys]
                    self.plot_canvas.plot(self.data_handler.basic_datalog['time[sec]'],
                                          self.data_handler.basic_datalog[elem], label=elem)
                is_data = True
        if is_data:
            self.plot_canvas.legend()

        self.canvas_.draw()
        return

    def plot_selected_data(self):
        plt.figure()
        plt.grid()
        plt.xlabel('Time [s]')
        flat_basic_list = [item for sublist in self.data_handler.basic_datalog_keys[1:] for item in sublist]
        len_aux_keys = len(self.data_handler.auxiliary_datalog_keys)
        for index in range(self.window.listWidget.count()):
            if self.window.listWidget.item(index).checkState() == Qt.Checked:
                if index < len_aux_keys:
                    elem = self.data_handler.auxiliary_datalog_keys[index]
                    plt.plot(self.data_handler.basic_datalog['time[sec]'],
                             self.data_handler.auxiliary_datalog[elem], label=elem)
                else:
                    elem = flat_basic_list[index - len_aux_keys]
                    plt.plot(self.data_handler.basic_datalog['time[sec]'],
                             self.data_handler.basic_datalog[elem], label=elem)
        plt.legend()
        plt.show()
        return

    def gstime(self, jdut1):
        tut1 = (jdut1 - 2451545.0) / 36525.0
        temp = -6.2e-6 * tut1 * tut1 * tut1 + 0.093104 * tut1 * tut1 + \
               (876600.0 * 3600 + 8640184.812866) * tut1 + 67310.54841  # sec
        temp = (temp * deg2rad / 240.0) % twopi  # 360/86400 = 1/240, to deg, to rad

        #  ------------------------ check quadrants ---------------------
        if temp < 0.0:
            temp += twopi
        return temp

    def jday(self, year, mon, day, hr, minute, sec):
        return (367.0 * year -
                7.0 * (year + ((mon + 9.0) // 12.0)) * 0.25 // 1.0 +
                275.0 * mon // 9.0 +
                day + 1721013.5 +
                ((sec / 60.0 + minute) / 60.0 + hr) / 24.0  # ut in days
                #  - 0.5*sgn(100.0*year + mon - 190002.5) + 0.5;
                )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Viewer()
    window.show()
    sys.exit(app.exec_())
