######################################################################################################
# @file PatternDemo.py
# @copyright HighFinesse GmbH.
# @version 0.1
#
# Homepage: http://www.highfinesse.com/
#

import sys
import ctypes

import matplotlib.pyplot as plt

# wlmData.dll related imports
import wlmData
import wlmConst

#########################################################
# Set the DLL_PATH variable according to your environment
#########################################################
# When using the networked wlmData.dll, put this script in the same path where you put the wlmData.dll or specify the full path.
DLL_PATH = "wlmData.dll"

# Load DLL from DLL_PATH
try:
	wlmData.LoadDLL(DLL_PATH)
except:
	sys.exit("Error: Couldn't find DLL on path %s. Please check the DLL_PATH variable!" % DLL_PATH)

# Checks the number of WLM server instance(s)
if wlmData.dll.GetWLMCount(0) == 0:
	print("There is no running wlmServer instance(s).")
else:
	# Enable pattern export.
	wlmData.dll.SetPattern(wlmConst.cSignal1Interferometers, wlmConst.cPatternEnable)
	wlmData.dll.SetPattern(wlmConst.cSignal1WideInterferometer, wlmConst.cPatternEnable)

	# Request pattern parameters (these don't change later).
	pattern_item_size_short = wlmData.dll.GetPatternItemSize(wlmConst.cSignal1Interferometers)
	pattern_item_size_long = wlmData.dll.GetPatternItemSize(wlmConst.cSignal1WideInterferometer)
	pattern_item_count_short = wlmData.dll.GetPatternItemCount(wlmConst.cSignal1Interferometers)
	pattern_item_count_long = wlmData.dll.GetPatternItemCount(wlmConst.cSignal1WideInterferometer)

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

	# Set up Matplotlib
	fig, axs = plt.subplots(2 if pattern_long else 1, 1)

	# Request pattern data.
	# If synchronization with measurements is desired, please perform this with the callback or WaitForWLMEvent mechanism.
	# If a multichannel switcher is attached, use GetPatternDataNum to distinguish different channels.
	wlmData.dll.GetPatternData(wlmConst.cSignal1Interferometers, ctypes.cast(pattern_short, ctypes.POINTER(ctypes.c_ulong)))
	if pattern_long:
		wlmData.dll.GetPatternData(wlmConst.cSignal1WideInterferometer, ctypes.cast(pattern_long, ctypes.POINTER(ctypes.c_ulong)))

	axs[0].plot(pattern_short)
	if pattern_long:
		axs[1].plot(pattern_long)
	plt.show()
