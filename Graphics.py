
import numpy as np
import pyqtgraph as pg
rad2deg = 180/np.pi
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class MainGraph(object):
    def __init__(self, datalog=None):
        self.datalog = datalog
        self.sim_time = self.datalog.basic_datalog['time[sec]']
        self.width_plot = 2
        self.win = pg.GraphicsWindow(title="Simulation data")

        self.win.resize(1000, 600)
        self.win.setWindowTitle('Satellite -')

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

    def plot1(self):
        p1 = self.win.addPlot(title="Groundtrack")
        p1.plot(rad2deg * self.datalog.basic_datalog['lon[rad]'],
                rad2deg * self.datalog.basic_datalog['lat[rad]'], pen=pg.mkPen('r', width=self.width_plot))
        p1.showGrid(x=True, y=True)
        p1.setLabel('left', "Latitude [deg]")
        p1.setLabel('bottom', "Longitude [deg]")

    def plot2(self):
        p2 = self.win.addPlot(title="Omega_t_b' [rad/s]")
        p2.plot(self.sim_time, self.datalog.basic_datalog['omega_t_b(X)[rad/s]'],
                pen=pg.mkPen('r', width=self.width_plot), width=10, name="omega_t_b(X)")
        p2.plot(self.sim_time, self.datalog.basic_datalog['omega_t_b(Y)[rad/s]'],
                pen=pg.mkPen('b', width=self.width_plot), name="omega_t_b(Y)")
        p2.plot(self.sim_time, self.datalog.basic_datalog['omega_t_b(Z)[rad/s]'],
                pen=pg.mkPen('g', width=self.width_plot), name="omega_t_b(Z)")
        p2.addLegend()
        p2.showGrid(x=True, y=True)
        p2.setLabel('bottom', "Time [s]")

    def plot3(self):
        p3 = self.win.addPlot(title="Quaternion_t_i2b [rad]")
        p3.plot(self.sim_time, self.datalog.basic_datalog['q_t_i2b(3)[-]'], pen=pg.mkPen('r', width=self.width_plot),
                name="q_t_i2b(-)")
        p3.plot(self.sim_time, self.datalog.basic_datalog['q_t_i2b(0)[-]'], pen=pg.mkPen('b', width=self.width_plot),
                name="q_t_i2b(j)")
        p3.plot(self.sim_time, self.datalog.basic_datalog['q_t_i2b(1)[-]'], pen=pg.mkPen('g', width=self.width_plot),
                name="q_t_i2b(k)")
        p3.plot(self.sim_time, self.datalog.basic_datalog['q_t_i2b(2)[-]'], pen=pg.mkPen('k', width=self.width_plot),
                name="q_t_i2b(k)")
        p3.setLabel('bottom', "Time [s]")
        p3.showGrid(x=True, y=True)

    def plot4(self):
        p4 = self.win.addPlot(title="Satellite position ECI [km]")
        p4.plot(self.sim_time, self.datalog.basic_datalog['sat_position_i(X)[m]']/1000,
                pen=pg.mkPen('r', width=self.width_plot), name="sat_pos_i(X)")
        p4.plot(self.sim_time, self.datalog.basic_datalog['sat_position_i(Y)[m]']/1000,
                pen=pg.mkPen('b', width=self.width_plot), name="sat_pos_i(Y)")
        p4.plot(self.sim_time, self.datalog.basic_datalog['sat_position_i(Z)[m]']/1000,
                pen=pg.mkPen('g', width=self.width_plot), name="sat_pos_i(Z)")
        p4.setLabel('bottom', "Time [s]")
        p4.showGrid(x=True, y=True)

    def plot5(self):
        p5 = self.win.addPlot(title="Satellite velocity ECI")
        p5.plot(self.sim_time, self.datalog.basic_datalog['sat_velocity_i(X)[m/s]'],
                pen=pg.mkPen('r', width=self.width_plot), name="sat_vel_i(X)")
        p5.plot(self.sim_time, self.datalog.basic_datalog['sat_velocity_i(Y)[m/s]'],
                pen=pg.mkPen('b', width=self.width_plot), name="sat_vel_i(Y)")
        p5.plot(self.sim_time, self.datalog.basic_datalog['sat_velocity_i(Z)[m/s]'],
                pen=pg.mkPen('g', width=self.width_plot), name="sat_vel_i(Z)")
        p5.showGrid(x=True, y=True)
        p5.setLabel('bottom', "Time [s]")

    def plot6(self):
        p7 = self.win.addPlot(title="Torque_t_b [Nm]")
        p7.plot(self.sim_time, self.datalog.basic_datalog['torque_t_b(X)[Nm]'],
                pen=pg.mkPen('r', width=self.width_plot), name="torque_t_b(X)[Nm]")
        p7.plot(self.sim_time, self.datalog.basic_datalog['torque_t_b(Y)[Nm]'],
                pen=pg.mkPen('b', width=self.width_plot), name="torque_t_b(Y)[Nm]")
        p7.plot(self.sim_time, self.datalog.basic_datalog['torque_t_b(Z)[Nm]'],
                pen=pg.mkPen('g', width=self.width_plot), name="torque_t_b(Z)[Nm]")
        p7.showGrid(x=True, y=True)
        p7.setLabel('bottom', "Time [s]")

    def plot_aux(self):
        p1 = self.win.addPlot(title="Groundtrack")
        p1.plot(rad2deg * self.datalog.basic_datalog['lon[rad]'],
                rad2deg * self.datalog.basic_datalog['lat[rad]'], pen=pg.mkPen('r', width=self.width_plot))
        p1.showGrid(x=True, y=True)
        p1.setLabel('left', "Latitude [deg]")
        p1.setLabel('bottom', "Longitude [deg]")
