# The goal of this code is to take a CSV image log from an AFM experiment and visualize it using matplotlib

# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import click
import os
import pyperclip
from utils import *

# use latex for font rendering
plt.rc('text', usetex=True)

@click.command()
@click.option('--use-clipboard-for-filename', '-c', default=True, help='Use the clipboard for the filename.')

def main(use_clipboard_for_filename):
    """
    Plots the data from the AFM data log CSV file specified by the filename in the user's clipboard. The data log file should be a CSV file with the following format:
        
        img-testing-data-log-[13-34-28]
    
    The .csv will be appended automatically.
    """
    # make the direcrory path absolute (user would have to change this depending on their Dropbox folder name)
    directory = os.path.expanduser('~/Dropbox (MIT)/Qatar 3D Printing/LabVIEW Files (Malek)/2023-Qatar-3D-Printing/afm-data-logs/')

    # print the directory
    print('Log Directory: {}'.format(directory))

    # get the filename from the clipboard if available
    if use_clipboard_for_filename:
        # get the filename from the clipboard
        filename = pyperclip.paste()
    else:
        input('Please Paste your filename here (no file extension, just the name): ')
    
    # add the .csv extension to the filename
    filename = filename + '.csv'

    # make sure the filename + directory exists
    fullfile = os.path.join(directory,filename)

    # if the file doesn't exist, print an error message and exit
    if not os.path.isfile(fullfile):
        print('File {} does not exist!'.format(fullfile))
        exit()
    
    # use a custom plot function to plot the data
    plot_image(fullfile)

def plot_image(fullfile):
    # read the data from the CSV file
    df = pd.read_csv(fullfile)

    # obtain the path of the experimental log data
    directory = os.path.dirname(fullfile)

    # get the filename without the extension
    filename = os.path.splitext(os.path.basename(fullfile))[0]

    # take out the image-testing- prefix
    filename = filename.replace('img-testing-','')

    # produce the path to the original experiment
    log_fullfile = os.path.join(directory,filename+'.csv')

    # read the original experiment data
    log_df = pd.read_csv(log_fullfile)

    # get the header information
    header = get_log_header_info(log_df)

    # get the experimental title string
    title = get_experiment_info_string(header)

    # get the image data
    img = df.iloc[:,:].to_numpy()

    # plot the image
    fig = plt.figure()
    plt.imshow(img,cmap='gray')
    plt.title('AFM Image: {}'.format(title))
    plt.tight_layout()
    plt.show(block=True)

if __name__ == "main":
    main()