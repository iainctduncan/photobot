import subprocess
from datetime import datetime
import time
import os
import sys
import logging
import argparse
from configparser import ConfigParser

from photobot_helpers import *

if __name__=="__main__":
    # try log with two paths so we can run this in non-pi envs
    log = get_logger()
    log.info("Reboot, init_photobot.py executing")

    #ip = get_ptz_ip()

    # Had some Pis that couldn't find eth0 unless we run this command
    #os.system("dhcpcd")
    notify_reboot()
    clean_tmp_files()

    # unmount to ensure gvfs isn't hogging the USB slr cam
    # doesn't seem to do anything. gvfs-mount not installed
    os.system("gvfs-mount -s gphoto2")

    mount_drive(get_usb_storage_path())
