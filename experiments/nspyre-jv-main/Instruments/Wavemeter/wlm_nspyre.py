# @Author: Eric Rosenthal
# @Date:   2022-07-13T17:49:52-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-18T10:46:03-07:00



"""
Module to work with Angstrom WS7 wavelength meter
"""

import argparse
import ctypes, os, sys, random, time
import numpy as np
import wlmData
import wlmConst
import sys
import matplotlib.pyplot as plt

class WavelengthMeter:

	def __init__(self, dllpath="C:\Windows\System32\wlmData.dll", debug=False):
		"""
		Wavelength meter class.
		Argument: Optional path to the dll. Default: "C:\Windows\System32\wlmData.dll"
		"""
		self.channels = []
		self.dllpath = dllpath
		# self._interferometer_enabled = False
		self.debug = debug
		if not debug:
			self.dll = ctypes.WinDLL(dllpath)
			self.dll.GetWavelengthNum.restype = ctypes.c_double
			self.dll.GetFrequencyNum.restype = ctypes.c_double
			self.dll.GetSwitcherMode.restype = ctypes.c_long

		# self._pattern_count = self.dll.GetPatternItemCount(0)

	def GetExposureMode(self):
		if not self.debug:
			return (self.dll.GetExposureMode(ctypes.c_bool(0))==1)
		else:
			return True

	def SetExposureMode(self, b):
		if not self.debug:
			return self.dll.SetExposureMode(ctypes.c_bool(b))
		else:
			return 0

	def GetWavelength(self, channel=1):
		if not self.debug:
			return self.dll.GetWavelengthNum(ctypes.c_long(channel), ctypes.c_double(0))
		else:
			wavelengths = [460.8618, 689.2643, 679.2888, 707.2016, 460.8618*2, 0, 0, 0]
			if channel>5:
				return 0
			return wavelengths[channel-1] + channel * random.uniform(0,0.0001)

	def GetFrequency(self, channel=1):
		if not self.debug:
			return self.dll.GetFrequencyNum(ctypes.c_long(channel), ctypes.c_double(0))
		else:
			return 38434900

	def GetAll(self):
		return {
			"debug": self.debug,
			"wavelength": self.GetWavelength(),
			"frequency": self.GetFrequency(),
			"exposureMode": self.GetExposureMode()
		}

	@property
	def wavelengths(self):
		return [self.GetWavelength(i+1) for i in range(8)]

	@property
	def wavelength(self):
		return self.GetWavelength(1)

	@property
	def switcher_mode(self):
		if not self.debug:
			return self.dll.GetSwitcherMode(ctypes.c_long(0))
		else:
			return 0

	@switcher_mode.setter
	def switcher_mode(self, mode):
		if not self.debug:
			self.dll.SetSwitcherMode(ctypes.c_long(int(mode)))
		else:
			pass

	# added by Eric Rosenthal, 2022-07-13
	def get_pattern(self, channel=1):
		""" :returns: the interferometer pattern """

		# Checks the number of WLM server instance(s)
		if self.dll.GetWLMCount(0) == 0:
			print("There is no running wlmServer instance(s).")
		else:
			# Enable pattern export.
			self.dll.SetPattern(wlmConst.cSignal1Interferometers, wlmConst.cPatternEnable)
			self.dll.SetPattern(wlmConst.cSignal1WideInterferometer, wlmConst.cPatternEnable)

			# Request pattern parameters (these don't change later).
			pattern_item_size_short = self.dll.GetPatternItemSize(wlmConst.cSignal1Interferometers)
			pattern_item_size_long = self.dll.GetPatternItemSize(wlmConst.cSignal1WideInterferometer)
			pattern_item_count_short = self.dll.GetPatternItemCount(wlmConst.cSignal1Interferometers)
			pattern_item_count_long = self.dll.GetPatternItemCount(wlmConst.cSignal1WideInterferometer)

			if pattern_item_size_short == 2:
				pattern_short = (ctypes.c_int16 * pattern_item_count_short)()
			elif pattern_item_size_short == 4:
				pattern_short = (ctypes.c_int32 * pattern_item_count_short)()
			else:
				sys.exit("Unknown pattern data format")

			# More precise wavelength meters have an additional photodiode array:
			if pattern_item_size_long == 2:
				pattern_long = (ctypes.c_int16 * pattern_item_count_long)()
			elif pattern_item_size_long == 4:
				pattern_long = (ctypes.c_int32 * pattern_item_count_long)()
			else:
				pattern_long = None

			# Request pattern data.
			# If synchronization with measurements is desired, please perform this with the callback or WaitForWLMEvent mechanism.
			# If a multichannel switcher is attached, use GetPatternDataNum to distinguish different channels.
			self.dll.GetPatternDataNum(channel, wlmConst.cSignal1Interferometers, ctypes.cast(pattern_short, ctypes.POINTER(ctypes.c_ulong)))
			if pattern_long:
				self.dll.GetPatternDataNum(channel, wlmConst.cSignal1WideInterferometer, ctypes.cast(pattern_long, ctypes.POINTER(ctypes.c_ulong)))

			# # plot pattern data
			# # if plot_pattern_onoff:
			# fig, axs = plt.subplots(2 if pattern_long else 1, 1)
			# axs[0].plot(pattern_short)
			# plt.grid()
			# if pattern_long:
			# 	axs[1].plot(pattern_long)
			# 	plt.grid()
			# plt.show()

			return pattern_short, pattern_long

if __name__ == '__main__':

	# command line arguments parsing
	parser = argparse.ArgumentParser(description='Reads out wavelength values from the High Finesse Angstrom WS7 wavemeter.')
	parser.add_argument('--debug', dest='debug', action='store_const',
						const=True, default=False,
						help='runs the script in debug mode simulating wavelength values')
	parser.add_argument('channels', metavar='ch', type=int, nargs='*',
						help='channel to get the wavelength, by default all channels from 1 to 8',
						default=range(1,8))

	args = parser.parse_args()

	wlm = WavelengthMeter(debug=args.debug)

	for i in args.channels:
		print("Wavelength at channel %d:\t%.4f nm" % (i, wlm.wavelengths[i]))

	print(wlm.wavelengths[1:6:2])
	# old_mode = wlm.switcher_mode

	# wlm.switcher_mode = True

	# print(wlm.wavelengths)
	# time.sleep(0.1)
	# print(wlm.wavelengths)

	# wlm.switcher_mode = old_mode
