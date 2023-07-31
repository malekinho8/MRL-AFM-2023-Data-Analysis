import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# use latex for font rendering, use serif font
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# change font size to 6 for legend
plt.rcParams.update({'font.size': 6})

# Define the paths to the data
data_paths = [
    "/Users/malek8/Dropbox (MIT)/Qatar 3D Printing/Reports/report-data-dump/p=1-data-log-[18-21-49]-experiment",
    "/Users/malek8/Dropbox (MIT)/Qatar 3D Printing/Reports/report-data-dump/p=2-data-log-[18-20-49]-experiment",
    "/Users/malek8/Dropbox (MIT)/Qatar 3D Printing/Reports/report-data-dump/p=3-data-log-[18-19-45]-experiment",
    "/Users/malek8/Dropbox (MIT)/Qatar 3D Printing/Reports/report-data-dump/p=4-data-log-[18-18-23]-experiment",
    "/Users/malek8/Dropbox (MIT)/Qatar 3D Printing/Reports/report-data-dump/p=5-data-log-[18-10-00]-experiment",
    "/Users/malek8/Dropbox (MIT)/Qatar 3D Printing/Reports/report-data-dump/p=6-data-log-[18-16-21]-experiment",
    "/Users/malek8/Dropbox (MIT)/Qatar 3D Printing/Reports/report-data-dump/p=7-data-log-[18-17-23]-experiment",
]

# Define the loop delay in seconds
loop_delay = 0.01  # 10ms

# Set up the subplot figure
fig, axs = plt.subplots(7, 1)


# Loop over the data paths
for i, data_path in enumerate(data_paths):
    # Get the pressure setting from the data path
    pressure_setting = int(data_path.split('=')[1].split('-')[0])

    # Load the data
    data = pd.read_csv(os.path.join(data_path, "pressure-reading.csv"),delimiter=',',skiprows=1,header=None)[0:2100]
    
    # Compute the time for pressure to go from 0.2 psi back to 0 psi
    transition_start = data[(data.iloc[:, 2] == 0) & (data.iloc[:, 2].shift(1) == 0.2)].index[0]
    settling_data = data[transition_start:]
    settling_time_idx = settling_data[(settling_data.iloc[:, 0] <= 0.05 * 0.2)].index[0]
    settling_time = (settling_time_idx - transition_start) * loop_delay

    # Create time variable for plotting
    time = (data.iloc[:, 1]) * loop_delay
    time = time - time[transition_start]

    # Set ylabel for the first subplot only
    if i == 3:
        axs[i].set_ylabel('Pressure (psi)')
        axs[i].set_yticks([0,0.25])
    else:
        axs[i].set_yticks([])
        axs[i].set_yticklabels([])

    # Plotting the data
    axs[i].plot(time, data.iloc[:, 0], label=f'Pressure Reading, Transition Time: {settling_time} s')
    axs[i].plot(time, data.iloc[:, 2], label='Command Pressure')
    axs[i].set_ylim([0, 0.25])
    axs[i].set_xlim([0,5])
    axs[i].legend()


plt.xlabel('Time (s)')
plt.tight_layout()

# Remove vertical space between subplots
plt.subplots_adjust(hspace=-0.02)

plt.show()
