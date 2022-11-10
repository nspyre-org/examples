"""
DAQ control based off of nspyre documentation, for more info see:
https://nidaqmx-python.readthedocs.io/en/latest/_modules/nidaqmx/_task_modules/ci_channel_collection.html#CIChannelCollection.add_ci_count_edges_chan
Hope Lee and Eric Rosenthal, 3/22/2022
"""

import nidaqmx
from nidaqmx.constants import (AcquisitionType, CountDirection, Edge, READ_ALL_AVAILABLE, TaskMode, TriggerType)
from nidaqmx.stream_readers import CounterReader
import numpy as np
import time

class DAQ():
    def __init__(self, PARAMS):
        # set sampling parameters
        print('setting sampling params...')
        self.DAQ_PARAMS = PARAMS

        # print('working channel names...')
        # di_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][0]['port_name']
        # ci_count_edges_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][0]['ctr_name']
        # ci_count_read_name = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][0]['pfi_name']
        # print(di_chan_name)
        # print(ci_count_edges_chan_name)
        # print(ci_count_read_name)

        # self.initialize()

    def initialize(self):

        # points = round(self.DAQ_PARAMS['sampling_rate'] * self.DAQ_PARAMS['averaging_time'])
        # self.rate = sampling_rate.to('Hz').m
        # self.buffer_size = int(points)

        self.DAQ_PARAMS['real_point_time'] = (self.DAQ_PARAMS['buffer_size']-1)/self.DAQ_PARAMS['sampling_rate']
        system = nidaqmx.system.System.local()
        sys_device = system.devices[self.DAQ_PARAMS['dev_name']]

        # set up sample clock task at port0, when this clock ticks, data is read from the counter channel
        clk_channel = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][0]['port_name'] # 'port0'
        self.samp_clk_task = nidaqmx.Task()
        self.samp_clk_task.di_channels.add_di_chan(clk_channel)
        self.samp_clk_task.timing.cfg_samp_clk_timing(
                                self.DAQ_PARAMS['sampling_rate'],
                                sample_mode=AcquisitionType.CONTINUOUS,
                                samps_per_chan=self.DAQ_PARAMS['buffer_size']
        )
        self.samp_clk_task.control(TaskMode.TASK_COMMIT)

        # the previous line gives this error:
        # Status Code: -50103
        # C:\Users\ericr\miniconda3\envs\nsp\lib\site-packages\nidaqmx\task.py:97: ResourceWarning: Task of name "_unnamedTask<0>" was not explicitly closed before it was destructed. Resources on the task device may still be reserved.
        #   warnings.warn(

        clk_src = '/' + self.DAQ_PARAMS['dev_name'] + '/di/SampleClock'

        # set up read channels and stream readers for all channels
        self.read_tasks = []
        self.readers = []
        self.n_chan = 0

        for ch_idx, key in enumerate(self.DAQ_PARAMS['ctrs_pfis']):
            dev_channel = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][key]['ctr_name'] #channel

            # set up read task counter channel
            self.read_tasks.append(nidaqmx.Task())
            self.read_tasks[ch_idx].ci_channels.add_ci_count_edges_chan(
                                    dev_channel,
                                    edge=Edge.RISING,
                                    initial_count=0,
                                    count_direction=CountDirection.COUNT_UP
            )

            # this is superfluous if the PFI channels are the default options
            # pfi_channel = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][key]['ctr_name'] # ctrs_pfis[channel]
            pfi_channel = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][key]['pfi_name'] # ctrs_pfis[channel]

            self.read_tasks[ch_idx].ci_channels.all.ci_count_edges_term = pfi_channel

            # set up read_task timing and triggering off the sample clock
            self.read_tasks[ch_idx].timing.cfg_samp_clk_timing(
                                    self.DAQ_PARAMS['sampling_rate'],
                                    source=clk_src,
                                    sample_mode=AcquisitionType.CONTINUOUS
            )
            self.read_tasks[ch_idx].in_stream.input_buf_size = self.DAQ_PARAMS['buffer_size']
            self.read_tasks[ch_idx].triggers.arm_start_trigger.trig_type = TriggerType.DIGITAL_EDGE
            self.read_tasks[ch_idx].triggers.arm_start_trigger.dig_edge_edge = Edge.RISING
            self.read_tasks[ch_idx].triggers.arm_start_trigger.dig_edge_src = clk_src

            self.readers.append(CounterReader(self.read_tasks[ch_idx].in_stream))
            self.read_tasks[ch_idx].start()

        # set up data array to dump read buffer into
        self.data_array = np.zeros((self.DAQ_PARAMS['buffer_size']), dtype=np.uint32)
        self.n_chan = len(self.DAQ_PARAMS['ctrs_pfis']) #self.DAQ_PARAMS['ctrs_pfis'] # channels.__len__()

    def read_counts(self):
        self.samp_clk_task.start() # takes about 1 ms
        d_ctrs = np.zeros(self.n_chan)

        for ch_idx, reader in enumerate(self.readers):


            # print('testing read_tasks...')
            # d_ctrs_test = self.read_tasks
            # print(d_ctrs_test)

            # print('timing read_tasks...')
            # print(ch_idx)
            # print(self.read_tasks[ch_idx])
            start_t = time.time()
            d_ctrs[ch_idx] = self.read_tasks[ch_idx].read()
            print(d_ctrs)
                    # takes 3 ms per channel, for 1 ms acquire time
                    # for 1 s acquire time, takes 1 s on first sweep, then 2 s on subsequent sweeps!!!!!
                    # same behavior as we change the acquire time!!!!!!
                    # not sure exactly what's going on, but very time inefficient!!! maybe we can improve somehow
            end_t = time.time()
            # print(str((end_t - start_t)*1e3) + ' ms')

            self.read_tasks[ch_idx].stop()

        # set counts to return
        # print(d_ctrs)
        ctrs_rate = d_ctrs # / self.DAQ_PARAMS['real_point_time']
        self.samp_clk_task.stop()

        return ctrs_rate

    def read_counts2(self,P):
        time_per_point = P['averaging_time']
        buffer_size = P['buffer_size']

        # self.samp_clk_task.start()
        d_ctrs = np.zeros(self.n_chan)

        for ch_idx, reader in enumerate(self.readers):
            print('testing read_counts2...')
            print(ch_idx)
            print(self.readers[ch_idx])

            # if self.channels[ii] != 'none':
            num_samps = self.readers[ch_idx].read_many_sample_uint32(
                    self.data_array,
                    number_of_samples_per_channel = self.DAQ_PARAMS['buffer_size']
            )
            if num_samps < self.buffer_size:
                print('something wrong: buffer issue')
                return
            d_ctrs[ch_idx] = self.data_array[-1] - self.data_array[0]

        ctrs_rate = d_ctrs / self.DAQ_PARAMS['averaging_time']

        # self.samp_clk_task.stop()
        return ctrs_rate

        # for ch_idx, reader in enumerate(self.readers):
        #     d_ctrs[ch_idx] = self.read_tasks[ch_idx].read()
        #     print('yay!')
        #     print(ch_idx)
        #     num_samps = self.readers[ch_idx].read_many_sample_uint32(
        #             self.data_array,
        #             number_of_samples_per_channel=self.DAQ_PARAMS['buffer_size']
        #     )
        #     print('testing yay!!')
        #     if num_samps < self.DAQ_PARAMS['buffer_size']:
        #         print('something wrong: buffer issue')
        #         return
        #     d_ctrs[ch_idx] = self.data_array[-1] - self.data_array[0]

        # for ii,reader in enumerate(self.readers):
        #     if self.channels[ii] != 'none':
        #         num_samps = self.readers[ii].read_many_sample_uint32(
        #                 self.data_array,
        #                 number_of_samples_per_channel=self.buffer_size
        #         )
        #         if num_samps < self.buffer_size:
        #             print('something wrong: buffer issue')
        #             return
        #         d_ctrs[ii] = self.data_array[-1] - self.data_array[0]

        # d_ctrs[0] = self.read_tasks[0].read()
        # d_ctrs[1] = self.read_tasks[1].read()

            # try this next:
            # self.samp_clk_task.start()
            # self.read_tasks[ch_idx].start()
            # data_array = np.zeros(self.DAQ_PARAMS['buffer_size'], dtype=np.uint32)

            # return read_task.read()


            # # from BaseDAQ
            # # if self.channels[ch_idx] != 'none':
            # num_samps = self.readers[ch_idx].read_many_sample_uint32(
            #         self.data_array,
            #         number_of_samples_per_channel=self.DAQ_PARAMS['buffer_size']
            # )
            # if num_samps < self.DAQ_PARAMS['buffer_size']:
            #     print('something wrong: buffer issue')
            #     return
            # d_ctrs[ch_idx] = self.data_array[-1] - self.data_array[0]


            # worked before in get_counts
            # reader = CounterReader(read_task.in_stream)
            # samp_clk_task.start()
            # read_task.start()
            # data_array = np.zeros(self.DAQ_PARAMS['buffer_size'], dtype=np.uint32)
            #
            # return read_task.read()

        # ctrs_rate = d_ctrs / self.real_point_time
        # self.samp_clk_task.stop()
        # return ctrs_rate

    def finalize(self):
        for ch_idx, read_task in enumerate(self.read_tasks):
            # self.read_tasks[ch_idx].stop()
            self.read_tasks[ch_idx].close()
        self.samp_clk_task.close()

###################
        # self.DAQ_PARAMS = self.specify_DAQ_params(DAQ_PARAMS)

        # print('testing DAQ...')
        # print(self.DAQ_PARAMS['ctrs_pfis'][0]['ctr_name'])

        # self.di_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][0]['port_name']
        # self.ci_count_edges_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][0]['ctr_name']
        # self.ci_count_read_name = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][0]['pfi_name']

        # print('DAQ params we have named')
        # print(self.di_chan_name)
        # print(self.ci_count_edges_chan_name)
        # print(self.ci_count_read_name)

    def read_counts_1ch(self, ctr_number=0):

        self.di_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number]['port_name']
        self.ci_count_edges_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number]['ctr_name']
        self.ci_count_read_name = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number]['pfi_name']

        with nidaqmx.Task() as read_task, nidaqmx.Task() as samp_clk_task:
            # self.read_task.close()
            # self.read_task.start()

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

            # get data
            ctrs_rate = read_task.read()

            # close task
            # self.read_task.stop()

            return ctrs_rate

    # def get_counts_2ch(self, ctr_number0=0, ctr_number1=1):
    #
    #     self.di_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number0]['port_name']
    #     self.ci_count_edges_chan_name = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number0]['ctr_name']
    #     self.ci_count_read_name = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number0]['pfi_name']
    #
    #     self.di_chan_name0 = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number0]['port_name']
    #     self.ci_count_edges_chan_name0 = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number0]['ctr_name']
    #     self.ci_count_read_name0 = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number0]['pfi_name']
    #
    #     self.di_chan_name1 = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number1]['port_name']
    #     self.ci_count_edges_chan_name1 = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number1]['ctr_name']
    #     self.ci_count_read_name1 = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][ctr_number1]['pfi_name']
    #
    #     # set up read channels and stream readers for all channels
    #     clk_src = '/' + self.DAQ_PARAMS['dev_name'] + '/di/SampleClock'
    #     self.read_tasks = []
    #     self.readers = []
    #     self.n_chan = 0
    #
    #     for ch_idx, key in enumerate(self.DAQ_PARAMS['ctrs_pfis']):
    #         # print(ch_idx)
    #         # print(key)
    #         dev_channel = self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][key]['ctr_name'] #channel
    #
    #         # set up read task counter channel
    #         self.read_tasks.append(nidaqmx.Task())
    #         self.read_tasks[ch_idx].ci_channels.add_ci_count_edges_chan(
    #                                 dev_channel,
    #                                 edge=Edge.RISING,
    #                                 initial_count=0,
    #                                 count_direction=CountDirection.COUNT_UP
    #         )
    #
    #         # this is superfluous if the PFI channels are the default options
    #         # pfi_channel = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][key]['ctr_name'] # ctrs_pfis[channel]
    #         pfi_channel = '/' + self.DAQ_PARAMS['dev_name'] + '/' + self.DAQ_PARAMS['ctrs_pfis'][key]['pfi_name'] # ctrs_pfis[channel]
    #
    #         # print(pfi_channel)
    #
    #         self.read_tasks[ch_idx].ci_channels.all.ci_count_edges_term = pfi_channel
    #
    #         # set up read_task timing and triggering off the sample clock
    #         self.read_tasks[ch_idx].timing.cfg_samp_clk_timing(
    #                                 self.DAQ_PARAMS['sampling_rate'],
    #                                 source=clk_src,
    #                                 sample_mode=AcquisitionType.CONTINUOUS
    #         )
    #         self.read_tasks[ch_idx].in_stream.input_buf_size = self.DAQ_PARAMS['buffer_size']
    #         self.read_tasks[ch_idx].triggers.arm_start_trigger.trig_type = TriggerType.DIGITAL_EDGE
    #         self.read_tasks[ch_idx].triggers.arm_start_trigger.dig_edge_edge = Edge.RISING
    #         self.read_tasks[ch_idx].triggers.arm_start_trigger.dig_edge_src = clk_src
    #
    #         self.readers.append(CounterReader(self.read_tasks[ch_idx].in_stream))
    #         self.read_tasks[ch_idx].start()
    #
    #     return 5

        # #######################################
        #
        # with nidaqmx.Task() as read_task, nidaqmx.Task() as samp_clk_task:
        #
        #     # channel 0
        #     samp_clk_task.di_channels.add_di_chan(self.di_chan_name)
        #     samp_clk_task.timing.cfg_samp_clk_timing(rate=self.DAQ_PARAMS['sampling_rate'],
        #                                     sample_mode=AcquisitionType.CONTINUOUS)
        #     samp_clk_task.control(TaskMode.TASK_COMMIT)
        #     read_task.ci_channels.add_ci_count_edges_chan(
        #                                 self.ci_count_edges_chan_name,
        #                                 edge=Edge.RISING,
        #                                 initial_count=0,
        #                                 count_direction=CountDirection.COUNT_UP)
        #     read_task.ci_channels.all.ci_count_edges_term = self.ci_count_read_name
        #     read_task.timing.cfg_samp_clk_timing(self.DAQ_PARAMS['sampling_rate'], source= '/' + self.DAQ_PARAMS['dev_name'] + '/di/SampleClock',
        #         active_edge=Edge.RISING, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        #
        #     read_task.in_stream.input_buf_size = self.DAQ_PARAMS['buffer_size']
        #     reader = CounterReader(read_task.in_stream)
        #     samp_clk_task.start()
        #     read_task.start()
        #     data_array = np.zeros(self.DAQ_PARAMS['buffer_size'], dtype=np.uint32)
        #
        #     return read_task.read()
        #
        #     #######################################



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
