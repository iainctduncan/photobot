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
from lorex import LorexCam
import argparse
from configparser import ConfigParser
from photobot_helpers.sample_uploader import *

from photobot_helpers import *

################################################################################
# beginning of main execution
if __name__=="__main__":
    capture_thermal_image()
    uploader = Sample_Uploader()
    uploader.settings = get_settings_dict()
    uploader.upload_by_type('thermal')
