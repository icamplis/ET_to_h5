from BIDS_converter import directory_to_BIDS
import os
from sys import exit as sys_exit
import numpy as np
import pandas as pd
import re
from tqdm import tqdm


# convert ET data to BIDS format (takes a while)
def convert_to_BIDS(path):
    subject_folders = os.listdir(path)
    for f in subject_folders:
        if ".DS_Store" not in f:
            directory_to_BIDS(path + '/' + f)


def check_and_get_ET_files(sub_subject, exp_folder):
    # get subject number
    print(sub_subject)
    subj = sub_subject.split('-')[1]

    # make sure only subject files are there
    if len(subj) != 6 or ' ' in subj:
        sys_exit('Unexpected subj folder format at:\n%s' % os.path.join(exp_folder, sub_subject))

    # get all files in subject eyetrack file
    subj_full_path = os.path.join(exp_folder, sub_subject, 'eyetrack')
    ET_files = sorted(os.listdir(subj_full_path))
    ET_files = [i for i in ET_files if '.DS_Store' not in i]

    # for each recording we expect 4 files: edf, mjson, asc, and metadata .mat,
    # otherwise probably theres is a problem...
    if np.divmod(len(ET_files), 4)[1] != 0:
        print('a potential problem in %s' % subj_full_path)

    return subj, subj_full_path, ET_files


def data_loader(path, bids):
    # convert
    if bids:
        convert_to_BIDS(path)

    # Eye-tracking data (location of scanner ET data)
    exp_folder = path + '/BIDS'

    # Output file to save processed ET data.
    separate_hdf_output_file = path + '/ET_data_all_v0_separate.h5'
    combined_hdf_output_file = path + '/ET_data_all_v0_combined.h5'

    subj_folders = os.listdir(exp_folder)
    while '.DS_Store' in subj_folders:
        subj_folders.remove('.DS_Store')

    return exp_folder, separate_hdf_output_file, combined_hdf_output_file, subj_folders


def make_dfs(sess_name, f, subj_full_path):
    # get task name (i.e. 'trailer1', 'Pixar') and files
    task_name = sess_name.split('_')[-2].rsplit('-')[1]
    edf_file = f

    if task_name not in ['trailer1', 'trailer2', 'Office1', 'Office2', 'Pixar', 'BangDead']:
        sys_exit('Undefined clip!')

    # get full path
    edf_full_path = os.path.join(subj_full_path, edf_file)
    assert os.path.isfile(edf_full_path), 'File does not exist: %s' % edf_full_path

    # get dfs
    times_df, saccs_df, fixes_df, blinks_df = get_ET_data(edf_full_path)

    return task_name, times_df, saccs_df, fixes_df, blinks_df


def get_ET_data(edf_path):
    with open(edf_path) as f:
        edf = f.readlines()
        f.close()

    times = []
    saccs = []
    fixes = []
    blinks = []

    for line in tqdm(edf):
        if line[0] in '0123456789':
            time = [i for i in re.split(' |\t|\n', line) if i != '' and i != '...']
            times.append(time)
        if line.split(' ')[0] in ['ESACC']:
            sacc = [i for i in re.split(' |\t|\n', line) if i != '']
            saccs.append(sacc)
        if line.split(' ')[0] in ['EFIX']:
            fix = [i for i in re.split(' |\t|\n', line) if i != '']
            fixes.append(fix)
        if line.split(' ')[0] in ['EBLINK']:
            blink = [i for i in re.split(' |\t|\n', line) if i != '']
            blinks.append(blink)

    times_cols = ['TIME', 'GAZE_X', 'GAZE_Y', 'PUP_SIZE']
    times_df = pd.DataFrame(times, columns=times_cols)

    saccs_cols = ['EVENT', 'EYE', 'START', 'END', 'DUR', 'X_START', 'Y_START', 'X_END', 'Y_END', 'AMPL', 'PUP_VEL']
    saccs_df = pd.DataFrame(saccs, columns=saccs_cols)
    saccs_df['EVENT'] = 2

    fixes_cols = ['EVENT', 'EYE', 'START', 'END', 'DUR', 'FIX_X', 'FIX_Y', 'PUP_AVG']
    fixes_df = pd.DataFrame(fixes, columns=fixes_cols)
    fixes_df['EVENT'] = 1

    blinks_cols = ['EVENT', 'EYE', 'START', 'END', 'DUR']
    blinks_df = pd.DataFrame(blinks, columns=blinks_cols)
    blinks_df['EVENT'] = 0

    return times_df, saccs_df, fixes_df, blinks_df


def create_combined_df(times, saccs, fixes, blinks):
    events = pd.concat([saccs, fixes, blinks], axis=0, sort=False, ignore_index=True)
    events = events.sort_values(by=['START'])
    events = events.reset_index(drop=True)
    events = events.drop(['END', 'PUP_AVG', 'X_START', 'Y_START', 'X_END', 'Y_END', 'AMPL', 'PUP_VEL'], axis=1)

    times["EVENT"] = np.nan
    times["EYE"] = np.nan
    times["DUR"] = np.nan
    times["FIX_X"] = np.nan
    times["FIX_Y"] = np.nan

    times.TIME = times.TIME.astype(int)
    events.START = events.START.astype(int)

    add_columns(times, events)

    return times


def add_columns(time_df, events_df):
    columns = ['EVENT', 'EYE', 'DUR', 'FIX_X', 'FIX_Y']

    for e_idx in tqdm(range(events_df.shape[0] - 1)):
        lb = events_df.iloc[e_idx].START
        ub = events_df.iloc[e_idx + 1].START
        mask = time_df.TIME.between(lb, ub - 1)
        s = events_df.loc[e_idx, columns].values
        time_df.loc[mask, columns] = s

    lb = events_df.iloc[-1].START
    ub = lb + int(events_df.iloc[-1].DUR)
    mask = time_df.TIME.between(lb, ub - 1)
    s = events_df.loc[events_df.index[-1], columns].values
    time_df.loc[mask, columns] = s
