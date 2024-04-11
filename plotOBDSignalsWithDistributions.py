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
from functools import partial

# use latex for font rendering
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# constant definitions
LOOP_DELAY = 100 # ms

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
    plot_obd_with_distributions(folder_dir,scale_factor,time_units,vs_distance, save, save_name, save_format, show_flag)

def plot_obd_with_distributions(folder_dir, scale_factor,time_units,vs_distance, save, save_name, save_format, show_flag):
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
    metadata_path = os.path.join(folder_dir,'metadata.txt')
    obdx_file = os.path.join(folder_dir,'obd-x.csv')
    obdy_file = os.path.join(folder_dir,'obd-y.csv')
    obdsum_file = os.path.join(folder_dir,'obd-sum.csv')

    # get the loop delay from the metadata file
    if os.path.exists(metadata_path):
        LOOP_DELAY = 1/get_loop_delay(metadata_path) * 1000 # ms

    # get the information dataframe
    info_df = pd.read_csv(info_file, header=None)

    # read the data files
    obdx_df = pd.read_csv(obdx_file, header=None)
    obdy_df = pd.read_csv(obdy_file, header=None)
    obdsum_df = pd.read_csv(obdsum_file, header=None)

    # set the header df to be the first 3 rows
    df_header = get_log_header_info(info_df)

    # specify time sample vector
    time_samples = np.arange(0,obdx_df.shape[0],1)

    # using loop delay, define the loop rate
    loop_rate = 1/(LOOP_DELAY/1000)

    # using the sample rate, create the time vector
    time = time_samples/loop_rate

    # convert to units of minutes
    time = time/div_factor

    # get the data, where the first column is the X Fourth is OBD X, Fifth is OBD Y, Sixth is OBD Sum
    data4 = np.array(obdx_df.iloc[:,0])
    data5 = np.array(obdy_df.iloc[:,0])
    data6 = np.array(obdsum_df.iloc[:,0])

    # create the plot title string. It should include the P, I, D parameter values in scientific notation, the LPS, Size X, and Size Y values, and the Z Set Point, Offset X, and Offset Y values
    title_string = get_experiment_info_string(df_header)

    # create a a 3x2 plot
    fig, ax = plt.subplots(3,2,figsize=(16,6))

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

    # plot the distribution of X
    ax[0,0].hist(data4, orientation='horizontal', bins=50)
    ax[0,0].set_title('Distribution of OBD X')
    # get the mean and standard deviation of the data
    mean, std = np.mean(data4), np.std(data4)
    legend_string = r"$\mu = {:.2f}$, $\sigma = {:.2f}$".format(mean,std)
    ax[0,0].legend([legend_string])

    # plot the distribution of Y
    ax[1,0].hist(data5, orientation='horizontal', bins=50)
    ax[1,0].set_title('Distribution of OBD Y')
    # get the mean and standard deviation of the data
    mean, std = np.mean(data5), np.std(data5)
    legend_string = r"$\mu = {:.2f}$, $\sigma = {:.2f}$".format(mean,std)
    ax[1,0].legend([legend_string])

    # plot the distribution of Sum
    ax[2,0].hist(data6, orientation='horizontal', bins=50)
    ax[2,0].set_title('Distribution of OBD Sum')
    # get the mean and standard deviation of the data
    mean, std = np.mean(data6), np.std(data6)
    legend_string = r"$\mu = {:.2f}$, $\sigma = {:.2f}$".format(mean,std)
    ax[2,0].legend([legend_string])

    # define partial functions for each axis
    update_distribution_x = partial(update_distribution, ax[0,0], ax[0,1], time, data4)
    update_distribution_y = partial(update_distribution, ax[1,0], ax[1,1], time, data5)
    update_distribution_sum = partial(update_distribution, ax[2,0], ax[2,1], time, data6)

    # Connect the update_distribution function to the xlim_changed event for each axis
    ax[0,1].callbacks.connect('xlim_changed', update_distribution_x)
    ax[1,1].callbacks.connect('xlim_changed', update_distribution_y)
    ax[2,1].callbacks.connect('xlim_changed', update_distribution_sum)

    # make all the OBD signals share the same x axis
    for i in range(3):
        ax[i,1].sharex(ax[0,1])

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

    if save:
        # specify the directory to save the figure (should be the same as the data log files)
        save_dir = folder_dir

        # specify the name of the figure to save by adding the file extension
        save_name = save_name + '.' + save_format

        # save the figure using fig
        fig.savefig(os.path.join(save_dir,save_name), format=save_format, dpi=600)

if __name__ == '__main__':
    main()