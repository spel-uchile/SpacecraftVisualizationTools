
import numpy as np

class DataHandler(object):
    def __init__(self, datalog):
        self.datalog = datalog

    def create_variable(self):
        self.time = np.array(self.datalog['time[sec]'].values)
        self.endTime = max(self.time)
        self.stepTime = self.time[1] - self.time[0]
        self.omega_t_b = np.array(self.datalog[['omega_t_b(X)[rad/s]', 'omega_t_b(Y)[rad/s]', 'omega_t_b(Z)[rad/s]']].values)
        self.sat_pos_i = np.array(self.datalog[['sat_position_i(X)[m]', 'sat_position_i(Y)[m]', 'sat_position_i(Z)[m]']].values)
        self.sat_vel_i = np.array(self.datalog[['sat_velocity_i(X)[m/s]', 'sat_velocity_i(Y)[m/s]', 'sat_velocity_i(Z)[m/s]']].values)
        self.q_t_i2b = np.array(self.datalog[['q_t_i2b(0)[-]', 'q_t_i2b(1)[-]', 'q_t_i2b(2)[-]', 'q_t_i2b(3)[-]']].values)
        #self.torque_t_b = np.array(self.datalog[['torque_t_b(X)[Nm]', 'torque_t_b(Y)[Nm]', 'torque_t_b(Z)[Nm]']].values)
        #self.h_total = np.array(self.datalog['h_total[Nms]'].values)
        #self.sat_vel_b = np.array(self.datalog[['sat_velocity_b(X)[m/s]', 'sat_velocity_b(Y)[m/s]', 'sat_velocity_b(Z)[m/s]']].values)
        self.geodesic  = np.array(self.datalog[['lat[rad]', 'lon[rad]', 'alt[m]']].values)
        #self.gyro_omega = np.array(self.datalog[['gyro_omega1_c(X)[rad/s]', 'gyro_omega1_c(Y)[rad/s]', 'gyro_omega1_c(Z)[rad/s]']].values)
