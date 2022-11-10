import sys
import numpy as np
import time
import random
from nspyre import DataSource
from nspyre import InstrumentGateway
from nspyre import ParamsWidget

import params
path_name = params.PATH_PARAMS['nspyre_path']
sys.path.insert(0,r'{}'.format(path_name))
sys.path.insert(0,r'{}\Utility\Sweeps'.format(path_name))
sys.path.insert(0,r'{}\Utility\Saving'.format(path_name))
from autosave_functions import *

class Sweep2DExample():
    def __init__(self, params):
        self.params = params.ALL
        self.print_x_progress = False
        self.print_y_progress = True
        self.c = 299792458

        self.dataset = {
            'x_label': 'x_variable', \
            'z_label': 'counts/s', \
        }

    def run(self, X, Y, Z, save_each_sweep=False):

        # define sweep parameters, including defaults if not otherwise set
        x = X.x
        y = Y.y

        try:
            x_avg = X.x_avg
        except:
            x_avg = 1
        try:
            x_label = X.x_label
        except:
            x_label = 'x_variable'
        try:
            x_pause = X.x_pause
        except:
            x_pause = self.params['pause_x']

        try:
            y_avg = Y.y_avg
        except:
            y_avg = 1
        try:
            y_label = Y.y_label
        except:
            y_label = 'y_variable'
        try:
            y_pause = Y.y_pause
        except:
            y_pause = self.params['pause_y']

        try:
            z_label = Z.z_label
        except:
            z_label = 'counts/s'

        with DataSource(self.params['data']) as data:

            print('initializing 2d sweep...')

            counts_per_s_ch0 = np.zeros(len(x))
            counts_per_s_ch0_last = np.zeros(len(x))
            counts_per_s_ch0_arr = np.zeros([len(x), len(y)])

            avg_x_counter = 0
            avg_y_counter = 0
            dataset = {
                'x':x,
                'y':y,
                'z_ch0':counts_per_s_ch0,
                'z_ch0_last':counts_per_s_ch0_last,
                'z_ch0_arr':counts_per_s_ch0_arr,
                'x_idx':0,
                'y_idx':0,
                'x_label':x_label,
                'y_label':y_label,
                'z_label':z_label,
                'avg_x_counter':avg_x_counter,
                'avg_y_counter':avg_y_counter,
                }

            if save_each_sweep == True:
                counts_per_s_ch0_all = np.zeros((len(x),x_avg))
                dataset['z_ch0_all'] = counts_per_s_ch0_all

            data.push(dataset)

            print('sweeping...')
            sweep_start_time = time.time()

            for y_idx, y_val in enumerate(y):

                # y
                Y.set_y(y_idx, y_val)
                time.sleep(y_pause)

                avg_x_counter = 0
                while avg_x_counter+1 <= x_avg:
                    for x_idx, x_val in enumerate(x):

                        # x
                        X.set_x(x_idx, x_val)

                        # record data
                        data_val = ctrs_rate = Z.get_z()

                        if avg_x_counter == 0:
                            counts_per_s_ch0[x_idx] = data_val
                        elif avg_x_counter > 0:
                            counts_per_s_ch0[x_idx] = (data_val + avg_x_counter*counts_per_s_ch0[x_idx])/(avg_x_counter+1)

                            # update 2d array
                        counts_per_s_ch0_arr[:,y_idx] = counts_per_s_ch0

                        # if avg_x_counter == 0:
                        #     counts_per_s_ch0[x_idx] = data_val
                        # elif avg_x_counter > 0:
                        #     counts_per_s_ch0[x_idx] = (data_val + avg_x_counter*counts_per_s_ch0.tolist()[x_idx])/(avg_x_counter+1)

                        # save value of last sweep, for plotting compared to average
                        counts_per_s_ch0_last[x_idx] =  data_val

                        # save the current data to the data server
                        dataset['x_idx'] = x_idx
                        dataset['avg_x_counter'] = avg_x_counter
                        if save_each_sweep == True:
                            counts_per_s_ch0_all[x_idx,avg_x_counter] = data_val

                        data.push(dataset)

                        try:
                            x_idx_10pct = round(len(x) / 10)
                        except:
                            x_idx_10pct = 1

                        if self.print_x_progress == True:
                            if x_idx_10pct > 0:
                                if x_idx % x_idx_10pct == 0:
                                    print('completed x data ' + str(x_idx+1) + ' out of ' + str(len(x)))
                            else:
                                print('completed x data ' + str(x_idx+1) + ' out of ' + str(len(x)))

                    avg_x_counter = avg_x_counter + 1
                    self.params['avg_x_counter'] = avg_x_counter
                    if x_avg > 1:
                        this_time = round(time.time() - sweep_start_time,3)
                        print('averaging ' + str(avg_x_counter) + ' of ' + str(x_avg) + ' sweeps, ' + str(this_time) + ' s')

                dataset['y_idx'] = y_idx
                dataset['avg_y_counter'] = avg_y_counter

                if self.print_y_progress == True:
                    this_time = round(time.time() - sweep_start_time,3)
                    print('completed y data ' + str(y_idx+1) + ' out of ' + str(len(y)) + ', ' + str(this_time) + ' s')

            print('sweep finished, total sweep time is: ' + str(round(time.time() - sweep_start_time,3)) + ' s')

            return dataset
