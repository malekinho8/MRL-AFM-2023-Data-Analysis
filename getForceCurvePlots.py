import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import numpy as np
import pyperclip
import os
import pandas as pd

# get the folder path from the clipboard
folderPath = "/Users/malek8/Dropbox (MIT)/Qatar 3D Printing/LabVIEW Files (Malek)/2023-Qatar-3D-Printing/afm-data-logs/data-log-[17-13-59]-experiment"

# use latex for font rendering
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# load the data vectors (zCommand, obdyData)
zCommandPath = os.path.join(folderPath, 'z-command.csv')
obdyDataPath = os.path.join(folderPath, 'obd-y.csv')

# load the data vectors
xData = pd.read_csv(zCommandPath, header=None).values
yData = pd.read_csv(obdyDataPath, header=None).values

# Initial plot setup
fig, (ax1, ax2, ax_zoom) = plt.subplots(3, 1, figsize=(10, 8))

# Plotting xData and yData in separate subplots
ax1.plot(xData, marker='.', linestyle='none')
ax1.set_title('Z Command vs. Index')
ax1.set_ylabel('Z Command Data ($\mu$m)')

ax2.plot(yData, marker='.', linestyle='none', color='orange')
ax2.set_title('OBD Y vs. Index')
ax2.set_ylabel('OBD Y (V)')

# make ax1 and ax2 share the same x-axis
ax1.get_shared_x_axes().join(ax1, ax2)

# Plot yData vs xData in the third subplot
ax_zoom.plot(xData, yData, marker='.', linestyle='none', color='green')
ax_zoom.set_title('OBD Y (V) vs. Z Command ($\mu$m (Zoomed)')
ax_zoom.set_xlabel('Z Command ($\mu$m)')
ax_zoom.set_ylabel('OBD Y (V)')

# Function to update the zoomed plot based on the visible range in the first subplot
def onselect(eclick, erelease):
    if eclick.ydata > erelease.ydata:
        eclick.ydata, erelease.ydata = erelease.ydata, eclick.ydata
    if eclick.xdata > erelease.xdata:
        eclick.xdata, erelease.xdata = erelease.xdata, eclick.xdata
    
    ax_zoom.cla()  # Clear the current zoomed plot
    # Redraw the zoomed plot based on the selected range
    slice_range = (np.arange(len(xData)) > eclick.xdata) & (np.arange(len(xData)) < erelease.xdata)
    xDataSlice = xData[slice_range]
    yDataSlice = yData[slice_range]
    ax_zoom.plot(xDataSlice, yDataSlice, marker='.', linestyle='none', color='green')
    ax_zoom.set_title('OBD Y (V) vs. Z Command ($\mu$m) (Zoomed)')
    ax_zoom.set_xlabel('Z Command ($\mu$m)')
    ax_zoom.set_ylabel('OBD Y (V)')
    fig.canvas.draw()

# Connect the selection event to the onselect function
toggle_selector = RectangleSelector(ax1, onselect,
                                    useblit=True,
                                    button=[1, 3],  # Don't use middle button
                                    minspanx=5, minspany=5,
                                    spancoords='pixels',
                                    interactive=True)

# turn on grid for all subplots
ax1.grid(True)
ax2.grid(True)
ax_zoom.grid(True)
plt.tight_layout()
plt.show()