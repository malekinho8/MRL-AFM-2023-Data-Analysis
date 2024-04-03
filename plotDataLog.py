# The main goal of this code is to plot the CSV data log output from AFM tests. 
# Files are automatically saved to the Dropbox.

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
plt.rc('font', family='serif')

# constant definitions
LOOP_DELAY = 1 # ms

# define a click argument for the input file name, add optional argument for file directory
@click.command()
@click.option('--use-clipboard-for-filename', '-c', default=True, help='Use the clipboard for the filename.')
@click.option('--scale_factor', '-s', default=1.25, help='Scale factor for the data plots y-axis scaling.')
@click.option('--directory', '-d', default='~/Dropbox (MIT)/Qatar 3D Printing/LabVIEW Files (Malek)/2023-Qatar-3D-Printing/afm-data-logs/', help='Directory where the data is stored')
@click.option('--time-units', '-t', default='min', help='Time units for the x-axis of the plots. Options are min, s, and ms.')
@click.option('--vs-distance', '-v', default=False, help='Plot the Z Command vs. X Command data instead of vs. time (default).')
@click.option('--save', '-s', default=True, help='Save the figure to the same directory as the data files.')
@click.option('--save-format', '-f', default='pdf', help='Save format for the figure. Options are png, pdf, and svg.')
@click.option('--save-name', '-n', default='plot-analysis', help='Save name for the figure. The file extension will be appended automatically.')
@click.option('--show-flag','-sh', default=False, help='Show the plot.')

def main(use_clipboard_for_filename,scale_factor,directory,time_units,vs_distance,save,save_format,save_name, show_flag):
    """
    Plots the data from the AFM data log folder of the following format:
        
        data-log-[13-34-28]
    
    The .csv will be appended automatically.
    """
    if use_clipboard_for_filename:
        # get the filename from the clipboard
        folder_name = pyperclip.paste()
    else:
        input('Please Paste your filename here: ')
    
    # make the direcrory path absolute
    directory = os.path.expanduser(directory)

    # add the .csv extension to the filename
    folder_dir = os.path.join(directory,folder_name)

    # if the folder doesn't exist, print an error message and exit
    if not os.path.isdir(folder_dir):
        print('Folder {} does not exist!'.format(folder_dir))
        exit()
    
    # use a custom plot function to plot the data
    plot_data(folder_dir,scale_factor,time_units,vs_distance, save, save_name, save_format, show_flag)

def plot_data(folder_dir, scale_factor,time_units,vs_distance, save, save_name, save_format, show_flag):
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
    z_file = os.path.join(folder_dir,'z-command.csv')
    obdx_file = os.path.join(folder_dir,'obd-x.csv')
    obdy_file = os.path.join(folder_dir,'obd-y.csv')
    obdsum_file = os.path.join(folder_dir,'obd-sum.csv')

    # check if the pressure file exists. If it does, then set a flag to be true
    pressure_file = os.path.join(folder_dir,'pressure.csv')
    pressure_flag = os.path.isfile(pressure_file)

    # specify the rt time samples file
    rt_time_samples_file = os.path.join(folder_dir,'rt-time-samples.csv')

    # get max column length
    # num_cols = get_max_column_length(info_file)

    # get the information dataframe
    info_df = pd.read_csv(info_file, header=None)

    # read the data files
    x_df = pd.read_csv(x_file, header=None)
    y_df = pd.read_csv(y_file, header=None)
    z_df = pd.read_csv(z_file, header=None)
    obdx_df = pd.read_csv(obdx_file, header=None)
    obdy_df = pd.read_csv(obdy_file, header=None)
    obdsum_df = pd.read_csv(obdsum_file, header=None)
    pressure_df = pd.read_csv(pressure_file, header=None) if pressure_flag else None

    # set the header df to be the first 3 rows
    df_header = get_log_header_info(info_df)

    # specify time sample vector
    time_samples = np.arange(0,x_df.shape[0],1)

    # using loop delay, define the loop rate
    loop_rate = 1/(LOOP_DELAY/1000)

    # using the sample rate, create the time vector
    time = time_samples/loop_rate

    # convert to units of minutes
    time = time/div_factor

    # get the data, where the first column is the X Command, Second is Y Command, Third is Z Command, Fourth is OBD X, Fifth is OBD Y, Sixth is OBD Sum
    data = x_df.iloc[:,0].tolist()
    data2 = y_df.iloc[:,0].tolist()
    data3 = z_df.iloc[:,0].tolist()
    data4 = obdx_df.iloc[:,0].tolist()
    data5 = obdy_df.iloc[:,0].tolist()
    data6 = np.array(obdsum_df.iloc[:,0].tolist())

    # create the plot title string. It should include the P, I, D parameter values in scientific notation, the LPS, Size X, and Size Y values, and the Z Set Point, Offset X, and Offset Y values
    title_string = get_experiment_info_string(df_header)

    # create a a 3x2 plot
    fig, ax = plt.subplots(3,2,figsize=(16,6))

    # plot the X Command
    ax[0,0].plot(time, data, label='X Command')
    ax[0,0].set_xlabel(time_label)
    ax[0,0].set_ylabel('X Command ($\mu m$)')
    ax[0,0].set_ylim([-50,50])
    ax[0,0].legend()

    # plot the Y Command
    ax[1,0].plot(time, data2, label='Y Command')
    ax[1,0].set_xlabel(time_label)
    ax[1,0].set_ylabel('Y Command ($\mu m$)')
    ax[1,0].set_ylim([-50,50])
    ax[1,0].legend()

    # plot the Z Command
    if vs_distance:
        z_xlabel = 'Distance ($\mu m$)'
        z_xdata = data
    else:
        z_xlabel = time_label
        z_xdata = time

    ax[2,0].plot(z_xdata, data3, label='Z Command')
    ax[2,0].set_xlabel(z_xlabel)
    ax[2,0].set_ylabel('Z Command ($\mu m$)')
    ax[2,0].set_ylim([-50,50])
    ax[2,0].legend()

    # plot the OBD X
    ax[0,1].plot(time, data4, label='OBD X')
    ax[0,1].set_xlabel(time_label)
    ax[0,1].set_ylabel('OBD X ($V$)')
    ax[0,1].set_ylim([-data6.max()*scale_factor,data6.max()*scale_factor])
    ax[0,1].legend()

    # plot the error data
    # ax[1,1].plot(time, error_data, label='Error ($e(t) = r(t) - y(t)$)')
    # ax[1,1].set_xlabel(time_label)
    # ax[1,1].set_ylabel('Error ($V$)')
    # ax[1,1].set_ylim([-data6.max()*scale_factor,data6.max()*scale_factor])
    # ax[1,1].legend()

    # Plot the OBD Y
    ax[1,1].plot(time, data5, label='OBD Y')
    ax[1,1].set_xlabel(time_label)
    ax[1,1].set_ylabel('OBD Y ($V$)')
    ax[1,1].set_ylim([-data6.max()*scale_factor,data6.max()*scale_factor])
    ax[1,1].legend()

    # plot the OBD Sum
    ax[2,1].plot(time, data6, label='OBD Sum')
    ax[2,1].set_xlabel(time_label)
    ax[2,1].set_ylabel('OBD Sum ($V$)')
    ax[2,1].set_ylim([-data6.max()*scale_factor,data6.max()*scale_factor])
    ax[2,1].legend()

    # make all axes share the same x axis
    if not vs_distance:
        for i in range(3):
            for j in range(2):
                ax[i,j].sharex(ax[0,0])

        # set the x axis limits
        ax[0,0].set_xlim([time.min(), time.max()])

    # turn the grid on for all plots
    for i in range(3):
        for j in range(2):
            ax[i,j].grid(True)

    # set the title
    fig.suptitle(title_string)

    # adjust the spacing
    plt.tight_layout()

    # add a space between the title and the plot area
    plt.subplots_adjust(top=0.92)

    # show the plot
    if not show_flag:
        plt.show(block=False)
    else:
        plt.show(block=True)

    # if the pressure flag is true, then plot the pressure data as well
    if pressure_flag:
        # initialize a new figure with 4 rows and 1 column
        fig2, ax2 = plt.subplots(4,1,figsize=(16,6))

        # get the pressure data
        pressure_data = pressure_df.iloc[:,0].tolist()

        # get the time samples based on the first/last time sample of the fpga time samples and interpolate based on the number of pressure samples
        initial_time = time[0]
        final_time = time[-1]
        pressure_time_samples = np.linspace(initial_time, final_time, len(pressure_data))

        # in the first row plot the pressure data
        ax2[0].plot(pressure_time_samples, pressure_data)
        ax2[0].set_xlabel(time_label)
        ax2[0].set_ylabel('Pressure (mbar)')
        ax2[0].set_title(title_string)
        ax2[0].grid(True)

        # in the second row plot the OBD Y data
        ax2[1].plot(time, data5)
        ax2[1].set_xlabel(time_label)
        ax2[1].set_ylabel('OBD Y ($V$)')
        ax2[1].grid(True)

        # in the third row plot the OBD X data
        ax2[2].plot(time, data4)
        ax2[2].set_xlabel(time_label)
        ax2[2].set_ylabel('OBD X ($V$)')
        ax2[2].grid(True)

        # in the fourth row plot the OBD Sum data
        ax2[3].plot(time, data6)
        ax2[3].set_xlabel(time_label)
        ax2[3].set_ylabel('OBD Sum ($V$)')
        ax2[3].grid(True)

        # make all axes share the same x axis
        for i in range(4):
            ax2[i].sharex(ax2[0])

        # show the plot
        if not show_flag:
            plt.show(block=False)
        else:
            plt.show(block=True)

    if save:
        # specify the directory to save the figure (should be the same as the data log files)
        save_dir = folder_dir

        # specify the name of the figure to save by adding the file extension
        save_name = save_name + '.' + save_format

        # save the figure using fig
        fig.savefig(os.path.join(save_dir,save_name), format=save_format, dpi=600)

        # save the pressure data if the pressure flag is true
        if pressure_flag:
            # specify the pressure file name
            pressure_save_name = 'pressure.' + save_format

            # save the pressure data
            fig2.savefig(os.path.join(save_dir,pressure_save_name), format=save_format, dpi=600)

if __name__ == '__main__':
    main()