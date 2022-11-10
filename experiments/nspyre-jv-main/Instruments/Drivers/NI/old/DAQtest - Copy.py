# Let's create a task for the counter channel and a task for a
# 'dummy' digital input channel to start the digital input Sample
# Clock. A ''with'' code block is used to implement automatic error
# handling and correctly stop and clear resources for each task
# when the program exits.
import nidaqmx
from nidaqmx.constants import (AcquisitionType, CountDirection, Edge,
    READ_ALL_AVAILABLE, TaskMode, TriggerType)
from nidaqmx.stream_readers import CounterReader
import numpy as np

# Load the NI-DAQmx system that is visible in the Measurement & Automation
# Explorer (MAX) software of NI-DAQmx for the local machine.
system = nidaqmx.system.System.local()

# We know on our current system that our DAQ is named 'Dev1'
DAQ_device = system.devices['Dev1']

with nidaqmx.Task() as read_task, nidaqmx.Task() as samp_clk_task:

    # create a digital input channel on 'port0' of 'Dev1'
    samp_clk_task.di_channels.add_di_chan('Dev1/port0')
        # """
        # Note that port 2 of a DAQ device does not support buffered
        # operations, so here port port0 is used. Additionally, the
        # line_grouping Arg (1 channel for all lines or 1 channel
        # per line) does not matter because this is a 'dummy' task.
        # """

    # configure the timing parameters of the sample clock so that
    # it has a sampling rate of 100 Hz and runs continuously so
    # that the digital input sample clock continues to run even if
    # it's associated task is not reading anything from the channel.
    sampling_rate = 1 # Hz
    samp_clk_task.timing.cfg_samp_clk_timing(rate=sampling_rate,
                                    sample_mode=AcquisitionType.CONTINUOUS)
    # commit the task from the Reserved state in system memory to
    # the Commit state on the DAQ; this programs the hardware
    # resources with those settings of the task which must be
    # configured before the task transitions into the Start state.
    # This speeds up the execution of the samp_clk_task.start() call
    # because the hardware will now be in the Commit state and must
    # only transition to the State state to run the task.
    samp_clk_task.control(TaskMode.TASK_COMMIT)

    # create a counter input channel using 'ctr0' on 'Dev1' to count
    # rising digital edges, counting up from initial_count
    read_task.ci_channels.add_ci_count_edges_chan(
                                'Dev1/ctr0',
                                edge=Edge.RISING,
                                initial_count=0,
                                count_direction=CountDirection.COUNT_UP)

    # set the input terminal of the counter input channel on which
    # the counter receives the signal on which it counts edges
    read_task.ci_channels.all.ci_count_edges_term = '/Dev1/PFI12'
       # """
       # When specifying the name of a terminal, all external
       # terminals - as defined by NI-DAQmx - must include a leading
       # '/' in its string. An external terminal is any terminal that
       # can be routed internally from one channel to another or from
       # DAQ to another; examples include: PFI lines, Sample Clocks,
       # physical analog channels, physical digital channels, the
       # output of a physical counter, etc. All external terminals
       # can be 'exported' using task.export_signals.export_signal(
       # *args). NI-DAQmx recognized devices do not include a leading
       # '/' in their string name because they are not terminals.
       # """

    # set the timing parameters of the counter input channel, using
    # the digial input Sample Clock as it's source, with the same
    # sampling rate used to generate the Sample Clock; the task will
    # work if a different sampling rate is set than the true rate
    # of the Sample Clock, but the hardware will not be optimized
    # for this clock signal. Additionally, set the counter to
    # readout its count to the buffer on the rising edge of the
    # Sample Clock signal.
    # """ max counter sampling rate allowed: 100e6 (i.e. 100MHz)"""
    read_task.timing.cfg_samp_clk_timing(sampling_rate, source='/Dev1/di/SampleClock',
        active_edge=Edge.RISING, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        # """
        # Other optional Arg is 'samps_per_chan': if ** sample_mode**
        # is **CONTINUOUS_SAMPLES**, NI-DAQmx uses this value to
        # determine the buffer size. 'cfg_samp_clk_timing' returns an
        # error if the specified value is negative.
        # """
    # set the buffer size of the counter, such that, given the
    # sampling rate at which the counter reads out its current value
    # to the buffer, it will give two minutes of samples before the
    # buffer overflows.

    read_task.in_stream.input_buf_size = 12000

    # # Create an arm start trigger for the counter so that it is
    # # synced with the digital input Sample Clock and only starts
    # # counting when the first Sample Clock tick is detected. This
    # # prevents the necessity of throwing out the first sample in the
    # # counter buffer (due to the uncertainity in the collection
    # # window of the first sample because it is set by when the
    # # counter and Sample Clock start operating
    # read_task.triggers.arm_start_trigger.trig_type = TriggerType.DIGITAL_EDGE
    # read_task.triggers.arm_start_trigger.dig_edge_edge = Edge.RISING
    # read_task.triggers.arm_start_trigger.dig_edge_src = '/Dev1/di/SampleClock'

    # create a counter reader to read from the counter InStream
    reader = CounterReader(read_task.in_stream)
    # start the tasks to begin data acquisition; note that because
    # the arm start trigger of the counter was set, it does not
    # matter which task is started first, the tasks will be synced
    samp_clk_task.start()
    read_task.start()
    # create a data buffer for the counter stream reader
    data_array = np.zeros(12000, dtype=np.uint32)


    print('reading task....')
    print(read_task.read())

    print('code that throws error...')
    # read all samples from the counter buffer to the system memory
    # buffer data_array; if the buffer is not large enough, it will
    # raise an error
    # reader.read_many_sample_uint32(data_array,
    #     number_of_samples_per_channel=READ_ALL_AVAILABLE)
