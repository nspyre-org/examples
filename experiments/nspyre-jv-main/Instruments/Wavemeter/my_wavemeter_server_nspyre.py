# @Author: Eric Rosenthal
# @Date:   2022-07-13T17:49:26-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-22T10:51:49-07:00



from xmlrpc.server import SimpleXMLRPCServer
from wlm_nspyre import *
import ctypes
from ctypes.util import find_library
import matplotlib.pyplot as plt
import numpy as np

wlm = WavelengthMeter() #initialize the wavemeter class

server = SimpleXMLRPCServer(('171.64.84.122',65432),allow_none=True) #initialize server
#server = SimpleXMLRPCServer(('171.64.84.122',49944)) #initialize server

#get wavelength
def get_wlen(channel):
	return wlm.GetWavelength(channel=channel)

def get_pattern(channel):
	# get pattern
	pattern_short, pattern_long = wlm.get_pattern(channel=channel)

	# convert from c_type pointer to numpy array
	pattern_short_arr = np.ctypeslib.as_array(pattern_short)
	pattern_long_arr = np.ctypeslib.as_array(pattern_long)

	return pattern_short_arr.tolist(), pattern_long_arr.tolist()

server.register_function(get_wlen, "get_wlen")
server.register_function(get_pattern, "get_pattern")

#run the server loop
try:
	print('Use Control-C to exit')
	server.serve_forever()
except KeyboardInterrupt:
	print('Exiting')
