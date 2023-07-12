# Here we want to plot and compare the normalized loop iteration variable computed on the FPGA level with the X and Y scan commands.
# Basically, one of the things we want to check is if if the normalized loop iteration values match up with the X and Y scan commands, and also if they are the values they should be.
# For example, if the Lines per seconds is 0.1 and the X scan amplitude is 50 um, then the X scan period should be 10 seconds (i.e. 0.1 lines per second * 50 um = 5 um per second, and 50 um / 5 um per second = 10 seconds).
# Then if the FPGA is running at 40 MHz, and our desired loop run rate is 100 KHz, then the loop delay should be 400 ticks (i.e. 40 MHz / 100 KHz = 400 ticks).
# This means that our FPGA will output 100,000 loop iterations per second, and each loop iteration will take 400 ticks to complete.
# Hence to complete one scan line in 10 seconds, we should expect 1,000,000 loop iterations (i.e. 100,000 loop iterations per second * 10 seconds = 1,000,000 loop iterations).
# Hence from this particular experiment, we should see that the X command will go from -25 to 25 um in 1,000,000 loop iterations, and the normalized loop iteration variable should go from 0 to 1,000,000 and then back to 0
# after which the X command will repeat.

# imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import click
import pyperclip
import os
from utils import *
from scipy.signal import savgol_filter, argrelextrema

# use latex for font rendering
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# ultimately we want to plot a 2x2 subplot with the following:
# (1,1) - X command vs. time
# (1,2) - Y command vs. time
# (2,1) - normalizedx x loop iteration vs. time
# (2,2) - normalized y loop iteration vs. time

# constants
RT_CLK_FREQ = 1000 # Hz

# specify click command line options
@click.command()
@click.option('--use-clipboard-for-filename', '-c', default=True, help='Use the clipboard for the filename.')
@click.option('--file-directory','-d', default='~/Dropbox (MIT)/Qatar 3D Printing/LabVIEW Files (Malek)/2023-Qatar-3D-Printing/afm-data-logs/', help='Directory where the data is stored')
@click.option('--rt-loop-delay', '-l', default=100, help='RT loop delay in milliseconds.')

def main(use_clipboard_for_filename,file_directory,rt_loop_delay):
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

    # use read_afm_data_log to read the data
    df, header = read_afm_log_csv(fullfile)

    # get the x command data (first column)
    x_command = df.iloc[:,0].to_numpy()

    # get the y command data (second column)
    y_command = df.iloc[:,1].to_numpy()

    # get the normalized x loop iteration data (third column)
    normalized_x_loop_iteration = df.iloc[:,2].to_numpy()

    # get the normalized y loop iteration data (fourth column)
    normalized_y_loop_iteration = df.iloc[:,3].to_numpy()

    # specify the sampling frequency
    fs = RT_CLK_FREQ / rt_loop_delay

    # set time to be arange of the length of the x command data
    time = np.arange(len(x_command))/fs

    # get the period overlay for the x command
    adjusted_periods = get_signal_period_overlay(x_command, time)

    # get the adjusted periods for the normalized x loop iteration
    adjusted_periods_normalized_x_loop_iteration = get_signal_period_overlay(normalized_x_loop_iteration, time)

    # create the subplots
    fig,ax = plt.subplots(2,2,sharex=True)

    # plot the x command data
    ax[0,0].plot(time,x_command)
    ax[0,0].set_ylabel('X Command (um)')
    ax[0,0].set_title('X Command vs. Time')

    ax3 = ax[0,0].twinx()
    lns3 = ax3.plot(time, adjusted_periods, 'r', label='Period')
    ax3.set_ylabel('Time Between Troughs (s)')

    # set the minimum of the y-axis to 0
    ax3.set_ylim(bottom=0)

    # set maximum of the y-axis to 1.25 times the maximum period value
    ax3.set_ylim(top=1.25*np.max(adjusted_periods[-len(time)//2::]))

    # set the color of the right y-axis to match the line color
    ax3.yaxis.label.set_color('red')
    ax3.tick_params(axis='y', colors='red')

    # plot the y command data
    ax[0,1].plot(time,y_command)
    ax[0,1].set_ylabel('Y Command (um)')
    ax[0,1].set_title('Y Command vs. Time')

    # plot the normalized x loop iteration data
    ax[1,0].plot(time,normalized_x_loop_iteration)
    ax[1,0].set_ylabel('Normalized X Loop Iteration')
    ax[1,0].set_title('Normalized X Loop Iteration vs. Time')
    ax[1,0].set_xlabel('Time (s)')

    ax4 = ax[1,0].twinx()
    lns3 = ax4.plot(time, adjusted_periods_normalized_x_loop_iteration, 'r', label='Period')
    ax4.set_ylabel('Time Between Troughs (s)')

    # set the minimum of the y-axis to 0
    ax4.set_ylim(bottom=0)

    # set maximum of the y-axis to 1.25 times the maximum period value
    ax4.set_ylim(top=1.25*np.max(adjusted_periods_normalized_x_loop_iteration[-len(time)//2::]))

    # set the color of the right y-axis to match the line color
    ax4.yaxis.label.set_color('red')
    ax4.tick_params(axis='y', colors='red')

    # plot the normalized y loop iteration data
    ax[1,1].plot(time,normalized_y_loop_iteration)
    ax[1,1].set_ylabel('Normalized Y Loop Iteration')
    ax[1,1].set_title('Normalized Y Loop Iteration vs. Time')
    ax[1,1].set_xlabel('Time (s)')

    # show the plot 
    plt.tight_layout()
    plt.show(block=True)

if __name__ == '__main__':
    main()




    
    