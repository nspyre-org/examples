# @Author: Eric Rosenthal
# @Date:   2022-05-13T09:39:13-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-16T16:01:44-07:00



import logging
from pathlib import Path
from nspyre import MainWidget
from nspyre import NspyreApp
import example_gui_elements

HERE = Path(__file__).parent

# if using the nspyre ProcessRunner, the main code must be guarded with if __name__ == '__main__':
# see https://docs.python.org/2/library/multiprocessing.html#windows
if __name__ == '__main__':

    # Create Qt application and apply nspyre visual settings.
    app = NspyreApp()

    # Create the GUI.
    main_widget = MainWidget(
        {
            'RandomVsTime_1D': {
                'module': example_gui_elements,
                'class': 'RandomVsTimeWidget_1D',
                'args': (),
                'kwargs': {},
            },
            'RandomVsTime_2D': {
                'module': example_gui_elements,
                'class': 'RandomVsTimeWidget_2D',
                'args': (),
                'kwargs': {},
            },
            'PlotRandomVsTime': {
                'module': example_gui_elements,
                'class': 'PlotWidgetRandomVsTime',
                'args': (),
                'kwargs': {},
            },
        }
    )
    main_widget.show()
    # Run the GUI event loop.
    app.exec()
