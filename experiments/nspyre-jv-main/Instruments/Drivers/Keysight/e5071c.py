# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 09:43:05 2014

@author: Seyed Iman Mirzaei, Oscar Gargiulo, Christian Schneider, David Zoepfl

Driver for ENA E5071C

v2.0.0 - CHR:
 - Adapted to Driver/Instrument structure
v2.0.1 - OSC:
    - migrated to VISA

adapted for nspyre-jv code
Eric Rosenthal, 2022-08-25
"""

import pyvisa as visa
import time
import numpy as np
from tqdm import tqdm_notebook

class E5071C():

    # def __init__(self, ip, *pars, **kwargs):
    #     rm = visa.ResourceManager()
    #     self._inst = rm.open_resource('TCPIP::{}::INSTR'.format(ip) )
    #     self.ip = ip

    def __init__(self, resource_name, *pars, **kwargs):
        rm = visa.ResourceManager()
        self._inst = rm.open_resource(resource_name)

        # Set timeout to a minute
        if 'timeout' in kwargs:
            self._inst.timeout = kwargs['timeout']
        else:
            self._inst.timeout = 60000   # Set to a minute

    def com(self, command, arg="?"):
        """Function to communicate with the device. Gives the current status
        if no arg is given"""
        if arg == "?":
            resp =  self._inst.query("{}?".format(command))
            try:
                return float(resp)
            except:
                return resp
        else:
            self._inst.write("{} {}".format(command, arg))
            return 0

    def identify(self):
        """Returns Identification String of the device"""
        str1 = '*OPT'
        return self.com(str1)

    def close(self):
        '''close connection to the instrument'''
        self._inst.close()

    def output(self, arg='?'):
        """Turns RF output power on/off
        Give no argument to query current status.

        Parameters
        -----------
        arg : int, str
            Set state to 'ON', 'OFF', 1, 0
        """
        return self.com(":OUTP", arg)

    def power(self, power='?', channel=''):
        """Set or read current power"""
        com_str = ":SOUR{}:POW:LEV:IMM:AMPL".format(channel)
        return float(self.com(com_str, power))

    def average_reset(self, channel=''):
        """Reset averages"""
        com_str = ":SENS{}:AVER:CLE".format(channel)
        return self.com(com_str, "")

    def average_count(self, count='?', channel=''):
        """Set/query number of averages"""
        com_str = ":SENS{}:AVER:COUN".format(channel)
        return int(self.com(com_str, count))

    def average_state(self, state='?', channel=''):
        """Sets/query averaging state"""
        com_str = ":SENS{}:AVER:STAT".format(channel)
        return self.com(com_str, state)

    def freq_start(self, freq='?', channel=''):
        """Set/query start frequency"""
        com_str = ":SENS{}:FREQ:STAR".format(channel)
        return float(self.com(com_str, freq))

    def freq_stop(self, freq='?', channel=''):
        """Set/query stop frequency"""
        com_str = ":SENS{}:FREQ:STOP".format(channel)
        return float(self.com(com_str, freq))

    def freq_center(self, freq='?', channel=''):
        """Set/query center frequency in Hz"""
        com_str = ":SENS{}:FREQ:CENT".format(channel)
        return float(self.com(com_str, freq))

    def freq_span(self, freq='?', channel=''):
        """Set/query span in Hz"""
        com_str = ":SENS{}:FREQ:SPAN".format(channel)
        return float(self.com(com_str, freq))

    def freq_npoints(self, points='?', channel=''):
        """Set/Query number of points"""
        com_str = ":SENS{}:SWE:POIN".format(channel)
        return int(self.com(com_str, points))

    def IFBW(self, BW='?', channel=''):
        """Set/query IF Bandwidth for specified channel"""
        com_str = ":SENS{}:BAND:RES".format(channel)
        return self.com(com_str, BW)

    def Spar(self, Par='?', trace=1):
        if type(Par) != str:
            print('Spar warning: Par must be a string')
            raise Exception('PAREXC')
        Par = Par.upper()
        if ((Par == 'S11') or (Par == 'S12') or (Par == 'S21') or
           (Par == 'S22')):
            self.com('CALC1:PAR{}:DEF'.format(trace), Par)
        elif Par == '?':
            return self.com('CALC1:PAR'+str(np.int(trace))+':DEF')
        else:
            print('No valid Par inserted')
            raise Exception('PAREXC')

    def traces_number(self, num='1', channel='1'):
        """Set number of traces"""
        com_str = "CALC{}:PAR:COUN".format(channel)
        return int(self.com(com_str, num))

    def trace_select(self, num=1, channel='1'):
        """Select trace number num"""
        self.com('CALC{}:PAR{}:SEL'.format(channel, num),'')

    def Format(self, Format='?', Trace=1):
        """Set Data Format

        Parameters
        -----------
        Format : str
            Choose from
             | 'MLOG' : magntidue in dB
             | 'PHAS': phase
             | 'MLIN': linear magnitude
             | 'REAL': real part of the complex data
             | 'IMAG' imaginary part of the complex data
             | 'UPH': Extended phase
             | 'PPH': Positive phase
             | '' (def): the format will be queried
        """
        com_str = 'CALC1:SEL:FORM'
        return self.com(com_str, Format)

    # READING data
    def freq_read(self):
        com_str = 'CALC:TRAC:DATA:XAXis'
        return self.com(com_str).split(',')

    def trace_read(self, trace=''):
        com_str = 'CALC:TRACe{}:DATA:FDATa'.format(trace)
        dat = self.com(com_str).split(',')
        return dat[0::2], dat[1::2]

    def read_settings(self):
        """Returns current state of VNA parameters as dict

        Frequency in GHz.
        """
        freq_start = self.freq_start()
        freq_stop = self.freq_stop()

        freq_span = freq_stop - freq_start
        freq_npoints = self.freq_npoints()
        BW = self.IFBW()
        Spar = self.Spar()
        format_meas = self.Format()
        power = self.power()
        output = self.output()
        avg = self.average_count()

        par = {'f_start (Hz)': freq_start,
               'f_stop (Hz)': freq_stop,
               'f_start (GHz)': freq_start*1e-9,
               'f_stop (GHz)': freq_stop*1e-9,
               'IF - BW (Hz)': BW,
               'S_parameter ': Spar,
               'Format': format_meas,
               'Span (Hz)': freq_span,
               'Points': freq_npoints,
               'power (dBm)': power,
               'output': output,
               'averages': avg,
               'averaging': self.average_state(),
               'correction': self.correction()}
        return par

    def set_settings(self, **kwargs):
        com_dict = {
                    'f_start (Hz)': self.freq_start,
                    'f_stop (Hz)': self.freq_stop,
                    'IF - BW (Hz)': self.IFBW,
                    'S_parameter ': self.Spar,
                    'Format': self.Format,
                    'Points': self.freq_npoints,
                    'power (dBm)': self.power,
                    'averaging': self.average_state,
                    'averages': self.average_count
                   }
        for k in kwargs.keys():
            try:
                com_dict[k](kwargs[k])
            except KeyError:
                pass

    def correction(self, state='?'):
        """Query or set correction status (to ON/OFF)

        Parameters
        -----------
        state : '?', 'ON', 'OFF', 1, 0
            State of correction. Use nothing or '?' for query
        """
        return self.com('SENS:CORR:STAT', state)

    def meas(self, f_range, npoints=1601, navg=1, power=-50, BW=1e3,
             Spar='S21', Format='MLOG', power_port2=False):
        """VNA Measurement for a single trace

        Parameters
        -----------
        f_range : array
            Frequency range [[f_start, f_stop]]
        npoints : int
            Number of Points
        navg : int
            Number of averages
        power : float
            VNA output power in dBm
        BW : int
            IF Bandwidth in Hz
        Spar : str
            S Parameter to measure. E.g. 'S21'
        Format : str
            Format for measurement. Choose from
             | 'MLOG' : magnitude in dB
             | 'PHAS': phase
             | 'MLIN': linear magnitude
             | 'REAL': real part of the complex data
             | 'IMAG' imaginary part of the complex data
             | 'UPH': Extended phase
             | 'PPH': Positive phase

        Returns
        --------
        np.array, np.array
            Frequencies (GHz), Data
        """
        # Check calibration and put error if HEMTs are in danger
        cal_type = self._inst.query(":SENS1:CORR:TYPE?").split(",")
        if cal_type[0] == "SOLT2" and not power_port2:
            raise Exception("Excitation on Port2. Careful with HEMTS! " +
                            "If you want to measure S22 and S12 set " +
                            "power_port2=True. This is probably due to a full 2 "+
                            "port calibration of the VNA. Please use 'Enhanced " +
                            "Calibration' of the VNA.")
        # Save currents pars
        VNA_pars = self.read_settings()
        # Set parameters
        self.IFBW(BW)
        self.freq_npoints(npoints)
        self.freq_start(f_range[0]*1e9)
        self.freq_stop(f_range[1]*1e9)
        self.power(power)
        self.Spar(Spar)
        self.Format(Format)
        if (navg == 0):
            self.average_state(0)
        else:
            self.average_state(1)
            self.average_count(navg)
            self.com(':TRIG:SEQ:AVER', 'ON')
        self.com(':TRIG:SEQ:SOUR', 'BUS')
        self.com('INIT:CONT', 'OFF')
        self.com('INIT:CONT', 'ON')
        self.average_reset()
        self.com(':STAT:OPER:PTR', '0')
        self.com(':STAT:OPER:NTR', '16')
        self.com(':STAT:OPER:ENAB', '16')
        self.com('*SRE', '128')
        self.com('*CLS','')  # Clear status byte
        # Start measurement
        self.output(1)
        self.com(':TRIG:SEQ:SINGLE','')
        # Wait for averaging
        sweep_time = self.com("SENS:SWE:TIME")
        if navg > 1:
            for i in tqdm_notebook(range(navg), unit="Sweep"):
                time.sleep(sweep_time)
        while int(self.com('*STB')) != 192:
            time.sleep(0.5)
        x = np.asarray(self.freq_read(), dtype='float')/1e9
        y = np.asarray(self.trace_read()[0], dtype='float')

        # Reset Device
        # Switch off power and return VNA to initial settings
        self.output(0)
        self.traces_number(1)
        # Removed reset of all settings since it caused confusion.
        # self.set_settings(**VNA_pars)
        self.Format(VNA_pars['Format'])
        self.com('*CLS','')
        self.com(':TRIG:AVER', 'OFF')
        self.com(':TRIG:SEQ:SOUR', 'INT')

        return x, y

    def meas_complex(self, f_range, npoints=1601, navg=1, power=-50,
                     Spar='S21', BW=1e3, power_port2=False,
                     scale="lin"):
        """Measure and save as complex voltage data format.

        Parameters
        -----------
        f_range : array
            Frequency range [[f_start, f_stop]]
        npoints : int
            Number of Points
        navg : int
            Number of averages
        power : float
            VNA output power in dBm
        Spar : str
            S Parameter to measure. E.g. 'S21'
        BW : int
            IF Bandwidth in Hz

        Returns
        --------
        np.array, np.array, np.array
            Frequencies (GHz), Real part of V, Imaginary part of V
        """
        # Check calibration and put error if HEMTs are in danger
        cal_type = self._inst.query(":SENS1:CORR:TYPE?").split(",")
        if cal_type[0] == "SOLT2" and not power_port2:
            raise Exception("Excitation on Port2. Careful with HEMTS! " +
                            "If you want to measure S22 and S21 set " +
                            "power_port2=True. Else use Enhanced " +
                            "Calibration of VNA.")

        # Save currents pars
        VNA_pars = self.read_settings()
        # Set VNA parameters
        self.IFBW(BW)
        self.freq_npoints(npoints)
        self.freq_start(f_range[0]*1e9)
        self.freq_stop(f_range[1]*1e9)
        self.power(power)
        self.output(1)
        self.Spar(Spar)
        self.traces_number(2)
        self.trace_select(1)
        self.Format('REAL')
        self.trace_select(2)
        self.Format('IMAG')
        self.Spar(Spar, 2)
        self.trace_select(1)
        if navg == 0:
            self.average_state(0)
        else:
            self.average_state(1)
            self.average_count(navg)
            self.com(':TRIG:SEQ:AVER', 'ON')

        # Set device to external Control
        self.com(':TRIG:SEQ:SOUR', 'BUS')
        self.com('INIT:CONT', 'OFF')
        self.com('INIT:CONT', 'ON')
        self.average_reset()
        # Tweaks for VNA
        self.com(':STAT:OPER:PTR', '0')
        self.com(':STAT:OPER:NTR', '16')
        self.com(':STAT:OPER:ENAB', '16')
        self.com('*SRE', '128')
        self.com('*CLS','')
        # Set electric delay to 0
        self.com("CALC:TRAC1:CORR:EDEL:TIME", 0)
        self.com("CALC:TRAC2:CORR:EDEL:TIME", 0)

        # Set scale for frequencies
        if scale.lower() == "log":
            self.com("sense:sweep:type", "log")
        else:
            self.com("sense:sweep:type", "lin")

        # Start VNA measurement
        self.com(':TRIG:SEQ:SINGLE','')

        # Wait for device
        sweep_time = self.com("SENS:SWE:TIME")
        if navg > 1:
            for i in tqdm_notebook(range(navg), unit="Sweep", leave=False):
                time.sleep(sweep_time)
        while int(self.com('*STB')) != 192:
            time.sleep(0.5)

        # Acquire data
        x = np.asarray(self.freq_read(), dtype=float)/1e9
        re = np.asarray(self.trace_read(1)[0], dtype=np.float)
        im = np.asarray(self.trace_read(2)[0], dtype=np.float)

        # Switch off power and return VNA to initial settings
        self.output(0)
        self.traces_number(1)
        # Removed reset of all settings since it caused confusion.
        # self.set_settings(**VNA_pars)
        self.Format(VNA_pars['Format'])
        self.com('*CLS','')
        self.com(':TRIG:AVER', 'OFF')
        self.com(':TRIG:SEQ:SOUR', 'INT')

        return x, re, im

    def meas_complex_segm(self, segments, navg=100, power=-50, Spar='S21',
                          BW=1e3):
        """VNA measurement with segments in complex data format.

        If optional entries in segment dictionary are not given it will take
        the overall BW and power set the arguments of this function.

        Parameters
        -----------
        segments : list
            [segment1, segment2, ...] where
            segment1 = {'start': 1, 'stop': 10, 'npoints': 1601,
                        'BW':1000 (optional), 'power': -20 (optional)}
        npoints : int
            Number of points
        navg : int
            Number of averages
        power : int, float
            RF power in dBm
        BW : int, float
            IF bandwidth
        Spar : str
            S Parameter to measure. 'S21' default
        """
        # Save currents pars
        VNA_pars = self.read_settings()
        # VNA specific string
        segment_str = '5,0,1,1,0,0,' + str(len(segments))
        # Format segments
        for d in segments:
            tmp = ','+str(d['start']*1e9)+',' + \
                str(d['stop']*1e9)+','+str(d['npoints'])
            try:
                tmp += ','+str(d['BW'])
            except KeyError:
                tmp += ','+str(BW)
            try:
                tmp += ','+str(d['power'])
            except KeyError:
                tmp += ','+str(power)
            segment_str += tmp

        self.com(':SENS:SWE:TYPE', 'SEGM')
        self.com(':SENS:SEGM:DATA', segment_str)
        self.output(1)
        self.Spar(Spar)
        self.traces_number(2)
        self.trace_select(1)
        self.Format('REAL')
        self.trace_select(2)
        self.Format('IMAG')
        self.Spar(Spar, 2)
        self.trace_select(1)
        if (navg == 0):
            self.average_state(0)
        else:
            self.average_state(1)
            self.average_count(navg)
            self.com(':TRIG:SEQ:AVER', 'ON')

        # Set electric delay to 0
        self.com("CALC:TRAC1:CORR:EDEL:TIME", 0)
        self.com("CALC:TRAC2:CORR:EDEL:TIME", 0)
        self.com(':TRIG:SEQ:SOUR', 'BUS')
        self.com('INIT:CONT', 'OFF')
        self.com('INIT:CONT', 'ON')
        self.average_reset()

        self.com(':STAT:OPER:PTR', '0')
        self.com(':STAT:OPER:NTR', '16')
        self.com(':STAT:OPER:ENAB', '16')
        self.com('*SRE', '128')
        self.com('*CLS','')

        # Start measurement and wait for averages
        self.com(':TRIG:SEQ:SINGLE','')
        while int(self.com('*STB')) != 192:
            time.sleep(0.5)

        # Receive data
        x = np.asarray(self.freq_read(), dtype='float')/1e9
        re = np.asarray(self.trace_read(1)[0], dtype='float')
        im = np.asarray(self.trace_read(2)[0], dtype='float')

        # Reset device
        self.output(0)
        # Switch off power and return VNA to initial settings
        self.traces_number(1)
        self.com('*CLS','')
        # Removed reset of all settings since it caused confusion.
        # self.set_settings(**VNA_pars)
        self.Format(VNA_pars['Format'])
        self.com(':TRIG:AVER', 'OFF')
        self.com(':TRIG:SEQ:SOUR', 'INT')
        self.com(':SENS:SWE:TYPE', 'LIN')

        return x, re, im
