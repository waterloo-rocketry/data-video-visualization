from matplotlib import pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import os
from matplotlib.animation import FuncAnimation
from scipy.signal import savgol_filter
from time import perf_counter
import math

from config_loader import load_config_ani, load_config_setup


class PlotAxis:
    def __init__(self, display_name, unit, min, max, config_ani, primary =False):
        self.display_name = display_name
        self.unit = unit
        if primary:
            self.axis = plt.gca()
        else:
            self.axis = plt.twinx()

        self.axis.set_ylabel(f"{display_name} ({unit})")
        self.axis.set_xlabel("Time (s)")
        starting_time_actual = config_ani.STARTING_TIME - config_ani.START_TIME_GRAPHICAL_OFFSET
        ending_time_actual = config_ani.TRUE_ENDING_TIME - config_ani.START_TIME_GRAPHICAL_OFFSET
        self.axis.set_xlim(starting_time_actual, ending_time_actual)
        self.axis.set_ylim(min, max)

# Each data item that will have a curve
class PlotItem:
    def __init__(self, display_name, axis_class, color, 
                 data, config_ani, filtered=True):

        self.name = display_name
        self.axis = axis_class.axis
        self.color = color
        self.config_ani = config_ani

        self.data = data
        if filtered:
            self.data = savgol_filter(self.data, config_ani.FILTERING_STRENGTH, 2)
        self.plotted_data = []  # Starts off empty and grows over time

        # Create the empty line object that will be filled out as the animiation runs
        self.line = self.axis.plot([], [], label=f"{display_name}", color=color)[0]

    def tick(self, time_cursor, plotted_time):
        """a tick pushing the data forward in an line one recording frame, and this might happen multiple 
        times per animation frame.
        """

        self.plotted_data.append(self.data[time_cursor])
        plotted_time_modified = [ts - self.config_ani.START_TIME_GRAPHICAL_OFFSET 
                                    for ts in plotted_time]

        self.line.set_data(plotted_time_modified, self.plotted_data)
        return self.line


class ConfigAni:
    def __init__(self) -> None:
        conf_ani = load_config_ani()

        # Convert the loaded yaml dictionary into class attributes
        for key, value in conf_ani.items():
            setattr(self, key, value)

        ## Set up additional values of the animation

        # Set the true end time value in config_ani based on how the configuration is set up
        if self.ENDING_TIME == None:
            self.TRUE_ENDING_TIME = self.STARTING_TIME + self.LENGTH_TIME
        else:
            # The time at which the data stops recording
            self.TRUE_ENDING_TIME =  self.ENDING_TIME

        self.TIME_LENGTH = self.TRUE_ENDING_TIME - self.STARTING_TIME  # seconds
        self.FRAME_INTERVAL = math.floor(1000 / self.FRAME_RATE)  # ms
        self.FRAME_LENGTH = self.FRAME_RATE *  self.TIME_LENGTH  # frames



class ConfigSetup:
    def __init__(self) -> None:
        conf_setup = load_config_setup()

        # Convert the loaded yaml dictionary into class attributes
        for key, value in conf_setup.items():
            setattr(self, key, value)

class DataAnimator:

    def __init__(self) -> None:
        self.config_ani = ConfigAni()
        self.config_setup = ConfigSetup()

        self.prev_timer_value = -1
        self.LOGGING_INTERVAL = 100
        self.INTERVAL_PERCENT =  (self.LOGGING_INTERVAL/self.config_ani.FRAME_LENGTH) * 100
        pass

    def animate(self, frame_number):
        """The method for this timing to work is that the animation runs at a certain framerate
        (converted to a time interval), and a time length.

        For each frame, it'll step up the running time variable by the time interval.
        It must then add all the data who's recorded timestamp is smaller than or equal to the
        running time variable. """
        self.time += self.config_ani.FRAME_INTERVAL / 1000  # adjusting to ms


        # keep adding while not caught up
        while (self.time_cursor < len(self.time_reference) and 
                self.time_reference[self.time_cursor] <= self.time):

            # Add a recording frame to the ploted time, then to each value
            self.plotted_time.append(self.time_reference[self.time_cursor])

            for line in self.lines:
                line.tick(self.time_cursor, self.plotted_time)

            if self.time_cursor < len(self.time_reference):
                self.time_cursor += 1

        updated_lines = [line.line for line in self.lines]

        if frame_number == 0:
            self.prev_timer_value = perf_counter()

        ## Log the render progress
        if (frame_number + 1) % self.LOGGING_INTERVAL == 0:

            # add 1 to frame counts to adjust for 0 index
            percent_completed = round((frame_number + 1)/self.config_ani.FRAME_LENGTH*100, 2)
            print_message_frames = f"Rendering frame {frame_number + 1}" +\
                    f" of {self.config_ani.FRAME_LENGTH} ({percent_completed}%)"

            ## Handle a non-cringers way of estimating remaining time
            if self.prev_timer_value == -1:
                self.prev_timer_value = perf_counter()
                print_message_timing = "Preparing time remaining estimate..."
                print_message_estimate = ""
            else:
                timer_duration = (perf_counter() - self.prev_timer_value) # value in seconds
                percent_remaining = 100.0 - percent_completed

                remaining_time_estimate = timer_duration*(percent_remaining/self.INTERVAL_PERCENT)
                print_message_timing = f"Time to render frame batch: {round(timer_duration, 2)} s"
                print_message_estimate = \
                    f"Estimated time remaining: {round(remaining_time_estimate, 2)} s"


                self.prev_timer_value = perf_counter() # reset timer

            print_message = print_message_frames + '  |  ' + print_message_timing
            print_message = print_message + '  |  ' + print_message_estimate

            print_message = print_message + " "*10 # For clearing stray chars by carriage return

            print(print_message, end="\r")

        return updated_lines


    def create_animation(self):
        """Main method for creating an animation."""


        plt.rcParams["animation.ffmpeg_path"] = self.config_setup.FFMPEG_PATH
        m = pd.read_csv(os.path.join(self.config_setup.DATA_WORKING_DIR, \
                                     self.config_ani.DATA_FILE_NAME))

        # Set the dimensions of the plot
        plt.rcParams["figure.figsize"] = (self.config_ani.PLOT_WIDTH, self.config_ani.PLOT_HEIGHT)

        # Timestap as a base refference
        self.time_reference = m["Timestamp"]
        self.plotted_time = []
        self.time_cursor = 0
        self.time = self.config_ani.STARTING_TIME  # animiation progress in seconds

        self.fig = plt.subplots()[0]


        # Import graphing settings from config
        unit_axies = {}

        for axis_name, axis_config in self.config_ani.AXIES.items():
            unit_axies[axis_name] = PlotAxis(
                axis_config["display_name"],
                axis_config["unit"],
                axis_config["min"],
                axis_config["max"],
                self.config_ani,
                axis_config["primary"]
            )

        self.lines = []

        for item_name, item_config in self.config_ani.PLOT_ITEMS.items():
            self.lines.append(
                PlotItem(
                    item_name,
                    unit_axies[item_config["axis"]],
                    item_config["color"],
                    m[item_config["csv_colum"]],
                    self.config_ani,
                    filtered = item_config["filtered"]
                )
            )


        if self.config_ani.FIGURE_GRID:
            plt.grid()

        plt.title(self.config_ani.FIGURE_TITLE, fontdict=self.config_ani.GLOBAL_FONT)

        # Generate one together legend for each of the curves
        handles = []
        labels = []
        for axis in unit_axies.values():
            h, l = axis.axis.get_legend_handles_labels()
            l_with_units = [f"{line} ({axis.unit})" for line in l]
            handles += h
            labels += l_with_units

        plt.legend(handles, labels, loc=self.config_ani.LEGEND_LOCATION,
                    prop=self.config_ani.GLOBAL_FONT)

        if self.config_ani.SKIP_TO_FINAL:
            for i in range(self.config_ani.FRAME_LENGTH):
                self.animate(i)
            print("Animation skipped, showing final plot")
            plt.show()
        else:
            ani = animation.FuncAnimation(
                self.fig, self.animate,
                interval=self.config_ani.FRAME_INTERVAL,
                frames=self.config_ani.FRAME_LENGTH, repeat=False
            )

            if not self.config_ani.PREVIEW:  # save the file
                file_name = f"{self.config_ani.DATA_FILE_NAME[:-4]}_animated.mp4"
                file_path = os.path.join(self.config_setup.DATA_WORKING_DIR, file_name)

                writer = animation.FFMpegWriter(
                    fps=self.config_ani.FRAME_RATE, metadata=dict(artist="Waterloo Rocketry Team")
                )

                print(f"Saving video...")
                try:
                    ani.save(file_path, writer=writer)
                except FileNotFoundError: # Override call to make custom message
                    raise FileNotFoundError("Animation.save was not able to locate the " +\
                                            "FFMPEG path. Ensure that the path is set correctly")

                print(" "*150 , end='\r')  # remove rendering log
                print("All frames rendered")
                print("Video saved sucessfully")
            else:
                print("Previewing animation")
                plt.show()
                print()
                print("Animation preview closed")

def data_visualizer_execute():
    """Wrapper method for creating a DataAnimator instance and running its main function"""
    animator = DataAnimator()
    animator.create_animation()
