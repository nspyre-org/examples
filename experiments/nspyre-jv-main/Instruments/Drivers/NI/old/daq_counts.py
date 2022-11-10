# Hope and Eric, 3/22/2022, based off of nspyre documentation
# for more info see: https://nidaqmx-python.readthedocs.io/en/latest/_modules/nidaqmx/_task_modules/ci_channel_collection.html#CIChannelCollection.add_ci_count_edges_chan

import nidaqmx
from nidaqmx.constants import (AcquisitionType, CountDirection, Edge, READ_ALL_AVAILABLE, TaskMode, TriggerType)
from nidaqmx.stream_readers import CounterReader
import numpy as np

def daq_counts(sampling_rate=100, buffer_size=12000, port_name='port0', ctr_name='ctr0', ch_name='PFI12', dev_name='Dev1'):
    with nidaqmx.Task() as read_task, nidaqmx.Task() as samp_clk_task:

        di_chan_name = dev_name + '/' + port_name
        ci_count_edges_chan_name = dev_name + '/' + ctr_name
        ci_count_read_name = '/' + dev_name + '/' + ch_name

        samp_clk_task.di_channels.add_di_chan(di_chan_name)
        samp_clk_task.timing.cfg_samp_clk_timing(rate=sampling_rate,
                                        sample_mode=AcquisitionType.CONTINUOUS)
        samp_clk_task.control(TaskMode.TASK_COMMIT)
        read_task.ci_channels.add_ci_count_edges_chan(
                                    ci_count_edges_chan_name,
                                    edge=Edge.RISING,
                                    initial_count=0,
                                    count_direction=CountDirection.COUNT_UP)

        read_task.ci_channels.all.ci_count_edges_term = ci_count_read_name
        read_task.timing.cfg_samp_clk_timing(sampling_rate, source= '/' + dev_name + '/di/SampleClock',
            active_edge=Edge.RISING, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

        read_task.in_stream.input_buf_size = buffer_size
        reader = CounterReader(read_task.in_stream)
        samp_clk_task.start()
        read_task.start()
        data_array = np.zeros(buffer_size, dtype=np.uint32)

        return read_task.read()
