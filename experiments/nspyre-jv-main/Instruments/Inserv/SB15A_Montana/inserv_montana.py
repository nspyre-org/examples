# @Author: Eric Rosenthal
# @Date:   2022-03-22T09:29:17-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-16T16:02:07-07:00



import logging
from pathlib import Path
from nspyre import inserv_cli
from nspyre import InstrumentServer

HERE = Path(__file__).parent

# create a new instrument server
with InstrumentServer() as inserv:
    # Montana Cryostat
    # name/driver path/class name/init arguments
    inserv.add('montana', HERE / '../../Drivers/Montana' / 'montana_driver.py', 'Montana', ip_addr='171.64.84.91')

    # run a CLI (command-line interface) that allows the user to enter commands to control the server
    inserv_cli(inserv)
