"""
ptz Camera version of photobot

TODO/Sort out
- python 2.7 only
- we need the wsdl dir
- we need the network location for the ptz, we might
  need to scan for that??
"""


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
from photobot_helpers.sample_uploader import *

from photobot_helpers.photobot_cameras import *
from photobot_helpers.pi_hq_camera import *


################################################################################
# beginning of main execution
if __name__=="__main__":
    settings = get_settings_dict()
    device_name = settings['camera']
    cam_settings = settings.get('devices', {}).get(device_name, {})

    if not cam_settings:
        print("Camera " + device_name + " not found in config.")
        sys.exit()
    #print(cam_settings)
    cam = Photobot_Camera_Run(device_name,cam_settings)
    cam.photo_run()
    #print("ran")