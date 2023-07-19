# the main  goal of this code is to characterize the PGMFC microcontroller by analyzing the first order
# response of the system and calculating the time constant.

# import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import click
import os
import pyperclip
from utils import *

# use latex for font rendering, use serif font
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

@click.command()
@click.option('--use-clipboard-for-experiment-folder-name', '-c', default=True, help='Use the clipboard for the experiment folder name.')

def main(use_clipboard_for_experiment_folder_name):
    if use_clipboard_for_experiment_folder_name:
        # get the filename from the clipboard
        file_name = pyperclip.paste()
    else:
        file_name = input('Please Paste your filename here (no file extension, just the name): ')
    
    # make the direcrory path absolute (user would have to change this depending on their Dropbox folder name)
    directory = os.path.expanduser('~/Dropbox (MIT)/Qatar 3D Printing/Reports/report-data-dump')

    # print the directory
    print('Log Directory: {}'.format(directory))

    # add the .txt extension to the filename
    filename = file_name + '.txt'

    # make sure the filename + directory exists
    fullfile = os.path.join(directory,filename)

    # if the file doesn't exist, print an error message and exit
    if not os.path.isfile(fullfile):
        print('File {} does not exist!'.format(fullfile))
        exit()

    # read the data from the CSV file
    df = pd.read_csv(fullfile, sep=r'\t')

    # get the time and pressure data. Time samples is the first column, and pressure samples is the second column
    time_samples = df.iloc[:,0]
    pressure_samples = df.iloc[:,1]

    # define the slice to look at for the first order response
    slice_start = 560 # seconds
    slice_end = 588 # seconds

    # convert time steps to seconds given that the sampling frequency is 1/T where T = 10 ms
    T = 10e-3 # second period loop
    sampling_frequency = 1/T # Hz
    time_seconds = time_samples/sampling_frequency

    # get the indices of the slice start and end
    slice_start_idx = np.where(np.abs(time_seconds - slice_start) < 1e-2)[0][0]
    slice_end_idx = np.where(np.abs(time_seconds - slice_end) < 1e-2)[0][0]

    # get the data slices
    time_seconds = time_seconds[slice_start_idx:slice_end_idx]
    pressures = pressure_samples[slice_start_idx:slice_end_idx]


    # plot the data
    plt.plot(time_seconds, pressures)
    plt.xlabel('Time (s)')
    plt.ylabel('Pressure (psi)')
    plt.title('PGMFC Pressure Command Response')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()