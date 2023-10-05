## SET YOUR SETTINGS IN A COPY OF THIS CALLED config_ani.py


# Drawing settings
SKIP_TO_FINAL = False # Allows the entire animation step to be skipped and just show you what the final plot looks like
PREVIEW = False # Allows the animation to be previewed instead of saving it to a file

# Animtion file config
DATA_FILE_NAME = "lcf1.csv"

FILTERING_STRENGTH = 50 # The size of the savgol filter window, bigger means its more filtered

# Animation config
FRAME_RATE = 60 # (fps)
STARTING_TIME = 2280 # The time of recording timestamps that the data starts (seconds)

# You can either define the ending time, or the length of the animation, set the other to None
ENDING_TIME = None # The time of recording timestamps that the data ends (seconds)
LENGTH_TIME = 80 # The length of the animation (seconds)

# Plot config
PLOT_HEIGHT = 5 # (inches)
PLOT_WIDTH = 10 # (inches)

FIGURE_GRID = True
GLOBAL_FONT = {'family':  'helvetica'} # Rocketry Standard font is helvetica
LEGEND_LOCATION = "lower left" # Where the legend is located, see https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.legend.html for more info

FIGURE_TITLE = "LCF1" # The title of the plot

AXIES = {
    "psi": {
        "display_name": "Pressure",
        "unit": "psi",
        "min": 0,
        "max": 900,
        "primary": True
    },
    "kg": {
        "display_name": "Mass",
        "unit": "kg",
        "min": 0,
        "max": 30,
        "primary": False
    },
}

PLOT_ITEMS = {
    "Ox Tank Mass": {
        "csv_colum": "Honeywell S-type - Ox Tank",
        "axis": "kg",
        "color": "black",
        "filtered": True
    },
    "PT-4 Injector Ox Pressure": {
        "csv_colum": "PT-4 Injector Oxidizer",
        "axis": "psi",
        "color": "blue",
        "filtered": True
    },
    "PT-2 Ox Tank Pressure": {
        "csv_colum": "PT-2 Ox Tank",
        "axis": "psi",
        "color": "red",
        "filtered": True
    },
}


# Config checks

if ENDING_TIME == None and LENGTH_TIME == None:
    raise ValueError("You must define either the ending time or the length of the animation")

if ENDING_TIME != None and LENGTH_TIME != None:
    raise ValueError("You must define either the ending time or the length of the animation, not both")