#!/usr/bin/env python3
#

from datetime import datetime
from datetime import timedelta
import time
import argparse
import requests
import sys
import os
import random

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pythonlibs"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
import positioner

def _do_experiment(slow_pixel, fast_pixel, slow_pos, fast_pos):
    print(f'Taking measurement: pixel={slow_pixel},{fast_pixel}  position={slow_pos},{fast_pos}')
    time.sleep(5)

def _wait_for_axis_not_busy(stack_number, axis_number):
    axis_moving = True
    while axis_moving:
        time.sleep(0.1)
        axis_moving = positioner.get_prop(f'stack{stack_number}/axes/axis{axis_number}/properties/busy')['busy']
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
    """
    Customer example demonstrating how to perform a 2-axis raster scan.

    Example:
    python positioner_rasterscan.py --ip 192.168.1.123 --slow-axis 2 --fast-axis 1 --slow-numsteps 1000 --fast-numsteps 1000 --slow-pixels 5 --fast-pixels 10
    """,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--ip", help="The IP address of the system to control.", required=True)
    parser.add_argument("--stack-number", help="Which stack to control (defaults to 1).", default=1, type=int, choices=range(1,5))
    parser.add_argument("--fast-axis", help="The number of the fast axis.", required=True, type=int, choices=range(1,5))
    parser.add_argument("--slow-axis", help="The number of the slow axis.", required=True, type=int, choices=range(1,5))
    parser.add_argument("--fast-numsteps", help="The number of steps to take each time the fast axis is moved.", required=True, type=int)
    parser.add_argument("--slow-numsteps", help="The number of steps to take each time the slow axis is moved.", required=True, type=int)
    parser.add_argument("--fast-pixels", help="The number of pixels for the fast axis.", required=True, type=int)
    parser.add_argument("--slow-pixels", help="The number of pixels for the slow axis.", required=True, type=int)
    args = parser.parse_args()

    print("Connecting to remote system at %s" % (args.ip))
    positioner = positioner.Positioner(args.ip)

    stack_number = args.stack_number

    # Selects the axes that will be used in the scan
    axis_fast   = args.fast_axis
    axis_slow = args.slow_axis

    try:
        # Set the step size to use for each axis
        positioner.set_prop(f'stack{stack_number}/axes/axis{axis_fast}/properties/numberOfSteps', args.fast_numsteps)
        positioner.set_prop(f'stack{stack_number}/axes/axis{axis_slow}/properties/numberOfSteps', args.slow_numsteps)

        for s in range(0, args.slow_pixels):
            if s != 0:
                # Move the fast axis to next pixel, wait for it to finish moving
                positioner.set_prop(f'stack1/axes/axis{axis_slow}/properties/movementMode', 'PositiveStep')
                _wait_for_axis_not_busy(stack_number = stack_number,
                                        axis_number  = axis_slow)

            for f in range(0, args.fast_pixels):
                if f != 0:
                    # Move the fast axis to next pixel, wait for it to finish moving.
                    # Switch directions based on whether the slow axis is on an odd or even row
                    positioner.set_prop(f'stack1/axes/axis{axis_fast}/properties/movementMode', 'PositiveStep' if s % 2 == 0 else 'NegativeStep')
                    _wait_for_axis_not_busy(stack_number = stack_number,
                                            axis_number  = axis_fast)
                
                slow_pos = positioner.get_prop(f'stack{stack_number}/axes/axis{axis_slow}/properties/estimatedPosition')['estimatedPosition']
                fast_pos = positioner.get_prop(f'stack{stack_number}/axes/axis{axis_fast}/properties/estimatedPosition')['estimatedPosition']
                _do_experiment(slow_pixel = s,
                               fast_pixel = f,
                               slow_pos   = slow_pos,
                               fast_pos   = fast_pos)


    except KeyboardInterrupt:
        # Exit loop on ctrl-c
        pass

    # Ground all axes before exiting
    positioner.call_method(f'stack{stack_number}/card/methods/groundAllAxes()')
