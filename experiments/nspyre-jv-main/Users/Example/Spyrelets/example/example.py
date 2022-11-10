import time
import json
import numpy as np
import random
from nspyre import DataSource
from nspyre import InstrumentGateway
from nspyre import ParamsWidget
from pulsestreamer import PulseStreamer, Sequence
import xmlrpc.client
import matplotlib.pyplot as plt
from importlib import reload
import sys

from importlib.machinery import SourceFileLoader
params = SourceFileLoader('params',r'C:\Users\Public\nspyre-jv\Users\Example\Spyrelets\example\params.py').load_module()

# import params
path_name = params.PATH_PARAMS['nspyre_path']
sys.path.insert(0,r'{}\Utility\Sweeps'.format(path_name))
sys.path.insert(0,r'{}\Utility\Saving'.format(path_name))
from Sweep1DExample import Sweep1DExample
from Sweep2DExample import Sweep2DExample
from autosave_functions import *
from autoplot_functions import *

class RandomVsTime():
    def __init__(self):
        self.params = params.ALL

    def sweep_1d(self):
        # sweep
        with InstrumentGateway() as gw:

            class X():
                x = np.linspace(self.params['x_min'],self.params['x_max'],self.params['num_x'])
                x_avg = self.params['x_avg']
                x_label = 'x variable (units)'
                def set_x(x_idx=0, x_val=0):
                    time.sleep(self.params['pause_x'])

            class Z():
                z_label='z variable (units)'
                def get_z():
                    return random.randint(-100,100)

            # run scan
            dataset = Sweep1DExample(params).run(X,Z)

            # save data
            filename = autosave_data(str(self.__class__.__name__), self.params, dataset)
            autoplot_sweep1d(filename)

    def sweep_2d(self):

        # sweep
        with InstrumentGateway() as gw:

            class X():
                x = np.linspace(self.params['x_min'],self.params['x_max'],self.params['num_x'])
                x_avg = self.params['x_avg']
                x_label = 'x variable (units)'
                def set_x(x_idx=0, x_val=0):
                    time.sleep(self.params['pause_x'])

            class Y():
                y = np.linspace(self.params['y_min'],self.params['y_max'],self.params['num_y'])
                y_avg = self.params['y_avg']
                y_label = 'y variable (units)'
                def set_y(y_idx=0, y_val=0):
                    time.sleep(self.params['pause_y'])

            class Z():
                z_label='z variable (units)'
                def get_z():
                    return random.randint(-100,100)

            # run scan
            dataset = Sweep2DExample(params).run(X,Y,Z)

            # save data
            filename = autosave_data(str(self.__class__.__name__), self.params, dataset)
            autoplot_sweep2d(filename)
