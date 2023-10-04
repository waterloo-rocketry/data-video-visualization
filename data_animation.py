from matplotlib import pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import math
import copy
import os
from matplotlib.animation import FuncAnimation, writers
# from mat
from scipy.signal import savgol_filter

FRAME_RATE = 30 # fps
TIME_LENGTH = 60 # seconds
FRAME_INTERVAL = math.floor(1000 / FRAME_RATE) # ms
FRAME_LENGTH = FRAME_RATE * TIME_LENGTH # frames

#FEATUREADD: make an ability to plot the final graph to see if it looks like what we want

#FIXME: make this read from a config file
plt.rcParams['animation.ffmpeg_path'] = r"C:\Users\AA\Desktop\FFMPEG\bin\ffmpeg.exe"

#FIXME: make this read from a config file
# Needs to be configured depending on what headings are given to the data
m = pd.read_csv("working_directory/lcf1.csv")

STARTING_TIME = m['Timestamp'][0] # The time at which the data starts recording

# FIXME: TO BE CLEANED UP AND MODULARIZED
fig = plt.figure()
ax1 = fig.add_subplot(111)
# ax1.set_xlim(0, 20)
# ax1.set_ylim(-100, 3000)

# Timestap as a base refference
time_refference = m['Timestamp']
plotted_time = []
time_cursor = 0 # The index of the current time refference, starts at -1 since no data is plotted

# A time varaible to track how far through the animation we are in seconds, used to determine what data to put into the plots
time = STARTING_TIME

# Each data item
class PlotItem:
    def __init__(self, display_name, csv_colum, unit, color,filtered=True):
        self.name = display_name
        self.csv_colum = csv_colum
        self.unit = unit
        self.color = color

        self.data = m[csv_colum]
        if filtered:
                self.data = savgol_filter(self.data, 10, 2)
        self.plotted_data = [] # Starts off empty and grows over time

        # Create the empty line object that will be filled out as the animiation runs
        self.line = ax1.plot([], [], label = f"{display_name} ({unit})", color = color)[0]

    def tick(self): # a tick pushing the data forward one recording frame, and this might happen multiple times per animation frame'
        self.plotted_data.append(self.data[time_cursor])
        self.line.set_data(plotted_time, self.plotted_data)

lines = []

tankMass = PlotItem("Honeywell S-type - Ox Tank", "Honeywell S-type - Ox Tank", "kg", "black")
# ccPressure = PlotItem("PT-3 CC 2", "PT-3 CC", "psi", "orange")
# # ccPressureUnfiltered = PlotItem("PT-3 CC Unfiltered", "PT-3 CC", "psi", "green",filtered=False)
# thrust = PlotItem("Thrust", "Thrust", "lbf", "red")

lines.append(tankMass)
# lines.append(ccPressure)
# # lines.append(ccPressureUnfiltered)
# lines.append(thrust)

#FIXME: make it easy to set which axies which lines are on
ax1.set_xlim(STARTING_TIME, STARTING_TIME+TIME_LENGTH) # add a way to change what time interval we're looking at easily, espcially given that often the recorded data starts like at very big numbers
#FIXME: config the axies
ax1.set_ylim(0, 25)
ax1.set_ylabel('psi/lbf')

#FIXME: legends for the axies need to be better (x axis)

ax1.legend(loc = 'upper left')
# ax2.legend(loc = 'upper right')


def animate(frame_number):
    global time_cursor
    global time
    time += FRAME_INTERVAL/1000 # time in seconds having a frame interval added to it in ms, so must be adjusted

    while time_refference[time_cursor] <= time: # while the time at the cursor is before what needs to be plotted
        # Add a recording frame to the plot
        plotted_time.append(time_refference[time_cursor])
        
        for line in lines:
            line.tick()

        time_cursor += 1

    # each line will be update by the update functions and reflected in the animation


# The interval and frames have to add up to the fps set later for the video to be real-time accurate

# Get the current working directory
cwd = os.getcwd()
file = f"{cwd}/working_directory/test.mp4"
writer = animation.FFMpegWriter(fps=FRAME_RATE,metadata=dict(artist='Waterloo Rocketry Team')) 
ani = animation.FuncAnimation(fig, animate, interval = FRAME_INTERVAL, frames = FRAME_LENGTH, repeat = False) 
print(f"Saving video, this will take {TIME_LENGTH}s...")
plt.show()
# ani.save(file, writer=writer) # Comment out this line to get a 'preview' via the matplotlib plot
print('Video saved sucessfully')


# The method for this timing to work is that the animation runs at a certain framerate (converted to a time interval), and a time length
# For each frame, it'll step up the running time variable by the time interval
# It must then add all the data who's recorded timestamp is smaller than or equal to the running time variable