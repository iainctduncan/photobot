# python script to setup photobot on pi
import subprocess
from datetime import datetime
import time
import sys
import os
import logging
import argparse
from string import Template

from install_helpers import InstallHelper

class PhotobotConfigurator(InstallHelper):

    def __init__(self, args):
        self.args = args
        self.config_template_path = "/var/photobot/src/photobot.template.ini"
        self.config_filename = "photobot.ini"
        self.config_dir = "/var/photobot/config/"

        self.defaults = {
            "install_path" : "/home/pi/photobot",
            "photos_per_round" : 3,
            "number_of_rounds" : 1,
            "delay_between_rounds" : 5,
            "delay_between_photos" : 3,
            "photobot_name" : "bobbot",
            "photobot_uuid" : "iamasnowlake"
        }

    def main(self):
        print("Running photobot configuration utilities")

        if not self.confirm("Did you execute this as sudo?"):
            self.exit()
        self.put_values_in_config(self.defaults)

    def put_values_in_config(self,values_dict):
        filein = open(self.config_template_path)
        # read it
        src = Template(filein.read())
        result = src.substitute(values_dict)
        print (result)
        self.mkdir(self.config_dir)
        config_file_path = self.config_dir + self.config_filename
        config_out = open(config_file_path,"w")
        config_out.write(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action="store_true", help="print commands but don't run them")
    parser.add_argument('--wpa-file', help="alternate networking file to patch")
    args = parser.parse_args()

    installer = PhotobotConfigurator(args)
    installer.main()