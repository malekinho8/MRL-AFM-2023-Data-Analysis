# July 7 2023 FIFO Test. The goal is to output a plot of the X and Y Scan Command signals for the FIFO Test.
# For this test, the FIFO sampled at a period of 40000 ticks on the FPGA, which runs at 40 MHz. This means that
# the scan command datum were sampled at 1 kHz. The FIFO was filled with 1000 samples of the X and Y scan command
# in the csv file for this test, the first column corresponds to the X Command, and the second column corresponds
# to the Y Command.

# imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import click
import os
import pyperclip
from utils import *

# use latex for font rendering
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# constants
FPGA_CLK_FREQ = 40e6 # Hz
FIFO_SAMPLE_PERIOD = 40000 # ticks
FIFO_SAMPLE_FREQ = FPGA_CLK_FREQ / FIFO_SAMPLE_PERIOD # Hz

# define a click argument for the input file name, add optional argument for file directory
@click.command()
@click.option('--use-clipboard-for-filename', '-c', default=True, help='Use the clipboard for the filename.')
@click.option('--file-directory','-d', default='~/Dropbox (MIT)/Qatar 3D Printing/LabVIEW Files (Malek)/2023-Qatar-3D-Printing/afm-data-logs/', help='Directory where the data is stored')

def main(use_clipboard_for_filename,file_directory):
    if use_clipboard_for_filename:
        # get the filename from the clipboard
        filename = pyperclip.paste()
    else:
        filename = input('Please Paste your filename here: ')
    
    # expand the file directory
    directory = os.path.expanduser(file_directory)

    # add the .csv extension to the filename
    filename = filename + '.csv'

    # make sure the filename + directory exists
    fullfile = os.path.join(directory,filename)

    # if the file doesn't exist, print an error message and exit
    if not os.path.isfile(fullfile):
        print('\n\n ERROR: File {} does not exist!\n\n'.format(fullfile))
        exit()

    # read the afm log data
    df, header = read_afm_log_csv(fullfile)

    # get the x command data malek
    x_command = df['X  Command (um)'].to_numpy()

    # get the y command
    y_command = df['Y Command (um)'].to_numpy()

    # get the time vector
    t = np.arange(0,len(x_command)) / FIFO_SAMPLE_FREQ

    # obtain the x period signal overlay
    x_period_overlay = get_signal_period_overlay(x_command,t,window_size=int(FIFO_SAMPLE_FREQ//10))

    # obtain the y period signal overlay
    y_period_overlay = get_signal_period_overlay(y_command,t,window_size=int(FIFO_SAMPLE_FREQ//10))

    # create a 2x1 figure
    fig, (ax1,ax2) = plt.subplots(2,1,sharex=True)

    # plot the x command
    ax1.plot(t,x_command)
    ax1.set_ylabel('X Command (um)')
    ax1.grid(True)

    # create a second twin axis for the x period overlay
    ax1_2 = ax1.twinx()
    ax1_2.plot(t,x_period_overlay,'r')
    ax1_2.set_ylabel('X Period Overlay (s)')
    ax1_2.set_ylim(bottom=0,top=1.1*np.max(x_period_overlay[-len(x_command)//2::]))

    # plot the y command
    ax2.plot(t,y_command)
    ax2.set_ylabel('Y Command (um)')
    ax2.set_xlabel('Time (s)')
    ax2.grid(True)

    # create a second twin axis for the y period overlay
    ax2_2 = ax2.twinx()
    ax2_2.plot(t,y_period_overlay,'r')
    ax2_2.set_ylabel('Y Period Overlay (s)')
    ax2_2.set_ylim(bottom=0,top=1.1*np.max(y_period_overlay[-len(y_command)//2::]))

    # set the title
    fig.suptitle('FIFO Scan Test: X and Y Command Signals')

    # show the plot
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
