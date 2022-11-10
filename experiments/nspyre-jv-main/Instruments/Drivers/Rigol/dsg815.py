
"""
Driver for Rigol DSG815 Function Generator
https://www.rigolna.com/products/rf-signal-generators/dsg800/
Programming guide: https://beyondmeasure.rigoltech.com/acton/attachment/1579/f-063b/1/-/-/-/-/DSG800%20Programming%20Guide.pdf
"""
import pyvisa
import time
usb_connection = "USB0::0x1AB1::0x099C::DSG8A241800119::INSTR"

class DSG815(object):
    def __init__(self, resource_name):
        rm = pyvisa.ResourceManager()
        self._inst = rm.open_resource(resource_name)

    # def conn(self, constr="USB0::0x1AB1::0x099C::DSG8A241800119::INSTR"):
    #     """Attempt to connect to instrument"""
    #     self.inst = pyvisa.Instrument(constr)
    #
    # def identify(self):
    #     """Return identify string which has serial number"""
    #     return self.inst.ask("*IDN?")

dsg815 = DSG815(usb_connection)
# test.conn("USB0::0x1AB1::0x099C::DSG8A241800119::INSTR")


# #Query:
rm = pyvisa.ResourceManager()
# rm.list_resources()
my_instrument = rm.open_resource(usb_connection)
print(my_instrument.query("*IDN?"))
