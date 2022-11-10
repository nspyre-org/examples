#!/usr/bin/env python3
#
"""
Class to simplify RESTful API communication with the CryoCore instrument.

Example usage:
 import cryocore
 cryo = cryocore.CryoCore('192.168.1.123')

 # Shows how to use high-level methods for accessing common functions
 cryo.cooldown()
 cryo.set_platform_target_temperature(3.1)
 cryo.get_platform_temperature()
 cryo.get_platform_temperature_stability()
 cryo.warmup()

 # Shows how to use generic post/get/put methods for accessing any REST url/end-point
 cryo.call_method('/controller/methods/cooldown()')
 cryo.get_prop('/sampleChamber/temperatureControllers/platform/thermometer/sample')['sample']['temperature']
 cryo.set_prop('/controller/properties/platformTargetTemperature', 1.7)
"""
import sys
import os
import instrument
import genericcryostat

Ports = instrument.Rest_Ports


@genericcryostat.register
class CryoCore(genericcryostat.GenericCryostat):
    def __init__(self, ip, version='v1', verbose=False, tunnel=False, port=Ports.cryocore_hlm):
        super().__init__(ip=ip,
                         port=port,
                         version=version,
                         verbose=verbose,
                         tunnel=tunnel)

    def cooldown(self):
        self.call_method('/controller/methods/cooldown()')

    def warmup(self):
        self.call_method('/controller/methods/warmup()')

    def vent(self):
        self.call_method('/controller/methods/vent()')

    def pull_vacuum(self):
        self.call_method('/controller/methods/pullVacuum()')

    def abort_goal(self):
        self.call_method('/controller/methods/abortGoal()')

    def get_system_goal(self):
        return self.get_prop('/controller/properties/systemGoal')['systemGoal']

    def get_system_state(self):
        return self.get_prop('/controller/properties/systemState')['systemState']

    def get_sample_chamber_pressure(self):
        return self.get_prop('/vacuumSystem/vacuumGauges/sampleChamberPressure/properties/pressureSample')['pressureSample']['pressure']

    def set_platform_bakeout_enabled(self, enabled):
        return self.set_prop('/controller/properties/platformBakeoutEnabled', enabled)

    def set_platform_bakeout_temperature(self, temperature):
        return self.set_prop('/controller/properties/platformBakeoutTemperature', temperature)

    def set_platform_bakeout_time(self, duration):
        return self.set_prop('/controller/properties/platformBakeoutTime', duration)

    def set_dry_nitrogen_purge_enabled(self, enabled):
        return self.set_prop('/controller/properties/dryNitrogenPurgeEnabled', enabled)

    def set_dry_nitrogen_purge_num_times(self, times):
        return self.set_prop('/controller/properties/dryNitrogenPurgeNumTimes', times)

    #
    # Vent methods
    #
    def set_vent_continuously_enabled(self, enabled):
        return self.set_prop('/controller/properties/ventContinuouslyEnabled', enabled)

    #
    # Pull Vacuum methods
    #
    def set_pull_vacuum_target_pressure(self, target):
        return self.set_prop('/controller/properties/pullVacuumTargetPressure', target)

    #
    # Stage1 methods
    #
    def get_stage1_temperature_sample(self):
        r = self.get_prop('/cooler/temperatureControllers/stage1/thermometer/properties/sample')
        return r['sample']

    def get_stage1_temperature(self):
        r = self.get_prop('/cooler/temperatureControllers/stage1/thermometer/properties/sample')
        return r['sample']['temperatureOK'], r['sample']['temperature']


    #
    # Stage2 methods
    #
    def get_stage2_temperature_sample(self):
        r = self.get_prop('/cooler/temperatureControllers/stage2/thermometer/properties/sample')
        return r['sample']

    def get_stage2_temperature(self):
        r = self.get_prop('/cooler/temperatureControllers/stage2/thermometer/properties/sample')
        return r['sample']['temperatureOK'], r['sample']['temperature']

    #
    # Platform methods
    #
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

    def get_platform_heater_sample(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/platform/heater/properties/sample')
        return r['sample']

    #
    # User1 methods
    #
    def get_user1_temperature_sample(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/user1/thermometer/properties/sample')
        return r['sample']

    def get_user1_temperature(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/user1/thermometer/properties/sample')
        return r['sample']['temperatureOK'], r['sample']['temperature']

    def get_user1_temperature_stability(self):
        r = self.get_prop('/sampleChamber/temperatureControllers/user1/thermometer/properties/sample')
        return r['sample']['temperatureStabilityOK'], r['sample']['temperatureStability']
    
