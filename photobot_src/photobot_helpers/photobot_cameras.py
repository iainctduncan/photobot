import subprocess
from datetime import datetime
import time as timer
import os
import sys
import logging
from lorex import *
import argparse
from configparser import ConfigParser
import importlib
import traceback

from . import *
from .sample_uploader import *


class ANPViz_Bullet(IPCam):
    def identify(self):
        print("I am anpviz bullet")


class CamHi_PTZ(IPCam):
    def identify(self):
        print("I am camhi")

    def _get_snaphot_uri(self):
        return "http://" + self._host + "/snap.jpg"

    @classmethod
    def customize_defaults(cls, defaults):
        defaults['delay_between_photos']=5
        return defaults

class Pi_HQ_Camera(Photobot_Camera):

    def __init__(self, settings):
        self.settings = settings

        print(self.settings)

    @classmethod
    def customize_defaults(cls, defaults):
        defaults['jpeg_quality'] = 25
        return defaults

    def save_image(self, filename):
        print("Taking Pi HQ image...")

        args =''

        rotation = self.setting('rotation_degrees')
        if rotation:
            args = args + " --rotation " + str(rotation)

        shutter_speed = self.setting('shutter_speed')
        if shutter_speed:
            args = args + " --shutter " + str(shutter_speed)

        jpeg_quality = self.setting('jpeg_quality')
        if jpeg_quality:
            args = args + " --quality " + str(jpeg_quality)

        print("raspistill " + args + " -o " + filename)
        os.system("raspistill " + args + " -o " + filename)


class Photobot_Camera_Run(object):

    def __init__(self,device_name,*settings):
        #print("default cam")
        self.device_name=device_name

        self.settings = settings[0]

    def setting(self,setting_name):

        default_value = self.get_setting_default(setting_name)
        return str(self.settings.get(setting_name,default_value))

    def get_setting_default(self,name):
        CameraClass = self.camera_class()
        return CameraClass.get_default_value(name)

    def get_required_settings(self):
        required_settings = [
            'photos_per_round',
            'number_of_rounds',
            'delay_between_photos',
            'wsdl_dir',
            'host',
            'port',
            'user',
            'password'
        ]

        return required_settings

    def camera_class(self):
        camera_class = self.settings["camera_class"]
        # print(camera_class)

        mod = sys.modules['photobot_helpers.photobot_cameras']

        CameraClass = getattr(mod, camera_class)
        return CameraClass

    def host(self):
        if self.setting('host'):
            return self.setting('host')
        else:
            return self.device_name

    def photo_run(self):

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

        if self.setting('enable') == '0':
            log.info(self.device_name + " is disabled. Exiting")
            send_ping(self.device_name, self.device_name + " disabled", "Off")
            sys.exit()

        if is_dark() and not self.setting('run_at_night'):
            send_ping(self.device_name, "No photo taken because it is dark", "SLEEP")
            sys.exit()

        # exit if settings file missing items
        for setting_name in self.get_required_settings():
            #print(setting_name)
            #print(self.setting(setting_name))
            if self.setting(setting_name) is None:
                #print("missing " + setting_name)
                error_and_quit("Missing setting '%s' in config" % setting_name, self.device_name)
                raise Exception("Missing setting '%s' in config" % setting_name)

        # set file path and log level for logging

        log.info("-----------------------------------------------------------------------------")
        log.info("EXECUTING RUN at %s" % datetime.now())


        cam = self.instantiate_camera()

        # execute X rounds of Y pictures according to settings

        for i in range(0, int(self.setting('photos_per_round'))):
            filename = get_photo_filename(settings['installation_id'], self.device_name + '_capture')

            # save capture from camera
            cam.save_image(get_capture_target_dir() + "/" + filename)
            log_latest_photo_path(get_capture_target_dir() + "/" + filename, self.device_name)

            if settings['high_res_sample_mode']:
                uploader = Sample_Uploader()
                uploader.settings = settings
                uploader.upload_by_type(self.device_name,0)
                sys.exit()

            timer.sleep(int(self.setting('delay_between_photos')))

            # photo home

        send_ping(self.device_name, "Completed " + self.device_name + " Run", "OK")

    def instantiate_camera(self):

        if self.setting("mac_address"):
            #print("using ip cam")
            return self.instatiate_ip_camera()
        else:
            #print("using attached cam")
            return self.instatiate_attached_camera()

    def instatiate_attached_camera(self):
        # instantiate our attached cameras
        # these settings could come from env variables. How will we get the network address??

        try:

            CameraClass = self.camera_class()

            cam = CameraClass(self.settings)
            #print(cam)

        except Exception:
            error_and_quit("Could not instantiate attached camera " + self.device_name,self.device_name)

        return cam

    def instatiate_ip_camera(self):
        # instantiate our ipcamera

        try:
            CameraClass = self.camera_class()

            cam = CameraClass(
                host=self.host(),
                port=self.setting('port'),
                user=self.setting('user'),
                password=self.setting('password'),
                wsdl_dir=self.setting('wsdl_dir'),
            )

        except Exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            mac_address = self.setting('mac_address') #settings.get('devices', {}).get(self.device_name, {}).get('mac_address')

            if mac_address:
                rescan_network_for_devices()

            error_and_quit("Could not connect to " + self.device_name+" camera at " + self.host(), self.device_name)

        return cam