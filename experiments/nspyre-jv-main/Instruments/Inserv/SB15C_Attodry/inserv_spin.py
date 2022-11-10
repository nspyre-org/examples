import logging
from pathlib import Path
from nspyre import inserv_cli
from nspyre import InstrumentServer

HERE = Path(__file__).parent

# create a new instrument server
with InstrumentServer() as inserv:

    # DAQ
    inserv.add('daq', HERE / '../../Drivers/NI' / 'PCIe6321.py', 'DAQ')

    # signal generator
    inserv.add('sg0', HERE / '../../Drivers/SRS' / 'sg396.py', 'SG396', resource_name='TCPIP::171.64.85.54::inst0::INSTR')

    # signal generator
    inserv.add('sg1', HERE / '../../Drivers/SRS' / 'sg396.py', 'SG396', resource_name='TCPIP::171.64.85.37::inst0::INSTR')

    # pulse streamer
    inserv.add('ps', HERE / '../../Drivers/Swabian' / 'ps82.py', 'PS82', ip='171.64.84.189')

    # power supply
    inserv.add('psu', HERE / '../../Drivers/Siglent' / 'siglent_psu_api.py', 'SIGLENT_PSU', ip='171.64.84.116')

    # wavemeter
    inserv.add('wm', HERE / '../../Drivers/Angstrom' / 'wavemeter.py', 'Wavemeter', ip='http://171.64.84.122:65432/')

    # magnet
    inserv.add('magnet', HERE / '../../Drivers/Attocube' / 'aps100.py', 'APS100', resource_name='COM6')

    # # power meter
    # inserv.add('pm', HERE / '../../Drivers/Thorlabs' / 'pm100.py', 'PM100', resource_name='USB0::0x1313::0x8072::1919276::INSTR')

    # m-squared laser
    # inserv.add('m2', HERE / '../../Drivers' / 'm2.py', 'Solstis', addr='171.64.84.33', port=39933)

    # voltage source
    # inserv.add('vs', HERE / '../../Drivers' / 'bk9129b.py', 'BK9129b', resource_name='ASRL4::INSTR')

    # run a CLI (command-line interface) that allows the user to enter commands to control the server
    inserv_cli(inserv)
