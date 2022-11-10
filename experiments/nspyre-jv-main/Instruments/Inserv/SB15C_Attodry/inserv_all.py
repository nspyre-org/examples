# @Author: Eric Rosenthal
# @Date:   2022-05-13T09:35:05-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-16T16:02:00-07:00



import logging
from pathlib import Path
from nspyre import inserv_cli
from nspyre import InstrumentServer

HERE = Path(__file__).parent

# create a new instrument server
with InstrumentServer() as inserv:
    # signal generator
    inserv.add('sg', HERE / '../../Drivers/SRS' / 'sg396.py', 'SG396', resource_name='TCPIP::171.64.85.54::inst0::INSTR')
    # pulse streamer
    inserv.add('ps', HERE / '../../Drivers/Swabian' / 'ps82.py', 'PS82', ip='171.64.84.189')
    # VNA
    inserv.add('vna', HERE / '../../Drivers/Keysight' / 'e5071c.py', 'E5071C', resource_name='TCPIP::171.64.84.92::inst0::INSTR')
    # power supply
    inserv.add('psu', HERE / '../../Drivers/Siglent' / 'siglent_psu_api.py', 'SIGLENT_PSU', ip='171.64.84.116')
    # wavemeter
    inserv.add('wm', HERE / '../../Drivers/Angstrom' / 'wavemeter.py', 'Wavemeter', ip='http://171.64.84.122:65432/')
    # m-squared laser
    # inserv.add('m2', HERE / '../../Drivers' / 'm2.py', 'Solstis', addr='171.64.84.33', port=39933)

    # run a CLI (command-line interface) that allows the user to enter commands to control the server
    inserv_cli(inserv)
