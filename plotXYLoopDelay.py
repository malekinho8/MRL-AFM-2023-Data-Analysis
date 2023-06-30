# We seek to plot the 7th column of a data log file in order to visualize what is happening with the XY Scan Loop Delay quantity

# import modules
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import click
import os
import pyperclip
from scipy.signal import savgol_filter, argrelextrema
from utils import *
from scipy.interpolate import interp1d

# define constant
LOOP_DELAY = 10 # in ms
RT_CLK_FREQ = 1000 # in Hz

# use latex for font rendering
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# define a click argument for the input file name, add optional argument for file directory
@click.command()
@click.option('--use-clipboard-for-filename', '-c', default=True, help='Use the clipboard for the filename.')
@click.option('--file-directory','-d', default='~/Dropbox (MIT)/Qatar 3D Printing/LabVIEW Files (Malek)/2023-Qatar-3D-Printing/afm-data-logs/', help='Directory where the data is stored')

def main(use_clipboard_for_filename,file_directory):
    if use_clipboard_for_filename:
        # get the filename from the clipboard
        filename = pyperclip.paste()
    else:
        input('Please Paste your filename here: ')
    
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

    # get the scan loop delay data
    scan_loop_delay = df['FPGA XY Scan Loop Delay (ticks)']

    # get the X command data
    x_command = df['X Command (um)'].to_numpy()

    # specify the sampling rate
    sampling_rate = RT_CLK_FREQ/LOOP_DELAY

    # specify the time vector
    time = np.arange(0,len(scan_loop_delay))/sampling_rate

    # Apply Savitzky-Golay filter
    window_size = 51  # choose an odd number, experiment with the size
    poly_order = 3  # experiment with the order
    smoothed_x_command = savgol_filter(x_command, window_size, poly_order)

    # Now detect troughs
    trough_indices = argrelextrema(smoothed_x_command, np.less)

    # find periods
    periods = np.diff(time[trough_indices])

    # create a new array for the adjusted periods
    adjusted_periods = np.empty_like(x_command)

    # assign period values to corresponding time ranges
    for i in range(len(periods)):
        start = trough_indices[0][i]
        end = trough_indices[0][i+1]
        adjusted_periods[start:end] = periods[i]

    # if there are remaining indices after the last trough, assign them the last period value
    if end < len(x_command):
        adjusted_periods[end:] = periods[-1]

    # create a 3x1 subplot with the loop delay data on top and the x command data on the bottom
    fig, (ax1, ax2) = plt.subplots(2,1,sharex=True)

    # plot the scan loop delay data
    ax1.plot(time, scan_loop_delay)
    ax1.set_ylabel('FPGA XY Scan Loop Delay (ticks)')
    ax1.set_title('FPGA XY Scan Loop Delay (ticks) vs. Time (s)')
    ax1.grid()

    # plot the x command data
    lns1 = ax2.plot(time, x_command)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('X Command (um)')
    ax2.set_title('X Command (um) vs. Time (s)')
    ax2.grid()

    ax3 = ax2.twinx()
    lns3 = ax3.plot(time, adjusted_periods, 'r', label='Period')
    ax3.set_ylabel('Time Between Troughs (s)')

    # set the minimum of the y-axis to 0
    ax3.set_ylim(bottom=0)

    # set maximum of the y-axis to 1.25 times the maximum period value
    ax3.set_ylim(top=1.25*np.max(adjusted_periods[-len(time)//2::]))

    # set the color of the right y-axis to match the line color
    ax3.yaxis.label.set_color('red')
    ax3.tick_params(axis='y', colors='red')

    # consolidate legend entries
    lns = lns1 + lns3
    labs = [l.get_label() for l in lns]
    ax2.legend(lns, labs, loc=0)

    # make the plot look nice
    plt.tight_layout()

    # show the plot
    plt.show()

if __name__ == '__main__':
    main()