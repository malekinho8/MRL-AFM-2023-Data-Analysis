# This code seeks to plot a spectrogram of the scan signals to see if we can detect any changes in frequency (i.e. scan speed) over time.

# import modules
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import click
import os
import pyperclip
from utils import *

# use latex for font rendering
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# define a click argument for the input file name, add optional argument for file directory
@click.command()
@click.option('--use-clipboard-for-filename', '-c', default=True, help='Use the clipboard for the filename.')
@click.option('--file-directory', '-d', default='~/Dropbox (MIT)/Qatar 3D Printing/LabVIEW Files (Malek)/2023-Qatar-3D-Printing/afm-data-logs/', help='Directory where the data is stored')
@click.option('--signal-type', '-s', default='X Command (um)', help='Signal type to plot. Options are X Command (um), Y Command (um), Z Command (um), OBD SUM (V), OBD X (V), OBD Y (V), and XY Scan Loop Delay (ticks).')
@click.option('--save-audio-flag', '-a', default=False, help='Save the audio file of the signal to the current directory.')
@click.option('--sampling-rate', '-r', default=44100, help='Sampling rate of the audio file in Hz.')

def main(use_clipboard_for_filename, file_directory, signal_type, save_audio_flag, sampling_rate):
    if use_clipboard_for_filename:
        # get the filename from the clipboard
        filename = pyperclip.paste()
    else:
        input('Please Paste your filename here: ')

    # expand the file directory
    file_directory = os.path.expanduser(file_directory)

    # add the .csv extension to the filename
    filename = filename + '.csv'

    # make sure the filename + directory exists
    fullfile = os.path.join(file_directory,filename)

    # if the file doesn't exist, print an error message and exit
    if not os.path.isfile(fullfile):
        print('File {} does not exist!'.format(fullfile))
        exit()
    
    # use a custom plot function to plot the spectrogram data
    plot_spectrogram(fullfile, signal_type, save_audio_flag, sampling_rate)

if __name__ == '__main__':
    main()

