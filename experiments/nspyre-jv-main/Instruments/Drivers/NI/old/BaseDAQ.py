import numpy as np
# from nspyre.spyrelet.spyrelet import Spyrelet
import nidaqmx
from nidaqmx.constants import (AcquisitionType, CountDirection, Edge, READ_ALL_AVAILABLE, TaskMode, TriggerType)
from nidaqmx.stream_readers import CounterReader

# for acquiring counts from the NI DAQ
# class BaseDAQ(Spyrelet):
class BaseDAQ():
    def __init__(self):
        self.device = 'Dev1'
        self.channels = {
            'channel1':{'type':list, 'items':list(['ctr0','ctr1','ctr2','ctr3','none']), 'default':'ctr0'},
            'channel2':{'type':list, 'items':list(['ctr0','ctr1','ctr2','ctr3','none']), 'default':'ctr1'},
        }
        self.sampling_rate = 10
        self.time_per_point = 0.1

    def initialize(self):
        # PFI channels corresponding to selected ctr
        ctrs_pfis = {'ctr0':'PFI0', 'ctr1':'PFI12'}

        # set sampling parameters
        points = round(self.sampling_rate*self.time_per_point)
        self.rate = self.sampling_rate
        self.buffer_size = int(points)
        self.real_point_time = (points-1)/self.sampling_rate
        system = nidaqmx.system.System.local()
        sys_device = system.devices[self.device]

        # set up sample clock task at port0, when this clock ticks, data is read from the counter channel
        clk_channel = self.device + '/' + 'port0'
        self.samp_clk_task = nidaqmx.Task()
        self.samp_clk_task.di_channels.add_di_chan(clk_channel)
        self.samp_clk_task.timing.cfg_samp_clk_timing(
                                self.rate,
                                sample_mode=AcquisitionType.CONTINUOUS,
                                samps_per_chan=self.buffer_size
        )
        self.samp_clk_task.control(TaskMode.TASK_COMMIT)
        clk_src = '/' + self.device + '/di/SampleClock'

        # set up read channels and stream readers for all channels
        self.read_tasks = []
        self.readers = []
        self.n_chan = 0
        for ii,channel in enumerate(self.channels):
            if channel != 'none':
                print('testing...')
                print(channel)

                if channel == 'channel1':
                    dev_channel = self.device + '/' + 'ctr0'
                elif channel == 'channel2':
                    dev_channel = self.device + '/' + 'ctr1'

                # set up read task counter channel
                self.read_tasks.append(nidaqmx.Task())
                self.read_tasks[ii].ci_channels.add_ci_count_edges_chan(
                                        dev_channel,
                                        edge=Edge.RISING,
                                        initial_count=0,
                                        count_direction=CountDirection.COUNT_UP
                )

                # this is superfluous if the PFI channels are the default options
                if channel == 'channel1':
                    pfi_channel = '/' + self.device + '/' + 'PFI0'
                elif channel == 'channel2':
                    pfi_channel = '/' + self.device + '/' + 'PFI12'

                self.read_tasks[ii].ci_channels.all.ci_count_edges_term = pfi_channel

                # set up read_task timing and triggering off the sample clock
                self.read_tasks[ii].timing.cfg_samp_clk_timing(
                                        self.rate,
                                        source=clk_src,
                                        sample_mode=AcquisitionType.CONTINUOUS
                )
                self.read_tasks[ii].in_stream.input_buf_size = self.buffer_size
                self.read_tasks[ii].triggers.arm_start_trigger.trig_type = TriggerType.DIGITAL_EDGE
                self.read_tasks[ii].triggers.arm_start_trigger.dig_edge_edge = Edge.RISING
                self.read_tasks[ii].triggers.arm_start_trigger.dig_edge_src = clk_src

                self.readers.append(CounterReader(self.read_tasks[ii].in_stream))
                self.read_tasks[ii].start()

        # set up data array to dump read buffer into
        self.data_array = np.zeros((self.buffer_size), dtype=np.uint32)
        self.n_chan = channels.__len__()

    def finalize(self): #, device, channels, sampling_rate, time_per_point):
        for ii,read_task in enumerate(self.read_tasks):
            self.read_tasks[ii].stop()
        self.samp_clk_task.close()

    def read(self):
        self.samp_clk_task.start()
        d_ctrs = np.zeros(self.n_chan)

        for ii,reader in enumerate(self.readers):
            if self.channels[ii] != 'none':
                num_samps = self.readers[ii].read_many_sample_uint32(
                        self.data_array,
                        number_of_samples_per_channel=self.buffer_size
                )
                if num_samps < self.buffer_size:
                    print('something wrong: buffer issue')
                    return
                d_ctrs[ii] = self.data_array[-1] - self.data_array[0]

        ctrs_rate = d_ctrs / self.real_point_time
        self.samp_clk_task.stop()
        return ctrs_rate
