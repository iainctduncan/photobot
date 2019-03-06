import subprocess
from datetime import datetime
import time
import os
import sys
import logging
import argparse
from configparser import ConfigParser

from photobot_helpers import *

class Process_Scheduler(object):

    def __init__(self):
        self.process_run_log = {'usb_upload': 0, 'fun': 0, 'ptz_upload':0 }

    def is_running(self):
        return True

    def is_time_for(self,process_name,interval):

        interval_seconds = interval
        process_last_run = self.process_run_log[process_name]

        next_run = process_last_run + interval_seconds

        now = time.time()

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
        self.send_image(orig_path,type)

    def send_image(self,path,type,width):

        last_sent_path = get_lastest_photo_sent_path(type)


        if last_sent_path == path:
            print("already sent")
            return

        print("would send " + path)





def main_loop():

    scheduler = Process_Scheduler()

    uploader = Sample_Uploader()

    while scheduler.is_running():

        usb_upload_interval = 36
        ptz_upload_interval = 36

        if scheduler.is_time_for("usb_upload",usb_upload_interval):
            uploader.upload_by_type('usb')

        if scheduler.is_time_for("ptz_upload", ptz_upload_interval):
            uploader.upload_by_type('ptz')

        if scheduler.is_time_for("fun",20):
            send_ping()

        # do your stuff...
        time.sleep(1)

if __name__=="__main__":

    #log = get_logger()
    # log.info("Sending Updates")
    main_loop()


