#!/usr/bin/env python
"""
Start up an instrument server and load drivers for ODMR experiments.

Author: Jacob Feder
Date: 12/27/2021
"""
import logging
from pathlib import Path

from nspyre import serve_instrument_server_cli
from nspyre import InstrumentServer
from nspyre import nspyre_init_logger

HERE = Path(__file__).parent

# log to the console as well as a file inside the logs folder
nspyre_init_logger(
    logging.INFO,
    log_path=HERE / 'logs',
    log_path_level=logging.DEBUG,
    prefix='odmr_inserv',
    file_size=10_000_000,
)

# create a new instrument server
with InstrumentServer() as inserv:
    # data acquisition instrument
    inserv.add('drv', HERE / 'drivers' / 'driver.py', 'FakeInstrument')

    # run a CLI (command-line interface) that allows the user to enter
    # commands to control the server
    serve_instrument_server_cli(inserv)
