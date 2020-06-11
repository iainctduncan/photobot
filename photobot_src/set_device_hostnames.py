#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
from datetime import datetime
import time as timer
import os
import sys
import logging
import argparse
#from configparser import configparser
import subprocess
from ruamel.yaml import YAML

from photobot_helpers import *
from photobot_helpers.network_lookup import *
"""
Determine a host's IP address given its MAC address and an IP address
range to scan for it.

I created this to discover a WLAN printer (which dynamically gets an IP
address assigned via DHCP) on the local network.

Calls Nmap_ to ping hosts and return their MAC addresses (requires root
privileges).

Requires Python_ 2.7+ or 3.3+.

.. _Nmap: http://nmap.org/
.. _Python: http://python.org/

:Copyright: 2014-2016 `Jochen Kupperschmidt
:Date: 27-Mar-2016 (original release: 25-Jan-2014)
:License: MIT
:Website: http://homework.nwsnet.de/releases/9577/#find-ip-address-for-mac-address
"""


if __name__ == '__main__':
    #mac_address = '00:24:1D:AA:A0:1E'
    #ip_range = '192.168.1.1-255'

    yaml = YAML()

    with open("/var/photobot/config/photobot.yml", 'r') as stream:
        try:
            config_array = yaml.load(stream)

        except yaml.YAMLError as exc:
            print(exc)

    #print(config_array)

    devices =config_array.get('devices')
    ip_range = config_array.get('network_ip_range')
    #print(devices)
    macs ={}
    for device in devices:
        mac = device.get('mac_address')
        name = device.get('name')
        if mac !=None:
            macs[name]=mac

    ips = {}
    xml = scan_for_hosts(ip_range)
    for device_name in macs:
        mac_address = macs[device_name]
        ip_address = find_ip_address_for_mac_address(xml, mac_address)
        if ip_address:
            ips[device_name] = ip_address
            print('Found IP address {} for MAC address {} in IP address range {}.'
                  .format(ip_address, mac_address, ip_range))
        else:
            print('No IP address found for MAC address {} in IP address range {}.'
                  .format(mac_address, ip_range))


    #print(ips)
    for host_name in ips:

        device_ip = ips[host_name]
        #print(host_name + device_ip)
        os.system("hostsman -r "+host_name)
        os.system("hostsman -i "+host_name+":"+device_ip)

