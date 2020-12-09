# following lines were used for trying to work on python 3, which proved unsuccessful
#import zeep
#from onvif import ONVIFCamera, ONVIFService
#def zeep_pythonvalue(self, xmlvalue):
#    return xmlvalue

#zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

import requests
from requests.auth import HTTPDigestAuth,HTTPBasicAuth
import shutil
from datetime import datetime
from .photobot_ip_cameras import *

import logging
log = logging.getLogger(__name__)
import pdb
from onvif import ONVIFCamera
#from . import photobot_cameras

ptz_delay_between_photos = 3
ptz_photos_per_round = 3
ptz_seconds_between_starts = 60

class LorexCam(IPCam):
    def auth_mode(self):
        return "digest"

    def identify(self):
        print("I am LOREX ")