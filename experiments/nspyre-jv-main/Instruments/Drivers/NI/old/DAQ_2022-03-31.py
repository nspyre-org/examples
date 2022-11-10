"""
DAQ control based off of nspyre documentation, for more info see:
https://nidaqmx-python.readthedocs.io/en/latest/_modules/nidaqmx/_task_modules/ci_channel_collection.html#CIChannelCollection.add_ci_count_edges_chan
Hope Lee and Eric Rosenthal, 3/22/2022
"""

import nidaqmx
from nidaqmx.constants import (AcquisitionType, CountDirection, Edge, READ_ALL_AVAILABLE, TaskMode, TriggerType)
from nidaqmx.stream_readers import CounterReader
import numpy as np

class DAQ():
    def __init__(self, DAQ_PARAMS):

        self.DAQ_PARAMS = DAQ_PARAMS
        # self.DAQ_PARAMS = self.specify_DAQ_params(DAQ_PARAMS)

        # print('testing DAQ...')
        print(self.DAQ_PARAMS['ctrs_pfis'][0]['ctr_name'])

        # self.di_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][0]['port_name']
        # self.ci_count_edges_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][0]['ctr_name']
        # self.ci_count_read_name = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][0]['pfi_name']

        # print('DAQ params we have named')
        # print(self.di_chan_name)
        # print(self.ci_count_edges_chan_name)
        # print(self.ci_count_read_name)

    def get_counts(self, ctr_number=0):

        self.di_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number]['port_name']
        self.ci_count_edges_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number]['ctr_name']
        self.ci_count_read_name = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number]['pfi_name']

        with nidaqmx.Task() as read_task, nidaqmx.Task() as samp_clk_task:

            samp_clk_task.di_channels.add_di_chan(self.di_chan_name)
            samp_clk_task.timing.cfg_samp_clk_timing(rate=self.DAQ_PARAMS['sampling_rate'],
                                            sample_mode=AcquisitionType.CONTINUOUS)
            samp_clk_task.control(TaskMode.TASK_COMMIT)
            read_task.ci_channels.add_ci_count_edges_chan(
                                        self.ci_count_edges_chan_name,
                                        edge=Edge.RISING,
                                        initial_count=0,
                                        count_direction=CountDirection.COUNT_UP)

            read_task.ci_channels.all.ci_count_edges_term = self.ci_count_read_name
            read_task.timing.cfg_samp_clk_timing(self.DAQ_PARAMS['sampling_rate'], source= '/' + self.DAQ_PARAMS['dev_name'] + '/di/SampleClock',
                active_edge=Edge.RISING, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

            read_task.in_stream.input_buf_size = self.DAQ_PARAMS['buffer_size']
            reader = CounterReader(read_task.in_stream)
            samp_clk_task.start()
            read_task.start()
            data_array = np.zeros(self.DAQ_PARAMS['buffer_size'], dtype=np.uint32)

            return read_task.read()

    def get_counts_2ctrs(self, ctr_number=0):

        self.di_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number]['port_name']
        self.ci_count_edges_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number]['ctr_name']
        self.ci_count_read_name = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number]['pfi_name']

        with nidaqmx.Task() as read_task, nidaqmx.Task() as samp_clk_task:

            samp_clk_task.di_channels.add_di_chan(self.di_chan_name)
            samp_clk_task.timing.cfg_samp_clk_timing(rate=self.DAQ_PARAMS['sampling_rate'],
                                            sample_mode=AcquisitionType.CONTINUOUS)
            samp_clk_task.control(TaskMode.TASK_COMMIT)
            read_task.ci_channels.add_ci_count_edges_chan(
                                        self.ci_count_edges_chan_name,
                                        edge=Edge.RISING,
                                        initial_count=0,
                                        count_direction=CountDirection.COUNT_UP)

            read_task.ci_channels.all.ci_count_edges_term = self.ci_count_read_name
            read_task.timing.cfg_samp_clk_timing(self.DAQ_PARAMS['sampling_rate'], source= '/' + self.DAQ_PARAMS['dev_name'] + '/di/SampleClock',
                active_edge=Edge.RISING, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

            read_task.in_stream.input_buf_size = self.DAQ_PARAMS['buffer_size']
            reader = CounterReader(read_task.in_stream)
            samp_clk_task.start()
            read_task.start()
            data_array = np.zeros(self.DAQ_PARAMS['buffer_size'], dtype=np.uint32)

            return read_task.read(), read_task.read()

    # def specify_DAQ_params(self, DAQ_PARAMS):
    #     # set default parameters if none are defined in DAQ_PARAMS
    #
    #     # default sampling_rate
    #     try:
    #         DAQ_PARAMS['sampling_rate']
    #     except:
    #         DAQ_PARAMS['sampling_rate'] = 100
    #     # default buffer_size
    #     try:
    #         DAQ_PARAMS['buffer_size']
    #     except:
    #         DAQ_PARAMS['buffer_size'] = 12000
    #     # default port_name
    #     try:
    #         DAQ_PARAMS['port_name']
    #     except:
    #         DAQ_PARAMS['port_name'] = 'port0'
    #     # default ctr_name
    #     try:
    #         DAQ_PARAMS['ctr_name']
    #     except:
    #         DAQ_PARAMS['ctr_name'] = 'ctr0'
    #     # default ch_name
    #     try:
    #         DAQ_PARAMS['ch_name']
    #     except:
    #         DAQ_PARAMS['ch_name'] = 'PFI12'
    #     # default dev_name
    #     try:
    #         DAQ_PARAMS['dev_name']
    #     except:
    #         DAQ_PARAMS['dev_name'] = 'Dev1'
    #
    #     return DAQ_PARAMS
