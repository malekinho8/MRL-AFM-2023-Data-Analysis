# The main goal of this code is to plot the CSV data log output from AFM tests. 
# Files are automatically saved to the Dropbox.

# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import click
import os
import pyperclip

# use latex for font rendering
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# constant definitions
loop_delay = 10 # ms

# define a click argument for the input file name, add optional argument for file directory
@click.command()
@click.option('--use-clipboard-for-filename', '-c', default=True, help='Use the clipboard for the filename.')
@click.option('--scale_factor', '-s', default=1.25, help='Scale factor for the data plots y-axis scaling.')
@click.option('--directory', '-d', default='~/Dropbox (MIT)/Qatar 3D Printing/LabVIEW Files (Malek)/2023-Qatar-3D-Printing/afm-data-logs/', help='Directory where the data is stored')
@click.option('--time-units', '-t', default='min', help='Time units for the x-axis of the plots. Options are min, s, and ms.')

def main(use_clipboard_for_filename,scale_factor,directory,time_units):
    """
    Plots the data from the AFM data log CSV file specified by the filename in the user's clipboard. The data log file should be a CSV file with the following format:
        
        data-log-[13-34-28]
    
    The .csv will be appended automatically.
    """
    if use_clipboard_for_filename:
        # get the filename from the clipboard
        filename = pyperclip.paste()
    else:
        input('Please Paste your filename here: ')
    
    # make the direcrory path absolute
    directory = os.path.expanduser(directory)

    # add the .csv extension to the filename
    filename = filename + '.csv'

    # make sure the filename + directory exists
    fullfile = os.path.join(directory,filename)

    # if the file doesn't exist, print an error message and exit
    if not os.path.isfile(fullfile):
        print('File {} does not exist!'.format(fullfile))
        exit()
    
    # use a custom plot function to plot the data
    plot_data(fullfile,scale_factor,time_units)

def plot_data(fullfile, scale_factor,time_units):
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

    # read the data file
    df = pd.read_csv(fullfile, header=None)

    # set the header df to be the first 3 rows
    df_header = df.iloc[:3]

    # set the column names to be the fourth row
    df.columns = df.iloc[3,:]

    # drop the first 4 rows
    df = df.iloc[4:]

    # reset the index
    df = df.reset_index(drop=True)

    # convert the data to numeric
    df = df.apply(pd.to_numeric)

    # get the header information, the first column contains P, I, D, and the second column contains the values, the third column contains LPS, Size X, and Size Y, and the fourth column contains the values, the fifth column contains Z Set Point, Offset X, Offset Y, and the sixth column contains the values
    header = df_header.iloc[:,0].tolist()
    header_values = df_header.iloc[:,1].apply(pd.to_numeric).tolist()
    header2 = df_header.iloc[:,2].tolist()
    header2_values = df_header.iloc[:,3].apply(pd.to_numeric).tolist()
    header3 = df_header.iloc[:,4].tolist()
    header3_values = df_header.iloc[:,5].apply(pd.to_numeric).tolist()

    # specify time sample vector
    time_samples = np.arange(0,df.shape[0],1)

    # using loop delay, define the loop rate
    loop_rate = 1/(loop_delay/1000)

    # using the sample rate, create the time vector
    time = time_samples/loop_rate

    # convert to units of minutes
    time = time/div_factor

    # get the data, where the first column is the X Command, Second is Y Command, Third is Z Command, Fourth is OBD X, Fifth is OBD Y, Sixth is OBD Sum
    data = df.iloc[:,0].tolist()
    data2 = df.iloc[:,1].tolist()
    data3 = df.iloc[:,2].tolist()
    data4 = df.iloc[:,3].tolist()
    error_data = header3_values[0] - np.array(df.iloc[:,4].tolist())
    data6 = np.array(df.iloc[:,5].tolist())

    # create the plot title string. It should include the P, I, D parameter values in scientific notation, the LPS, Size X, and Size Y values, and the Z Set Point, Offset X, and Offset Y values
    title_string = '$K_P$ = {:.1e}, $K_I$ = {:.1e}, $K_D$ = {:.1e}, $LPS$ = {:.2f}, $L_X$ = {:d}~$\\mu m$, $L_Y$ = {:d}~$\\mu m$, $r(t)$ = {:.2f} V, $\\delta_X$ = {:.1f}~$\\mu m$, $\\delta_Y$ = {:.1f}'.format(
        header_values[0], header_values[1], header_values[2],
        header2_values[0], int(header2_values[1]/1000), int(header2_values[2]/1000),
        header3_values[0], header3_values[1]/1000, header3_values[2]/1000
    )

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
    ax[2,0].plot(time, data3, label='Z Command')
    ax[2,0].set_xlabel(time_label)
    ax[2,0].set_ylabel('Z Command ($\mu m$)')
    ax[2,0].set_ylim([-50,50])
    ax[2,0].legend()

    # plot the OBD X
    ax[0,1].plot(time, data4, label='OBD X')
    ax[0,1].set_xlabel(time_label)
    ax[0,1].set_ylabel('OBD X (V)')
    ax[0,1].set_ylim([-data6.max()*scale_factor,data6.max()*scale_factor])
    ax[0,1].legend()

    # plot the error data
    ax[1,1].plot(time, error_data, label='Error ($e(t) = r(t) - y(t)$)')
    ax[1,1].set_xlabel(time_label)
    ax[1,1].set_ylabel('Error ($V$)')
    ax[1,1].set_ylim([-data6.max()*scale_factor,data6.max()*scale_factor])
    ax[1,1].legend()

    # plot the OBD Sum
    ax[2,1].plot(time, data6, label='OBD Sum')
    ax[2,1].set_xlabel(time_label)
    ax[2,1].set_ylabel('OBD Sum (V)')
    ax[2,1].set_ylim([-data6.max()*scale_factor,data6.max()*scale_factor])
    ax[2,1].legend()

    # make all axes share the same x axis
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
    plt.show(block=True)

    # specify the file name from the full file
    filename = os.path.basename(fullfile)

    # specify the output directory
    output_dir = os.path.dirname(fullfile)

    # save the figure to the same directory as the data file, with the same name, but replace the .csv extension with .png and replace data-log with plot-analysis
    time_tag = time_label.split('(')[1].split(')')[0]
    outname = filename.replace('.csv', '.png').replace('data-log', f'plot-analysis-[{time_tag}]')

    # specify save file
    output_file = os.path.join(output_dir, outname)

    fig.savefig(output_file, dpi=300)

if __name__ == '__main__':
    main()
