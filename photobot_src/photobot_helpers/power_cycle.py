try:
    import RPi.GPIO as GPIO
except:
    GPIO=None

import time
import os
import time as timer
from .config_fetch import *

def power_cycle():

    yaml_config = get_yaml_config_dict()

    webbar_outlet = yaml_config.get('devices').get('usb').get('webbar_outlet')
    creds = yaml_config.get('devices').get('webbar').get('api_creds')

    print(webbar_outlet);
    print(creds);

    if webbar_outlet:
        power_cycle_via_webbar(webbar_outlet,creds)
    else:
        power_cycle_gpio(5,21)

def power_cycle_gpio(seconds=5,pin=21):

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

    time.sleep(seconds)
    GPIO.output(pin, GPIO.LOW)

    time.sleep(1)
    GPIO.cleanup()

def power_cycle_via_webbar(outlet_num,api_creds,off_seconds=5):
    outlet_num = int(outlet_num)
    outlet_internal = str(outlet_num-1)

    username = api_creds.get('username');
    password = api_creds.get('password');
    port = api_creds.get('port');

    off_command = "curl --digest -u "+ username +":"+password+" -X PUT -H \"X-CSRF: x\" --data \"value=false\" \"http://webbar:"+port+"/restapi/relay/outlets/"+outlet_internal+"/state/\""

    on_command = "curl --digest -u " + username + ":" + password + " -X PUT -H \"X-CSRF: x\" --data \"value=true\" \"http://webbar:" + port + "/restapi/relay/outlets/" + outlet_internal + "/state/\""

    #print(off_command)
    os.system(off_command)
    timer.sleep(off_seconds)
    os.system(on_command)