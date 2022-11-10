#
# Driver file for s200 montana cryostat
#
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
import scryostation
import rook

class Montana():
    def __init__(self, ip_addr):
        # create connections
        self.cryo = scryostation.SCryostation(ip_addr)
        self.rook = rook.Rook(ip_addr)

    # Cryostat functions
    def cryo_get_temp(self): # return format (success: bool, temp: kelvin)
        return self.cryo.get_platform_temperature()
    def cryo_get_system_goal(self):
        return self.cryo.get_system_goal()
    def cryo_get_system_state(self):
        return self.cryo.get_system_state()
    def cryo_get_sc_pressure(self): # return pressure in torr
        return self.cryo.get_sample_chamber_pressure()

    def cryo_cooldown(self):
        self.cryo.cooldown()
    def cryo_warmup(self):
        self.cryo.warmup()
    def cryo_vent(self):
        self.cryo.vent()
    def cryo_pull_vacuum(self):
        self.cryo.pull_vacuum()

    # def abort_goal(self):
    #     self.call_method('/controller/methods/abortGoal()')
    #
    # def set_platform_bakeout_enabled(self, enabled):
    #     return self.set_prop('/controller/properties/platformBakeoutEnabled', enabled)
    #
    # def set_platform_bakeout_temperature(self, temperature):
    #     return self.set_prop('/controller/properties/platformBakeoutTemperature', temperature)
    #
    # def set_platform_bakeout_time(self, duration):
    #     return self.set_prop('/controller/properties/platformBakeoutTime', duration)
    #
    # def set_dry_nitrogen_purge_enabled(self, enabled):
    #     return self.set_prop('/controller/properties/dryNitrogenPurgeEnabled', enabled)
    #
    # def set_dry_nitrogen_purge_num_times(self, times):
    #     return self.set_prop('/controller/properties/dryNitrogenPurgeNumTimes', times)

    # Rook (motor) functions

if '__name__' == '__main__':
    montana = Montana(ip_addr='171.64.84.91')
