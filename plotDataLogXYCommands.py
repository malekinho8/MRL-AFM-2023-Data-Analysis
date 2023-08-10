# The main goal of this code is to plot the CSV data log output from AFM tests. 
# Files are automatically saved to the Dropbox.

# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import click
import os
import pyperclip
import matplotlib as mpl
from utils import *

# use latex for font rendering
mpl.rcParams.update(mpl.rcParamsDefault)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# constant definitions
LOOP_DELAY = 10 # ms

# define a click argument for the input file name, add optional argument for file directory
@click.command()
@click.option('--use-clipboard-for-filename', '-c', default=True, help='Use the clipboard for the filename.')
@click.option('--scale_factor', '-s', default=1.25, help='Scale factor for the data plots y-axis scaling.')
@click.option('--directory', '-d', default='~/Dropbox (MIT)/Qatar 3D Printing/LabVIEW Files (Malek)/2023-Qatar-3D-Printing/afm-data-logs/', help='Directory where the data is stored')
@click.option('--time-units', '-t', default='min', help='Time units for the x-axis of the plots. Options are min, s, and ms.')
@click.option('--vs-distance', '-v', default=False, help='Plot the Z Command vs. X Command data instead of vs. time (default).')
@click.option('--title-string', '-T', default='XY Nanocube Commands', help='Main Title string for the plots.')

def main(use_clipboard_for_filename,scale_factor,directory,time_units,vs_distance,title_string):
    """
    Plots the data from the AFM data log folder of the following format:
        
        data-log-[13-34-28]
    
    The .csv will be appended automatically.
    """
    if use_clipboard_for_filename:
        # get the filename from the clipboard
        folder_name = pyperclip.paste()
    else:
        folder_name = input('Please Paste your folder name here: ')
    
    # make the direcrory path absolute
    directory = os.path.expanduser(directory)

    # add the .csv extension to the filename
    folder_dir = os.path.join(directory,folder_name)

    # if the folder doesn't exist, print an error message and exit
    if not os.path.isdir(folder_dir):
        print('Folder {} does not exist! Please copy folder name to clipboard.'.format(folder_dir))
        exit()
    
    # create the new title string from the folder name
    title_string += f' ({folder_name})'

    # use a custom plot function to plot the data
    plot_data(folder_dir,scale_factor,time_units,vs_distance,title_string)

def plot_data(folder_dir, scale_factor,time_units,vs_distance,title_string):
    # maek the time axis unit label
    if time_units == 'min':
        time_label = 'Time (min)'
        div_factor = 60
    elif time_units == 's':
        time_label = 'Time (s)'
        div_factor = 1
    elif time_units == 'ms':
        time_label = 'Time (ms)'
        div_factor = 1/1000
    
    # define data filenames
    info_file = os.path.join(folder_dir,'experiment-info.csv')
    x_file = os.path.join(folder_dir,'x-command.csv')
    y_file = os.path.join(folder_dir,'y-command.csv')

    # # get max column length
    # num_cols = get_max_column_length(info_file)

    # # read the data file
    # df = pd.read_csv(info_file, names=range(num_cols), delimiter = '\\t', header = None, skiprows = 1)

    # load the x_df
    x_df = pd.read_csv(x_file, delimiter = ',', header = None)

    # load the y_df
    y_df = pd.read_csv(y_file, delimiter = ',', header = None)

    # specify time sample vector
    time_samples = np.arange(0,x_df.shape[0],1)

    # using loop delay, define the loop rate
    loop_rate = 1/(LOOP_DELAY/1000)

    # using the sample rate, create the time vector
    time = time_samples/loop_rate

    # convert to units of minutes
    time = time/div_factor

    # get the data, where the first column is the X Command, Second is Y Command, Third is Z Command, Fourth is OBD X, Fifth is OBD Y, Sixth is OBD Sum
    data = x_df.iloc[:, 0].tolist()
    data2 = y_df.iloc[:,0].tolist()
    # create the plot title string. It should include the P, I, D parameter values in scientific notation, the LPS, Size X, and Size Y values, and the Z Set Point, Offset X, and Offset Y values

    # create a a 3x2 plot
    fig, ax = plt.subplots(2,1,figsize=(16,6))

    # plot the X Command
    ax[0].plot(time, data, label='X Command')
    ax[0].set_ylabel('X Command ($\mu m$)')
    ax[0].set_ylim([-50,0])
    ax[0].legend()

    # plot the Y Command
    ax[1].plot(time, data2, label='Y Command')
    ax[1].set_xlabel(time_label)
    ax[1].set_ylabel('Y Command ($\mu m$)')
    ax[1].set_ylim([-50,0])
    ax[1].legend()

    # make all axes share the same x axis
    if not vs_distance:
        for i in range(2):
            for j in range(1):
                ax[i].sharex(ax[0])

        # set the x axis limits
        ax[0].set_xlim([time.min(), time.max()])

    # turn the grid on for all plots
    for i in range(2):
        for j in range(1):
            ax[i].grid(True)

    # set the title
    fig.suptitle(title_string)

    # adjust the spacing
    plt.tight_layout()

    # add a space between the title and the plot area
    plt.subplots_adjust(top=0.92)

    # show the plot
    plt.show(block=True)

if __name__ == '__main__':
    main()