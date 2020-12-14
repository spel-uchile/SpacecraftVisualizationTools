"""
@author: Elias Obreque
@Date: 11/13/2020 9:25 PM
els.obrq@gmail.com
"""

import numpy as np
basic_datalog_keys = [['time[sec]'],
                      ['omega_t_b(X)[rad/s]', 'omega_t_b(Y)[rad/s]', 'omega_t_b(Z)[rad/s]'],
                      ['sat_position_i(X)[m]', 'sat_position_i(Y)[m]', 'sat_position_i(Z)[m]'],
                      ['sat_velocity_i(X)[m/s]', 'sat_velocity_i(Y)[m/s]', 'sat_velocity_i(Z)[m/s]'],
                      ['q_t_i2b(3)[-]', 'q_t_i2b(0)[-]', 'q_t_i2b(1)[-]', 'q_t_i2b(2)[-]'],
                      ['torque_t_b(X)[Nm]', 'torque_t_b(Y)[Nm]', 'torque_t_b(Z)[Nm]'],
                      ['lat[rad]', 'lon[rad]', 'alt[m]']]


class DataHandler(object):
    def __init__(self, datalog):
        self.datalog = datalog
        self.basic_datalog = {}
        self.basic_datalog_keys = basic_datalog_keys
        self.auxiliary_datalog = {}
        self.auxiliary_datalog_keys = self.get_aux_keys()
        self.endTime = 0
        self.stepTime = 0

    def get_aux_keys(self):
        flat_list = [item for sublist in basic_datalog_keys[1:] for item in sublist]
        keys_ = [elem for elem in self.datalog.keys() if elem not in flat_list]
        return keys_

    def create_variable(self):
        for elem in basic_datalog_keys:
            if len(elem) == 1:
                self.basic_datalog[elem[0]] = np.array(self.datalog[elem[0]].values)
            else:
                for subelem in elem:
                    self.basic_datalog[subelem] = np.array(self.datalog[subelem].values)
        self.endTime = max(self.basic_datalog['time[sec]'])
        self.stepTime = self.basic_datalog['time[sec]'][1] - self.basic_datalog['time[sec]'][0]
        for elem in self.auxiliary_datalog_keys:
            self.auxiliary_datalog[elem] = np.array(self.datalog[elem].values)
