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
from photobot_helpers.lorex import LorexCam
import argparse
from configparser import ConfigParser

from photobot_helpers import *
from photobot_helpers.sample_uploader import *

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
        send_disabled_ping("ptz")
        sys.exit()

    if is_dark():
        send_ping("ptz","No photo taken because it is dark", "SLEEP")
        sys.exit()


    # exit if settings file missing items
    for setting_name in required_settings:
        try:
            assert settings[setting_name]
        except:
            error_and_quit("Missing setting '%s' in ini file" % setting_name,"ptz")
            raise Exception("Missing setting '%s' in ini file" % setting_name)

    # set file path and log level for logging


    log.info("-----------------------------------------------------------------------------")
    log.info("EXECUTING RUN at %s" % datetime.now() )

    lorex_cam = LorexCam(
        host=settings['ptz_host'],
        port=settings['ptz_port'],
        user=settings['ptz_user'],
        password=settings['ptz_password'],
        wsdl_dir=settings['wsdl_dir'],
    )
    
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
        ptz_mac = settings.get('devices',{}).get('lorex',{}).get('mac_address')

        if ptz_mac:
            rescan_network_for_devices()

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

            if settings['high_res_sample_mode']:
                uploader = Sample_Uploader()
                uploader.settings = settings
                uploader.upload_by_type('ptz')
                sys.exit()
            # move the file from pi to usb drive
            #move_command = "mv %s %s" % (local_filepath, ext_filepath)
            #try:
            #    output = subprocess.check_output(move_command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
            #    log.info("image moved to %s" % ext_filepath)
            #except subprocess.CalledProcessError as exc:
            #    error_and_quit("ERROR moving image: '%s'" % exc.output)

            timer.sleep(int(settings['ptz_delay_between_photos']))

        # photo home

        # sleep until next round
        timer.sleep( int(settings['ptz_delay_between_rounds']))

    send_ping('ptz', "Completed PTZ Run", "OK")