# @Author: Eric Rosenthal
# @Date:   2022-07-13T14:45:59-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-18T16:30:04-07:00



import xmlrpc.client
import matplotlib.pyplot as plt
import scipy.signal
import numpy as np
import statistics

class Wavemeter():

    # in order to initialize, need to be running the wavemeter server
    # instructions:
    #   open a new cmder terminal on the old attodry computer
    #   go to Desktop\wavemeter_python_server\py-ws7-master
    #   run the command: python my_wavemeter_server.py
    #   after doing so, the following commands will connect to the wavemeter and read a wavelength:
    #       import xmlrpc.client
    #       proxy = xmlrpc.client.ServerProxy("http://171.64.84.122:65432/")
    #       print(proxy.get_wlen(2))

    def __init__(self, ip):
        super().__init__()
        self.wm = xmlrpc.client.ServerProxy("http://171.64.84.122:65432/")
        return

    def get_wavelength(self, channel=2):
        wavelength = self.wm.get_wlen(channel)
        return wavelength

    def get_frequency(self, channel=2):
        wavelength = self.wm.get_wlen(channel)
        c = 3e8
        f = c / wavelength
        return f

    def get_pattern_short(self, channel=2):
        pattern_short, pattern_long = self.wm.get_pattern(channel)
        return pattern_short

    def get_pattern_long(self, channel=2):
        pattern_short, pattern_long = self.wm.get_pattern(channel)
        return pattern_long

    def plot_pattern(self, pattern):
        plt.plot(pattern)
        plt.title('interferometer')
        plt.grid()
        plt.show()

    def smooth_pattern(self, y, box_pts=1):
        box = np.ones(box_pts)/box_pts
        y_smooth = np.convolve(y, box, mode='same')
        return y_smooth

    # find peaks and return distance between peaks
    def get_peak_diff(self, y, pk_prominence=5):
        peaks = scipy.signal.find_peaks(y, prominence=pk_prominence)
        return np.diff(peaks[0])

    def check_single_mode(self, channel=2, sm_threshold=0.2, pattern_type='short', pts_to_smooth=5, pk_prominence=10, plot_pattern_onoff=0):

        # acquire pattern
        if pattern_type=='short':
            pattern = np.array(self.get_pattern_short(channel))
        elif pattern_type=='long':
            pattern = np.array(self.get_pattern_long(channel))
        else:
            print('error: pattern must be "long" or "short"')
            pattern = []

        # smooth pattern
        pattern_smoothed = self.smooth_pattern(pattern, pts_to_smooth)

        # get difference between peaks
        pk_diff = self.get_peak_diff(pattern_smoothed, pk_prominence)

        # compute statistics on the distribution of different lengths between the peaks
        pk_diff_mean = statistics.mean(pk_diff)
        pk_diff_var = statistics.variance(pk_diff)

        # make a determination about if singlemode or multimode
        pk_diff_ratio = pk_diff_var / pk_diff_mean
        if pk_diff_ratio > sm_threshold:
            print('warning: multimode operation detected, var/mean = ' + str(round(pk_diff_ratio,2)) + ', threshold = ' + str(sm_threshold))
            singlemode_status = False
        else:
            print('wavemeter single mode check successful')
            singlemode_status = True

        return singlemode_status, pattern
