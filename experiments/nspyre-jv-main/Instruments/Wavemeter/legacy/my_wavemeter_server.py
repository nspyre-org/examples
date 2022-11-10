from xmlrpc.server import SimpleXMLRPCServer
from wlm import *

wlm = WavelengthMeter() #initialize the wavemeter class

server = SimpleXMLRPCServer(('171.64.84.122',65432)) #initialize server
#server = SimpleXMLRPCServer(('171.64.84.122',49944)) #initialize server

#define server functions
#def get_wlen():
#    return wlm.wavelength

#get second channel wavelength
def get_wlen(channel):
    return wlm.GetWavelength(channel=channel)

server.register_function(get_wlen, "get_wlen")

#run the server loop
try:
    print('Use Control-C to exit')
    server.serve_forever()
except KeyboardInterrupt:
    print('Exiting')
