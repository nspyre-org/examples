# @Author: Eric Rosenthal
# @Date:   2022-05-13T09:33:28-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-16T16:02:03-07:00



import logging
from pathlib import Path
from nspyre import inserv_cli
from nspyre import InstrumentServer

HERE = Path(__file__).parent

# create a new instrument server
with InstrumentServer() as inserv:

    # run a CLI (command-line interface) that allows the user to enter commands to control the server
    inserv_cli(inserv)
