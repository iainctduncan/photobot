import requests
import json
import socket
import logging
from configparser import ConfigParser
import argparse
import sys
import os
from datetime import datetime


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z
def get_phone_home_url():
    return "http://photobots.info/ping"

def setup_logging(log_filepath, log_level=logging.INFO):
    "setup the python logging structure"
    # set up logging, saves output to a log file
    log = logging.getLogger("PHOTOBOT")
    fh = logging.FileHandler(log_filepath)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    log.addHandler(fh)
    log.addHandler(ch)
    log.level = log_level
    return log

def get_settings_dict():
    # register the process identifier utility for multiprocess logging
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--settings',
        help='Path to settings INI file for Lorex photobot',
        required=True)
    options = argparser.parse_args()
    settings_file = options.settings

    config = ConfigParser()
    config.read(settings_file)
    settings = dict(config.items('app:main'))
    return settings

def get_logger():
    try:
        log = setup_logging('/mnt/usbstorage/captures/photobot.log', logging.INFO)
    except IOError as exc:
        # fall back to logging in local dir
        try:
            log = setup_logging('/var/photobot/photobot.log', logging.INFO)
        except IOError as exc:
            log = setup_logging('photobot.log', logging.INFO)
    return log

def send_ping(settings,msg='Ping',status='OK',custom_params={}):

    hostname = socket.gethostname()

    # register the process identifier utility for multiprocess logging
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--settings',
        help='Path to settings INI file for Lorex photobot',
        required=True)

    options = argparser.parse_args()
    settings_file = options.settings

    bot_name = settings['photobot_name']
    installation_id = settings['installation_id']
    # print (per_round)
    data = {
        'name': bot_name,
        'installation_id': installation_id,
        'pi_cpu_id': settings['pi_cpu_serial'],
        'msg' : msg,
        'status': status
    }

    data = merge_two_dicts(data,custom_params)

    phone_home_url = get_phone_home_url() #settings['phone_home_url']
    data_json = json.dumps(data)

    print("sending ping to " + phone_home_url)

    try:
        r = requests.put(phone_home_url, data_json)
    except:
        print("Couldn't connect to host")

def error_and_quit(error_msg):
    log = get_logger()
    log.info(error_msg)
    settings = get_settings_dict()
    send_ping(settings,error_msg, "ERROR")
    sys.exit()

def get_photo_filename(installation_id,prefix='capture'):
    "return a filename with date and time, ie: capture_2017-04-02_02-03-12"
    time_str = str(datetime.now()).split('.')[0].replace(' ','_').replace(':','-')
    filename = installation_id+ '_'+prefix + '_%s.jpg' % time_str

    return filename

def drive_is_mounted(path):
    mounted_result = os.system("grep -qs '"+path+" ' /proc/mounts")

    if mounted_result:
        is_mounted = False
    else:
        is_mounted = True

    #print("path" + path + " is mounted? "+str(is_mounted))
    return is_mounted



#todo complete mounting
def mount_drive(drive_path):
    return False

def notify_drive_full(drive_path):
    settings = get_settings_dict()
    send_ping(settings,"Drive: " + drive_path + " is full ","Error")

def notify_drive_unmountable(drive_path):
    settings = get_settings_dict()
    send_ping(settings,"Drive: " + drive_path + " is unmbountable ","Error")

def get_capture_target_dir():
    drive_path = "/mnt/usbstorage"
    if drive_is_mounted(drive_path):
        #print("is mounted!!")
        free_space = get_mb_free_by_path(drive_path)
        #print("free space is: "+str(free_space) + "MB")
        if free_space > 100:
            return drive_path + "/captures"
        else:
            notify_drive_full(drive_path)

    else:
        mount_drive(drive_path)
        if drive_is_mounted(drive_path):
            return get_capture_target_dir()
        else:
            notify_drive_unmountable(drive_path)


def get_mb_free_by_path(path):
    full_result = os.popen("df -m "+path+" --output=avail ").read()
    mb_free = full_result.splitlines()[1]
    return mb_free

def log_latest_photo_path(path):
    with open("/var/photobot/logs/latest_photo.log", "w") as f:
        f.write( str(path) )

def get_lastest_photo_path():
    with open("/var/photobot/logs/latest_photo.log", "r") as f:
        return str(f.read())