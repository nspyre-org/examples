# @Author: Eric Rosenthal
# @Date:   2022-06-08T13:37:25-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-16T15:41:40-07:00



import time
from lantz.core import DictFeat, Q_
from lantz.core.foreign import LibraryDriver

# from lantz.drivers import Wavemeter
from lantz.drivers.toptica.ws7Const import *
from lantz.drivers.toptica.ws7LoadDll import LoadDLL
from lantz.core import Driver

# class WS7(LibraryDriver, Wavemeter):
class WS7(Driver):
    LIBRARY_NAME = r'C:\Windows\System32\wlmData.dll'  # This must be the same file used by the Server application ("Wavelength Meter Application")
    LIBRARY_PREFIX = ''

    def __init__(self):
        super().__init__()

        self.LIBRARY_NAME

        self.lib = LoadDLL(self.LIBRARY_NAME)
        # self.lib = LoadDLL(self.lib)
        self.timeout = Q_(10, 's')
        return

    def initialize(self, devNo=None):
        pass

    def finalize(self):
        pass

    @DictFeat(keys=[1, 2, 3, 4], units='THz')
    def frequency(self, key):
        """This allows multiple retry if the signal is too high or too low
        This assumes automatic exposure mode where the signal might be adjusted over time"""
        start_time = time.time()
        while time.time() - start_time < self.timeout.to('s').m:
            ans = self.lib.GetFrequencyNum(key, 0)
            if GetFrequency_Errorvalues.has_value(ans):
                if not ans in [-3, -4]:  # Raise exception if error is not signal strength related
                    break
            else:
                return ans
        raise Exception("WS7 GetFrequency Error" + str(GetFrequency_Errorvalues(ans)))

    @DictFeat(keys=[1, 2, 3, 4], units='nm')
    def wavelength(self, key):
        """This allows multiple retry if the signal is too high or too low
        This assumes automatic exposure mode where the signal might be adjusted over time"""
        start_time = time.time()
        while time.time() - start_time < self.timeout.to('s').m:
            ans = self.lib.GetWavelengthNum(key, 0)
            if GetWavelength_Errorvalues.has_value(ans):
                if not ans in [-3, -4]:  # Raise exception if error is not signal strength related
                    break
            else:
                return ans
        raise Exception("WS7 GetFrequency Error" + str(GetWavelength_Errorvalues(ans)))

    @DictFeat(keys=[1, 2, 3, 4], units='THz')
    def raw_frequency(self, key):
        ans = self.lib.GetFrequencyNum(key, 0)
        if GetFrequency_Errorvalues.has_value(ans):
            raise Exception("WS7 GetFrequency Error" + str(GetFrequency_Errorvalues(ans)))
        else:
            return ans

    @DictFeat(keys=[1, 2, 3, 4], units='nm')
    def raw_wavelength(self, key):
        ans = self.lib.GetWavelengthNum(key, 0)
        if GetWavelength_Errorvalues.has_value(ans):
            raise Exception("WS7 GetWavelength Error" + str(GetFrequency_Errorvalues(ans)))
        else:
            return ans
