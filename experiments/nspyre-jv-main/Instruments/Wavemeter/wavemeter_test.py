# @Author: Eric Rosenthal
# @Date:   2022-07-15T11:02:29-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-22T10:51:55-07:00



# script for checking if the laser is multimode,
# pulls trace from the wavemeter and processes it
# run in command window:
# python C:\Users\Public\nspyre-jv\Instruments\Wavemeter\wavemeter_test.py

import matplotlib.pyplot as plt
import xmlrpc.client
import time
import numpy as np
import scipy.signal
import diptest
import statistics

# get data
# start = time.process_time()
channel = 1
    # channel = 1: 700-1000 nm
    # channel = 2: ~600 nm

# load saved singlemode and multimode traces for comparison (no pulling from wavemeter here, only for testing purposes)
sm_long = np.load(r'C:\Users\Public\nspyre-jv\Instruments\Wavemeter\example_patterns\sm_long.npz')
sm_short = np.load(r'C:\Users\Public\nspyre-jv\Instruments\Wavemeter\example_patterns\sm_short.npz')
sm_long = sm_long['arr_0']
sm_short = sm_short['arr_0']

mm_long = np.load(r'C:\Users\Public\nspyre-jv\Instruments\Wavemeter\example_patterns\mm_long.npz')
mm_short = np.load(r'C:\Users\Public\nspyre-jv\Instruments\Wavemeter\example_patterns\mm_short.npz')
mm_long = mm_long['arr_0']
mm_short = mm_short['arr_0']

# alternatively, load current wavemeter patterns
proxy = xmlrpc.client.ServerProxy("http://171.64.84.122:65432/")
pattern_long, pattern_short = proxy.get_pattern(channel)
#     # takes 15.6 ms to get trace from server
#     # for trace speed best not to run every data point
# mm_long = pattern_long
# mm_short = pattern_short

print('testing...')
wavelength = proxy.get_wlen(1)
print(wavelength)
plt.plot(pattern_short)


# parameters for data processing
pts_to_smooth = 10
pk_prominence = 20

# smooth out ripples
def smooth(y, box_pts=0):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

# find peaks and return distance between peaks
def get_peak_diff(y):
    peaks = scipy.signal.find_peaks(y, prominence=pk_prominence)
    return np.diff(peaks[0])

# smooth traces
sm_long_smoothed = smooth(sm_long, box_pts=pts_to_smooth)
sm_short_smoothed = smooth(sm_short, box_pts=pts_to_smooth)
mm_long_smoothed = smooth(mm_long, box_pts=pts_to_smooth)
mm_short_smoothed = smooth(mm_short, box_pts=pts_to_smooth)

# plot distributions
fig, ax = plt.subplots(2)
ax[0].plot(mm_long)
ax[0].plot(mm_long_smoothed)
ax[0].grid()
ax[1].plot(mm_short)
ax[1].plot(mm_short_smoothed)
ax[1].grid()
plt.show()

# from here work with the "short" pattern, not the "long" one
pk_diff_sm = get_peak_diff(sm_short_smoothed)
pk_diff_mm = get_peak_diff(mm_short_smoothed)

print('single mode diff between peaks:')
print(pk_diff_sm)
print('multi mode diff between peaks:')
print(pk_diff_mm)

# plot distributions
plt.hist(pk_diff_sm, label='single mode distribution')
plt.hist(pk_diff_mm, label='multi mode distribution')
plt.xlabel('pixels between peaks')
plt.ylabel('number of occurances')
plt.legend()
plt.grid()
plt.show()

# compute mean and variance of each distribution
sm_mean = statistics.mean(pk_diff_sm)
sm_var = statistics.variance(pk_diff_sm)
mm_mean = statistics.mean(pk_diff_mm)
mm_var = statistics.variance(pk_diff_mm)

print('single mode:')
print('mean = ' + str(sm_mean))
print('var = ' + str(sm_var))
print('multi mode:')
print('mean = ' + str(mm_mean))
print('var = ' + str(mm_var))

# check if distribution is single or multimode by comparing the mean to the variance
# set a threshold of variance/mean
# should be << 1 for our multimode distribution which is not centered at zero
# if below threshold return single mode, if above threshold return multimode
sm_threshold = 0.5
print('single mode threshold is set to:')
print(sm_threshold)
print('var/mean for single mode distribution:')
print(round(sm_var / sm_mean,2))
print('var/mean for multi mode distribution:')
print(round(mm_var / mm_mean,2))
