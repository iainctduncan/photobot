import subprocess
from datetime import datetime
import time as timer
import os
import sys
import logging
import argparse
from configparser import ConfigParser

import importlib
import traceback
from .sample_uploader import *
from .photobot_camera import *
from picamera import PiCamera

class Pi_HQ_Camera(Photobot_Camera):

    def __init__(self, settings):
        self.settings = settings

        print(self.settings)

        self.camera = PiCamera()

        # camera.capture(filename)

        rotation = self.setting('rotation_degrees')
        if rotation:
            self.camera.rotation = rotation

        shutter_speed = self.setting('shutter_speed')
        if shutter_speed:
            self.camera.shutter_speed=int(shutter_speed)


    @classmethod
    def customize_defaults(cls, defaults):
        defaults['jpeg_quality'] = 75
        return defaults


    def save_image(self, filename):
        print("Taking Pi HQ image using Python Library")

       # args = ' -awb cloud -t 50'


        self.camera.capture(filename,format="jpeg",quality=int(self.setting('jpeg_quality')))

    def save_image_commandline(self, filename):
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
