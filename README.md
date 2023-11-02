# data-video-visualization
Code for taking csv data and turning it into an mp4 file to be used in videos (poster session, static fire videos, and so on). 

Example of config from LCF1 is included, and should be used as a template for future animations.

## Setup

- Install all the python requirements with `pip install -r requirements.txt`
- Ensure that the font being used is installed
- Make a copy of `config_setup_example.yaml` and rename it to `config_setup.yaml`
- Download ffmpeg from https://ffmpeg.org/download.html
- Place the FFMPEG executable wherever you want (we recomend in the same directory as the python script)
- Set the FFMPEG executable path in the `config_setup.yaml` file `FFMPEG_PATH = "path/to/ffmpeg/executable"`
  
## Usage

- Place the data you want to visualize (csv) in the `working_directory` folder
- Make a copy of `config_ani_example.yaml` and rename it to `config_ani.yaml`. This is where you will set the config settings for the animation to be rendered
- Set the animation settings (see animation config section below)
- Run the script with `python main.py` (from the root directory of `\data-video-visualization`)
- Depending on your config settings, the animation will either be saved to a file in `working_directory` or displayed in a window

## Animation Config

Most configuration is specific to each animation, and therefore has to be redone for each new plot (except often for the controls and rendering settings section). We recomend just commenting out the data, axies and line section for each new animation, and then copying and pasting the config from a previous animation below and modifying it to fit the new one.

### Controls

- `SKIP_TO_FINAL` lets you skip to the final frame of the animation and display it, to get a preview of what the final animation will look like. Use this before rendering the final animation to make sure everything looks good
- `PREVIEW` lets you show the entire animation in a window instead of saving it to a file

### Rendering settings

- `FRAME_RATE` is the frame rate of the animation, in frames per second.the script works with any value >= 1, but we recomend 30-60. It does not have to by sycned with the recording rate of the data
- `FILTERING_STRENGTH` is the size of the savgol filter window, bigger means its more filtered. Do not set to anything lower than 3. If you do not want filtering, configure that in each indiviual line's data.
- `PLOT_HEIGHT` and `PLOT_WIDTH` are the height and width of the plot in inches (thanks matplotlib)
- `FIGURE_GRID` is a boolean that describes wether or not to draw grid lines in the plot. We recomend setting this to `True` for most applications
- `GLOBAL_FONT` sets the font of all the text in the animiation. Leave it at helvetica, it's the rocketry branding
- `LEGEND_LOCATION` sets the location of the legend in the plot. It can be any of the values listed here: https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.legend.html. Just make sure it stays out of the way of the lines being drawn

### Data settings

- `DATA_FILE_NAME` is the name of the csv file to be read from. It should be in the `working_directory` folder, or whichever is specified in `DATA_WORKING_DIR` in the `config_setup.py` file
- `STARTING_TIME` is the time in seconds that the animation will start reading data from the CSV at. This should be set to the second of the first line in the CSV usually, but can then be adjusted to crop out data according to your needs
- `ENDING_TIME` / `LENGTH_TIME` you can set one or the other, but not both. `ENDING_TIME` is the time in seconds that the animation will stop reading data from the CSV at. `LENGTH_TIME` is the length of the animation in seconds. Set the other to `None` to use the one you want
- `START_TIME_GRAPHICAL_OFFSET` is an amount of time subtracted from the recorded times when displaying the graph (so that for example starting time is always 0 if it's equal to the STARTING_TIME)
- `FIGURE_TITLE` is the title of the plot. It can be anything you want, but we recomend something like "SF 6" or "LCF 4 (Combined)"

### Axies and lines

The plotting system works on a system of axies and lines.

Each line is attached to an axis that describes it's unit.

You will have to configure the axies and lines for each differnt animation you want to make.

#### Axies

Define a dictionary in `config_ani.py` called `AXIES` with the following format for each entry:

```yaml
"name" : {
    "display_name": "Display name",
    "unit": "unit",
    "min": min,
    "max": max,
    "primary": True/False
}
```

- `name` is the reference name of the axis. It can be anything you want, but it should be unique, and will be used later to attach lines to the axis
- `display_name` is the name of the axis that will be displayed in the plot. It should be clear and explain the unit (ex: `Pressure`). Do not include the unit in this name, it will be automatically added
- `unit` is the unit of the axis. It should be a string that can be used in a matplotlib plot (ex: `psi`). This will usually be the same as the name
- `min\max` are the minimum and maximum values of the axis. These will be used to set the limits of the plot. Set them in accordance with the data you are plotting
- `primary` is a boolean that describes wether or not the axis is a primary axis. Primary axies are drawn on the left side of the plot, and secondary axies are drawn on the right side. There can only be one primary axis

When axies are of similar scale, they can be combined into one axis. For example, pressure and thrust are often in the scale of hundreds, so may therefore be combined into `psi/lbf`. Just set the display name to reflect this (ex: `Pressure/Thrust`) and the unit.

#### Lines

Define a dictionary in `config_ani.py` called `PLOT_ITEMS` with the following format for each entry:

```yaml
"Display Name": {
    "csv_column": "csv_column",
    "axis": "axis",
    "color": "color",
    "filtered": True/False,
}
```

- `Display Name` is the name of the line that will be displayed in the legend. It should be clear and explain what the line is (ex: `Ox Tank Mass`). Do not include the unit in this name, it will be automatically added
- `csv_column` is the name of the column in the CSV file that the data for the line is in. It should be a string that can be used to index a dictionary (ex: `Honeywell S-type - Ox Tank`)
- `axis` is the name of the axis that the line is attached to. It should be the name of an axis that you defined in the `AXIES` dictionary (ex: `psi`)
- `color` is the color of the line. It should be a string that can be used in a matplotlib plot (ex: `#ff0000`, or `"red"`)
- `filtered` is a boolean that describes wether or not the line should be filtered. If it is set to `True`, the line will be filtered with a savgol filter with a window size of `FILTERING_STRENGTH` (see rendering settings). If it is set to `False`, the line will not be filtered. We recomend keeping this on for most applications

## Troubleshooting

### Fonts not found

The simple remedy is to install the correct font. The font has to match exactly. For example, helvetica (the default font) might be installed as a variant (such as Helvetica Neue). A link to a verified install of helvetica (tested on Windows) is provided below:

https://dwl.freefontsfamily.com/download/Helvetica-Font/#google_vignette

Additionally, the following issue must be addressed:

https://stackoverflow.com/questions/26085867/matplotlib-font-not-found

Where the .json cache of matplotlib must be deleted so that a re-build of the cache is forced, picking up the newly installed font.

If neither of these options work and a export is urgently required, the direct solution of removing the font specification arguments inside the code will also work.
