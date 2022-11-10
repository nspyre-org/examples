import numpy as np
import serial, sys
import pyvisa as visa
import time

# pyvisa documentation at:
# https://pyvisa.readthedocs.io/_/downloads/en/1.6/pdf/

# class APS100(MessageBasedDriver):
class APS100():
    def __init__(self,resource_name):
        # make sure the "local" button on the front panel is not pressed
        # input magnetic field units are in Tesla

        self.initialize(resource_name)

        # commands to change both fields and wait for a set amount of time
        # self.set_fields_and_wait(Bz=0.0,Bx=0.0,wait_time=1)

        # commands to change field, continuously check its value, then stop the sweep when finished
        # Bz_T = 0.01
        # self.set_field(Bz_T, axis='z') # change field
        #
        # Bx_T = 0.01
        # self.set_field(Bx_T, axis='x') # change field

    def initialize(self,resource_name):
        rm = visa.ResourceManager()
        self._inst = rm.open_resource(resource_name, query_delay=0.5)

        self._inst.open()
        self._inst.read_termination = '\r\n'
        self._inst.write_termination = '\r\n'

        print('...........................')
        print('magnet parameters:')
        print(self._inst)
        print('baud_rate: ' + str(self._inst.baud_rate))
        print('chunk_size: ' + str(self._inst.chunk_size))
        print('data_bits: ' + str(self._inst.data_bits))
        print('session: ' + str(self._inst.session))
        print('spec_version: ' + str(self._inst.spec_version))
        print('timeout: ' + str(self._inst.timeout))
        # print('last status: ' + str(self._inst.last_status))

        print('...........................')

        self.set_control_mode("REMOTE")

    def set_fields_and_wait(self, Bx, Bz, wait_time=1):
        # magnetic field units are in Tesla
        print('setting x-axis field to: ' + str(Bx) + ' T')
        print('setting z-axis field to: ' + str(Bz) + ' T')

        # x-axis
        ret = self._inst.query('CHAN 2')
        self._set_limits(Bx)
        if Bx >= 0:
            ret = self._inst.query("SWEEP UP")
        elif Bx < 0:
            ret = self._inst.query("SWEEP DOWN")
        print('setting x-axis field to: ' + str(Bx) + ' T')

        time.sleep(0.1)

        # z-axis
        ret = self._inst.query('CHAN 1')
        self._set_limits(Bz)
        if Bz >= 0:
            ret = self._inst.query("SWEEP UP")
        elif Bz < 0:
            ret = self._inst.query("SWEEP DOWN")
        print('setting z-axis field to: ' + str(Bz) + ' T')
        ret = self._inst.query("SWEEP UP")

        # wait while sweeping field
        print('waiting for ' + str(wait_time) + ' s...')
        time.sleep(wait_time)
        print('manget set to: Bx = ' + str(Bx) + ' T, Bz = ' + str(Bz) + ' T.')

    def set_field(self, B, axis='z'):
        # magnetic field units are in Teslas
        print('setting field along the ' + axis + ' axis...')

        if axis == 'z':
            ret = self._inst.query('CHAN 1')
            print('setting channel:')
            print(ret)
            # print('channel set to: ' + str(ret) + ', (expected "CHAN 1" or "CHAN 2")')
        elif axis == 'x':
            ret = self._inst.query('CHAN 2')
            print('setting channel:')
            print(ret)
            # print('channel set to: ' + str(ret) + ', (expected "CHAN 1" or "CHAN 2")')
        else:
            print('error, "axis" must be set to either "z" or "x".')
            return

        self._set_limits(B)
        # print('field is: ' + self.get_field() + ' T')
        self.sweep_field(B, axis)

    def finalize(self):
        self._inst.close()
        del self._inst

    def _set_limits(self, B):
        if B > 0:
            UL = B
            LL = 0
        elif B < 0:
            LL = B
            UL = 0
        elif B == 0:
            UL = 0
            LL = 0

        print('lower limit (kG) set to: ' + self._set_lower_limit_T(LL))
        print('upper limit (kG) set to: ' + self._set_upper_limit_T(UL))

    def get_field(self, axis='z'):
        # WHY DOESN'T WORK IF ONLY RUN ONCE???
        ret = self._inst.query('IOUT?')
        ret = self._inst.query('IOUT?')

        val = ret[:-2]
        try:
            val = float(val)
            val = str(round(val*0.1,3))
        except:
            val = ret
            print('warning... measured magnetic field not a float, return value is: ' + str(val))
        return val

    def zero_field(self):
        print('sweeping to zero...')
        ret = self._inst.query("SWEEP ZERO")

    def sweep_field(self, B_stop, axis='z'):
        print('sweeping ' + axis + ' axis to new set value... ' + str(B_stop) + ' T')
        ret = self._inst.query("SWEEP UP")

        continue_sweeping = True
        sweep_pause = 1 # s
        sweep_accuracy_T = 0.005
        sweep_counter = 0
        sweep_timeout = 60 # s

        while continue_sweeping==True:
            time.sleep(sweep_pause)
            B_now = self.get_field(axis)
            # B_now = self.get_field(axis)
            try:
                if abs(float(B_now) - B_stop) < sweep_accuracy_T:
                    print('magnet set to ' + str(B_stop) + ' T, sweep completed.')
                    continue_sweeping = False
                else:
                    print('magnet at ' + str(B_now) + ' T...')
            except:
                if sweep_counter*sweep_pause > sweep_timeout:
                    print('sweep timeout, unknown magnet state.')
                    continue_sweeping == False
            sweep_counter = sweep_counter + 1

    def _set_lower_limit_T(self, limit_T):
        limit_kG = float(limit_T * 10)
        cmd_str = "LLIM " + str(limit_kG)
        ret = self._inst.query(cmd_str)
        return ret

    def _set_upper_limit_T(self, limit_T):
        limit_kG = float(limit_T * 10)
        cmd_str = "ULIM " + str(limit_kG)
        ret = self._inst.query(cmd_str)
        return ret

    def query_upper_limit(self):
        # seems to work better if we run the command twice. WHY??????
        self._inst.query("ULIM?")
        ret = self._inst.query("ULIM?")
        return ret

    def query_lower_limit(self):
        # seems to work better if we run the command twice. WHY??????
        self._inst.query("LLIM?")
        ret = self._inst.query("LLIM?")
        return ret

    def set_control_mode(self, arg="REMOTE"):
        if arg=="REMOTE":
            self._inst.query(arg)
            self._inst.query("RWLOCK")
        elif arg=="LOCAL":
            self._inst.query(arg)
        else:
            print("APS100 magnet power supply error: must be in 'LOCAL' or 'REMOTE' control mode.")
