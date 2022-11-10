#!/usr/bin/env python3
#

import sys
import os
import instrument

class Positioner(instrument.Instrument):
    def __init__(self, ip, version='v1', verbose=False, tunnel=False):
        super().__init__(ip=ip,
                         port=instrument.Rest_Ports.positioner_hlm,
                         version=version,
                         verbose=verbose,
                         tunnel=tunnel)

    def axis_busy(self, stack, axis):
        """Is stack currently busy on the given axis"""
        r = self.get_prop(f'stack{stack}/axes/axis{axis}/properties/busy')
        return r['busy']

    def set_axis_number_of_steps(self, stack, axis, num_steps):
        '''Set the number of steps to move each time move_axis_step is called'''
        self.set_prop(f'stack{stack}/axes/axis{axis}/properties/numberOfSteps', num_steps)
        return
    
    def move_axis_step(self, stack, axis, move_positive_direction):
        '''Move axis in step mode'''
        movement_mode = 'PositiveStep' if move_positive_direction else 'NegativeStep'
        if self.verbose: print(f'  Stepping axis {stack}:{axis}, {movement_mode}')
        self.set_prop(f'stack{stack}/axes/axis{axis}/properties/movementMode', movement_mode)
        return

    def move_axis_continuous(self, stack, axis, move_positive_direction):
        '''Move axis in continuous mode'''
        movement_mode = 'PositiveContinuous' if move_positive_direction else 'NegativeContinuous'
        if self.verbose: print(f'  Moving axis {stack}:{axis}, {movement_mode}')
        self.set_prop(f'stack{stack}/axes/axis{axis}/properties/movementMode', movement_mode)
        return

    def stop_axis(self, stack, axis):
        '''Stop an axis'''
        if self.verbose: print(f'  Stopping axis {stack}:{axis}')
        self.set_prop(f'stack{stack}/axes/axis{axis}/properties/movementMode', 'Stop')
        return

    def activate_axis(self, stack, axis):
        '''Activate an axis'''
        self.set_prop(f'stack{stack}/axes/axis{axis}/properties/active', True)
        return

    def set_axis_voltage(self, stack, axis, voltage):
        '''Set the voltage (V) of an axis'''
        self.set_prop(f'stack{stack}/axes/axis{axis}/properties/voltage', voltage)
        return

    def set_axis_frequency(self, stack, axis, frequency):
        '''Set the frequency (Hz) of an axis'''
        self.set_prop(f'stack{stack}/axes/axis{axis}/properties/frequency', frequency)
        return
