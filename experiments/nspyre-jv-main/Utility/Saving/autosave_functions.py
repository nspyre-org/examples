import numpy as np
from datetime import datetime
import os
from pathlib import Path
import json

def autosave_data(dataset_name='unnamed_dataset', params='{}', dataset='{}'):
    print('autosaving....')

    # automatically save params to datasets
    dataset['params'] = params

    # convert numpy arrays to lists, which are json serializable
    for key in dataset:
        if isinstance(dataset[key], np.ndarray):
            dataset[key] = dataset[key].tolist()

    # create folder to store data
    folder_name = datetime.today().strftime('%Y-%m-%d')

    # check if averaging is turned on or off
    key = 'averaging_onoff'
    avg_counter = 1
    if key in params.keys():
        if params['averaging_onoff'] == 1:
            try:
                avg_counter = params['avg_counter']
            except:
                avg_counter = 1
            if avg_counter > 1:
                print('reminder: overwriting previous filename, because averaging is enabled')

    try:
        print(params['save_path'] + '\\' + params['experiment_name'] + '\\' + folder_name)
    except:
        print('Warning: no experiment name. Experiment is called "unnamed" by default.')
        params['experiment_name'] = 'unnamed'
        pass

    # add optional prefix to the beginning of the filename
    try:
        if params['prefix'] == '':
            prefix = ''
        else:
            prefix = params['prefix'] + '_'
    except:
        prefix = ''

    # add optional comment to end of filename
    try:
        if params['comment'] == '':
            comment = ''
        else:
            comment = '_' + params['comment']
    except:
        comment = ''

    filename = generate_data_name(
                                    params, \
                                    dataset_name, \
                                    folder_name=folder_name, \
                                    prefix=prefix, \
                                    comment=comment, \
                                    avg_counter=avg_counter, \
                                    )
    with open(filename,'w') as df:
        json.dump(serialize_dict(dataset), df)

    return filename

def serialize_dict(dict_original):
    # make dictionary "serializable", necessary for kwargs to be saved as a json file
    dict_serialized = {}
    for key in dict_original:
        dict_serialized[key] = dict_original[key]
    return dict_serialized

def get_last_sweep_path_and_name():
    path_name = params['nspyre_path']
    text_file = open(r'{}\Utility\Saving\last_path_and_name.txt'.format(path_name),'r')
    last_path_and_name = text_file.read()
    text_file.close()
    return last_path_and_name

def generate_data_name(params, dataset_name='unnamed_spyrelet', folder_name='unnamed_folder', prefix='', comment='', avg_counter=0):
    # import params
    path_name = params['nspyre_path']
    save_path_name = params['save_path']
    experiment_dir = params['experiment_name']

    # make serial number based on current date and time
    current_time = datetime.now()
    year = int(str(current_time.year)[-2:])
    # year = current_time.year
    if year < 10:
        year = str(0) + str(year)
    day = current_time.day
    month = current_time.month
    if month < 10:
        month = str(0) + str(month)
    day = current_time.day
    if day < 10:
        day = str(0) + str(day)
    hour = current_time.hour
    if hour < 10:
        hour = str(0) + str(hour)
    minute = current_time.minute
    if minute < 10:
        minute = str(0) + str(minute)
    second = current_time.second
    if second < 10:
        second = str(0) + str(second)

    sn = str(year) + str(month) + str(day) + '_' + str(hour) + str(minute) + str(second)

    # create filename
    file_name = prefix + sn + '_' + dataset_name + comment
    print(file_name)

    parent_dir = r'{}'.format(save_path_name)
    directory = experiment_dir + '\\' + folder_name

    path = os.path.join(parent_dir, directory)
    if not os.path.exists(path):
        os.makedirs(path)

    # name of file to be saved
    path_and_name = path + '\\' + file_name + '.json'

    # save text file with path and name, to be used by plotting scripts
    last_path_and_name_file = params['nspyre_path'] + '\\Utility\\Saving\\last_path_and_name.txt'

    with open(last_path_and_name_file, "w") as text_file:
        text_file.write(path_and_name)

    # return name of file to be saved
    return path_and_name
