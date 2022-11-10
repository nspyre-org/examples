from pulsestreamer import PulseStreamer, Sequence
import numpy as np
import time

class PS82():
    def __init__(self, ip):
        super().__init__()
        self.ps = PulseStreamer(ip)
        self.last_wfm = []

    def stream_wfm(self, wfm, wfm_onoff=1, n_runs='inf'):
        try:
            if wfm_onoff==1:
                if n_runs=='inf':
                    self.stream_channels(wfm, n_runs)
                    print(str(wfm.wfm_name) + ' ...is running for ' + str(n_runs) + ' runs.')
                else:
                    self.stream_channels(wfm, int(n_runs))
                    print(str(wfm.wfm_name) + ' ...is running for ' + str(int(n_runs)) + ' runs.')
            elif wfm_onoff==0:
                print('wfm off')
        except:
            print('warning: wfm could not be streamed, wfm not running')
            pass
        self.last_wfm = wfm

    def stream_channels(self, wfm, n_runs):

        # create new sequence
        self.sequence = self.ps.createSequence()
        this_wfm = self.sequence.getData()

        # update channels
        for key in wfm.wfm_params['ch_dict']:
            if key[0:2] == 'di':
                try:
                    pattern = wfm.wfm_params[key]['pattern']
                    # pattern = self.compress_pattern(pattern) # takes 15 ms, may be useful depending on sequence
                    self.sequence.setDigital(int(wfm.wfm_params[key]['idx']), pattern)
                except:
                    error_msg = 'error, channel: ' + str(key) + ' not loaded.'
                    print(error_msg)
            elif key[0:2] == 'an':
                try:
                    self.sequence.setAnalog(int(wfm.wfm_params[key]['idx']), wfm.wfm.wfm_params[key]['pattern'])
                except:
                    error_msg = 'error, channel: ' + str(key) + ' not loaded.'
                    print('error')
            else:
                print('wfm error: channel must be "digi" or "analog"')

        # stream
        if (n_runs == 'inf'):
            self.ps.stream(self.sequence, PulseStreamer.REPEAT_INFINITELY)
        else:
            self.ps.stream(self.sequence, n_runs)

    def stream_all_channels(self, wfm, n_runs):

        # create new sequence
        self.sequence = self.ps.createSequence()
        this_wfm = self.sequence.getData()

        # update digital channels
        try:
            self.sequence.setDigital(int(wfm.digi0['idx']), wfm.digi0['pattern'])
        except:
            print('error, digi0 not loaded')
        try:
            self.sequence.setDigital(int(wfm.digi1['idx']), wfm.digi1['pattern'])
        except:
            print('error, digi1 not loaded')
        try:
            self.sequence.setDigital(int(wfm.digi2['idx']), wfm.digi2['pattern'])
        except:
            print('error, digi2 not loaded')
        try:
            self.sequence.setDigital(int(wfm.digi3['idx']), wfm.digi3['pattern'])
        except:
            print('error, digi3 not loaded')
        try:
            self.sequence.setDigital(int(wfm.digi4['idx']), wfm.digi4['pattern'])
        except:
            print('error, digi4 not loaded')
        try:
            self.sequence.setDigital(int(wfm.digi5['idx']), wfm.digi5['pattern'])
        except:
            print('error, digi5 not loaded')
        try:
            self.sequence.setDigital(int(wfm.digi6['idx']), wfm.digi6['pattern'])
        except:
            print('error, digi6 not loaded')
        try:
            self.sequence.setDigital(int(wfm.digi7['idx']), wfm.digi7['pattern'])
        except:
            print('error, digi7 not loaded')

        # update analog channels
        try:
            self.sequence.setAnalog(int(wfm.analog0['idx']), wfm.analog0['pattern'])
        except:
            print('error, analog0 not loaded')
        try:
            self.sequence.setAnalog(int(wfm.analog1['idx']), wfm.analog1['pattern'])
        except:
            print('error, analog1 not loaded')

        # stream
        if (n_runs == 'inf'):
            self.ps.stream(self.sequence, PulseStreamer.REPEAT_INFINITELY)
        else:
            self.ps.stream(self.sequence, n_runs)

    def compress_pattern(self, pattern, ch_type='digi'):
        if ch_type == 'digi':
            for idx, val in enumerate(pattern):
                if idx == 0:
                    new_pattern = [val]
                elif idx > 0:
                    if (pattern[idx][1] == pattern[idx-1][1]):
                        new_time = pattern[idx][0] + new_pattern[-1][0]
                        new_amp = pattern[idx][1]
                        new_pattern[-1] = (new_time, new_amp)
                    else:
                        new_pattern.append(val)
        elif ch_type == 'analog':
            print('warning: "analog" channels not supported in "compress_pattern" function, returning pattern.')
            new_pattern = pattern
        else:
            print('warning, ch_type must be "digi" or "analog" in "compress_pattern" function.')

        return new_pattern
