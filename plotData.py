# The main goal of this code is to plot the CSV data log output from AFM tests. 
# Files are automatically saved to the Dropbox.

# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import click

# use latex for font rendering
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# define a click argument for the input file name, add optional argument for file directory
@click.command()
@click.argument('filename', type=click.Path(exists=True), help='The name of the data log file to plot')
@click.option('--directory', '-d', default='~Dropbox (MIT)/Qatar 3D Printing/LabVIEW Files (Malek)/2023-Qatar-3D-Printing/afm-data-logs/', help='Directory where the data is stored')

def main(filename,directory):
    # read the data file
    df = pd.read_csv(filename)

    # use a custom plot function to plot the data
    plot_data(df,directory)

def plot_data(df, output_dir):
    # set the header df to be the first 3 rows
    df_header = df.iloc[:3]

    # set the column names to be the fourth row
    df.columns = df.iloc[3]

    # drop the first 4 rows
    df = df.iloc[4:]

    # reset the index
    df = df.reset_index(drop=True)

    # convert the data to numeric
    df = df.apply(pd.to_numeric)

    # get the header information, the first column contains P, I, D, and the second column contains the values, the third column contains LPS, Size X, and Size Y, and the fourth column contains the values, the fifth column contains Z Set Point, Offset X, Offset Y, and the sixth column contains the values
    header = df_header.iloc[:,0].tolist()
    header_values = df_header.iloc[:,1].tolist()
    header2 = df_header.iloc[:,2].tolist()
    header2_values = df_header.iloc[:,3].tolist()
    header3 = df_header.iloc[:,4].tolist()
    header3_values = df_header.iloc[:,5].tolist()

    # get the data, where the first column is the X Command, Second is Y Command, Third is Z Command, Fourth is OBD X, Fifth is OBD Y, Sixth is OBD Sum
    data = df.iloc[:,0].tolist()
    data2 = df.iloc[:,1].tolist()
    data3 = df.iloc[:,2].tolist()
    data4 = df.iloc[:,3].tolist()
    error_data = df.iloc[:,4].tolist() - header3_values[0]
    data6 = df.iloc[:,5].tolist()

    # create the plot title string. It should include the P, I, D parameter values in scientific notation, the LPS, Size X, and Size Y values, and the Z Set Point, Offset X, and Offset Y values
    title_string = '$K_P$ = {:.1e}, $K_I$ = {:.1e}, $K_D$ = {:.1e}, $LPS$ = {:.1e}, $L_X = {:.1f}~\mu m$, $L_Y = {:.1f}~\mu m$, $R = {:.1f} V$, $\delta_X = {:.1f}~\mu m$, \delta_Y = {:.1f}'.format(
        header_values[0], header_values[1], header_values[2],
        header2_values[0]/1000, header2_values[1]/1000, header2_values[2],
        header3_values[0], header3_values[1]/1000, header3_values[2]/1000
    )

    # create a a 3x2 plot
    fig, ax = plt.subplots(3,2,figsize=(10,16))

    # plot the X Command
    ax[0,0].plot(data, label='X Command')
    ax[0,0].set_title('X Command')
    ax[0,0].set_xlabel('Time (s)')
    ax[0,0].set_ylabel('X Command ($\mu m$)')
    ax[0,0].legend()

    # plot the Y Command
    ax[1,0].plot(data2, label='Y Command')
    ax[1,0].set_title('Y Command')
    ax[1,0].set_xlabel('Time (s)')
    ax[1,0].set_ylabel('Y Command ($\mu m$)')
    ax[1,0].legend()

    # plot the Z Command
    ax[2,0].plot(data3, label='Z Command')
    ax[2,0].set_title('Z Command')
    ax[2,0].set_xlabel('Time (s)')
    ax[2,0].set_ylabel('Z Command ($\mu m$)')
    ax[2,0].legend()

    # plot the OBD X
    ax[0,1].plot(data4, label='OBD X')
    ax[0,1].set_title('OBD X')
    ax[0,1].set_xlabel('Time (s)')
    ax[0,1].set_ylabel('OBD X (V)')
    ax[0,1].legend()

    # plot the error data
    ax[1,1].plot(error_data, label='Error ($e(t) = r(t) - y(t)$)')
    ax[1,1].set_title('Error')
    ax[1,1].set_xlabel('Time (s)')
    ax[1,1].set_ylabel('Error ($V$)')
    ax[1,1].legend()

    # plot the OBD Sum
    ax[2,1].plot(data6, label='OBD Sum')
    ax[2,1].set_title('OBD Sum')
    ax[2,1].set_xlabel('Time (s)')
    ax[2,1].set_ylabel('OBD Sum (V)')
    ax[2,1].legend()

    # set the title
    fig.suptitle(title_string)

    # adjust the spacing
    plt.tight_layout()

    # show the plot
    plt.show()

    # save the figure to the same directory as the data file, with the same name, but replace the .csv extension with .png and replace data-log with plot-analysis
    filename = filename.replace('.csv', '.png').replace('data-log', 'plot-analysis')

    # specify save file
    output_file = os.path.join(output_dir, filename)

    plt.savefig(output_file, dpi=300)

if __name__ == '__main__':
    main()
