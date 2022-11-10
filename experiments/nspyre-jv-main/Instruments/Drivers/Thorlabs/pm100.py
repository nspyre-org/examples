# Thorlabs power meter software must be closed in order to run this, otherwise get an error
# see programming manual here:

import pyvisa as visa
import time
import numpy as np

class PM100():

    def __init__(self, resource_name):
        rm = visa.ResourceManager()
        self._inst = rm.open_resource(resource_name)
        self._inst.read_termination = '\r\n'
        self._inst.write_termination = '\r\n'

    def id(self):
        self._inst.open()
        ret = self._inst.query("*IDN?")
        self._inst.close()
        return ret

    def read_power(self):
        self._inst.open()

        # units in watts
        try:
            self._inst.open()
            pow = self._inst.query("MEASure:POWER?")
            self._inst.close()
        except:
            print('error reading power on Thorlabs PM100USB.')
            pow = 'NA'
        return pow

    def read_powers(self, n, t=0):
        powers = np.zeros(n)
        for idx in range(n):
            powers[idx] = self.read_power()
            time.sleep(t)

        return powers
