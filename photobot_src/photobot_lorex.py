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
import time
import os
import sys
import logging
from lorex import LorexCam
import argparse
from configparser import ConfigParser

from photobot_helpers import *

# settings that must be present in the ini file
required_settings = [
    'ptz_photos_per_round',
    'ptz_number_of_rounds',
    'ptz_delay_between_rounds',
    'ptz_delay_between_photos',
    'capture_dir',
    'wsdl_dir',
    'ptz_host',
    'ptz_port',
    'ptz_user',
    'ptz_password'
]




################################################################################
# beginning of main execution
if __name__=="__main__":


    # check if system has been up for a minute, if not, exit
    # this is to make sure our housekeeper has finished its job first
    # NB: this does NOT work on OSX/BSD, you'll need to disable it for dev on OSX
    uptime_str = subprocess.check_output("uptime -p",
        stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    # when uptime is less than 1 minute, the output is just "up"
    if uptime_str.strip() == "up":
        sys.exit()

    settings = get_settings_dict()

    log = get_logger()

    if settings['enable_ptz_camera'] == '0':
        log.info("PTZ is disabled. Exiting")
        sys.exit()

    #send_ping(settings,"Starting PTZ Capture","OK")

    # exit if settings file missing items
    for setting_name in required_settings:
        try:
            assert settings[setting_name]
        except:
            error_and_quit("Missing setting '%s' in ini file" % setting_name)
            raise Exception("Missing setting '%s' in ini file" % setting_name)

    # set file path and log level for logging


    log.info("-----------------------------------------------------------------------------")
    log.info("EXECUTING RUN at %s" % datetime.now() )

    # instantiate our lorex camera
    # these settings could come from env variables. How will we get the network address??
    try:
        lorex_cam = LorexCam(
            host = settings['ptz_host'],
            port = settings['ptz_port'],
            user = settings['ptz_user'],
            password = settings['ptz_password'],
            wsdl_dir = settings['wsdl_dir'],
        )
    except:
       error_and_quit("Could not connect to PTZ camera at " + settings['ptz_host'],'ptz')

    # execute X rounds of Y pictures according to settings
    for i in range(0, int(settings['ptz_number_of_rounds'])):
        for i in range(0, int(settings['ptz_photos_per_round'])):
            filename = get_photo_filename(settings['installation_id'],'ptz_capture')
            #local_filepath = "%s" % filename
            #ext_filepath = "%s/%s" % (settings['capture_dir'], filename)
            # save capture from camera
            lorex_cam.save_image(get_capture_target_dir()+"/"+filename)
            log_latest_photo_path(get_capture_target_dir()+"/"+filename,'ptz')
            # move the file from pi to usb drive
            #move_command = "mv %s %s" % (local_filepath, ext_filepath)
            #try:
            #    output = subprocess.check_output(move_command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
            #    log.info("image moved to %s" % ext_filepath)
            #except subprocess.CalledProcessError as exc:
            #    error_and_quit("ERROR moving image: '%s'" % exc.output)

            time.sleep(int(settings['ptz_delay_between_photos']))

        # photo home

        # sleep until next round
        time.sleep( int(settings['ptz_delay_between_rounds']))

    send_ping('ptz', "Completed PTZ Run", "OK")