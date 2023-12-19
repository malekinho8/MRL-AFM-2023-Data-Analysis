import matplotlib.pyplot as plt
import pandas as pd

# use latex for font rendering
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# load the data using pd read csv
csv_path = "/Users/malek8/Dropbox (MIT)/Qatar 3D Printing/Reports/mrl-report-23/bioprinting/afm-test-v1/afm-tracking-test.csv"
data = pd.read_csv(csv_path)

# Extract relevant columns
time_data = data['Time (s)']
amplitude_data = data['Amplitude - Plot 0.1']

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(time_data, amplitude_data, label='Amplitude vs Time')
plt.xlabel('Time (s)')
plt.ylabel('PID Z Command (um)')
plt.title('Time vs Amplitude Plot')
plt.legend()
plt.grid(True)
plt.show()
