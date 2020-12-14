
from pyvista import examples
import numpy as np
import pyvista as pv
from pyquaternion import Quaternion


class GeometricElements(object):
    datalog = None

    def __init__(self, vtk_widget):
        self.vtk_widget = vtk_widget
        self.show_nadir = False
        self.spacecraft_model_2_orbit = None
        self.spacecraft_model_2_attitude = None
        # def add_sphere(self):
        # add a sphere to the pyqt frame
        self.vtk_widget.subplot(0, 0)
        sphere = examples.load_globe()
        sphere.points /= 1000
        self.sphere = sphere
        self.vtk_widget.add_mesh(self.sphere, smooth_shading=True)
        self.sphere.rotate_z(0)
        self.vtk_widget.view_isometric()

        # self.vtk_widget.reset_camera()

    def add_orbit(self, sat_pos_i):
        self.vtk_widget.subplot(0, 0)
        self.vtk_widget.add_text('Satellite position', font_size=10)
        self.vtk_widget.add_points(sat_pos_i, point_size=0.8)

    def add_spacecraft_2_orbit(self, sat_pos_i_0):
        self.vtk_widget.subplot(0, 0)
        self.spacecraft_model_2_orbit = pv.PolyData('./Model/PlantSat/PlantSat.stl')
        # self.spacecraft_in_orbit.translate(np.array([0, 0, -34.05 / 2]))
        self.spacecraft_model_2_orbit.translate(-self.spacecraft_model_2_orbit.center_of_mass())
        self.spacecraft_model_2_orbit.points *= 15000.0
        self.vtk_widget.add_mesh(self.spacecraft_model_2_orbit)
        self.spacecraft_model_2_orbit.translate(sat_pos_i_0)
        self.vtk_widget.show_bounds()

    def add_spacecraft_2_attitude(self, q_t_i2b):
        self.vtk_widget.subplot(0, 1)
        self.spacecraft_model_2_attitude = pv.PolyData('./Model/PlantSat/PlantSat.stl')
        self.vtk_widget.add_mesh(self.spacecraft_model_2_attitude, opacity=0.1)
        self.spacecraft_model_2_attitude.translate(np.array([0, 0, -34.05 / 2]))
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

    def add_b_frame_attitude(self, show_nadir=False):
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

        if show_nadir:
            self.show_nadir = True
            self.nadir_0 = self.datalog.nadir_t_b[0, :]
            # self.nadir_0 = self.datalog.sat_pos_i[0, :]/np.linalg.norm(self.datalog.sat_pos_i[0, :])
            self.body_nadir = pv.Arrow(center_ref, self.nadir_0)
            self.body_nadir.transform(np.identity(4) * np.array([25, 25, 25, 1]))

            self.vtk_widget.add_mesh(self.body_nadir, color=[60, 63, 65])
            self.vtk_widget.show_bounds()
            self.vtk_widget.show_axes()
            # self.ct0 = self.datalog.control_torque[0, :]
            # self.body_control_torque = pv.Arrow(center_ref, self.ct0)
            # self.body_control_torque.transform(np.identity(4) * np.array([15, 15, 15, 1]))
            # self.vtk_widget.add_mesh(self.body_control_torque, color=[30, 15, 30])
            # self
            # self.vtk_widget.add_axes

    def add_bar(self):
        self.vtk_widget.subplot(0, 0)
        self.vtk_widget.add_slider_widget(self.sim_speed, [0.5, 100], value=1, title='Simulation speed')

    def add_aries_arrow(self):
        self.vtk_widget.subplot(0, 0)
        self.vtk_widget.add_arrows(cent=np.array([[0.0, 0.0, 0.0]]),
                                   direction=np.array([100000, 0, 0]), mag=1, color=[0, 0, 0])