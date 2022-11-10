# @Author: Eric Rosenthal
# @Date:   2022-02-22T16:41:43-08:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-16T16:02:15-07:00



import logging
from pathlib import Path
from nspyre import inserv_cli
from nspyre import InstrumentServer

HERE = Path(__file__).parent

# create a new instrument server
with InstrumentServer() as inserv:
    # VNA
    inserv.add('vna', HERE / '../../Drivers/Keysight' / 'e5071c.py', 'E5071C', resource_name='TCPIP::171.64.84.92::inst0::INSTR')
    # voltage source
    inserv.add('vs', HERE / '../../Drivers/BK' / 'bk9129b.py', 'BK9129b', resource_name='ASRL4::INSTR')

    # run a CLI (command-line interface) that allows the user to enter commands to control the server
    inserv_cli(inserv)
