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

from photobot_helpers import *

################################################################################
# beginning of main execution
if __name__=="__main__":
    power_cycle()
