"""
@author: Elias Obreque
@Date: 11/13/2020 9:25 PM
els.obrq@gmail.com
"""

from pyvista import examples
import numpy as np
import pyvista as pv
from pyquaternion import Quaternion


class GeometricElements(object):
    datalog = None

    def __init__(self, vtk_widget):
        self.vtk_widget = vtk_widget
        self.show_ref_vector_point = False
        self.spacecraft_model_2_orbit = None
        self.spacecraft_model_2_attitude = None
        # def add_sphere(self):
        # add a sphere to the pyqt frame
        self.vtk_widget.subplot(0, 0)
        sphere = examples.load_globe()
        sphere.points /= 1000
        # self.vtk_widget.add_background_image(examples.mapfile)
        self.vtk_widget.add_background_image("Model/background4.jpg")
        self.vtk_widget.set_background(color='k')
        self.sphere = sphere
        self.vtk_widget.add_mesh(self.sphere, smooth_shading=True)
        self.sphere.rotate_z(0)
        self.add_eci_frame()
        self.vtk_widget.view_isometric()
        self.body_ref_point = None

        # self.vtk_widget.reset_camera()

    def add_orbit(self, sat_pos_i):
        self.vtk_widget.subplot(0, 0)
        self.vtk_widget.add_text('Satellite position', font_size=10)
        self.vtk_widget.add_points(sat_pos_i, point_size=0.8)
        self.vtk_widget.show_axes()

    def add_spacecraft_2_orbit(self, sat_pos_i_0, q_t_i2b):
        center_ref = np.array([0.0, 0.0, 0.0])
        self.vtk_widget.subplot(0, 0)
        self.spacecraft_model_2_orbit = pv.PolyData('./Model/PlantSat/PlantSat.stl')
        self.quaternion_t0 = Quaternion(q_t_i2b[0, :])
        self.KMatrix = self.quaternion_t0.transformation_matrix
        self.spacecraft_model_2_orbit.translate(-np.array([0, 0, 34/2]))
        self.spacecraft_model_2_orbit.transform(self.KMatrix)
        self.spacecraft_model_2_orbit.points *= 15000.0
        self.vtk_widget.add_mesh(self.spacecraft_model_2_orbit)
        self.spacecraft_model_2_orbit.translate(sat_pos_i_0)
        self.body_x_i = pv.Arrow(center_ref, [1e4, 0, 0], scale=20e3)
        self.body_y_i = pv.Arrow(center_ref, [0, 1e4, 0], scale=20e3)
        self.body_z_i = pv.Arrow(center_ref, [0, 0, 1e4], scale=20e3)

        self.body_x_i.transform(self.KMatrix.dot(np.identity(4) * np.array([30e5, 15e5, 15e5, 1e5])))
        self.body_y_i.transform(self.KMatrix.dot(np.identity(4) * np.array([15e5, 30e5, 15e5, 1e5])))
        self.body_z_i.transform(self.KMatrix.dot(np.identity(4) * np.array([15e5, 15e5, 30e5, 1e5])))
        self.vtk_widget.add_mesh(self.body_x_i, color=[50, 0, 0])
        self.vtk_widget.add_mesh(self.body_y_i, color=[0, 50, 0])
        self.vtk_widget.add_mesh(self.body_z_i, color=[0, 0, 50])
        self.body_x_i.translate(sat_pos_i_0)
        self.body_y_i.translate(sat_pos_i_0)
        self.body_z_i.translate(sat_pos_i_0)

    def add_vector_line_in_orbit(self, center_point, vector_point):
        self.vtk_widget.subplot(0, 0)
        self.vector_line_from_sc = pv.lines_from_points(np.array([center_point, center_point + 1e7*vector_point]))
        self.vtk_widget.add_mesh(self.vector_line_from_sc, color='w')
        return

    def add_spacecraft_2_attitude(self, q_t_i2b):
        self.vtk_widget.subplot(0, 1)
        self.spacecraft_model_2_attitude = pv.PolyData('./Model/PlantSat/PlantSat.stl')
        self.vtk_widget.add_mesh(self.spacecraft_model_2_attitude, opacity=0.1)
        self.spacecraft_model_2_attitude.translate(-np.array([0, 0, 34/2]))
        self.quaternion_t0 = Quaternion(q_t_i2b[0, :])
        self.KMatrix = self.quaternion_t0.transformation_matrix
        self.spacecraft_model_2_attitude.transform(self.KMatrix)
        self.prev_vector = [0, 0, 1]

    def add_i_frame_attitude(self):
        center_ref = np.array([0.0, 0.0, 0.0])
        self.vtk_widget.subplot(0, 1)
        self.vtk_widget.add_arrows(cent=center_ref, direction=np.array([0, 0, 1]), mag=30, color='blue', opacity=0.7)
        self.vtk_widget.add_arrows(cent=center_ref, direction=np.array([0, 1, 0]), mag=30, color='green', opacity=0.7)
        self.vtk_widget.add_arrows(cent=center_ref, direction=np.array([1, 0, 0]), mag=30, color='red', opacity=0.7)

    def add_b_frame_attitude(self, show_ref_vector_point=False, vector_point=None):
        center_ref = np.array([0.0, 0.0, 0.0])
        self.vtk_widget.subplot(0, 1)
        self.body_x = pv.Arrow(center_ref, [1, 0, 0])
        self.body_y = pv.Arrow(center_ref, [0, 1, 0])
        self.body_z = pv.Arrow(center_ref, [0, 0, 1])

        self.body_x.transform(self.KMatrix.dot(np.identity(4) * np.array([30, 15, 15, 1])))
        self.body_y.transform(self.KMatrix.dot(np.identity(4) * np.array([15, 30, 15, 1])))
        self.body_z.transform(self.KMatrix.dot(np.identity(4) * np.array([15, 15, 30, 1])))
        self.vtk_widget.add_mesh(self.body_x, color=[50, 0, 0], opacity=0.2)
        self.vtk_widget.add_mesh(self.body_y, color=[0, 50, 0], opacity=0.2)
        self.vtk_widget.add_mesh(self.body_z, color=[0, 0, 50], opacity=0.2)

        if show_ref_vector_point:
            if vector_point is None:
                vector_point = np.array([0, 0, 1])
            self.body_ref_point = pv.Arrow(center_ref, vector_point)
            self.body_ref_point.transform(np.identity(4) * np.array([25, 25, 25, 1]))
            self.vtk_widget.add_mesh(self.body_ref_point, color=[60, 63, 65])
        self.vtk_widget.show_axes()
        self.vtk_widget.view_isometric()

    def add_bar(self):
        self.vtk_widget.subplot(0, 0)
        self.vtk_widget.add_slider_widget(self.sim_speed, [0.5, 1000], value=1, title='Simulation speed')

    def sim_speed(self, value):
        return

    def add_eci_frame(self):
        self.vtk_widget.subplot(0, 0)
        self.vtk_widget.add_lines(np.array([[0, 0, 0], [1e7, 0, 0]]), color=[50, 0, 0], width=2, label='X-axis')
        self.vtk_widget.add_lines(np.array([[0, 0, 0], [0, 1e7, 0]]), color=[0, 50, 0], width=2, label='Y-axis')
        self.vtk_widget.add_lines(np.array([[0, 0, 0], [0, 0, 1e7]]), color=[0, 0, 50], width=2, label='Z-axis')

