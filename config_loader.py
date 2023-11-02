from yaml import safe_load
from os.path import exists

def load_config_setup() -> dict:
    """Load and execute checks on the setup configuration file"""
    try:
        with open("config/config_setup.yaml", "r") as file:
            config_setup = safe_load(file)
    except ModuleNotFoundError:
        raise RuntimeError(
            "config_setup.yaml not found, please copy config_setup_example.yaml " +\
                "to config_setup.yaml and set your values there"
        )

    ffmpeg_path_valid = exists(config_setup['FFMPEG_PATH'])
    if not ffmpeg_path_valid:
        raise FileNotFoundError("FFMPEG path not set correctly, the system is unable to find it")
    
    working_dir_valid = exists(config_setup['DATA_WORKING_DIR'])
    if not working_dir_valid:
        raise FileNotFoundError(f"Working directory not set correctly, the system is unable to find it. Make sure '{config_setup['DATA_WORKING_DIR']}' exists under this script's directory")

    return config_setup

def load_config_ani() -> dict:
    """Load and execute checks on the animation configuration file"""
    try:
        with open("config/config_ani.yaml", "r") as file:
            config_ani = safe_load(file)
    except ModuleNotFoundError:
        raise RuntimeError(
            "config_ani.py not found, please copy config_ani_example.yaml to config_ani.yaml and" +\
                " set your values there. See README.md for instructions on how to set configuration"
        )


    if config_ani["ENDING_TIME"] == None and config_ani["LENGTH_TIME"] == None:
        raise ValueError("You must define either the ending time or the length of the animation")

    if config_ani["ENDING_TIME"] != None and config_ani["LENGTH_TIME"] != None:
        raise ValueError("You must define either the ending time or " +\
                         "the length of the animation, not both")


    # Check for multiple primary axies
    primary_axies = 0
    for axis in config_ani["AXIES"].values():
        if axis["primary"]:
            primary_axies += 1

    if primary_axies > 1:
        raise ValueError("You can only have one primary axis")

    return config_ani
