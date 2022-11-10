#!/usr/bin/env python3
"""
Class to simplify RESTful API communication with the xp-series Cryostation instrument.

Example usage:
 from xpcryostation import *
 cryo = XPCryostation('192.168.1.123')

 # Shows how to use high-level methods for accessing common functions
 cryo.cooldown_sample_chamber()
 cryo.set_platform_target_temperature(1.7)
 cryo.get_platform_temperature()
 cryo.get_platform_temperature_stability()
 cryo.warmup_sample_chamber()

 # Shows how to use generic post/get/put methods for accessing any REST url/end-point
 cryo.call_method('/controller/methods/sampleChamberCooldown()')
 cryo.get_prop('/sampleChamber/temperatureControllers/platform/thermometer/sample')['sample']['temperature']
 cryo.set_prop('/controller/properties/platformTargetTemperature', 1.7)
"""

import sys
import os
import instrument
import genericcryostat

Ports = instrument.Rest_Ports

@genericcryostat.register
class XPCryostation(genericcryostat.GenericCryostat):
    def __init__(self, ip, version='v1', verbose=False, tunnel=False, port=Ports.xpcryostation_hlm):
        super().__init__(ip=ip,
                         port=port,
                         version=version,
                         verbose=verbose,
                         tunnel=tunnel)

    def get_sample_chamber_goal(self):
        r = self.get_prop('/controller/properties/sampleChamberGoal')
        return r['sampleChamberGoal']

    def get_sample_chamber_state(self):
        r = self.get_prop('/controller/properties/sampleChamberState')
        return r['sampleChamberState']

    def cooldown_sample_chamber(self):
        self.call_method('/controller/methods/cooldownSampleChamber()')

    def warmup_sample_chamber(self):
        self.call_method('/controller/methods/warmupSampleChamber()')

    def vent_sample_chamber(self):
        self.call_method('/controller/methods/ventSampleChamber()')

    def pull_vacuum_sample_chamber(self):
        self.call_method('/controller/methods/pullVacuumSampleChamber()')

    def abort_sample_chamber_goal(self):
        self.call_method('/controller/methods/abortSampleChamberGoal()')

    def get_sample_chamber_pressure(self):
        r = self.get_prop('/vacuumSystem/vacuumGauges/sampleChamberPressure/properties/pressureSample')
        return r['pressureSample']['pressure']

    def set_platform_bakeout_enabled(self, enabled):
        return self.set_prop('/controller/properties/platformBakeoutEnabled', enabled)

    def set_platform_bakeout_temperature(self, temperature):
        return self.set_prop('/controller/properties/platformBakeoutTemperature', temperature)

    def set_platform_bakeout_time(self, duration):
        return self.set_prop('/controller/properties/platformBakeoutTime', duration)

    def set_sample_chamber_dry_nitrogen_purge_enabled(self, enabled):
        return self.set_prop('/controller/properties/sampleChamberDryNitrogenPurgeEnabled', enabled)

    def set_sample_chamber_dry_nitrogen_purge_num_times(self, times):
        return self.set_prop('/controller/properties/sampleChamberDryNitrogenPurgeNumTimes', times)


    def get_cooler_goal(self):
        r = self.get_prop('/controller/properties/coolerGoal')
        return r['coolerGoal']

    def get_cooler_state(self):
        r = self.get_prop('/controller/properties/coolerState')
        return r['coolerState']

    def cooldown_cooler(self):
        self.call_method('/controller/methods/cooldownCooler()')

    def warmup_cooler(self):
        self.call_method('/controller/methods/warmupCooler()')

    def abort_cooler_goal(self):
        self.call_method('/controller/methods/abortCoolerGoal()')

    def get_cooler_pressure(self):
        r = self.get_prop('/vacuumSystem/vacuumGauges/coolerPressure/properties/pressureSample')
        return r['pressureSample']['pressure']


    def get_platform_target_temperature(self):
        r = self.get_prop('/controller/properties/platformTargetTemperature')
        return r['platformTargetTemperature']

    def set_platform_target_temperature(self, target):
        return self.set_prop('/controller/properties/platformTargetTemperature', target)

    def get_platform_temperature(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/platform/thermometer/properties/sample')
        return r['sample']['temperatureOK'], r['sample']['temperature']

    def get_platform_temperature_stability(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/platform/thermometer/properties/sample')
        return r['sample']['temperatureStabilityOK'], r['sample']['temperatureStability']

    def set_platform_stability_target(self, target):
        return self.set_prop('/sampleChamber/temperatureControllers/platform/thermometer/properties/stabilityTarget', target)

    def get_platform_temperature_stable(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/platform/thermometer/properties/sample')
        return r['sample']['temperatureStabilityOK'], r['sample']['temperatureStable']

    def get_platform_temperature_sample(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/platform/thermometer/properties/sample')
        return r['sample']


    # User 1
    def set_user1_temperature_controller_enabled(self, enabled):
        return self.set_prop('/sampleChamber/temperatureControllers/user1/properties/controllerEnabled', enabled)
    
    def get_user1_target_temperature(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/user1/properties/targetTemperature')
        return r['targetTemperature']
    
    def set_user1_target_temperature(self, target):
        return self.set_prop('/sampleChamber/temperatureControllers/user1/properties/targetTemperature', target)

    def get_user1_temperature(self):
        r = self.user1_temperature_sample()
        return r['sample']['temperatureOK'], r['sample']['temperature']

    def get_user1_temperature_stable(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/user1/thermometer/properties/sample')
        return r['sample']['temperatureStabilityOK'], r['sample']['temperatureStable']

    def get_user1_temperature_stability(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/user1/thermometer/properties/sample')
        return r['sample']['temperatureStabilityOK'], r['sample']['temperatureStability']

    def get_user1_temperature_sample(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/user1/thermometer/properties/sample')
        return r['sample']

    def set_user1_stability_target(self, target):
        return self.set_prop('/sampleChamber/temperatureControllers/user1/thermometer/properties/stabilityTarget', target)


    # User 2
    def set_user2_temperature_controller_enabled(self, enabled):
        return self.set_prop('/sampleChamber/temperatureControllers/user2/properties/controllerEnabled', enabled)

    def set_user2_target_temperature(self, target):
        return self.set_prop('/sampleChamber/temperatureControllers/user2/properties/targetTemperature', target)

    def get_user2_temperature(self):
        r = self.user2_temperature_sample()
        return r['sample']['temperatureOK'], r['sample']['temperature']

    def get_user2_temperature_stable(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/user2/thermometer/properties/sample')
        return r['sample']['temperatureStabilityOK'], r['sample']['temperatureStable']

    def get_user2_temperature_stability(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/user2/thermometer/properties/sample')
        return r['sample']['temperatureStabilityOK'], r['sample']['temperatureStability']

    def get_user2_temperature_sample(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/user2/thermometer/properties/sample')
        return r['sample']

    def set_user2_stability_target(self, target):
        return self.set_prop('/sampleChamber/temperatureControllers/user2/thermometer/properties/stabilityTarget', target)
