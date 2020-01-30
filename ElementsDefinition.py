from pyvista import examples
import numpy as np
import pyvista as pv
from pyquaternion import Quaternion


class GeoDef(object):
    datalog = None

    def __init__(self, vtk_widget):
        self.vtk_widget = vtk_widget

    #def add_sphere(self):
        # add a sphere to the pyqt frame
        self.vtk_widget.subplot(0, 0)
        sphere = examples.load_globe()
        sphere.points /= 1000
        self.sphere = sphere
        self.vtk_widget.add_mesh(self.sphere)
        self.sphere.rotate_z(0)
        self.vtk_widget.view_isometric()
        #self.vtk_widget.reset_camera()

    def add_orbit(self):
        if self.datalog:
            self.vtk_widget.subplot(0, 0)
            self.vtk_widget.add_text('Satellite position', font_size=10)
            self.vtk_widget.add_points(self.datalog.sat_pos_i, point_size=0.8)
        else:
            print('Can not add orbit withouth data log')

    def add_spacecraft_2_orbit(self):
        self.vtk_widget.subplot(0, 0)
        self.spacecraft_in_orbit = pv.PolyData('./Model/PlantSat/PlantSat.stl')
        self.spacecraft_in_orbit.translate(np.array([0, 0, -34.05 / 2]))
        self.spacecraft_in_orbit.points *= 15000.0
        self.vtk_widget.add_mesh(self.spacecraft_in_orbit)
        self.spacecraft_in_orbit.translate(self.datalog.sat_pos_i[0, :])

    def add_spacecraft_2_attitude(self):
        self.vtk_widget.subplot(0, 1)
        self.spacecraft_in_attitude = pv.PolyData('./Model/PlantSat/PlantSat.stl')
        self.vtk_widget.add_mesh(self.spacecraft_in_attitude)
        self.spacecraft_in_attitude.translate(np.array([0, 0, -34.05/2]))
        self.quaternion_t0 = Quaternion(self.datalog.q_t_i2b[0, :])
        self.KMatrix = self.quaternion_t0.transformation_matrix
        self.spacecraft_in_attitude.transform(self.KMatrix)

    def add_i_frame_attitude(self):
        center_ref = np.array([[0.0, 0.0, 0.0]])
        self.vtk_widget.subplot(0, 1)
        self.vtk_widget.add_arrows(cent=center_ref, direction=np.array([0, 0, 1]), mag=30, color='blue')
        self.vtk_widget.add_arrows(cent=center_ref, direction=np.array([0, 1, 0]), mag=30, color='green')
        self.vtk_widget.add_arrows(cent=center_ref, direction=np.array([1, 0, 0]), mag=30, color='red')

    def add_b_frame_attitude(self):
        center_ref = np.array([[0.0, 0.0, 0.0]])
        self.vtk_widget.subplot(0, 1)
        self.body_x = pv.Arrow(center_ref, [30, 0, 0])
        self.body_y = pv.Arrow(center_ref, [0, 30, 0])
        self.body_z = pv.Arrow(center_ref, [0, 0, 30])
        self.body_x.transform(self.KMatrix)
        self.body_y.transform(self.KMatrix)
        self.body_z.transform(self.KMatrix)
        self.vtk_widget.add_mesh(self.body_x, color=[100, 0, 0])
        self.vtk_widget.add_mesh(self.body_y, color=[0, 100, 0])
        self.vtk_widget.add_mesh(self.body_z, color=[0, 0, 100])

    def add_bar(self):
        self.vtk_widget.subplot(0, 0)
        self.vtk_widget.add_slider_widget(self.sim_speed, [0.5, 100], value = 1, title='Simulation speed')

    def add_aries_arrow(self):
        self.vtk_widget.add_arrows(cent=np.array([[0.0, 0.0, 0.0]]),
                                   direction = np.array([1, 0, 0]), mag=10000, color=[0, 0, 0])
