# The goal of this code is to take a CSV image log from an AFM experiment and visualize it using matplotlib

# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import click
import os
import pyperclip
from utils import *
from mpl_toolkits.axes_grid1 import make_axes_locatable 

# use latex for font rendering, use serif font
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

@click.command()
@click.option('--use-clipboard-for-experiment-folder-name', '-c', default=True, help='Use the clipboard for the experiment folder name.')
@click.option('--topo-low', '-l', default=None, help='The default min color value to use for the topography plots.')
@click.option('--topo-high', '-h', default=None, help='The default max color value to use for the topography plots.')

def main(use_clipboard_for_experiment_folder_name, topo_low, topo_high):
    """
    Plots the data from the AFM data log CSV file specified by the filename in the user's clipboard.
            
    The .csv will be appended automatically.
    """
    # make the direcrory path absolute (user would have to change this depending on their Dropbox folder name)
    directory = os.path.expanduser('~/Dropbox (MIT)/Qatar 3D Printing/LabVIEW Files (Malek)/2023-Qatar-3D-Printing/afm-data-logs/')

    # print the directory
    print('Log Directory: {}'.format(directory))

    # get the filename from the clipboard if available
    if use_clipboard_for_experiment_folder_name:
        # get the filename from the clipboard
        folder_name = pyperclip.paste()
    else:
        input('Please Paste your filename here (no file extension, just the name): ')
    
    # add the .csv extension to the filename
    topo_filename = 'topo-image.csv'

    # make sure the filename + directory exists
    topo_fullfile = os.path.join(directory,folder_name,topo_filename)

    # if the file doesn't exist, print an error message and exit
    if not os.path.isfile(topo_fullfile):
        print('File {} does not exist!'.format(topo_fullfile))
        exit()
    
    # make the error file name
    error_fullfile = os.path.join(directory,folder_name,'error-image.csv')

    # create the topography range
    if topo_low is None and topo_high is None:
        topo_range = None
    else:
        topo_range = [topo_low, topo_high]
    
    # use a custom plot function to plot the data
    plot_image(topo_fullfile, error_fullfile, topo_range)

def plot_image(topo_fullfile, error_fullfile, topo_range=None):
    # read the data from the CSV file
    df = pd.read_csv(topo_fullfile, sep=r'\t', header=None)
    df_error = pd.read_csv(error_fullfile, sep=r'\t', header=None)

    # obtain the path of the experimental log data
    directory = os.path.dirname(topo_fullfile)

    # get the filename without the extension
    filename = 'experiment-info.csv'

    # produce the path to the original experiment
    log_fullfile = os.path.join(directory,filename)

    # read the original experiment data
    log_df = pd.read_csv(log_fullfile, header=None)

    # get the header information
    header = get_log_header_info(log_df)

    # get the experimental title string
    title = get_experiment_info_string(header)

    # get the range of the scan for this experiment from the title
    x_range = float(title.split('L_X$ = ')[1].split('~')[0])
    y_range = float(title.split('L_Y$ = ')[1].split('~')[0])

    # get the xtick range by using the df shape
    xtick_range = df.shape[0]
    ytick_range = df.shape[1]

    # create ticks with 10 equally spaced ticks using the xtick_range and ytick_range
    xticks = np.linspace(0,xtick_range-1,10)
    yticks = np.linspace(0,ytick_range-1,10)

    # get the experiment date string from the folder name
    experiment_time = os.path.basename(directory).split('[')[-1].split(']')[0].replace('-',':')[0:-3]

    # get the image data
    img = df.iloc[:,:].to_numpy().T
    img_error = df_error.iloc[:,:].to_numpy().T

    # create a 2 column subplot
    fig, (ax1, ax2) = plt.subplots(1,2,figsize=(10,5))

    # set the super title (don't set any axes titles)
    fig.suptitle(f'AFM Image - Experiment Performed at {experiment_time}\n{title}')

    # create the topo range
    if topo_range is None:
        topo_range = [img.min(), img.max()]

    # Plot the topo image on the left.
    im1 = ax1.imshow(img, cmap='plasma', clim=topo_range)
    ax1.set_title('Topography Image ($\mu$m)')

    # Define the click event handler
    def onclick(event):
        if event.inaxes == ax1:
            x, y = int(event.xdata), int(event.ydata)
            value = img[y, x]
            ax1.annotate(f"{value:.2f}", (x, y), color='white' if img[y, x] < 0.5 else 'black', 
                        ha='center', va='center')
            fig.canvas.draw()

    # Set ticks.
    ax1.set_xticks(xticks)
    ax1.set_yticks(yticks)
    num_ticks = len(fig.axes[0].get_xticks())
    # make the x and y ranges into vectors for plotting
    x_range = np.round(np.linspace(-x_range/2,x_range/2,num_ticks),2)
    y_range = np.round(np.linspace(y_range/2,-y_range/2,num_ticks),2)

    # Set tick labels.
    ax1.set_xticklabels(x_range)
    ax1.set_yticklabels(y_range)

    # Set axes limits.
    divider = make_axes_locatable(ax1)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im1, cax=cax)

    # plot the error image on the right
    im2 = ax2.imshow(img_error,cmap='plasma')
    ax2.set_title('Error Image (V)')
    ax2.set_xticks(xticks)
    ax2.set_yticks(yticks)
    divider = make_axes_locatable(ax2)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im2, cax=cax)

    # Connect the click event handler
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    # show the plot
    plt.tight_layout()
    plt.show(block=True)

    # # plot the image
    # fig = plt.figure()
    # plt.imshow(img,cmap='plasma')
    # plt.colorbar()
    # plt.title(f'AFM Image - Experiment Performed at {experiment_time}\n{title}')
    # plt.tight_layout()
    # plt.show(block=True)

if __name__ == "__main__":
    main()