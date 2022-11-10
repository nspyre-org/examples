#!/usr/bin/env python3
#
# Example script that demonstrates a cooldown where the platform
# temperature is controlled to a desired cooling rate.
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
    parser = argparse.ArgumentParser(description="Example script that demonstrates a cooldown with a controlled cooling rate.")
    parser.add_argument("--ip", "-i", help="The IP address of the system to control.", required=True)
    parser.add_argument('--tunnel', action='store_true', help="Communicate securely though an SSH tunnel.")

    args = parser.parse_args()

    # Setup object used to communicate with Cryostation
    cryo = scryostation.SCryostation(args.ip, tunnel=args.tunnel)

    #
    # Customize cooldown options
    #
    # Platform Bakeout
    cryo.set_platform_bakeout_enabled(False)
    #cryo.set_platform_bakeout_temperature(325)
    #cryo.set_platform_bakeout_time(10 * 60)  # 10 minutes, duration is specified in seconds
    # Purge
    cryo.set_dry_nitrogen_purge_enabled(False)
    #cryo.set_dry_nitrogen_purge_num_times(3)

    # Set desired stability target used to determine if temperature is stable
    target_stability = 0.1 # deg K
    
    # Set platform target temperature to hold at room temp for a bit,
    # to wait until we have sufficient cooling power to achieive our
    # desired cooling rate
    cryo.set_platform_target_temperature(295)

    # Initiate the cooldown
    cryo.cooldown()

    # Make sure cooldown started successfully
    time.sleep(1)
    if cryo.get_system_goal() != 'Cooldown':
        print('Failed to initiate Cooldown!')
        exit(1)
    print('Started cooldown')

    #
    # The actual temperature should change close to the desired rate,
    # but how closely it can achieve this rate will depend upon the
    # system and current PID settings.
    #
    target_base_temperature = 4 # deg K
    target_cooling_rate     = 1 # deg K/min

    # Smoothness factor can be used to adjust how often the target
    # temperature is changed. For example:
    #  0.1 = Change every 600 seconds  (Coarser incremental temperature steps)
    #  1   = Change every 60 seconds
    #  2   = Change every 30 seconds
    #  10  = Change every 6 seconds    (Finer incremental temperature steps)
    #
    #  For example:
    #     1                   2           
    #   ------               ---
    #         \                 \           
    #          \                 ---
    #           \                   \       
    #            -----               ---
    #                 \                 \   
    #                  \                 ---
    #                   \                   \
    #                    ------              ---
    #
    smoothness_factor = 10
        
    # Wait for stage 2 to cool before cooling platform
    _log(f'Waiting for sufficient cooling power before cooling platform.')
    while True:
        time.sleep(10)
        stage2_ok, stage2_temp = cryo.get_stage2_temperature()
        if stage2_ok and stage2_temp < 200:
            break

    _log(f'Moving to target base temperature of {target_base_temperature:.3f} K with rate of {target_cooling_rate:.3f} K/min.')

    curr_setpoint = cryo.get_platform_target_temperature()
    next_setpoint = curr_setpoint

    while True:
        # Calculate next setpoint by applying ramp rate, but don't
        # overshoot the target setpoint
        next_setpoint = max(next_setpoint - (target_cooling_rate / smoothness_factor), target_base_temperature)

        _log(f'  Moving to incremental setpoint of {next_setpoint:.3f} K.')
        cryo.set_platform_target_temperature(next_setpoint)

        if next_setpoint == target_base_temperature:
            break

        # Ramp rate is in K/min, so wait 1 min before moving to next incremental setpoint
        time.sleep(60 / smoothness_factor)

    #
    # Reached desired base setpoint temperature, now wait for stable
    # temperature before exiting
    #
    _log(f'Reached base temperature setpoint of {target_base_temperature:.3f} K.  Waiting for platform to stabilize, target stability is {target_stability:.3f} K.')
    cryo.set_platform_stability_target(target_stability) # deg K
    while True:
        time.sleep(10)
        if cryo.get_platform_temperature_stable():
            break
            
    _log(f'Platform is now stable at base temperature.')

if __name__ == "__main__":
    _main()
