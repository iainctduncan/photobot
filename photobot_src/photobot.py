#!/usr/bin/python3

import subprocess
from datetime import datetime
import time as timer
import sys
import os
import argparse
from configparser import ConfigParser

from photobot_helpers import *
from photobot_helpers.sample_uploader import *


# settings that must be present in the ini file
required_settings = [
    'photos_per_round',
    'number_of_rounds',
    'delay_between_rounds',
    'capture_dir',
]


# beginning of main execution
if __name__=="__main__":

    # check if system has been up for a minute, if not, exit
    # this is to make sure our housekeeper has finished its job first
    uptime_str = subprocess.check_output("uptime -p",
        stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    # when uptime is less than 1 minute, the output is just "up"
    if uptime_str.strip() == "up":
        sys.exit()


    log = get_logger()
    settings = get_settings_dict()

    if settings['enable_usb_camera'] == '0':
        log.info("USB Camera is disabled. Exiting")
        send_ping("usb", "USB disabled", "Off")
        sys.exit()

    if is_dark():
        send_ping("usb", "No photo taken because it is dark", "SLEEP")
        sys.exit()

    log.info("-----------------------------------------------------------------------------")
    log.info("EXECUTING RUN at %s" % datetime.now())



    # exit if settings file missing items
    for setting_name in required_settings:
        try:
            assert settings[setting_name]
        except:
            send_ping(settings,"Missing setting '%s' in ini file" % setting_name,"ERROR")
            raise Exception("Missing setting '%s' in ini file" % setting_name)

    # get the pid of the last run of photobot, and try to kill that process
    # this because sometimes the camera and script can hang
    # it's harmless if the previous pass didn't hang
    try:
        # open the text file with the last pid
        with open("/var/photobot/logs/photobot.pid", "r") as f:
            last_pid = int( f.read() )
            kill_command = "kill -9 %s" % last_pid
            output = subprocess.check_output(kill_command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True) 
            log.info("killed previous process: %i" % last_pid)
    except Exception, e:
        # previous process did not hang, do nothing
        pass 

    # save pid of this pass so that subsequent photobot passes can kill a hung photobot process
    this_pid = os.getpid()
    with open("/var/photobot/logs/photobot.pid", "w") as f:
        f.write( str(this_pid) )
        log.info("saved current pid %i to file" % this_pid)
   
    # done process housekeeping 

    # take two rounds of pictures, separated by 30 seconds 
    for i in range(0, int(settings['number_of_rounds'])):

        for i in range(0, int(settings['photos_per_round'])):
            filename = get_photo_filename(settings['installation_id'])
            local_filepath = "%s" % filename
            ext_filepath = "%s/%s" % (get_capture_target_dir(), filename)

            # NB: no sleep necessary, time delay is in the command
            # NB: this long form with eosremotereleases is the ONLY version that has worked reliably
            # for the camera, the simpler version you can find online hung frequently for us
            photo_command = ("gphoto2 --wait-event=1s --set-config eosremoterelease=2 --wait-event=1s "
                " --set-config eosremoterelease=4 --wait-event-and-download=2s --filename=%s "
                "--force-overwrite --get-all-files --delete-all-files" % ext_filepath)
           
            try: 
                output = subprocess.check_output(photo_command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
                log.info("captured photo: %s" % ext_filepath)
                try:
                    size = os.path.getsize(ext_filepath)
                    log.info("file size is %s",size)
                    if size > 0:
                        log_latest_photo_path(ext_filepath)
                        if settings['high_res_sample_mode']:
                            uploader = Sample_Uploader()
                            uploader.settings = settings
                            uploader.upload_by_type('usb')
                            sys.exit()
                    else:
                        power_cycle()
                        error_and_quit("Captured Photo Image " + ext_filepath + " has zero filesize", 'usb')
                except Exception as err:
                    power_cycle()
                    error_and_quit("Captured Photo Image " + ext_filepath + " does not exist ", 'usb')

            except subprocess.CalledProcessError as exc:
                power_cycle()
                error_and_quit("ERROR capturing photo: '%s'" % exc.output,'usb')

            # move the file from pi to usb drive
            #move_command = "mv %s %s" % (local_filepath, ext_filepath)
            #try:
            #    output = subprocess.check_output(move_command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
            #    log.info("image moved to %s" % ext_filepath)
            #except subprocess.CalledProcessError as exc:
            #    error_and_quit("ERROR moving image '%s'" % exc.output)

            # delay between photos not necessary here, in the gphoto command

        # sleep until next round
        timer.sleep( int(settings['delay_between_rounds']) )

    send_ping('usb', "Completed USB Photo Run","OK")