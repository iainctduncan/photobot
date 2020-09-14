import subprocess
from datetime import datetime
import time as timer
import os
import sys
import logging
#from photobot_helpers.lorex import IPCam
import argparse
from configparser import ConfigParser

from photobot_helpers import *
from photobot_helpers.safe_config_editor import SafeConfigEditor

#from photobot_helpers.photobot_cameras import *




################################################################################
# beginning of main execution
if __name__=="__main__":
    settings = get_settings_dict()
    #device_name = settings['camera']
    which_config = settings['which_config']

    print(which_config)

    if which_config == 'yaml':
        config_file = settings['yaml_config_file']
        example_file = '/var/photobot/repo/docs/example_photobot.yml'

    elif which_config== 'tunnels':
        config_file = "/var/photobot/config/tunnels.yml"
        example_file = '/var/photobot/repo/docs/example_tunnels.yml'
    else:
        print("Please enter a valid config file to edit. Options are: \n yaml - Main yaml config \n tunnels - Localxpose tunnels config")
        sys.exit()

    config_editor = SafeConfigEditor(config_file,example_file)
    config_editor.run_safe_edit()

    # copy the default configuration file in if needed

    # make a copy of the file for editing

    # open the copy in a text editor (maybe nano is easiest? Patrick, what do you prefer?)

    # On save, validate the temporary file to make sure it works.

    # if the file is valid, give the option to replace the live config. if not let them edit the temp file to fix it.


    #cam_settings = settings.get('devices', {}).get(device_name, {})
