
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import sys
from pyquaternion import Quaternion

rad2deg = 180/np.pi

class MainGraph(object):
    def __init__(self, datalog = None):
        self.datalog = datalog
        #QtGui.QApplication.setGraphicsSystem('raster')

        #mw = QtGui.QMainWindow()
        #mw.resize(800,800)

        self.win = pg.GraphicsWindow(title="Fly Simulator")
        self.win.resize(1000,600)
        self.win.setWindowTitle('Satellite components')

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        self.plot_all()

    def plot_all(self):
        self.plot1()
        self.plot2()
        self.plot3()
        self.win.nextRow()
        self.plot4()
        self.plot5()
        self.plot6()
        self.win.nextRow()
        self.plot7()
        self.plot8()
        self.plot9()

    def plot1(self):
        p1 = self.win.addPlot(title="Groundtrack")
        p1.plot(rad2deg*self.datalog.geodesic[:, 1], rad2deg*self.datalog.geodesic[:, 0], pen=None, symbolBrush=(255,255,255), symbolSize = 2)
        p1.showGrid(x=True, y=True)
        p1.setLabel('left', "Latitude [deg]")
        p1.setLabel('bottom', "Longitude [deg]")

    def plot2(self):
        p2 = self.win.addPlot(title="'Omega_t_b' and 'gyro_omega1_c' [rad/s]")
        p2.plot(self.datalog.time, self.datalog.omega_t_b[:, 0], pen=(255,0,0), name="omega_t_b(X)")
        p2.plot(self.datalog.time, self.datalog.omega_t_b[:, 1], pen=(0,255,0), name="omega_t_b(Y)")
        p2.plot(self.datalog.time, self.datalog.omega_t_b[:, 2], pen=(0,0,255), name="omega_t_b(Z)")
        p2.showGrid(x=True, y=True)
        diam = 2
        p2.plot(self.datalog.time, self.datalog.gyro_omega[:, 0], pen=None, symbolBrush=(240,0,0),
                symbolPen='w', symbolSize = diam, name="gyro_omega1_c(X)")
        p2.plot(self.datalog.time, self.datalog.gyro_omega[:, 1], pen=None, symbolBrush=(0,240,0),
                symbolPen='w', symbolSize = diam, name="gyro_omega1_c(Y)")
        p2.plot(self.datalog.time, self.datalog.gyro_omega[:, 2], pen=None, symbolBrush=(0,0,240),
                symbolPen='w', symbolSize = diam, name="gyro_omega1_c(Z)")
        p2.setLabel('left', "Omega_b [rad/s]")
        p2.setLabel('bottom', "Time [s]")

    def plot3(self):
        p3 = self.win.addPlot(title="Quaternion_t_i2b [rad]")
        p3.plot(self.datalog.time, self.datalog.q_t_i2b[:, 0], pen=(255, 0, 0), name="q_t_i2b(0)")
        p3.plot(self.datalog.time, self.datalog.q_t_i2b[:, 1], pen=(0, 255, 0), name="q_t_i2b(1)")
        p3.plot(self.datalog.time, self.datalog.q_t_i2b[:, 2], pen=(0, 0, 255), name="q_t_i2b(2)")
        p3.plot(self.datalog.time, self.datalog.q_t_i2b[:, 3], pen=(200, 200, 200), name="q_t_i2b(3)")
        p3.setLabel('left', "quaternion_i2b [rad/s]")
        p3.setLabel('bottom', "Time [s]")
        p3.showGrid(x=True, y=True)

    def plot4(self):
        p4 = self.win.addPlot(title="Satellite position ECI")
        p4.plot(self.datalog.time, self.datalog.sat_pos_i[:, 0]/1000, pen=(255, 0, 0), name="sat_pos_i(X)")
        p4.plot(self.datalog.time, self.datalog.sat_pos_i[:, 1]/1000, pen=(0, 255, 0), name="sat_pos_i(Y)")
        p4.plot(self.datalog.time, self.datalog.sat_pos_i[:, 2]/1000, pen=(0, 0, 255), name="sat_pos_i(Z)")
        p4.setLabel('left', "Pos_i [m/s]")
        p4.setLabel('bottom', "Time [s]")
        p4.showGrid(x=True, y=True)

    def plot5(self):
        p5 = self.win.addPlot(title="Satellite velocity ECI")
        p5.plot(self.datalog.time, self.datalog.sat_vel_i[:, 0], pen=(255, 0, 0), name="sat_vel_i(X)")
        p5.plot(self.datalog.time, self.datalog.sat_vel_i[:, 1], pen=(0, 255, 0), name="sat_vel_i(Y)")
        p5.plot(self.datalog.time, self.datalog.sat_vel_i[:, 2], pen=(0, 0, 255), name="sat_vel_i(Z)")
        p5.showGrid(x=True, y=True)
        p5.setLabel('left', "Vel_i [m/s]")
        p5.setLabel('bottom', "Time [s]")

    def plot6(self):
        p6 = self.win.addPlot(title="Euler angles [rad]")
        p6.showGrid(x=True, y=True)

    def plot7(self):
        p7 = self.win.addPlot(title="torque_t_b [Nm]")
        p7.plot(self.datalog.time, self.datalog.torque_t_b[:, 0], pen=(255, 0, 0), name="torque_t_b(X)[Nm]")
        p7.plot(self.datalog.time, self.datalog.torque_t_b[:, 1], pen=(0, 255, 0), name="torque_t_b(Y)[Nm]")
        p7.plot(self.datalog.time, self.datalog.torque_t_b[:, 2], pen=(0, 0, 255), name="torque_t_b(Z)[Nm]")
        p7.showGrid(x=True, y=True)
        p7.setLabel('left', "Torque_t_b [Nm]")
        p7.setLabel('bottom', "Time [s]")

    def plot8(self):
        x2 = np.linspace(-100, 100, 1000)
        data2 = np.sin(x2) / x2
        p8 = self.win.addPlot(title="Region Selection")
        p8.plot(data2, pen=(255, 255, 255, 200))
        lr = pg.LinearRegionItem([400, 700])
        lr.setZValue(-10)
        p8.addItem(lr)

    def plot9(self):
        x2 = np.linspace(-100, 100, 1000)
        lr = pg.LinearRegionItem([400, 700])
        data2 = np.sin(x2) / x2
        lr.setZValue(-10)
        p9 = self.win.addPlot(title="Zoom on selected region")
        p9.plot(data2)
        def updatePlot():
            p9.setXRange(*lr.getRegion(), padding=0)

        def updateRegion():
            lr.setRegion(p9.getViewBox().viewRange()[0])

        lr.sigRegionChanged.connect(updatePlot)
        p9.sigXRangeChanged.connect(updateRegion)
        updatePlot()

## Start Qt event loop unless running in interactive mode or using pyside.

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    wd  = MainGraph()
    app.instance().exec_()