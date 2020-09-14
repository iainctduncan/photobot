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

import logging
log = logging.getLogger(__name__)
import pdb
from onvif import ONVIFCamera
#from . import photobot_cameras

ptz_delay_between_photos = 3
ptz_photos_per_round = 3
ptz_seconds_between_starts = 60

class Photobot_Camera(object):


    @classmethod
    def get_default_values(cls):
        defaults = dict()

        defaults['port'] = 80
        defaults['enable'] = 1
        defaults['delay_between_photos']=3
        defaults['photos_per_round']=3
        defaults['seconds_between_starts'] = 60
        defaults['run_at_night'] = 0
        #defaults['number_of_rounds'] = 1
        #defaults['delay_between_rounds'] = 5
        defaults['user'] = 'admin'
        defaults['wsdl_dir'] = '/var/photobot/env2/wsdl'
        return defaults

    @classmethod
    def customize_defaults(cls,defaults):
        return defaults

    @classmethod
    def get_default_value(cls,name):
        defaults = cls.get_default_values()
        defaults = cls.customize_defaults(defaults)

        default_val = defaults.get(name)
        if not default_val:
            return ""

        return default_val

    def setting(self,setting_name):

        default_value = self.get_default_value(setting_name)
        return str(self.settings.get(setting_name,default_value))

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
            log.info("Image saved to %s" % filename)
        else:
            print("ERROR saving file, response: %s" % res)

class LorexCam(IPCam):
    def auth_mode(self):
        return "digest"

    def identify(self):
        print("I am LOREX ")