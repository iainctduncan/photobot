import subprocess
from datetime import datetime
import time as timer
import os
import sys
import logging
import argparse
from configparser import ConfigParser
import subprocess

from photobot_helpers import *
from photobot_helpers.sample_uploader import *

class Process_Scheduler(object):

    def __init__(self):
        self.process_run_log = {'usb_upload': 0, 'alive_ping': 0, 'ptz_upload': 0,'thermal_upload': 0, 'disk_check': 0, 'thermal_capture': 0, 'usb_run': 0, 'ptz_run': 0}

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


def main_loop():

    scheduler = Process_Scheduler()

    uploader = Sample_Uploader()

    settings = get_settings_dict()

    #print(settings)

    uploader.settings = settings

    cam_settings = settings.get('devices')

    devices_to_run = dict()
    devices_to_send_samples = dict()
    device_sample_widths = dict()
    if cam_settings:

        for device_name in cam_settings:
            #print(device_name + "has settings: ")
            device_settings = cam_settings[device_name]
            scheduler.process_run_log["photo_run_"+device_name]=0
            scheduler.process_run_log["sample_upload_"+device_name]=0
            if device_settings.get('seconds_between_starts'):
                devices_to_run[device_name]=device_settings.get('seconds_between_starts')

            if device_settings.get('seconds_between_sample_uploads'):
                devices_to_send_samples[device_name]=device_settings.get('seconds_between_sample_uploads')
            else:
                devices_to_send_samples[device_name]=settings['sample_upload_interval']

            if device_settings.get('sample_width'):
                device_sample_widths[device_name] = device_settings.get('sample_width')
            else:
                device_sample_widths[device_name] = settings['sample_width_default']


                #print(cam_settings)
    #print (devices_to_run)

    #sys.exit()

    #print(device_sample_widths)
    #print(devices_to_send_samples)

    while scheduler.is_running():

        for device_to_run_name in devices_to_run:
            run_name = "photo_run_" + device_to_run_name
            sample_upload_name = "sample_upload_" + device_to_run_name

            device_to_run_seconds = devices_to_run[device_to_run_name]

            if scheduler.is_time_for(run_name, device_to_run_seconds):
                #print(str(device_to_run_seconds) + "launch run for" + device_to_run_name)
                subprocess.Popen(["photobot", "run",device_to_run_name])

            #print("schedule sample for " + device_to_run_name + " for " + str(devices_to_send_samples[device_to_run_name]) + " width " + str(device_sample_widths[device_to_run_name]))

            if scheduler.is_time_for(sample_upload_name,devices_to_send_samples[device_to_run_name]):

                uploader.upload_by_type(device_to_run_name,device_sample_widths[device_to_run_name])

        if scheduler.is_time_for("usb_run",settings['usb_seconds_between_starts']):
            subprocess.Popen(["/var/photobot/env3/bin/python", "/var/photobot/src/photobot.py", "--settings", "/var/photobot/config/photobot.ini"])

        if scheduler.is_time_for("ptz_run",settings['ptz_seconds_between_starts']):
            subprocess.Popen(["/var/photobot/env2/bin/python", "/var/photobot/src/photobot_lorex.py", "--settings=/var/photobot/config/photobot.ini"])

        if scheduler.is_time_for("thermal_capture", settings['thermal_delay_between_photos']):
            if is_dark() or not settings.get('thermal_sync_to_usb',None):
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


