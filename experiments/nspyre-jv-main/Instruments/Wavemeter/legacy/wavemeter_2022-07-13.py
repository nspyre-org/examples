import xmlrpc.client

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
