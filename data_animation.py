from matplotlib import pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import math
import copy
import os
from matplotlib.animation import FuncAnimation, writers
# from mat
from scipy.signal import savgol_filter

import config_setup
import config_ani

FRAME_RATE = config_ani.FRAME_RATE # fps
TIME_LENGTH = config_ani.ENDING_TIME - config_ani.STARTING_TIME # seconds
FRAME_INTERVAL = math.floor(1000 / FRAME_RATE) # ms
FRAME_LENGTH = FRAME_RATE * TIME_LENGTH # frames
STARTING_TIME = config_ani.STARTING_TIME # The time at which the data starts recording
ENDING_TIME = config_ani.ENDING_TIME # The time at which the data stops recording
# A time varaible to track how far through the animation we are in seconds, used to determine what data to put into the plots

plt.rcParams['animation.ffmpeg_path'] = config_setup.FFMPEG_PATH
m = pd.read_csv(os.path.join(config_setup.DATA_WORKING_DIR, config_ani.DATA_FILE_NAME))

# Set the dimensions of the plot
plt.rcParams["figure.figsize"] = (config_ani.PLOT_WIDTH, config_ani.PLOT_HEIGHT)

# Timestap as a base refference
time_refference = m['Timestamp']
plotted_time = []
time_cursor = 0 # The index of the current time refference, starts at -1 since no data is plotted
time = STARTING_TIME

fig, _ = plt.subplots()

class PlotAxis:
    def __init__(self, name, unit, min, max,primary=False):
        self.name = name
        self.unit = unit
        if primary:
            self.axis = plt.gca()
        else:
            self.axis = plt.twinx()
        self.axis.set_ylabel(f"{name} ({unit})")
        self.axis.set_xlabel('Time (s)')
        self.axis.set_xlim(STARTING_TIME, ENDING_TIME)
        self.axis.set_ylim(min, max)


# Each data item that will have a curve
class PlotItem:
    def __init__(self, display_name, csv_colum, axis_class, color,filtered=True):
        self.name = display_name
        self.csv_colum = csv_colum
        self.axis = axis_class.axis
        self.color = color

        self.data = m[csv_colum]
        if filtered:
                self.data = savgol_filter(self.data, 10, 2)
        self.plotted_data = [] # Starts off empty and grows over time

        # Create the empty line object that will be filled out as the animiation runs
        self.line = self.axis.plot([], [], label = f"{display_name}", color = color)[0]

    def tick(self): # a tick pushing the data forward one recording frame, and this might happen multiple times per animation frame'
        self.plotted_data.append(self.data[time_cursor])
        self.line.set_data(plotted_time, self.plotted_data)

################# CHANGE ME TO SET WHAT IS PLOTTED #######################
# the axies should all be on the same figure, just have differnt y axies for different units
unit_axies = { # a dictionary for axies where the key is the unit it's in, and the value is the axis object
    "psi/lbf": PlotAxis("Pressure / Thrust", "psi/lbf", 0, 1000,primary=True),
    "kg": PlotAxis("Mass", "kg", 0, 25),
}

## IMPORTANT: THERE MUST BE AT LEAST ONE PRIMARY AXIS, IN THE UNIT AXIES OTHERWISE THINGS MIGHT LOOK WACK

lines = [
    PlotItem("Honeywell S-type - Ox Tank", "Honeywell S-type - Ox Tank", unit_axies["kg"], "black"),
    PlotItem("PT-4 Injector Oxidizer", "PT-4 Injector Oxidizer", unit_axies["psi/lbf"], "blue"),
]

###########################################################################

################# CHANGE ME TO CHANGE ESTHEICS ABOUT THE PLOT #######################

figure_title = "LCF1" # The title of the plot

grid = True

legend_location = "lower left" # Where the legend is located, see https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.legend.html for more info
global_font = {'family':  'helvetica'} # The font of the legend

###########################################################################



# The method for this timing to work is that the animation runs at a certain framerate (converted to a time interval), and a time length
# For each frame, it'll step up the running time variable by the time interval
# It must then add all the data who's recorded timestamp is smaller than or equal to the running time variable
def animate(frame_number):
    global time_cursor
    global time
    time += FRAME_INTERVAL/1000 # time in seconds having a frame interval added to it in ms, so must be adjusted

    while time_refference[time_cursor] <= time: # while the time at the cursor is before what needs to be plotted, keep adding data
        # Add a recording frame to the ploted time, then to each value
        plotted_time.append(time_refference[time_cursor])
        
        for line in lines:
            line.tick()

        time_cursor += 1


# Generate one together legend for each of the curves
handles = []
labels = []
for axis in unit_axies.values():
    h, l = axis.axis.get_legend_handles_labels()
    l_with_units = [f"{l[0]} ({axis.unit})"]
    handles += h
    labels += l_with_units

# Set all the esthetics of the plot
plt.title(figure_title, fontdict=global_font)
plt.legend(handles, labels, loc=legend_location, prop=global_font)
if grid: plt.grid()


SKIP_TO_FINAL = False # Allows the entire animation step to be skipped and just show you what the final plot looks like
PREVIEW = False # Allows the animation to be previewed instead of saving it to a file

if SKIP_TO_FINAL:
    for i in range(FRAME_LENGTH):
        animate(i)
    print('Animation skipped, showing final plot')
    plt.show()
else:
    ani = animation.FuncAnimation(fig, animate, interval = FRAME_INTERVAL, frames = FRAME_LENGTH, repeat = False) 

    if not PREVIEW: # save the file
        file = os.path.join(config_setup.DATA_WORKING_DIR, f"{config_ani.DATA_FILE_NAME[:-4]}_animated.mp4")
        writer = animation.FFMpegWriter(fps=FRAME_RATE,metadata=dict(artist='Waterloo Rocketry Team')) 

        print(f"Saving video, this will take at least {TIME_LENGTH}s...")
        ani.save(file, writer=writer)
        print('Video saved sucessfully')
    else:
        plt.show()
