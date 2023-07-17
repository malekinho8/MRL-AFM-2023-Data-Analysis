# main goal of this script is to check my scan command math that I am using in LabVIEW to control probe/sample
# interaction. It's a bit of a mind-bender because we are actuating the sample and not the probe.

import numpy as np
import matplotlib.pyplot as plt
import time

# specify the amount of time to wait between each loop iteration (basically specifying how fast to run the loop)
loopDelay = 0.01 # units: seconds --> clock rate = 1/loopDelay
clockRate = 1/loopDelay # units: Hz
N = 1000 # number of loop iterations

# print the loop delay and clock rate
print(f'\n\nLoop delay: {loopDelay} seconds')
print(f'Loop rate: {clockRate} loops/second\n')

# define the triangle wave constants
xOffset = 30000
yOffset = 30000
xRange = 10000
yRange = 10000
xFreq = 1 # Hz
yFreq = 0.1 # Hz
xPeriod = 1/xFreq # seconds per cycle
yPeriod = 1/yFreq # seconds per cycle

# calculate the triangle wave amplitudes
xAmp = xRange/2
yAmp = yRange/2

# convert amps and offsets to units of microns (divide by 1000)
xAmp = xAmp/1000
yAmp = yAmp/1000
xOffset = xOffset/1000
yOffset = yOffset/1000

# get the amount of time between each loop iteration
loop_times = []
for i in range(0,1000):
    t0 = time.time()
    t1 = time.time()
    loop_times.append(t1-t0)

# calculate the average clock period
baseClockPeriod = np.mean(loop_times) # units: seconds per clock cycle

# print the average clock period
print(f'\n\nAverage clock period: {baseClockPeriod} seconds per loop iteration')

# calculate the average clock rate
baseClockRate = 1/baseClockPeriod # units: clock cycles per second

# print the average clock rate
print(f'\n\nAverage clock rate: {baseClockRate} Hz')

# assert that the user specified loopDelay is less than the baseClockPeriod
assert loopDelay > baseClockPeriod, "loopDelay must be less than the baseClockPeriod"

# calcuate the corrected x and y freqyuencies/periods
xPeriodCorrected = xPeriod*clockRate
yPeriodCorrected = yPeriod*clockRate
xFreqCorrected = 1/xPeriodCorrected
yFreqCorrected = 1/yPeriodCorrected

# print the corrected x and y frequencies/periods
print(f'\n\nCorrected x frequency: {xFreqCorrected} cycles per loop iteration')
print(f'Corrected y frequency: {yFreqCorrected} cycles per loop iteration')
print(f'Corrected x period: {xPeriodCorrected} loop iterations per cycle')
print(f'Corrected y period: {yPeriodCorrected} loop iterations per cycle\n')


# define x and y command functions
def xCommand(Amp,fi,offset,Ti,i):
    return 4*Amp*fi*i - Amp + offset if i >= 0 and i < Ti/2 else -4*Amp*fi*i + 3*Amp + offset 

def yCommand(Amp,fi,offset,Ti,i):
    return -4*Amp*fi*i + Amp + offset if i >= 0 and i < Ti/2 else 4*Amp*fi*i - 3*Amp + offset

# initialize the x and y commands
xCommands = []
yCommands = []

# perform the main loop
i = -1
ix = -1
iy = -1
while i < N:
    # get the current time
    t0 = time.time()

    # specify the loop iteration
    ix = ix + 1 if ix < xPeriodCorrected else 0
    iy = iy + 1 if iy < yPeriodCorrected else 0
    i += 1

    print(f'ix: {ix}, iy: {iy}')

    # calculate the current x and y commands
    xCommandCurrent = xCommand(xAmp,xFreqCorrected,xOffset,xPeriodCorrected,ix)
    yCommandCurrent = yCommand(yAmp,yFreqCorrected,yOffset,yPeriodCorrected,iy)

    # print the current x and y commands
    print(f'xCommandCurrent: {xCommandCurrent}, yCommandCurrent: {yCommandCurrent}')

    # append the current x and y commands to the x and y commands lists
    xCommands.append(xCommandCurrent)
    yCommands.append(yCommandCurrent)

    # get the current time
    t1 = time.time()

    # calculate the time to wait before the next loop iteration
    waitTime = loopDelay - (t1-t0)

    print(f'waitTime: {waitTime}')

    # wait until the next loop iteration
    time.sleep(waitTime)

# plot the x and y commands in a 2x1 subplot
fig, ax = plt.subplots(2,1)

# plot the x commands
ax[0].plot(xCommands)
ax[0].set_title('xCommands')

# plot the y commands
ax[1].plot(yCommands)
ax[1].set_title('yCommands')

# show the plot
plt.show()