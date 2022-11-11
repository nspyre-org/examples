"""
Example GUI elements for an ODMR application.

Copyright (c) 2022, Jacob Feder
All rights reserved.

This work is licensed under the terms of the 3-Clause BSD license.
For a copy, see <https://opensource.org/licenses/BSD-3-Clause>.
"""
from functools import partial
from importlib import reload

import numpy as np
import odmr
from nspyre import DataSink
from nspyre import LinePlotWidget
from nspyre import FlexLinePlotWidget
from nspyre import ExperimentWidget
from nspyre import ParamsWidget
from nspyre import ProcessRunner
from nspyre import SaveWidget
from pyqtgraph import SpinBox
from pyqtgraph.Qt import QtWidgets


class ODMRWidget(ExperimentWidget):
    def __init__(self):
        params_config = {
            'start_freq': {
                'display_text': 'Start Frequency',
                'widget': SpinBox(
                    value=3e9,
                    suffix='Hz',
                    siPrefix=True,
                    bounds=(100e3, 10e9),
                    dec=True,
                ),
            },
            'stop_freq': {
                'display_text': 'Stop Frequency',
                'widget': SpinBox(
                    value=4e9,
                    suffix='Hz',
                    siPrefix=True,
                    bounds=(100e3, 10e9),
                    dec=True,
                ),
            },
            'num_points': {
                'display_text': 'Number of Scan Points',
                'widget': SpinBox(value=100, int=True, bounds=(1, None), dec=True),
            },
            'iterations': {
                'display_text': 'Number of Experiment Repeats',
                'widget': SpinBox(value=20, int=True, bounds=(1, None), dec=True),
            },
            'dataset': {
                'display_text': 'Data Set',
                'widget': QtWidgets.QLineEdit('odmr'),
            },
        }

        super().__init__(params_config, 
                        odmr,
                        'SpinMeasurements',
                        'odmr_sweep',
                        title='ODMR')

class FlexLinePlotWidgetWithSomeDefaults(FlexLinePlotWidget):
    """This is meant to give the user some hints as to how to use the FlexSinkLinePlotWidget.
    Generally there should be no need to subclass it in this way."""
    def __init__(self):
        super().__init__()
        self.add_plot('avg', 'mydata', '', '', 'Average')
        self.add_plot('latest', 'mydata', '-1', '', 'Average')
        self.add_plot('first', 'mydata', '0', '1', 'Average')
        self.add_plot('latest_10', 'mydata', '-10', '', 'Average')
        self.hide_plot('first')
        self.hide_plot('latest_10')
        self.datasource_lineedit.setText('odmr')

