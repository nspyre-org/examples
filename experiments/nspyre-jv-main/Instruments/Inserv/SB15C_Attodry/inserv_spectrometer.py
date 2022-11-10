# @Author: Eric Rosenthal
# @Date:   2022-05-16T17:13:27-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-16T16:02:12-07:00



import logging
from pathlib import Path
from nspyre import inserv_cli
from nspyre import InstrumentServer

HERE = Path(__file__).parent

# create a new instrument server
with InstrumentServer() as inserv:
    # spectrometer
    inserv.add('andor_ccd', HERE / '../../Drivers/Andor' / 'andor_ccd.py', 'CCD')


    # # spectrometer
    # inserv.add('andor', HERE / '../Drivers/Andor' / 'andor.py', 'E5071C', resource_name='TCPIP::171.64.84.92::inst0::INSTR')
    # # spectrometer
    # inserv.add('ccd', HERE / '../Drivers/Andor' / 'ccd.py', 'E5071C', resource_name='TCPIP::171.64.84.92::inst0::INSTR')

    # run a CLI (command-line interface) that allows the user to enter commands to control the server
    inserv_cli(inserv)
