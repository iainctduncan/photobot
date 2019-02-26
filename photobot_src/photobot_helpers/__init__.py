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
        log = setup_logging('/var/photobot/logs/photobot.log', logging.INFO)
    except IOError as exc:
        print("can't setup log")
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
    print(mounted_result)

    if mounted_result:
        is_mounted = False
    else:
        is_mounted = True

    #print("path" + path + " is mounted? "+str(is_mounted))
    return is_mounted




def get_usb_storage_path():
    return "/mnt/usbstorage"

def get_usb_drive_dev_address():
    return "/dev/sda1"

def mount_drive(drive_path,dev_address='/dev/sda1'):

    if drive_is_mounted(drive_path):
        return True

    mount_failed = os.system("mount %s %s" % (dev_address, drive_path))
    if mount_failed:

        #notify_drive_unmountable(drive_path)
        return False
    else:
        return True

def notify_reboot():
    settings = get_settings_dict()
    install_id = settings['installation_id']
    send_ping(settings,install_id + " rebooted","OK")

def clean_tmp_files():
    os.system("rm -f /root/tmpfile*")

def notify_drive_full(drive_path):

    error_and_quit("Drive: " + drive_path + " is full ")

def notify_drive_unmountable(drive_path):

    error_and_quit("Drive: " + drive_path + " could not be mounted")

def get_capture_target_dir():
    drive_path = get_usb_storage_path()
    if drive_is_mounted(drive_path):
        #print("is mounted!!")
        free_space = get_mb_free_by_path(drive_path)
        #print("free space is: "+str(free_space) + "MB")
        if free_space > 100:
            return drive_path + "/captures"
        else:
            clean_tmp_files()
            notify_drive_full(drive_path)

    else:
        mount_drive(drive_path)
        if drive_is_mounted(drive_path):
            return get_capture_target_dir()
        else:
            notify_drive_unmountable(drive_path)


def get_mb_free_by_path(path):
    full_result = os.popen("df -m "+path+" --output=avail ").read()
    mb_free = int(full_result.splitlines()[1])
    return mb_free

def log_latest_photo_path(path,type='usb'):
    with open("/var/photobot/logs/latest_photo_"+type+".log", "w") as f:
        f.write( str(path) )

def get_lastest_photo_path(type='usb'):
    with open("/var/photobot/logs/latest_photo_"+type+".log", "r") as f:
        return str(f.read())