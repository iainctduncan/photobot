import subprocess
from datetime import datetime
import time as timer
import os
import sys
import logging
import argparse
from configparser import ConfigParser

from photobot_helpers import *

class Process_Scheduler(object):

    def __init__(self):
        self.process_run_log = {'usb_upload': 0, 'alive_ping': 0, 'ptz_upload':0,'thermal_upload':0, 'disk_check':0, 'thermal_capture':0 }

    def is_running(self):
        return True

    def is_time_for(self,process_name,interval):

        interval_seconds = int(interval)
        process_last_run = self.process_run_log[process_name]

        next_run = process_last_run + interval_seconds

        now = timer.time()

        if next_run < now:
            self.process_run_log[process_name]=now
            return True

        else:
            return False

class Sample_Uploader(object):
    def upload_by_type(self,type='usb'):

        sample_width_var = type + '_sample_width'

        width = self.settings[sample_width_var]

        orig_path = get_lastest_photo_path(type)
        self.send_image(orig_path,type,width)

    def send_image(self,path,type,width):

        last_sent_path = get_lastest_photo_sent_path(type)

        width = str(width)


        if last_sent_path == path:
            print("already sent")
            return

        dir, filename = os.path.split(path)
        samples_dir = dir + "/samples"
        ensure_dir(samples_dir)
        sample_path = samples_dir + "/sample_" + filename

        #print("convert -geometry " + width + "x" + width + " " + path + " " + sample_path)
        os.system("convert -geometry " + width + "x" + width + " " + path + " " + sample_path )
        #print("scp " + sample_path + " " + self.settings['samples_user_host'] + ":" + self.settings['samples_dest_path'])
        os.system("scp " + sample_path + " " + self.settings['samples_user_host'] + ":" + self.settings['samples_dest_path'])

        send_ping(type,"Sample Photo Uploaded: " +filename,"OK")
        log_latest_photo_path(path,type)


def main_loop():

    scheduler = Process_Scheduler()

    uploader = Sample_Uploader()

    settings = get_settings_dict()

    uploader.settings = settings

    while scheduler.is_running():

        if scheduler.is_time_for("thermal_capture", settings['thermal_delay_between_photos']):
            capture_thermal_image()

        if scheduler.is_time_for("usb_upload",settings['usb_upload_interval']):
            uploader.upload_by_type('usb')

        if scheduler.is_time_for("ptz_upload", settings['ptz_upload_interval']):
            uploader.upload_by_type('ptz')

        if scheduler.is_time_for("thermal_upload", settings['thermal_upload_interval']):
            uploader.upload_by_type('thermal')

        if scheduler.is_time_for("alive_ping",settings['alive_ping_interval']):
            send_ping("pi","Internal Scheduler Running","OK")

        if scheduler.is_time_for("disk_check",settings['disk_check_interval']):
            mb_free = get_mb_free_by_path(get_capture_target_dir())
            gb_free = mb_free / 1000

            send_ping("disk","Disk Free",gb_free)



        timer.sleep(1)

if __name__=="__main__":

    #log = get_logger()
    # log.info("Sending Updates")
    main_loop()


