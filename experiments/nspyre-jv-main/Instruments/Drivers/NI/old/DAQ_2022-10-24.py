import numpy as np
import time
import nidaqmx
from nidaqmx.constants import (AcquisitionType, CountDirection, Edge, READ_ALL_AVAILABLE, TaskMode, TriggerType)
from nidaqmx.stream_readers import CounterReader

# acquire counts from NI DAQ
class DAQ():

    def __init__(self, params):
        self.params = params
        self.last_v = []

    def reset(self):
        print('DAQ reset.')

    def initialize(self):

        # reset any tasks that are currently open
        try:
            self.finalize()
        except:
            pass

        # set sampling parameters
        points = round(self.params['sampling_rate']*self.params['time_per_point'])



        # print('testing daq...')
        # print('sampling rate: ' + str(self.params['sampling_rate']) + ' Hz?')
        # print('time per point: ' + str(self.params['time_per_point']) + ' s')
        # print('points: ' + str(points))



        # check to make sure buffer size is large enough
        if points < 2:
            print('Warning: buffer size must be greater than 2.')
            points = 2
            self.params['sampling_rate'] = int(points/self.params['time_per_point'])
            print('Changing sampling rate to ' + str(self.params['sampling_rate']) + ' so that buffer size = 2.')

        self.buffer_size = int(points)
        # self.buffer_size = self.params['buffer_size'] #int(points)

        self.real_point_time = (points-1)/self.params['sampling_rate']



        # print('real_point_time')
        # print(self.real_point_time)



        system = nidaqmx.system.System.local()
        sys_device = system.devices[self.params['dev_name']]

        # set up sample clock task at port0, when this clock ticks, data is read from the counter channel
        clk_channel = self.params['dev_name'] + '/' + 'port0'
        self.samp_clk_task = nidaqmx.Task()

        # set up sample clock task at port0, when this clock ticks, data is read from the counter channel
        self.samp_clk_task.di_channels.add_di_chan(clk_channel)
        self.samp_clk_task.timing.cfg_samp_clk_timing(
                                self.params['sampling_rate'],
                                sample_mode=AcquisitionType.CONTINUOUS,
                                samps_per_chan=self.buffer_size
        )
        self.samp_clk_task.control(TaskMode.TASK_COMMIT)
        clk_src = '/' + self.params['dev_name'] + '/di/SampleClock'

        # set up read channels and stream readers for all channels
        self.read_tasks = []
        self.readers = []
        self.n_chan = 0

        # for ch_idx, key in enumerate(self.params['channels']):
        #     dev_channel = self.params['dev_name'] + '/' + self.params['channels'][key]['ctr_name'] #channel

        for ch_idx, key in enumerate(self.params['channels']):
            dev_channel = self.params['dev_name'] + '/' + self.params['channels'][key]['ctr_name'] #channel

            # set up read task counter channel
            self.read_tasks.append(nidaqmx.Task())
            self.read_tasks[ch_idx].ci_channels.add_ci_count_edges_chan(
                                    dev_channel,
                                    edge=Edge.RISING,
                                    initial_count=0,
                                    count_direction=CountDirection.COUNT_UP
            )

            # this is superfluous if the PFI channels are the default options
            pfi_channel = '/' + self.params['dev_name'] + '/' + self.params['channels'][key]['pfi_name']
            self.read_tasks[ch_idx].ci_channels.all.ci_count_edges_term = pfi_channel

            # set up read_task timing and triggering off the sample clock
            self.read_tasks[ch_idx].timing.cfg_samp_clk_timing(
                                    self.params['sampling_rate'],
                                    source=clk_src,
                                    sample_mode=AcquisitionType.CONTINUOUS
            )
            self.read_tasks[ch_idx].in_stream.input_buf_size = self.buffer_size
            self.read_tasks[ch_idx].triggers.arm_start_trigger.trig_type = TriggerType.DIGITAL_EDGE
            self.read_tasks[ch_idx].triggers.arm_start_trigger.dig_edge_edge = Edge.RISING
            self.read_tasks[ch_idx].triggers.arm_start_trigger.dig_edge_src = clk_src

            self.readers.append(CounterReader(self.read_tasks[ch_idx].in_stream))
            self.read_tasks[ch_idx].start()

        # set up data array to dump read buffer into
        self.data_array = np.zeros((self.buffer_size), dtype=np.uint32)
        self.n_chan = self.params['channels'].__len__()

    def finalize(self):
        for idx, read_task in enumerate(self.read_tasks):
            # self.read_tasks[idx].stop()
            self.read_tasks[idx].close()
        self.samp_clk_task.close()

    def read(self):
        self.samp_clk_task.start()
        d_ctrs = np.zeros(self.n_chan)

        for ch_idx, reader in enumerate(self.readers):
            num_samps = self.readers[ch_idx].read_many_sample_uint32(
                    self.data_array,
                    number_of_samples_per_channel=self.buffer_size
            )
            d_ctrs[ch_idx] = self.data_array[-1] - self.data_array[0]

        ctrs_rate = d_ctrs / self.real_point_time

        self.samp_clk_task.stop()
        return ctrs_rate

    def set_ao_voltage(self, v, ch=0):
        ch_name = self.params['dev_name'] + '/' + 'ao' + str(ch)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(ch_name, max_val=5, min_val=-5)
            samples_written = task.write(v)
            self.last_v = v
            if samples_written != 1:
                print('DAQ warning: number of written samples = ' + str(samples_written))

        # print('setting ' + str(ch_name) + ' to: ' + str(v) + ' V')

    def set_ao_voltage_ramp(self, v, ch=0, dv=0.01, time_per_step=1e-3):

        if self.last_v == []:
            print('warning: no current voltage specified, setting voltage to ' + str(v) + ' V without ramp')
            self.set_ao_voltage(v, ch)
            self.last_v = v
            return

        if v != self.last_v:
            if self.last_v < v:
                v_vec = np.arange(self.last_v, v+dv, dv)
            elif self.last_v >= v:
                v_vec = np.arange(self.last_v, v-dv, -dv)
            for v_idx, v_val in enumerate(v_vec):
                self.set_ao_voltage(v_val, ch)
                time.sleep(time_per_step)
        else:
            self.set_ao_voltage(v, ch)

    def read_ai_voltage(self, ch=0):
        ch_name = self.params['dev_name'] + '/' + 'ai' + str(ch)
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(ch_name)
            return task.read()
