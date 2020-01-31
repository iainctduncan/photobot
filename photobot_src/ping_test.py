import requests
import json
import socket
from configparser import ConfigParser
import argparse
import subprocess

def send_ping():

    hostname = socket.gethostname()

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

    per_round = settings['photos_per_round']
    bot_name = settings['photobot_name']
    #print (per_round)
    data = {'photos_per_round': settings['photos_per_round'],'name': bot_name}
    data_json = json.dumps(data)

    r = requests.put('http://127.0.0.1:6543/receiver', data_json)

if __name__ == "__main__":
    subprocess.Popen(["/var/photobot/env3/bin/python", "/var/photobot/src/photobot.py",
                      "--settings /var/photobot/config/photobot.ini"])
