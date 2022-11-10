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
import rook

def _do_experiment(slow_pixel, fast_pixel, slow_pos, fast_pos):
    print(f'Taking measurement: pixel={slow_pixel},{fast_pixel}  position={slow_pos},{fast_pos}')
    time.sleep(1)

def _wait_for_axis_not_moving(axis):
    axis_moving = True
    while axis_moving:
        time.sleep(0.1)
        axis_moving = rook.get_axis_moving(axis)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
    """
    Customer example demonstrating how to perform a 2-axis raster scan.

    Example:
    python rook_rasterscan.py --ip 192.168.1.123 --slow-axis 2 --fast-axis 1 --slow-stepsize 0.0001 --fast-stepsize 0.0001 --slow-pixels 5 --fast-pixels 10
    """,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--ip", help="The IP address of the system to control.", required=True)
    parser.add_argument("--fast-axis", help="The number of the fast axis.", required=True, type=int, choices=range(1,5))
    parser.add_argument("--slow-axis", help="The number of the slow axis.", required=True, type=int, choices=range(1,5))
    parser.add_argument("--fast-stepsize", help="The step size (m) to take each time the fast axis is moved.", required=True, type=float)
    parser.add_argument("--slow-stepsize", help="The step size (m) to take each time the slow axis is moved.", required=True, type=float)
    parser.add_argument("--fast-pixels", help="The number of pixels for the fast axis.", required=True, type=int)
    parser.add_argument("--slow-pixels", help="The number of pixels for the slow axis.", required=True, type=int)
    args = parser.parse_args()

    print("Connecting to remote system at %s" % (args.ip))
    rook = rook.Rook(args.ip)

    try:
        for s in range(0, args.slow_pixels):
            if s != 0:
                # Move the slow axis to next pixel, wait for it to finish moving
                rook.move_axis_relative_position(axis      = args.slow_axis,
                                                 step_size = args.slow_stepsize)
                _wait_for_axis_not_moving(axis = args.slow_axis)

            for f in range(0, args.fast_pixels):
                if f != 0:
                    # Move the fast axis to next pixel, wait for it to finish moving.
                    # Switch directions based on whether the slow axis is on an odd or even row
                    rook.move_axis_relative_position(axis      = args.fast_axis,
                                                     step_size = (1 if s % 2 == 0 else -1) * args.fast_stepsize)
                    _wait_for_axis_not_moving(axis = args.fast_axis)
                
                slow_pos = rook.get_axis_encoder_position(axis = args.slow_axis)
                fast_pos = rook.get_axis_encoder_position(axis = args.fast_axis)
                _do_experiment(slow_pixel = s,
                               fast_pixel = f,
                               slow_pos   = slow_pos,
                               fast_pos   = fast_pos)


    except KeyboardInterrupt:
        # Exit loop on ctrl-c
        pass

