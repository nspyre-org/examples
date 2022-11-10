import numpy as np
import sys
from functools import partial
from nspyre import DataSink, LinePlotWidget, ProcessRunner, SaveWidget, InstrumentGateway, DataSource, ParamsWidget
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget
from importlib.machinery import SourceFileLoader
import os

import params
path_name = params.PATH_PARAMS['nspyre_path']
sys.path.insert(0,r'{}\Utility\Widgets'.format(path_name))
sys.path.insert(0,r'{}\Utility\Style'.format(path_name))
from example import RandomVsTime
from gui_shared import GUISweep, GUIPlot1D
from colors_matplotlib import colors
from colors_matplotlib import cyclic_colors
from style import nspyre_font

class RandomVsTimeWidget_1D(GUISweep):
    def __init__(self):
        super().__init__()

        # define parameters that show up in GUI
        self.params_widget = ParamsWidget(params.GUI_PARAMS, params.SAVE_PARAMS['experiment_name'])
        self.params_layout.addWidget(self.params_widget)

    def stream_wfm_gui(self):
        # reload parameters and create waveform
        print('stream wfm currently not enabled')

    def sweep_clicked(self):
        Example = SourceFileLoader('example',os.path.abspath(__file__)).load_module() # reload
        self.sweep_proc.run(Example.RandomVsTime().sweep_1d) # run

    def stop(self):
        """Stop the sweep process."""
        self.sweep_proc.kill()

class RandomVsTimeWidget_2D(GUISweep):
    def __init__(self):
        super().__init__()

        # define parameters that show up in GUI
        self.params_widget = ParamsWidget(params.GUI_PARAMS, params.SAVE_PARAMS['experiment_name'])
        self.params_layout.addWidget(self.params_widget)

    def stream_wfm_gui(self):
        # reload parameters and create waveform
        print('stream wfm currently not enabled')

    def sweep_clicked(self):
        Example = SourceFileLoader('example',os.path.abspath(__file__)).load_module() # reload
        self.sweep_proc.run(Example.RandomVsTime().sweep_2d) # run

    def stop(self):
        """Stop the sweep process."""
        self.sweep_proc.kill()

class PlotWidgetRandomVsTime(GUIPlot1D):
    def __init__(self):
        super().__init__()

        params.ALL['x_label'] = 'x variable (units)'
        params.ALL['z_label'] = 'z variable (units)'
        self.plot_style = {
            'plot_last_data': True, # options: True, False
            'data_pen_style': 'SolidLine', # options: SolidLine, NoPen
            'last_data_pen_style' : 'NoPen', # options: SolidLine, NoPen
        }

        self.setup1d(params, self.plot_style)

    def update(self):
        try:
            if self.sink.pop():
                self.set_data('ch0', self.sink.x, self.sink.z_ch0)
                if self.plot_style['plot_last_data']:
                    try:
                        self.set_data('ch0_last', self.sink.x, self.sink.z_ch0_last)
                    except:
                        pass
        except:
            pass
