# @Author: Eric Rosenthal
# @Date:   2022-05-13T09:39:13-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-21T14:36:11-07:00



"""
List of all experimental parameters.
    SAVE_PARAMS should include 'experiment_name', the folder under Experiments\Data\ which data is saved.
    GUI_PARAMS in spinboxs must be dictionaries with sub-entry 'value'
    GUI_PARAMS must have 'style': 'spinbox' or 'checkbox',
                         'info':   specifying parameters, including a 'value'

"""
PATH_PARAMS = {
        # 'nspyre_path': 'C:\\Users\\hopel\\Documents\\nspyre-jv',
        'nspyre_path': 'C:\\Users\\Public\\nspyre-jv',
        'save_path': 'G:\\Shared drives\\Diamond team - Vuckovic group\\Data\\Montana_test',  #enter path of where nspyre and save folder is on machine, add double slashes for some reason.
    }

SAVE_PARAMS = {
        'experiment_name': '2022-11-05_test\\test',
        'prefix': '', # optional text at the beginning of the filename
        'comment': '', # optional text at the end of the filename
    }

SWEEP_PARAMS = {
        'num_x': 41,
        'x_min':0,
        'x_max':10,
        'x_avg':2,
        'pause_x': 50e-3,
        'num_y': 2,
        'y_min':0,
        'y_max':2,
        'y_avg':1,
        'pause_y': 10e-3,
    }

DATA_PARAMS = {
    'data': 'data', # data source name for sweep data
    }

GUI_PARAMS = {
        'autosave_status': {'style':'checkbox', 'info':{'value': 1, 'bounds':(0, 1), 'int':True}},
    }

# required: dictionary of all parameters
ALL = PATH_PARAMS | SAVE_PARAMS | SWEEP_PARAMS | DATA_PARAMS | GUI_PARAMS
