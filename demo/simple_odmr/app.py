#!/usr/bin/env python
"""
This is an example script that demonstrates the basic functionality of nspyre.

Copyright (c) 2022, Jacob Feder
All rights reserved.

This work is licensed under the terms of the 3-Clause BSD license.
For a copy, see <https://opensource.org/licenses/BSD-3-Clause>.
"""
import logging
from pathlib import Path

# in order for dynamic reloading of code to work, you must pass the specifc
# module containing your class to MainWidgetItem, since the python reload()
# function does not recursively reload modules
import gui_elements
import nspyre.gui.widgets.save_widget
# TODO import nspyre.gui.widgets.load_widget
import nspyre.gui.widgets.flex_line_plot_widget
from nspyre import MainWidget
from nspyre import MainWidgetItem
from nspyre import nspyre_init_logger
from nspyre import nspyreApp

HERE = Path(__file__).parent


def main():
    # Log to the console as well as a file inside the logs folder.
    nspyre_init_logger(
        log_level=logging.INFO,
        log_path=HERE / 'logs',
        log_path_level=logging.DEBUG,
        prefix='odmr_app',
        file_size=10_000_000,
    )

    # Create Qt application and apply nspyre visual settings.
    app = nspyreApp()

    # Create the GUI.
    main_widget = MainWidget(
        {
            'ODMR': MainWidgetItem(gui_elements, 'ODMRWidget', stretch=(1, 1)),
            'Plots': {
                'FlexLinePlotDemo': MainWidgetItem(
                    gui_elements,
                    'FlexLinePlotWidgetWithSomeDefaults',
                    stretch=(100, 100),
                ),
                'FlexLinePlot': MainWidgetItem(
                    nspyre.gui.widgets.flex_line_plot_widget,
                    'FlexLinePlotWidget',
                    stretch=(100, 100),
                ),
            },
            'Save': MainWidgetItem(nspyre.gui.widgets.save_widget, 'SaveWidget', stretch=(1, 1)),
            # TODO 'Load': MainWidgetItem(nspyre.gui.widgets.load_widget, 'LoadWidget', stretch=(1, 1)),
        }
    )
    main_widget.show()
    # Run the GUI event loop.
    app.exec()


# if using the nspyre ProcessRunner, the main code must be guarded with if __name__ == '__main__':
# see https://docs.python.org/2/library/multiprocessing.html#windows
if __name__ == '__main__':
    main()
