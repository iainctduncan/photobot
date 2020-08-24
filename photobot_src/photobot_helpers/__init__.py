import requests
import json
import socket
import logging
from configparser import ConfigParser
import argparse
import sys
import os
import string
from datetime import datetime as date_time
from datetime import timedelta
import time as timer
import pytz

from .sunset import *

from .power_cycle import power_cycle
import subprocess
from subprocess import Popen, PIPE
from .config_fetch import *

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z
def get_phone_home_url():
    #return "http://127.0.0.1:6543/ping"
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


def get_logger():
    try:
        log = setup_logging('/var/photobot/logs/photobot.log', logging.INFO)
        return log
    except IOError as exc:
        print("can't setup log")
        return False


def send_ping(subsystem='PI',msg='Ping',status='OK',custom_params={}):

    hostname = socket.gethostname()

    settings = get_settings_dict()

    bot_name = settings['photobot_name']
    installation_id = settings['installation_id']
    # print (per_round)
    data = {
        'name': bot_name,
        'installation_id': installation_id,
        'pi_cpu_id': settings['pi_cpu_serial'],
        'subsystem': subsystem,
        'msg': msg,
        'status': status
    }

    data = merge_two_dicts(data,custom_params)

    phone_home_url = get_phone_home_url() #settings['phone_home_url']
    data_json = json.dumps(data)


    print("sending ping to " + phone_home_url)
    print(msg)

    try:
        r = requests.put(phone_home_url, data_json)
    except:
        print("Couldn't connect to host")

def error_and_quit(error_msg,subsystem):
    log = get_logger()
    log.info(error_msg)
    #settings = get_settings_dict()
    send_ping(subsystem,error_msg, "ERROR")
    sys.exit()

def get_photo_filename(installation_id,prefix='capture',extension='jpg'):
    "return a filename with date and time, ie: capture_2017-04-02_02-03-12"
    time_str = str(date_time.now()).split('.')[0].replace(' ','_').replace(':','-')
    filename = installation_id+ '_'+prefix + '_' + time_str + '.' + extension

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
    settings = get_settings_dict()
    return settings.get("drive_dev_address","/dev/sda1")

def mount_drive(drive_path):


    dev_address = get_usb_drive_dev_address()

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
    send_ping('pi',install_id + " rebooted","OK")

def clean_tmp_files():
    os.system("rm -f /root/tmpfile*")

def notify_drive_full(drive_path):

    error_and_quit("Drive: " + drive_path + " is full ","disk")

def notify_drive_readonly(drive_path):

    error_and_quit("Drive: " + drive_path + " is read only - will reboot ","disk")

def notify_drive_unmountable(drive_path):

    error_and_quit("Drive: " + drive_path + " could not be mounted","disk")

def notify_drive_mounted(drive_path):

    error_and_quit("Drive: " + drive_path + " was mounted successfully","disk")


def test_if_writeable(path):
    filepath = path + "/writetest.txt"

    try:
        filehandle = open(filepath, 'w')

    except IOError:
        os.system('reboot')
        #error_and_quit("Drive is Readonly - Rebooting", "DISK")
        notify_drive_readonly(path)

        return False

    return True

def get_capture_target_dir():
    drive_path = get_usb_storage_path()
    if drive_is_mounted(drive_path):
        #print("is mounted!!")
        free_space = get_mb_free_by_path(drive_path)
        #print("free space is: "+str(free_space) + "MB")
        if free_space > 100:
            test_if_writeable(drive_path)
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
    try:
        mb_free = int(full_result.splitlines()[1])
    except:
        mb_free=-1

    return mb_free

def log_latest_photo_path(path,type='usb'):
    with open("/var/photobot/logs/latest_photo_"+type+".log", "w") as f:
        f.write( str(path) )

def get_lastest_photo_path(type='usb'):
    try:
        with open("/var/photobot/logs/latest_photo_"+type+".log", "r") as f:
            path = str(f.read())
            return path.rstrip()

    except:
        return False

def log_latest_photo_sent_path(path,type='usb'):
    with open("/var/photobot/logs/latest_photo_sent_"+type+".log", "w") as f:
        f.write( str(path) )

def get_lastest_photo_sent_path(type='usb'):
    try:
        with open("/var/photobot/logs/latest_photo_sent_"+type+".log", "r") as f:
            path = str(f.read())
            return path.rstrip()

    except:
        return False

def ensure_dir(dir):

    exists = os.path.isdir(dir)
    if not exists:
       os.system("mkdir " + dir)

def get_ptz_ip():
    full_result = os.popen("lanscan scan").read()
    for line in full_result:
        print(line)

def add_seconds_to_time(tm, secs):
    fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + timedelta(seconds=secs)
    return fulldate.time()

def rescan_network_for_devices():

    now = int(timer.time())
    #print(now)

    settings = get_settings_dict()

    latest_netsearch = int(get_lastest_netsearch_time())

    diff = now - latest_netsearch

    minimum_seconds_between_scans = settings['netscan_minimum_interval']

    #print(minimum_seconds_between_scans)

    if diff>minimum_seconds_between_scans:
        os.system("photobot netsearch")
        log_latest_netsearch_time(now)
        send_ping("pi","Rescanned Network for Devices")
    else:
        minimum_minutes_between_scans = str(minimum_seconds_between_scans/60)
        print("skipping netsearch, since it was done within last " + minimum_minutes_between_scans + " mins")


def log_latest_netsearch_time(time):
    with open("/var/photobot/logs/latest_netsearch.log", "w") as f:
        f.write( str(time) )

def get_lastest_netsearch_time():
    try:
        with open("/var/photobot/logs/latest_netsearch.log", "r") as f:
            path = str(f.read())
            return path.rstrip()

    except:
        return False

def is_dark():
    settings = get_settings_dict()
    s = sun(float(settings['minimum_latitude']), float(settings['minimum_longitude']))

    now = date_time.now(pytz.timezone(settings['timezone']))

    sunset_extension_minutes = int(settings.get('sunset_extension_minutes',45))

    sunset_extension_seconds = 60 * sunset_extension_minutes
    ##print(sunset_extension_seconds)

    #print (s.sunset(now))

    if(now.time().hour >12):

        sunset = s.sunset(now)
        sunset_adjusted = add_seconds_to_time(sunset,sunset_extension_seconds)

        #sunset_timestamp = timer.mktime(sunset)
        #print (sunset_timestamp)
        if now.time() > sunset_adjusted:
            return True
    else:
        sunrise = s.sunrise(now)
        sunrise_adjusted = add_seconds_to_time(sunrise, (-1 * sunset_extension_seconds))

        if now.time() < sunrise_adjusted:
            return True


    return False

def popen_timeout(command, timeout):
    p = Popen(command, stdout=PIPE, stderr=PIPE)
    for t in xrange(timeout):
        timer.sleep(1)
        if p.poll() is not None:
            return p.communicate()
    p.kill()
    return False

def capture_thermal_image():

    log = get_logger()
    settings = get_settings_dict()

    if str(settings['enable_thermal_camera']) =='0':
        log.info("Thermal Camera is disabled. Exiting")
        send_ping("thermal", "Thermal disabled", "Off")
        return;

    target = get_capture_target_dir()
    os.chdir(target)
    photo_command="FLIRA65-Capture"
    log.info("starting thermal photo capture")

    if popen_timeout(photo_command,4):


        latest_image_path = os.path.abspath(os.readlink(target + "/latest.png"))
        final_path = target + "/" + get_photo_filename(settings['installation_id'],'thermal','png')

        if os.path.exists(latest_image_path):
            log.info("completed thermal photo capture")
            os.rename(latest_image_path,final_path)
            rotation_degrees = str(settings.get('thermal_rotation_degrees', 180))
            log_latest_photo_path(final_path, "thermal")
            send_ping("thermal", "Captured Thermal Image")

            if rotation_degrees:

                #rotation degrees could also be 'flip' for vertical flip or 'flop' for horizontal flip
                if str.isdigit(rotation_degrees):
                    os.system("mogrify -rotate " + rotation_degrees + " " + final_path)
                else:
                    os.system("mogrify -" + rotation_degrees + " " + final_path)
        else:
            send_ping("thermal", "Error Capturing Photo - Could not connect to camera","ERROR")



    else:
        send_ping("thermal", "ERROR capturing photo (process hung)","ERROR")
        log.info("thermal capture failed (process hung)")
        #error_and_quit("ERROR capturing photo (process hung)", 'thermal')
