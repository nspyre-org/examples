#!/usr/bin/env python3
#
# Example script that demonstrates a stepping the magnetic field of
# the Magneto-Optic using the SCryostation wrapper class for
# convenience.
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

def _do_experiment(setpoint):
    """Fill this function in with logic and calls to other instruments to
    perform the experiment.  This function will be called at each
    magnetic field setpoint.
    """    
    print(f'  Doing experiment at target field {setpoint} mT')
    time.sleep(10)
    
    return

def _main():    
    parser = argparse.ArgumentParser(description="Example script that does a cooldown, steps platform temperature, and then does a system warmup.")
    parser.add_argument("--ip", "-i", help="The IP address of the system to control.", required=True)
    parser.add_argument('--tunnel', action='store_true', help="Communicate securely though an SSH tunnel.")
    
    args = parser.parse_args()

    # Setup object used to communicate with Cryostation
    cryo = scryostation.SCryostation(args.ip, tunnel=args.tunnel)
        
    # List of target field setpoints we want to step through (mT)
    setpoints = [100, -100,
                 200, -200,
                 300, -300,
                 400, -400,
                 500, -500]

    # Enable magnetic field
    cryo.set_mo_enabled(True)
    
    # Step magnetic field through a series of setpoints,
    # performing experiment at each setpoint
    for sp in setpoints:
        print(f'Setting field to {sp} mT')
        cryo.set_mo_target_field(sp / 1000)  # Convert to SI units (Tesla)

        time.sleep(5)
        _do_experiment(setpoint = sp)

        # Watch for safe mode
        if cryo.get_mo_safe_mode():
            print(f'Magnet went into safe mode, aborting script!')
            exit(1)
        
    # Finished all setpoints, disable magnetic field
    cryo.set_mo_enabled(False)

    
if __name__ == "__main__":         
    _main()
