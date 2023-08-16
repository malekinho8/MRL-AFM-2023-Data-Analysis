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
import matplotlib.animation as animation
import threading
from matplotlib.collections import LineCollection
from utils import *

# use latex for font rendering
mpl.rcParams.update(mpl.rcParamsDefault)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# constant definitions
LOOP_DELAY = 1 # ms
# prev_index = 0 # this keeps track of the previous index to draw the line from

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
    # plot_command_animation(folder_dir,scale_factor,time_units,vs_distance,title_string)

    plot_custom_command_animation(folder_dir,title_string)

def plot_command_animation(folder_dir, scale_factor,time_units,vs_distance,title_string):
    # start the timer on a separate thread
    timer = Timer()
    timer_thread = threading.Thread(target=timer.start)

    # Function to initialize the plot
    def animation_init():
        line.set_data([], [])
        return line,
    
    def update(frame):
        global prev_index
        max_index = len(normalized_timestamps) - 1
        current_index = min(np.searchsorted(normalized_timestamps, timer.current_time), max_index)
        if current_index != max_index:
            line.set_data(x_data[:current_index],y_data[:current_index])
        else:
            timer.stop()
        return line,
        
    # define data filenames
    info_file = os.path.join(folder_dir,'experiment-info.csv')
    x_file = os.path.join(folder_dir,'x-command.csv')
    y_file = os.path.join(folder_dir,'y-command.csv')
    pressure_file = os.path.join(folder_dir,'pressure.csv')
    timestamp_file = os.path.join(folder_dir,'time-samples.csv')

    # load the dfs
    x_df = pd.read_csv(x_file, delimiter = ',', header = None)
    y_df = pd.read_csv(y_file, delimiter = ',', header = None)
    pressure_df = pd.read_csv(pressure_file, delimiter = ',', header = None)
    timestamp_df = pd.read_csv(timestamp_file, delimiter = ',', header = None)

    # Assuming timestamp_df contains the timestamps in seconds
    total_duration = timestamp_df.iloc[-1, 0] - timestamp_df.iloc[0, 0]
    normalized_timestamps = (timestamp_df.iloc[:, 0] - timestamp_df.iloc[0, 0])
    average_interval = (total_duration * 1000) / len(timestamp_df)

    # get the data, where the first column is the X Command, Second is Y Command, Third is Z Command, Fourth is OBD X, Fifth is OBD Y, Sixth is OBD Sum
    x_data = x_df.iloc[:, 0].tolist()
    y_data = y_df.iloc[:,0].tolist()
    # create the plot title string. It should include the P, I, D parameter values in scientific notation, the LPS, Size X, and Size Y values, and the Z Set Point, Offset X, and Offset Y values

    # create a a 3x2 plot
    fig, ax = plt.subplots(1,1,figsize=(8,8))

    # plot the X Command
    ax.set_ylabel('X Command ($\mu m$)')
    ax.set_ylim([-55,55])
    ax.set_xlim([-55,55])
    ax.grid(True)

    line, = ax.plot(x_data,y_data,'-',linewidth=2,color='blue')

    # start the timer
    timer_thread.start()

    # Create the animation object
    ani = animation.FuncAnimation(fig, update, frames=len(x_data), init_func=animation_init, blit=True, interval=50,cache_frame_data=True, repeat=False)

    # set the title
    fig.suptitle(title_string)

    # adjust the spacing
    plt.tight_layout()

    # add a space between the title and the plot area
    plt.subplots_adjust(top=0.92)

    # show the plot
    plt.show(block=True)

    timer.stop()
    timer_thread.join()

def plot_custom_command_animation(folder_dir,title_string):
    # Start the timer on a separate thread
    # timer = Timer(dt=0.1)
    # timer_thread = threading.Thread(target=timer.start)

    # define data filenames
    info_file = os.path.join(folder_dir,'experiment-info.csv')
    x_file = os.path.join(folder_dir,'x-command.csv')
    y_file = os.path.join(folder_dir,'y-command.csv')
    pressure_file = os.path.join(folder_dir,'pressure.csv')
    timestamp_file = os.path.join(folder_dir,'time-samples.csv')

    # load the dfs
    x_df = pd.read_csv(x_file, delimiter = ',', header = None)
    y_df = pd.read_csv(y_file, delimiter = ',', header = None)
    pressure_df = pd.read_csv(pressure_file, delimiter = ',', header = None)
    timestamp_df = pd.read_csv(timestamp_file, delimiter = ',', header = None)

    # Assuming timestamp_df contains the timestamps in seconds
    total_duration = timestamp_df.iloc[-1, 0] - timestamp_df.iloc[0, 0]
    normalized_timestamps = np.array(timestamp_df.iloc[:, 0] - timestamp_df.iloc[0, 0])

    x_data = np.array(x_df.iloc[:, 0])
    y_data = np.array(y_df.iloc[:,0])

    # specify lines to be stored 
    lines = []

    # initialize the figure
    fig, ax = plt.subplots(1,1,figsize=(8,8))
    ax.set_xlabel('X Command ($\mu m$)')
    ax.set_ylabel('Y Command ($\mu m$)')
    ax.set_ylim([-55,55])
    ax.set_xlim([-55,55])
    ax.grid(True)
    fig.suptitle(title_string)
    plt.tight_layout()

    fig.canvas.draw()
    background = fig.canvas.copy_from_bbox(ax.bbox) # cache the background

    plt.show(block=False)
    
    # wait a bit to make sure everything is initialized
    time.sleep(0.5)

    segments = []
    colors = []
    linewidths = []
    linestyles = []

    # timer_thread.start()
    prev_index = 0
    elapsed_time = 0
    while elapsed_time < normalized_timestamps[-1]:
        begin = time.time()
        max_index = len(normalized_timestamps) - 1
        current_index = min(np.searchsorted(normalized_timestamps, elapsed_time), max_index)
        
        if prev_index != current_index:
            # Define the segment and its properties
            segment = [(x_data[i], y_data[i]) for i in range(prev_index, current_index+1)]
            segments.append(segment)
            
            color = 'blue' if np.array(pressure_df)[current_index][0] == 0 else 'limegreen'
            colors.append(color)

            lw = 1 if color == 'blue' else 2
            linewidths.append(lw)

            linestyle = '--' if color == 'blue' else '-'
            linestyles.append(linestyle)

            # Create or update the LineCollection
            lc = LineCollection(segments, colors=colors, linewidths=linewidths, linestyles=linestyles)
            
            ax.clear()  # Clear the axis
            ax.add_collection(lc)  # Add the line collection
            ax.set_xlim([-55, 55])
            ax.set_ylim([-55, 55])
            ax.set_xlabel('X Command ($\mu m$)')
            ax.set_ylabel('Y Command ($\mu m$)')
            ax.grid(True)
            
            fig.canvas.restore_region(background)
            ax.draw_artist(lc)
            fig.canvas.blit(ax.bbox)
            
            prev_index = current_index

        plt.pause(0.001)

        elapsed_time += time.time() - begin

    plt.show()

if __name__ == '__main__':
    main()