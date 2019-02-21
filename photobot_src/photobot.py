#!/usr/bin/python3

import subprocess
from datetime import datetime
import time
import sys
import os
import argparse
from configparser import ConfigParser

from photobot_helpers import *


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

    log.info("-----------------------------------------------------------------------------")
    log.info("EXECUTING RUN at %s" % datetime.now())

    settings = get_settings_dict()

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
                log_latest_photo_path(ext_filepath)
            except subprocess.CalledProcessError as exc:
                error_and_quit("ERROR capturing photo: '%s'" % exc.output)

            # move the file from pi to usb drive
            #move_command = "mv %s %s" % (local_filepath, ext_filepath)
            #try:
            #    output = subprocess.check_output(move_command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
            #    log.info("image moved to %s" % ext_filepath)
            #except subprocess.CalledProcessError as exc:
            #    error_and_quit("ERROR moving image '%s'" % exc.output)

            # delay between photos not necessary here, in the gphoto command

        # sleep until next round
        time.sleep( int(settings['delay_between_rounds']) )

    send_ping(settings, "Completed USB Photo Run","OK")