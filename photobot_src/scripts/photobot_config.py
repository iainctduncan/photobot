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

def get_pi_cpu_serial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial

class InstallHelper(object):
    def do(self, command, kw=None):
        "print and execute a shell command, exiting on failure"
        if kw:
            command = command.format(**kw)
        print(command)
        if not self.args.dry_run:
            try:
                subprocess.check_call(command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
            except:
                print("\nERROR executing command: '%s'" % command)
                if self.confirm("continue anyway?"):
                    return
                else:
                    sys.exit()

    def mkdir(self,dir):

        exists = os.path.isdir(dir)
        if exists:
            print (dir + " exists already") # Store configuration file values
        else:
            self.do("mkdir " + dir)

    def confirm(self, question, allow_no=True):
        "ask user for confirmation to do task, returns result as boolean"
        while True:
            if allow_no:
                res = raw_input("%s y/n/x >> " % question)
            else:
                res = raw_input("%s y/x >> " % question)

            if res.lower() == 'x':
                print("\nEXITING")
                self.exit()
            if res.lower() in ('y','yes'):
                return True
            if res.lower() in ('n','no'):
                return False
            # anything else, we reask the question


    def exit(self):
        print("EXITING")
        sys.exit()

class PhotobotConfigurator(InstallHelper):

    def __init__(self, args):
        self.args = args
        self.config_template_path = "/var/photobot/src/photobot.template.ini"
        self.config_filename = "photobot.ini"
        self.config_dir = "/var/photobot/config/"

        self.subquestion_order = {
            "enable_ptz_camera":[
                "ptz_host",
                "ptz_port",
                "ptz_user",
                "ptz_password",
                "wsdl_dir",
                "ptz_photos_per_round",
                "ptz_number_of_rounds",
                "ptz_delay_between_rounds",
                "ptz_delay_between_photos"
            ],
            "enable_usb_camera":[
                "photos_per_round",
                "number_of_rounds",
                "delay_between_rounds",
                "delay_between_photos"
            ],
            "enable_ais_receiver":[
                "db_url",
                "minimum_latitude",
                "minimum_longitude",
                "maximum_latitude",
                "maximum_longitude"
            ],
            "enable_thermal_camera": [
                "thermal_delay_between_photos"
            ]

        }
        self.question_order = [
            "installation_id",
            "photobot_name",
            "capture_dir",
            "enable_usb_camera",
            "enable_ptz_camera",
            "enable_thermal_camera",
            "enable_ais_receiver"

        ]

        self.defaults = {
            "installation_id": "",
            "photobot_name": "",
            "capture_dir": "/var/captures",

            "enable_usb_camera": {
                "photos_per_round": 3,
                "number_of_rounds": 1,
                "delay_between_rounds": 5,
                "delay_between_photos": 3,
            },

            "enable_ptz_camera": {
                "ptz_host": "",
                "ptz_port": "80",
                "ptz_user": "admin",
                "ptz_password": "admin",
                "wsdl_dir": "/var/photobot/env2/wsdl",
                "ptz_photos_per_round": 3,
                "ptz_number_of_rounds": 1,
                "ptz_delay_between_rounds": 5,
                "ptz_delay_between_photos": 3,
            },
            "enable_ptz_camera": {
                "thermal_delay_between_photos":60
            },
            "enable_ais_receiver": {
                "db_url": "sqlite:////mnt/usbstorage/ais/ais_receiver.db",
                "minimum_latitude": 48.8,
                "minimum_longitude": -123.37,
                "maximum_latitude": 48.9,
                "maximum_longitude": -123.25
            }

        }


        self.final_values = {
            "pi_cpu_serial" : get_pi_cpu_serial()
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


        if type(default) is dict:
            response_val = raw_input(key + " y/n : ")

            if response_val == 'y':
                self.final_values[key] = 1
                sub_order = self.subquestion_order[key]
                for sub_question in sub_order:
                    sub_default =self.defaults[key][sub_question]
                    self.ask_for_configuration(sub_question,sub_default)
                return

            elif response_val== 'n':
                self.final_values[key] = 0
                sub_order = self.subquestion_order[key]
                for sub_question in sub_order:
                    sub_default = self.defaults[key][sub_question]
                    self.final_values[sub_question]=sub_default
                return
            else:
                print("Please choose Y or N");
                return self.ask_for_configuration(key,default)

        else:
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