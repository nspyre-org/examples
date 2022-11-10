#!/usr/bin/env python3
#
# Example script that demonstrates a typical cooldown using the
# CryoCore wrapper class for convenience.
#

import time
import datetime
import argparse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pythonlibs"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from instrument import TunnelError
import cryocore
import instrument

def _do_experiment(setpoint, temperature, stability):
    """Fill this function in with logic and calls to other instruments to
    perform the experiment.  This function will be called each time
    the setpoint is reached and the temperature is stable."""
    
    print(f'  Doing experiment at setpoint {setpoint} K, platform temperature is {temperature:.3f} K with a stability {stability:.3f} K')
    time.sleep(10)
    
    return

def _main():    
    parser = argparse.ArgumentParser(description="Example script that does a cooldown, steps platform temperature, and then does a system warmup.")
    parser.add_argument("--ip", "-i", help="The IP address of the system to control.", required=True)
    parser.add_argument('--tunnel', action='store_true', help="Communicate securely though an SSH tunnel.")
    
    args = parser.parse_args()

    # Setup object used to communicate with CryoCore
    cryo = cryocore.CryoCore(args.ip, tunnel=args.tunnel)

    #
    # Customize cooldown options
    #
    # Platform Bakeout
    cryo.set_platform_bakeout_enabled(True)
    cryo.set_platform_bakeout_temperature(325)
    cryo.set_platform_bakeout_time(10 * 60)  # 10 minutes, duration is specified in seconds
    # Purge
    cryo.set_dry_nitrogen_purge_enabled(True)
    cryo.set_dry_nitrogen_purge_num_times(3)

    # Set platform target temperature to 0 to go to lowest base
    # temperature possible
    cryo.set_platform_target_temperature(0)

    # Set desired stability target used to determine if temperature is stable below
    cryo.set_platform_stability_target(0.1)  # 100 mK

    # Initiate the cooldown
    cryo.cooldown()

    # Make sure cooldown started successfully
    time.sleep(1)
    if cryo.get_system_goal() != 'Cooldown':
        print('Failed to initiate Cooldown!')
        exit(1)
    print('Started cooldown')
        
    # List of platform temperature setpoints we want to step through
    setpoints = [5, 50, 100, 200, 300]

    # Wait for platform to get below first setpoint
    print('Waiting for platform to get below first setpoint')
    while True:
        time.sleep(60)
        temp_okay, temp = cryo.get_platform_temperature()
        print(f'  Current platform temperature is {temp:.3f} K')
        if  temp_okay and temp < setpoints[0]:
            break 

    # Step platform target temperature through a series of setpoints,
    # performing experiment once stable at each setpoint
    for sp in setpoints:
        print(f'Moving platform to set-point {sp} K')
        cryo.set_platform_target_temperature(sp)
        
        while True:
            time.sleep(10)
            platform_temp_sample = cryo.get_platform_temperature_sample() # Read current ATSM temperature sample
            temp_okay         = platform_temp_sample['temperatureOK']           
            temp              = platform_temp_sample['temperature']
            stab_okay         = platform_temp_sample['temperatureStabilityOK']
            stability         = platform_temp_sample['temperatureStability']
            stable            = platform_temp_sample['temperatureStable']

            # Wait for platform to become stable at the setpoint before doing experiment
            if temp_okay and stab_okay and stable:
                _do_experiment(setpoint    = sp,
                               temperature = temp,
                               stability   = stability)
                break # Go to next setpoint

    # Finished all setpoints, initiate warmup
    cryo.warmup()

    # Wait for warmup to complete
    while True:
        time.sleep(60)
        if cryo.get_system_goal() == 'None':
            break # Warmup finished
    
if __name__ == "__main__":         
    _main()
