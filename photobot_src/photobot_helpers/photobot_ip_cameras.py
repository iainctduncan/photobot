import subprocess
from datetime import datetime
import time as timer
import os
import sys
import logging

#from lorex import *

import argparse
from configparser import ConfigParser
import importlib
import traceback
from onvif import ONVIFCamera
from requests.auth import HTTPDigestAuth,HTTPBasicAuth
import shutil

from . import *
from .sample_uploader import *
from .photobot_camera import *
#from .photobot_camera import *

class IPCam(Photobot_Camera):

    def identify(self):
        print("I am Generic")

    def __init__(self, **settings):
        self._host = settings['host']
        self._port = settings['port']
        # default to the out of box lorex user/pass combo
        self._user = settings.get('user', 'admin')
        self._password = settings.get('password', 'admin')
        self._wsdl_dir = settings.get('wsdl_dir', './wsdl')

        self.identify()

        self._cam = ONVIFCamera(self._host, self._port, self._user,
            self._password, self._wsdl_dir)

        # Create media service object and save media profile
        # this is copied from the onvif examples
        media = self._cam.create_media_service()
        profiles = media.GetProfiles()
        #print(profiles)
        self._media_profile = profiles[1]
        self._media_service = media

    def _get_snaphot_uri(self):

        #print(self._media_profile._token)
        "method to return the uri for saving a snapshot from the camera"
        request = self._media_service.create_type('GetSnapshotUri')
        request.ConfigurationToken = self._media_profile.VideoSourceConfiguration._token
        snapshot_uri_obj = self._media_service.GetSnapshotUri({
            'ProfileToken': self._media_profile._token})
        snapshot_uri = snapshot_uri_obj['Uri']
        return snapshot_uri

    def auth_mode(self):
        return "basic"

    def get_snapshot_resource(self):
        snapshot_uri = self._get_snaphot_uri()

        if(self.auth_mode()=='basic'):
            res = requests.get(snapshot_uri, auth=HTTPBasicAuth(self._user, self._password), stream=True)
        else:
            res = requests.get(snapshot_uri, auth=HTTPDigestAuth(self._user, self._password), stream=True)

        return res

    def save_image(self, filename):
        "save an image from the camera to filename"

        #print(snapshot_uri)

        res = self.get_snapshot_resource()

        if res.status_code == 200:
            with open(filename, 'wb') as f:
                res.raw.decode_content = True
                shutil.copyfileobj(res.raw, f)
            #log.info("Image saved to %s" % filename)
        else:
            print("ERROR saving file, response: %s" % res)

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

