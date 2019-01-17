# python script to setup photobot on pi
import subprocess
from datetime import datetime
import time
import sys
import os
import logging
import argparse
from string import Template
import uuid

from install_helpers import InstallHelper

class PhotobotConfigurator(InstallHelper):

    def __init__(self, args):
        self.args = args
        self.config_template_path = "/var/photobot/src/photobot.template.ini"
        self.config_filename = "photobot.ini"
        self.config_dir = "/var/photobot/config/"

        self.question_order = [
            "photobot_name",
            "capture_dir",
            "photos_per_round",
            "number_of_rounds",
            "delay_between_rounds",
            "delay_between_photos",
            "lorex_host",
            "lorex_port",
            "lorex_user",
            "lorex_password",
            "wsdl_dir",
            "db_url",
            "minimum_latitude",
            "minimum_longitude",
            "maximum_latitude",
            "maximum_longitude"
        ]

        self.defaults = {
            "photobot_name": "",
            "photos_per_round": 3,
            "number_of_rounds": 1,
            "delay_between_rounds": 5,
            "delay_between_photos": 3,
            "capture_dir": "/var/captures",
            "wsdl_dir": "/var/photobot/env2/wsdl",
            "lorex_host": "",
            "lorex_port": "80",
            "lorex_user": "admin",
            "lorex_password": "admin",
            "db_url": "sqlite:////mnt/usbstorage/ais/ais_receiver.db",
            "minimum_latitude": 48.8,
            "minimum_longitude": -123.37,
            "maximum_latitude": 48.9,
            "maximum_longitude": -123.25

        }
        new_uuid = uuid.uuid4()
        self.final_values = {
            "photobot_uuid" : new_uuid
        }

    def main(self):
        print("Running photobot configuration utilities")

        if not self.confirm("Did you execute this as sudo?"):
            self.exit()
        self.ask_for_configurations()
        self.put_values_in_config(self.final_values)

    def put_values_in_config(self,values_dict):
        filein = open(self.config_template_path)
        # read it
        src = Template(filein.read())
        result = src.substitute(values_dict)
        print (result)
        self.mkdir(self.config_dir)
        config_file_path = self.config_dir + self.config_filename
        config_out = open(config_file_path,"w")
        print ("writing config to file: " + config_file_path)
        config_out.write(result)

    def ask_for_configurations(self):
        print ("Choose Configuration Values. Just hit enter to use the default (if provided) ")
        for question in self.question_order:
            default = self.defaults[question]
            self.ask_for_configuration(question,default)

    def ask_for_configuration(self,key,default):

        default = str(default)
        response_val = raw_input(key + " [" + default + "]: ")

        if response_val == '':
            response_val = default

        if response_val == '':
            print(key + " needs a value. Please choose one ")
            self.ask_for_configuration(key,default)

        self.final_values[key]=response_val



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action="store_true", help="print commands but don't run them")
    parser.add_argument('--wpa-file', help="alternate networking file to patch")
    args = parser.parse_args()

    installer = PhotobotConfigurator(args)
    installer.main()