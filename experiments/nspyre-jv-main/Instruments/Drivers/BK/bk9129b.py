# @Author: Eric Rosenthal
# @Date:   2022-06-16T15:06:41-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-16T15:41:50-07:00


import pyvisa as visa
from collections import OrderedDict
from lantz.core import Action, DictFeat, Feat, MessageBasedDriver

class BK9129b(MessageBasedDriver):
# class BK9129b():
#     def __init__(self, resource_name, *pars, **kwargs):
#         rm = visa.ResourceManager()
#
#         # print('testing...')
#         # print(rm)
#         # print(rm.__dict__)
#         # print(rm.list_resources())
#         # help(rm.open_resource)
#         # # rm.open_resource(resource_name)
#         # help(rm)
#         self._inst = rm.open_resource(resource_name)

        # self.CHANNELS = {1: 1, 2: 2, 3: 3}

    # DEFAULTS = {
    #     'ASRL': {
    #         'write_termination': '\n',
    #         'read_termination': '\n',
    #         'timeout': 1000,
    #     }
    # }

    # @Feat()
    def idn(self):
        return self.query('*IDN?')

    # @Action()
    def remote(self):
        self.write('SYST:REM')

    # @Action()
    def local(self):
        self.write('SYST:LOC')

    # @Feat()
    def channel(self):
        return int(self.query('INST?').lstrip('CH'))

    # @channel.setter
    def channel(self, value):
        self.write('INST CH{}'.format(value))

    # @DictFeat(units='A')
    def meas_current(self, ch):
        return self.query('MEAS:CURR? CH{}'.format(ch))

    # @DictFeat(units='V')
    def meas_voltage(self, ch):
        return self.query('MEAS:VOLT? CH{}'.format(ch))

    # @DictFeat(units='V')
    def voltage(self, ch):
        vals = self.query('APP:VOLT?').split(',')
        return float(vals[ch - 1])

    # @voltage.setter
    def voltage(self, ch, value):
        vals = self.query('APP:VOLT?').split(',')
        vals = list(map(float, vals))
        vals[ch - 1] = value
        self.write('APP:VOLT {:.6f},{:.6f},{:.6f}'.format(*vals))

    # @DictFeat(units='A')
    def current(self, ch):
        vals = self.query('APP:CURR?').split(',')
        return float(vals[ch - 1])

    # @current.setter
    def current(self, ch, value):
        vals = self.query('APP:CURR?').split(',')
        vals = list(map(float, vals))
        vals[ch - 1] = value
        self.write('APP:CURR {:.6f},{:.6f},{:.6f}'.format(*vals))

    # @DictFeat(values={False: '0', True: '1'})
    def output(self, ch):
        self.channel = ch
        return self.query('CHAN:OUTP?')

    # @output.setter
    def output(self, ch, value):
        self.channel = ch
        self.write('CHAN:OUTP {}'.format(value))

    # @Action()
    def all_on(self):
        self.write('OUTP 1')

    # @Action()
    def all_off(self):
        self.write('OUTP 0')

    # @Feat(units='V')
    def voltage_limit(self):
        return self.query('VOLT:LIMIT?')

    # @voltage_limit.setter
    def voltage_limit(self, value):
        self.write('VOLT:LIMIT {:1.2f}'.format(value))

    # @Feat(values={False: 0, True: 1})
    def state(self):
        return int(self.query('CHAN:OUTP?'))

    # @state.setter
    def state(self, value):
        self.write('CHAN:OUTP {:d}'.format(value))

# def main():
#     import logging
#     import sys
#     from lantz.log import log_to_screen
#     log_to_screen(logging.CRITICAL)
#     res_name = sys.argv[1]
#     with BK9129b(res_name) as inst:
#         print(inst.idn)
#         inst.remote()
#         inst.channel = 2
#         print(inst.channel)
#         print(inst.current[1])
#         print(inst.voltage[1])
#         inst.state = True
#         print(inst.state)
#         inst.voltage_limit = 1.23
#         print(inst.voltage_limit)
#
# if __name__ == '__main__':
#     main()
