# imports
import os
import shutil
import numpy as np
import glob
import json


def edf_to_asc(path):
    """
    Convert EDF file to ASC file
    :param path: full path to EDF file, or to directory containing EDF files
    :return: None, creates ASC file in same directory as EDF file
    """

    # if path points to single file
    if os.path.isfile(path):
        if path[-4:] == '.edf':
            command = "/Applications/Eyelink/EDF_Access_API/Example/edf2asc " + path
            os.system(command)

    # if path points to directory
    elif os.path.isdir(path):
        paths = [path + '/' + i for i in os.listdir(path) if i[-4:] == '.edf']
        for _ in paths:
            edf_to_asc(_)


def make_json_individual_description(new_path):
    """
    Creates json file for specific task in BIDS directory based on edf file
    :param new_path: new path to directory containing edf file
    :return: None
    """

    fileformat = '.edf'
    samplingfrequency, includedeyemovementevents, manufacturer, manufacturersmodelname, calibrationtype, recordedeye \
        = json_details(new_path + '.asc')


    jsonDict = {
        'SamplingFrequency': samplingfrequency,
        'FileFormat': fileformat,
        'IncludedEyeMovementEvents': includedeyemovementevents,
        'Manufacturer': manufacturer,
        'ManufacturersModelName': manufacturersmodelname,
        'CalibrationType': calibrationtype,
        'RecordedEye': recordedeye
    }

    text = str(new_path) + '.json'

    with open(text, 'w') as json_file:
        json.dump(jsonDict, json_file)


def json_details(path):
    """
    Finds and returns information for json file from ASC file
    :param path: path to ASC file
    :return: string variables for the sampling rate (rate), recorded events (events), manufacturer, model,
    calibration type (calibrationtype), and recorded eye (eye).
    """

    with open(path, 'r') as f:
        text = f.read()
        if 'RATE' in text:
            ind = text.split().index('RATE') + 1
            rate = text.split()[ind]
        else:
            rate = "unknown"

        events = []
        if 'SFIX' in text:
            events.append('Start of fixation: "SFIX"')
        if 'EFIX' in text:
            events.append('End of fixation: "EFIX"')
        if 'SSACC' in text:
            events.append('Start of saccade: "SSACC"')
        if 'ESACC' in text:
            events.append('End of saccade: "ESACC"')
        if 'SBLINK' in text:
            events.append('Start of blink: "SBLINK"')
        if 'EBLINK' in text:
            events.append('End of blink: "EBLINK"')

        if 'H3' in text:
            calibrationtype = 'H3'
        elif 'HV9' in text:
            calibrationtype = 'HV9'
        else:
            calibrationtype = 'unknown'

        if 'RIGHT' in text:
            eye = 'RIGHT'
        if 'LEFT' in text:
            eye = 'LEFT'
        if 'BOTH' in text:
            eye = 'BOTH'

        f.close()

    with open(path, 'r') as f:
        lines = f.readlines()
        manufacturer = lines[4][11:-1]
        model = lines[3][12:-1]

        f.close()

    return rate, events, manufacturer, model, calibrationtype, eye


def BIDS_edf_asc_json(path, new_dr, subject_num, tasks):
    """
    Adds EDF, ASC, and JSON files to BIDS directory
    :param new_dr: newly created BIDS directory
    :param path: (old) path to subject directory
    :param subject_num: subject number ID
    :param tasks: ordered list of tasks
    :return: None
    """

    i = 0
    os.chdir(path)

    for file in glob.glob("*.edf"):
        # copy over and rename edf file
        file_name = 'sub-' + subject_num + '_ses-01' + '_acq-' + str(i + 1) + '_task-' + tasks[i] + '_eyetrack'
        old_path = path + '/' + file
        new_path = new_dr + '/' + file_name + '.edf'
        shutil.copy(old_path, new_path)

        # create asc
        edf_to_asc(new_path)

        # create json
        make_json_individual_description(new_path[:-4])
        i += 1


def BIDS_mat(path, new_dr, subject_num, tasks):
    """
    Adds MAT files to BIDS directory
    :param new_dr: newly created BIDS directory
    :param path: (old) path to subject directory
    :param subject_num: subject number ID
    :param tasks: ordered list of tasks
    :return: None
    """

    os.chdir(path)

    for file in glob.glob("*.mat"):
        for task in tasks:
            if task.lower() in file.lower():
                task_num = np.where(np.asarray(tasks) == task)[0][0] + 1
                name = 'sub-' + subject_num + '_ses-01' + '_acq-' + str(task_num) + '_task-' + task + '_eyetrack.mat'
                old_path = path + '/' + file
                new_path = new_dr + '/' + name
                shutil.copy(old_path, new_path)


def directory_to_BIDS(path):
    """
    Converts a directory to BIDS format while maintaining the original directory as [name]_RAW
    :param path: full path to a directory to be converted to BIDS format
    :return: None, creates BIDS-formatted folder in same directory as the raw directory
    """

    # assumes directory is the subject name
    subject_num = os.path.split(path)[1][:6]

    # task names --> need to know if there is a more general way of getting the task names in the right order
    tasks = ['trailer1', 'trailer2', 'Office1', 'Office2', 'Pixar', 'BangDead']

    # make new dr
    new_dr = os.path.split(path)[0] + '/BIDS/' + 'sub-' + subject_num + '/eyetrack'
    os.makedirs(new_dr)

    BIDS_edf_asc_json(path, new_dr, subject_num, tasks)
    BIDS_mat(path, new_dr, subject_num, tasks)


if __name__ == '__main__':
    path_name = input("Path name: ")
    directory_to_BIDS(path_name)
