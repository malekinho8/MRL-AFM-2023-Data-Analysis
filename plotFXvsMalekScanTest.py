# The main goal of this script is to generate a plot of the command signals obtained between using Malek's scan code and FX (Fangzhou Xia) scan code.
# The output of the test was a csv file with columns for Malek's X Command, Y Command, (columns 1 and 2) and FX's X Command, Y Command (columns 5 and 6).

# imports
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

# constants
RT_CLK_FREQ = 1000 # Hz

# define a click argument for the input file name, add optional argument for file directory
@click.command()
@click.option('--use-clipboard-for-filename', '-c', default=True, help='Use the clipboard for the filename.')
@click.option('--file-directory','-d', default='~/Dropbox (MIT)/Qatar 3D Printing/LabVIEW Files (Malek)/2023-Qatar-3D-Printing/afm-data-logs/', help='Directory where the data is stored')
@click.option('--rt-loop-delay', '-l', default=100, help='Loop delay in miliseconds.')

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

    # read the afm log data
    df, header = read_afm_log_csv(fullfile)

    # get the x command data malek
    x_command_malek = df['X Command (um)'].to_numpy()

    # get the y command data malek
    y_command_malek = df['Y Command (um)'].to_numpy()

    # get the x command data fx
    x_command_fx = df['FX X Command (um)'].to_numpy()

    # get the y command data fx
    y_command_fx = df['FX Y Command (um)'].to_numpy()

    # specify the sampling rate
    sampling_rate = RT_CLK_FREQ/rt_loop_delay

    print(f'Sampling rate is {sampling_rate} Hz')

    # specify the time vector
    time = np.arange(0,len(x_command_malek)/sampling_rate,1/sampling_rate)

    # obtain the period overlay for each of the command signals
    period_x_malek = get_signal_period_overlay(x_command_malek,time)
    period_y_malek = get_signal_period_overlay(y_command_malek,time)
    period_x_fx = get_signal_period_overlay(x_command_fx,time)
    period_y_fx = get_signal_period_overlay(y_command_fx,time)

    # create a 2x2 plot first row should be malek, second row should be fx
    fig, ((ax0,ax1),(ax2,ax3)) = plt.subplots(2,2,sharex=True)

    # plot the malek x command
    ax0.plot(time,x_command_malek)
    ax0.set_title('Malek X Command')
    ax0.set_ylabel('X Command (um)')

    # overlay the period x malek by creating a twin
    ax0_twin = ax0.twinx()
    ax0_twin.plot(time,period_x_malek,'r')
    ax0_twin.set_ylabel('Time Between Troughs (s)',color='r')
    ax0_twin.tick_params(axis='y',labelcolor='r')
    ax0_twin.set_ylim(top=1.25*np.max(period_x_malek[-len(time)//2::]), bottom=0)

    # plot the malek y command
    ax1.plot(time,y_command_malek)
    ax1.set_title('Malek Y Command')
    ax1.set_ylabel('Y Command (um)')
    
    # overlay the period y malek by creating a twin
    ax1_twin = ax1.twinx()
    ax1_twin.plot(time,period_y_malek,'r')
    ax1_twin.set_ylabel('Time Between Troughs (s)',color='r')
    ax1_twin.tick_params(axis='y',labelcolor='r')
    ax1_twin.set_ylim(top=1.25*np.max(period_y_malek[-len(time)//2::]), bottom=0)

    # plot the fx x command
    ax2.plot(time,x_command_fx)
    ax2.set_title('FX X Command')
    ax2.set_ylabel('X Command (um)')
    ax2.set_xlabel('Time (s)')

    # overlay the period x fx by creating a twin
    ax2_twin = ax2.twinx()
    ax2_twin.plot(time,period_x_fx,'r')
    ax2_twin.set_ylabel('Time Between Troughs (s)',color='r')
    ax2_twin.tick_params(axis='y',labelcolor='r')
    ax2_twin.set_ylim(top=1.25*np.max(period_x_fx[-len(time)//2::]), bottom=0)

    # plot the fx y command
    ax3.plot(time,y_command_fx)
    ax3.set_title('FX Y Command')
    ax3.set_ylabel('Y Command (um)')
    ax3.set_xlabel('Time (s)')

    # overlay the period y fx by creating a twin
    ax3_twin = ax3.twinx()
    ax3_twin.plot(time,period_y_fx,'r')
    ax3_twin.set_ylabel('Time Between Troughs (s)',color='r')
    ax3_twin.tick_params(axis='y',labelcolor='r')
    ax3_twin.set_ylim(top=1.25*np.max(period_y_fx[-len(time)//2::]), bottom=0)

    # adjust the layout
    plt.tight_layout()

    # show the plot
    plt.show(block=True)

if __name__ == '__main__':
    main()

    



