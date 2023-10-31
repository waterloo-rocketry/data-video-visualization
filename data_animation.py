from matplotlib import pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import math
import os
from matplotlib.animation import FuncAnimation
from scipy.signal import savgol_filter

try:
    import config.config_setup as config_setup
except ModuleNotFoundError:
    print(
        "config_setup.py not found, please copy config_setup_example.py to config_setup.py" +\
            "and set your values there"
    )
    exit()

try:
    import config.config_ani as config_ani
except ModuleNotFoundError:
    print(
        "config_ani.py not found, please copy config_ani_example.py to config_ani.py and" +\
             " set your values there. See README.md for instructions on how to set configuration"
    )
    exit()

FRAME_RATE = config_ani.FRAME_RATE  # fps
STARTING_TIME = config_ani.STARTING_TIME  # The time at which the data starts recording
if config_ani.ENDING_TIME == None:
    ENDING_TIME = STARTING_TIME + config_ani.LENGTH_TIME
else:
    ENDING_TIME = config_ani.ENDING_TIME  # The time at which the data stops recording

TIME_LENGTH = ENDING_TIME - STARTING_TIME  # seconds
FRAME_INTERVAL = math.floor(1000 / FRAME_RATE)  # ms
FRAME_LENGTH = FRAME_RATE * TIME_LENGTH  # frames

FILTERING_STRENGTH = (config_ani.FILTERING_STRENGTH)  # Size of savgol filter

plt.rcParams["animation.ffmpeg_path"] = config_setup.FFMPEG_PATH
m = pd.read_csv(os.path.join(config_setup.DATA_WORKING_DIR, config_ani.DATA_FILE_NAME))

# Set the dimensions of the plot
plt.rcParams["figure.figsize"] = (config_ani.PLOT_WIDTH, config_ani.PLOT_HEIGHT)

# Timestap as a base refference
time_refference = m["Timestamp"]
plotted_time = []
time_cursor = 0
time = STARTING_TIME  # animiation progress in seconds

fig, _ = plt.subplots()


class PlotAxis:
    def __init__(self, display_name, unit, min, max, primary=False):
        self.display_name = display_name
        self.unit = unit
        if primary:
            self.axis = plt.gca()
        else:
            self.axis = plt.twinx()
        self.axis.set_ylabel(f"{display_name} ({unit})")
        self.axis.set_xlabel("Time (s)")
        starting_time_actual = STARTING_TIME - config_ani.START_TIME_GRAPHICAL_OFFSET
        ending_time_actual = ENDING_TIME - config_ani.START_TIME_GRAPHICAL_OFFSET
        self.axis.set_xlim(starting_time_actual, ending_time_actual)
        self.axis.set_ylim(min, max)


# Each data item that will have a curve
class PlotItem:
    def __init__(self, display_name, csv_colum, axis_class, color, filtered=True):
        self.name = display_name
        self.csv_colum = csv_colum
        self.axis = axis_class.axis
        self.color = color

        self.data = m[csv_colum]
        if filtered:
            self.data = savgol_filter(self.data, FILTERING_STRENGTH, 2)
        self.plotted_data = []  # Starts off empty and grows over time

        # Create the empty line object that will be filled out as the animiation runs
        self.line = self.axis.plot([], [], label=f"{display_name}", color=color)[0]

    """a tick pushing the data forward one recording frame, and this might happen multiple 
    times per animation frame"""
    def tick(self):
        self.plotted_data.append(self.data[time_cursor])
        plotted_time_modified = [ts - config_ani.START_TIME_GRAPHICAL_OFFSET for ts in plotted_time]
        self.line.set_data(plotted_time_modified, self.plotted_data)
        return self.line


# Import graphing settings from config
unit_axies = {}

for axis_name, axis_config in config_ani.AXIES.items():
    unit_axies[axis_name] = PlotAxis(
        axis_config["display_name"],
        axis_config["unit"],
        axis_config["min"],
        axis_config["max"],
        axis_config["primary"],
    )

lines = []

for item_name, item_config in config_ani.PLOT_ITEMS.items():
    lines.append(
        PlotItem(
            item_name,
            item_config["csv_colum"],
            unit_axies[item_config["axis"]],
            item_config["color"],
            item_config["filtered"],
        )
    )

figure_title = config_ani.FIGURE_TITLE
if config_ani.FIGURE_GRID:
    plt.grid()
plt.title(config_ani.FIGURE_TITLE, fontdict=config_ani.GLOBAL_FONT)

# Generate one together legend for each of the curves
handles = []
labels = []
for axis in unit_axies.values():
    h, l = axis.axis.get_legend_handles_labels()
    l_with_units = [f"{line} ({axis.unit})" for line in l]
    handles += h
    labels += l_with_units

plt.legend(handles, labels, loc=config_ani.LEGEND_LOCATION, prop=config_ani.GLOBAL_FONT)


# The method for this timing to work is that the animation runs at a certain framerate 
# (converted to a time interval), and a time length
# For each frame, it'll step up the running time variable by the time interval
# It must then add all the data who's recorded timestamp is smaller than or equal to the
# running time variable
def animate(frame_number):
    global time_cursor
    global time
    time += FRAME_INTERVAL / 1000  # adjusting to ms


    # keep adding while not caught up
    while (time_cursor < len(time_refference) and time_refference[time_cursor] <= time):  
        # Add a recording frame to the ploted time, then to each value
        plotted_time.append(time_refference[time_cursor])

        for line in lines:
            line.tick()

        if time_cursor < len(time_refference): 
            time_cursor += 1

    updated_lines = [line.line for line in lines]

    if frame_number % 100 == 0:
        print(
            f"Frame {frame_number+1} of {FRAME_LENGTH}" +\
                f"({round((frame_number+1)/FRAME_LENGTH*100, 2)}%)        ",
            end="\r",
        )  # add 1 to frame counts to adjust for 0 index

    return updated_lines


SKIP_TO_FINAL = config_ani.SKIP_TO_FINAL
PREVIEW = config_ani.PREVIEW

def run_animation():
    if SKIP_TO_FINAL:
        for i in range(FRAME_LENGTH):
            animate(i)
        print("Animation skipped, showing final plot")
        plt.show()
    else:
        ani = animation.FuncAnimation(
            fig, animate, interval=FRAME_INTERVAL, frames=FRAME_LENGTH, repeat=False
        )

        if not PREVIEW:  # save the file
            file = os.path.join(
                config_setup.DATA_WORKING_DIR,
                f"{config_ani.DATA_FILE_NAME[:-4]}_animated.mp4",
            )
            writer = animation.FFMpegWriter(
                fps=FRAME_RATE, metadata=dict(artist="Waterloo Rocketry Team")
            )

            print(f"Saving video, this will take about {TIME_LENGTH}s...")
            ani.save(file, writer=writer)
            print()  # newline
            print("Video saved sucessfully")
        else:
            print("Previewing animation")
            plt.show()
            print()
            print("Animation preview closed")


if __name__ == "__main__":
    run_animation()
