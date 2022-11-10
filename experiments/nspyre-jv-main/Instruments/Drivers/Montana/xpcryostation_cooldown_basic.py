#!/usr/bin/env python3
#
# Example script that demonstrates a typical cooldown using the
# XPCryostation wrapper class for convenience.
#

import time
import datetime
import argparse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pythonlibs"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from instrument import TunnelError
import xpcryostation
import instrument

def _do_experiment(setpoint, temperature):
    """Fill this function in with logic and calls to other instruments to
    perform the experiment.  This function will be called each time
    the setpoint is reached and the temperature is stable."""
    
    print(f'  Doing experiment at setpoint {setpoint} K.  Platform temperature is {temperature:.3f} K.')
    time.sleep(10)
    
    return

def _main():    
    parser = argparse.ArgumentParser(description="Example script that does a cooldown, steps Platform temperature, and then does a system warmup.")
    parser.add_argument("--ip", "-i", help="The IP address or hostname of the system to control.", required=True)
    parser.add_argument('--tunnel', action='store_true', help="Communicate securely though an SSH tunnel.")
    
    args = parser.parse_args()

    # Setup object used to communicate with Cryostation
    cryo = xpcryostation.XPCryostation(args.ip, tunnel=args.tunnel)

    #
    # Customize cooldown options
    #
    # Bakeout
    cryo.set_platform_bakeout_enabled(True)
    cryo.set_platform_bakeout_temperature(325)
    cryo.set_platform_bakeout_time(10 * 60)  # 10 minutes, duration is specified in seconds
    # Purge
    cryo.set_sample_chamber_dry_nitrogen_purge_enabled(True)
    cryo.set_sample_chamber_dry_nitrogen_purge_num_times(3)

    # Set Platform target temperature to 0 to go to lowest base
    # temperature possible
    cryo.set_platform_target_temperature(0)

    # Initiate the cooldown
    cryo.cooldown_sample_chamber()

    # Make sure cooldown started successfully
    time.sleep(1)
    if cryo.get_sample_chamber_goal() != 'Cooldown':
        print('Failed to initiate Cooldown! Aborting script.')
        exit(1)
    print('Started cooldown')
        
    # List of Platform temperature setpoints we want to step through
    setpoints = [1.7, 2, 5, 10, 15, 20]    

    # Wait for Platform to get below first setpoint
    
    print('Waiting for system to get below first Platform setpoint')
    while True:
        time.sleep(60)
        temp_okay, temp = cryo.get_platform_temperature()
        print(f'  Current Platform temperature is {temp:.3f} K')
        if  temp_okay and temp < setpoints[0]:
            break
        
    # Step Platform through a series of setpoints, performing
    # experiment once stable at each setpoint        
    for sp in setpoints:
        print(f'Moving Platform to set-point {sp} K.')

        # Update Platform target temperature
        cryo.set_platform_target_temperature(sp)
        
        while True:
            time.sleep(10)
            temp_okay, temp   = cryo.get_platform_temperature()         # Read current Platform temperature
            stab_okay, stable = cryo.get_platform_temperature_stable()  # Read whether Platform temperature is stabilized at the setpoint
            if temp_okay and stab_okay and stable:
                _do_experiment(sp, temp)
                break # Go to next setpoint

    # Finished all setpoints, initiate warmup
    cryo.warmup_sample_chamber()

    # Wait for warmup to complete
    while True:
        time.sleep(60)
        if cryo.get_sample_chamber_goal() == 'None':
            break # Warmup finished
    
if __name__ == "__main__":         
    _main()
