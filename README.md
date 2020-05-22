# ET_to_h5
ET_to_h5 is a Python script used to convert a directory of Eyelink .mat and .edf files into hdf format.

## Installation
Clone or download this repository, and ensure all packages in requirements.txt are installed. This can be done by navigating to the directory containing requirements.txt in a terminal and entering:
```bash
pip3 install --user -r /path/requirements.txt
```

Download the **EyeLink Developers Kit for Mac OS X** from [here](https://www.sr-support.com/forum/downloads/eyelink-display-software/45-eyelink-developers-kit-for-mac-os-x-mac-os-x-display-software?15-EyeLink-Developers-Kit-for-Mac-OS-X=).

## Usage
Navigate to the directory containing ET_h5_converter.py in a terminal and run the script with the path to the ET data directory as a command line arguement. Make sure that you haven't already used this to create a hdf file in this directory. For example:
```bash
python3 BIDS_converter.py --path /Users/isabellacamplisson/Documents/AdolphsLab/Eyetracking/ET_data
```

If you wish to also create the BIDS directory at the same time, make sure that this directory doesn't already exist and include ```bash --BIDS true``` as a command line argument. If you wish to create the combined files, include ```bash --combined true```. For example:
```bash
python3 BIDS_converter.py --path /Users/isabellacamplisson/Documents/AdolphsLab/Eyetracking/ET_data --BIDS true --combined true
```

An hdf file named **ET_data_all_v0.h5** will appear in the directory containing files of time data, fixation data, blink data, and saccade data, as well as a ile combining this data together if combined is true.

If creating BIDS, a new directory named 'BIDS' containing the new file structure will be created on the same level as the original directory, and this original directory will be unchanged.

