#!/usr/bin/env python3
#
# Example script that demonstrates temperature setpoint ramping on
# the Platform.
#

import time
import datetime
import argparse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pythonlibs"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from instrument import TunnelError
import scryostation
import instrument

def _log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f'{timestamp}  {message}')

def _main():
    parser = argparse.ArgumentParser(description="Example script that steps through a series of platform setpoints while implementing a controlled temperature ramp rate.  It is expected that system is in Cooldown mode and will start from the current Platform setpoint.")
    parser.add_argument("--ip", "-i", help="The IP address of the system to control.", required=True)
    parser.add_argument('--tunnel', action='store_true', help="Communicate securely though an SSH tunnel.")

    args = parser.parse_args()

    # Setup object used to communicate with Cryostation
    cryo = scryostation.SCryostation(args.ip, tunnel=args.tunnel)

    # Make sure system is in cooldown
    time.sleep(1)
    if cryo.get_system_goal() != 'Cooldown':
        print('System not in Cooldown mode.')
        exit(1)

    #
    # List of platform temperature setpoints to step through, with
    # different stability targets at each setpoint to account for
    # non-linearity in platform stability and desired temperature ramp
    # rate used when going up and down in temperature.  The actual
    # temperature should change close to the desired rate, but how
    # closely it can achieve this rate will depend upon the system and
    # current PID settings.
    #
    # Each item in the list represents:
    #   [Temperature Setpoint (deg K), Temperature Stability (deg K), Ramp Rate (deg K/min)]
    setpoints = [
        [  10,  0.150, 0.25 ],
        [   4,  0.050, 0.25 ],
        [  10,  0.150, 0.5  ],
        [   4,  0.050, 0.5  ],
        [  10,  0.150, 1    ],
        [   4,  0.050, 1    ],
        [  10,  0.150, 2    ],
        [   4,  0.050, 2    ],
        [  10,  0.150, 3    ],
        [   4,  0.050, 3    ],
        [ 100,  0.050, 1    ],
        [   4,  0.050, 1    ],
    ]

    # Smoothness factor can be used to adjust how often the target
    # temperature is changed. For example:
    #  0.1 = Change every 600 seconds  (Coarser incremental temperature steps)
    #  1   = Change every 60 seconds
    #  2   = Change every 30 seconds
    #  10  = Change every 6 seconds    (Finer incremental temperature steps)
    #
    #  For example:   1                   2           
    #                     ------               ---
    #                    /                    /
    #                   /                  ---
    #                  /                  /
    #             -----                ---
    #            /                    /
    #           /                  ---
    #          /                  /
    #    ------                ---
    #
    smoothness_factor = 10

    for sp in setpoints:
        target_temperature = sp[0] # deg K
        target_stability   = sp[1] # deg K
        rate               = sp[2] # deg K/min
        
        _log(f'Moving to setpoint of {target_temperature:.3f} K with rate of {rate:.3f} K/min.')

        curr_setpoint = cryo.get_platform_target_temperature()
        next_setpoint = curr_setpoint

        while True:
            # Calculate next setpoint by applying ramp rate, but
            # don't overshoot the target setpoint
            if target_temperature > curr_setpoint:
                next_setpoint = min(next_setpoint + (rate / smoothness_factor), target_temperature)
            else:
                next_setpoint = max(next_setpoint - (rate / smoothness_factor), target_temperature)

            _log(f'  Moving to incremental setpoint of {next_setpoint:.3f} K.')
            cryo.set_platform_target_temperature(next_setpoint)

            if next_setpoint == target_temperature:
                break

            # Ramp rate is in K/min, so wait 1 min before moving to next incremental setpoint
            time.sleep(60 / smoothness_factor)

        #
        # Reached desired setpoint temperature, set desired stability
        # target used to determine if temperature is stable, wait for
        # stable temperature, and then wait a period for conducting
        # experiment at setpoint
        #
        _log(f'  Reached setpoint of {target_temperature} K.  Waiting for platform to stabilize at setpoint, target stability is {target_stability:.3f} K.')
        cryo.set_platform_stability_target(target_stability) # deg K
        while True:
            time.sleep(10)
            stability_ok, is_stable = cryo.get_platform_temperature_stable()
            if is_stable:
                break

        experiment_hold_time = datetime.timedelta(minutes=2)
        _log(f'  Stabilized at setpoint of {target_temperature} K.  Waiting {experiment_hold_time} to conduct experiment at setpoint.')
        time.sleep(experiment_hold_time.total_seconds())


if __name__ == "__main__":
    _main()
