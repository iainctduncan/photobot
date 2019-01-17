import requests
import json
import socket
from configparser import ConfigParser
import argparse

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def send_ping(settings,custom_params={}):

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
    installation_uuid = settings['photobot_uuid']
    # print (per_round)
    data = {
        'name': bot_name,
        'installation_uid': installation_uuid,
        'status': 'OK'
    }

    data = merge_two_dicts(data,custom_params)

    phone_home_url = settings['phone_home_url']
    data_json = json.dumps(data)

    r = requests.put(phone_home_url, data_json)