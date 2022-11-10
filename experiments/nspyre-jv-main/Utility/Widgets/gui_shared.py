# class containing functions shared between many types of GUIs

from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from parameters_widget import ParamsWidget
from lineplot_widget import LinePlotWidget
from colorplot_widget import ColorPlotWidget
from nspyre import DataSink, ProcessRunner, SaveWidget, InstrumentGateway, DataSource
from functools import partial
import pyqtgraph as pg
from colors_matplotlib import colors

class GUISweep(QWidget):
    def __init__(self):
        super().__init__()

        # define parameters that show up in GUI
        # self.params_widget = ParamsWidget(params.GUI_PARAMS, params.SAVE_PARAMS['experiment_name'])

        # buttons that appear in GUI
        self.wfm_button = QPushButton('Stream Waveform')
        self.stop_button = QPushButton('Stop')
        self.sweep_button = QPushButton('Sweep')

        # the process running the sweep function
        self.sweep_proc = ProcessRunner()

        # specify action to take when clicking buttons
        self.wfm_button.clicked.connect(self.stream_wfm_gui)
        self.sweep_button.clicked.connect(self.sweep_clicked)
        self.stop_button.clicked.connect(self.sweep_stopped)
        self.destroyed.connect(partial(self.stop))

        # Qt layout that arranges the params and button vertically
        self.params_layout = QVBoxLayout()
        self.params_layout.addWidget(self.wfm_button)
        self.params_layout.addWidget(self.stop_button)
        self.params_layout.addWidget(self.sweep_button)

        self.setLayout(self.params_layout)

    # kills process
    def sweep_stopped(self):
        self.sweep_proc.kill()
        print('sweep stopped.')

    # kills process
    def stop(self):
        self.sweep_proc.kill()

class GUIPlot1D_2Ch(LinePlotWidget):
    def __init__(self):
        super().__init__()

    def setup1d(self, params, plot_style={}): #, data_pen_style='SolidLine', last_data_pen_style='NoPen'):

        # specify plot style
        #   possible line styles:
        #       QtCore.Qt.NoPen
        #       QtCore.Qt.SolidLine
        #       QtCore.Qt.DashedLine
        #       QtCore.Qt.DotLine

        # plot styles by default
        plot_last_data = True
        data_pen_style = QtCore.Qt.SolidLine
        last_data_pen_style = QtCore.Qt.NoPen

        # define plot style for supported options
        if 'plot_last_data' in plot_style:
            if plot_style['plot_last_data'] == True:
                plot_last_data = True
            elif plot_style['plot_last_data'] == False:
                plot_last_data = False
            else:
                print('warning: "plot_last_data" must be "True" or "False"')
        if 'data_pen_style' in plot_style:
            if plot_style['data_pen_style'] == 'SolidLine':
                data_pen_style = QtCore.Qt.SolidLine
            elif plot_style['data_pen_style'] == 'NoPen':
                data_pen_style = QtCore.Qt.NoPen
            else:
                print('warning: "data_pen_style" must be "SolidLine" or "NoPen"')
        if 'last_data_pen_style' in plot_style:
            if plot_style['last_data_pen_style'] == 'SolidLine':
                last_data_pen_style = QtCore.Qt.SolidLine
            elif plot_style['last_data_pen_style'] == 'NoPen':
                last_data_pen_style = QtCore.Qt.NoPen
            else:
                print('warning: "last_data_pen_style" must be "SolidLine" or "NoPen"')

        # make plots
        self.new_plot('ch0',
            symbol='o',
            pen=pg.mkPen(color=colors['C0'], width=1.5, style=data_pen_style),
            symbolSize=5,
            symbolBrush=(colors['C0'][0], colors['C0'][1], colors['C0'][2], 255),
            symbolPen=(colors['C0'][0], colors['C0'][1], colors['C0'][2], 255),
            )

        if plot_last_data:
            self.new_plot('ch0_last',
                symbol='o',
                pen=pg.mkPen(color=colors['C0'], width=1.0, style=last_data_pen_style),
                symbolSize=5,
                symbolBrush=(colors['C0'][0], colors['C0'][1], colors['C0'][2], 100),
                symbolPen=(colors['C0'][0], colors['C0'][1], colors['C0'][2], 100),
                )

        self.new_plot('ch1',
            symbol='o',
            pen=pg.mkPen(color=colors['C1'], width=1.5, style=data_pen_style),
            symbolSize=5,
            symbolBrush=(colors['C1'][0], colors['C1'][1], colors['C1'][2], 255),
            symbolPen=(colors['C1'][0], colors['C1'][1], colors['C1'][2], 255),
            )

        if plot_last_data:
            self.new_plot('ch1_last',
                symbol='o',
                pen=pg.mkPen(color=colors['C1'], width=1.0, style=last_data_pen_style),
                symbolSize=5,
                symbolBrush=(colors['C1'][0], colors['C1'][1], colors['C1'][2], 100),
                symbolPen=(colors['C1'][0], colors['C1'][1], colors['C1'][2], 100),
                )

        self.sink = DataSink(params.ALL['data'])

        self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left',params.ALL['z_label'])
        self.plot_widget.getAxis('left').setTextPen('k')
        self.plot_widget.getAxis('left').setPen(color='k',width=2)
        self.plot_widget.setLabel('bottom',params.ALL['x_label'])
        self.plot_widget.getAxis('bottom').setTextPen('k')
        self.plot_widget.getAxis('bottom').setPen(color='k',width=2)
        # self.plot_widget.setYRange(0, 1500)
        # self.plot_widget.setXRange(619.269, 619.274)

class GUIPlot1D(LinePlotWidget):
    def __init__(self):
        super().__init__()

    def setup1d(self, params, plot_style={}): #, data_pen_style='SolidLine', last_data_pen_style='NoPen'):

        # specify plot style
        #   possible line styles:
        #       QtCore.Qt.NoPen
        #       QtCore.Qt.SolidLine
        #       QtCore.Qt.DashedLine
        #       QtCore.Qt.DotLine

        # plot styles by default
        plot_last_data = True
        data_pen_style = QtCore.Qt.SolidLine
        last_data_pen_style = QtCore.Qt.NoPen

        # define plot style for supported options
        if 'plot_last_data' in plot_style:
            if plot_style['plot_last_data'] == True:
                plot_last_data = True
            elif plot_style['plot_last_data'] == False:
                plot_last_data = False
            else:
                print('warning: "plot_last_data" must be "True" or "False"')
        if 'data_pen_style' in plot_style:
            if plot_style['data_pen_style'] == 'SolidLine':
                data_pen_style = QtCore.Qt.SolidLine
            elif plot_style['data_pen_style'] == 'NoPen':
                data_pen_style = QtCore.Qt.NoPen
            else:
                print('warning: "data_pen_style" must be "SolidLine" or "NoPen"')
        if 'last_data_pen_style' in plot_style:
            if plot_style['last_data_pen_style'] == 'SolidLine':
                last_data_pen_style = QtCore.Qt.SolidLine
            elif plot_style['last_data_pen_style'] == 'NoPen':
                last_data_pen_style = QtCore.Qt.NoPen
            else:
                print('warning: "last_data_pen_style" must be "SolidLine" or "NoPen"')

        # make plots
        self.new_plot('ch0',
            symbol='o',
            pen=pg.mkPen(color=colors['C0'], width=1.5, style=data_pen_style),
            symbolSize=5,
            symbolBrush=(colors['C0'][0], colors['C0'][1], colors['C0'][2], 255),
            symbolPen=(colors['C0'][0], colors['C0'][1], colors['C0'][2], 255),
            )

        if plot_last_data:
            self.new_plot('ch0_last',
                symbol='o',
                pen=pg.mkPen(color=colors['C0'], width=1.0, style=last_data_pen_style),
                symbolSize=5,
                symbolBrush=(colors['C0'][0], colors['C0'][1], colors['C0'][2], 100),
                symbolPen=(colors['C0'][0], colors['C0'][1], colors['C0'][2], 100),
                )

        self.sink = DataSink(params.ALL['data'])

        self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left',params.ALL['z_label'])
        self.plot_widget.getAxis('left').setTextPen('k')
        self.plot_widget.getAxis('left').setPen(color='k',width=2)
        self.plot_widget.setLabel('bottom',params.ALL['x_label'])
        self.plot_widget.getAxis('bottom').setTextPen('k')
        self.plot_widget.getAxis('bottom').setPen(color='k',width=2)
        # self.plot_widget.setYRange(0, 1500)
        # self.plot_widget.setXRange(619.269, 619.274)

class GUIPlot1DSpectrometer(LinePlotWidget):
    def __init__(self):
        super().__init__()

    # def set_x_label(self, x_label):
    #     print('testing set x')
        # self.plot_widget.setLabel('bottom',x_label)

    # def set_y_label(self, y_label):
    #     self.plot_widget.setLabel('bottom',y_label)

    def setup1d(self, params, plot_style={}): #, data_pen_style='SolidLine', last_data_pen_style='NoPen'):

        # specify plot style
        #   possible line styles:
        #       QtCore.Qt.NoPen
        #       QtCore.Qt.SolidLine
        #       QtCore.Qt.DashedLine
        #       QtCore.Qt.DotLine

        # make plots
        self.new_plot('spectrometer_data',
            symbol='o',
            pen=pg.mkPen(color=colors['C0'], width=1.5, style=QtCore.Qt.SolidLine),
            symbolSize=0,
            symbolBrush=(colors['C0'][0], colors['C0'][1], colors['C0'][2], 255),
            symbolPen=(colors['C0'][0], colors['C0'][1], colors['C0'][2], 255),
            )

        self.sink = DataSink('spectrometer_data')

        self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left',params.ALL['y_label'])
        self.plot_widget.getAxis('left').setTextPen('k')
        self.plot_widget.getAxis('left').setPen(color='k',width=2)
        self.plot_widget.setLabel('bottom',params.ALL['x_label'])
        self.plot_widget.getAxis('bottom').setTextPen('k')
        self.plot_widget.getAxis('bottom').setPen(color='k',width=2)
        # self.plot_widget.setYRange(0, 1500)
        self.plot_widget.setXRange(619.290, 619.293)
