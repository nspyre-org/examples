# @Author: Eric Rosenthal
# @Date:   2022-05-13T09:39:13-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-16T15:40:48-07:00



"""
List of all experimental parameters.
    SAVE_PARAMS should include 'experiment_name', the folder under Experiments\Data\ which data is saved.
    GUI_PARAMS in spinboxs must be dictionaries with sub-entry 'value'
    GUI_PARAMS must have 'style': 'spinbox' or 'checkbox',
                         'info':   specifying parameters, including a 'value'

"""
PATH_PARAMS = {
        'nspyre_path': 'C:\\Users\\hopel\\Documents\\nspyre-jv',
        'save_path': 'G:\\Shared drives\\Diamond team - Vuckovic group\\Data\\Montana_test',  #enter path of where nspyre and save folder is on machine, add double slashes for some reason.
    }

GUI_PARAMS = {
        'num_x': {'style':'spinbox', 'info':{'value': 401, 'int': True, 'bounds':(1, None), 'dec':True}},
        'time_per_point': {'style':'spinbox', 'info':{'value':0.02, 'suffix':'s'}},
    }

INT_PARAMS = {
        'pause_init': 10e-3,
        'pause_x': 10e-3,
    }

PLOT_PARAMS = {
        'plot_name': 'CountsVsTime', # must be defined
        'ch0': 'ch0',
        'ch1': 'ch1',
        'x_label': 'frequency (GHz)',
        'y_label': 'counts/s',
    }

SAVE_PARAMS = {
        'experiment_name': 'CountsVsTime',
    }

DAQ_PARAMS = {
        'sampling_rate': 100,
        'buffer_size': 12000,
        'channels': {0:{'ctr_name':'ctr0', 'pfi_name':'PFI0', 'port_name':'port0'}, 1:{'ctr_name':'ctr1', 'pfi_name':'PFI12', 'port_name':'port0'}},
        'dev_name': 'Dev1',
    }

# required: dictionary of all parameters

ALL = PATH_PARAMS | GUI_PARAMS | INT_PARAMS | PLOT_PARAMS | SAVE_PARAMS | DAQ_PARAMS
