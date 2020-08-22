from ruamel.yaml import YAML
from configparser import ConfigParser
import argparse
import sys
import os


def get_settings_dict():
    # register the process identifier utility for multiprocess logging
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--settings',
        help='Path to settings INI file for Lorex photobot',
        required=True)

    argparser.add_argument(
        '--send_high_res_sample',
        help='Set this option to take a single photo and upload a full-res sample',
        required=False)

    argparser.add_argument(
        '--camera',
        help='Set this option to specify the camera to run',
        required=False)


    options = argparser.parse_args()
    settings_file = options.settings
    high_res_mode = options.send_high_res_sample
    camera = options.camera

    config = ConfigParser()
    config.read(settings_file)
    settings = dict(config.items('app:main'))

    # if we have a yaml config add it to this array
    yaml_config_path = settings.get('yaml_config_file')
    if yaml_config_path and os.path.isfile(yaml_config_path):
        settings.update(read_yaml_config(yaml_config_path))


    if camera:
        settings['camera'] = camera
    settings['samples_user_host'] = 'samples@photobots.info'
    settings['samples_dest_path'] = '~'

    settings['usb_upload_interval'] = 3600
    settings['ptz_upload_interval'] = 3600
    settings['thermal_upload_interval'] = 3600

    if high_res_mode:
        settings['usb_sample_width'] = 0
        settings['ptz_sample_width'] = 0
        settings['high_res_sample_mode'] = True
    else:
        settings['usb_sample_width'] = 800
        settings['ptz_sample_width'] = 800
        settings['high_res_sample_mode'] = False

    #settings['usb_sample_width'] = 800

    settings['thermal_sample_width'] = 0

    settings['alive_ping_interval'] = 500
    settings['disk_check_interval'] = 3600
    settings['netscan_minimum_interval'] = 900

    settings['timezone'] = 'US/Pacific'

    if 'thermal_delay_between_photos' not in settings:
        settings['thermal_delay_between_photos'] = 60

    if 'usb_seconds_between_starts' not in settings:
        settings['usb_seconds_between_starts'] = 60

    if 'ptz_seconds_between_starts' not in settings:
        settings['ptz_seconds_between_starts'] = 60

    if 'enable_thermal_camera' not in settings:
        settings['enable_thermal_camera'] = 0

    # Set old default values to prevent breaking. Shouldn't really be used.
    settings["ptz_number_of_rounds"] = 1
    settings["ptz_delay_between_rounds"] = 5
    settings["number_of_rounds"] = 1
    settings["delay_between_rounds"] = 5



    return settings

def get_yaml_config_dict():


    settings = get_settings_dict()

    yaml_config_file = settings.get('yaml_config_file')

    if not yaml_config_file:
        print("no YAML config file path")
        exit()

    return read_yaml_config(yaml_config_file)

def read_yaml_config(yaml_config_file):
    yaml = YAML()
    with open(yaml_config_file, 'r') as stream:
        try:
            config_dict = yaml.load(stream)

        except yaml.YAMLError as exc:
            print(exc)

    return config_dict