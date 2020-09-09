import os
import sys
from . import *
from datetime import datetime

class SafeConfigEditor(object):
    def __init__(self, config_file_path,example_file_path):
        self.config_file_path = config_file_path
        self.example_file_path=example_file_path

        now = datetime.now()
        self.date_time_string = now.strftime("%Y-%m-%d-%H-%M-%S-")

        #print(self.config_file_path)

    def run_safe_edit(self):
        self.ensure_file_exists()
        self.backup_existing_config()
        self.edit_file()

    def ensure_file_exists(self):
        if not os.path.isfile(self.config_file_path):
            print("No existing config file found - copying example config file")
            self.do("cp " + self.example_file_path + " " + self.config_file_path)

    def edit_file(self):

        self.mkdir(self.config_root_path() + "editing")
        if not os.path.isfile(self.temp_edit_path()):
            self.copy(self.config_file_path,self.temp_edit_path())

        self.do("nano " + self.temp_edit_path())

        if(self.has_valid_yaml(self.temp_edit_path())):
            self.bold_status("Configuration looks good!")
            if self.confirm("Replace live config?"):
                self.copy(self.temp_edit_path(),self.config_file_path,True)
            else:
                self.bold_status("OK, aborting. Original file is unmodified and temporary version with your changes is at:\n" + self.temp_edit_path())
        else:
            self.bold_status("---------------\nYAML parse error!\n---------------")
            if self.confirm("Try editing again?"):
                self.edit_file()
            else:
                self.bold_status("OK, aborting. Original file is unmodified and temporary version with your changes is at:\n"+self.temp_edit_path())


    def bold_status(self,msg):
        print("\n--------------------------------------------------------\n " + msg +" \n--------------------------------------------------------\n")

    def has_valid_yaml(self,yaml_config_file):
        yaml = YAML()
        with open(yaml_config_file, 'r') as stream:
            try:
                config_dict = yaml.load(stream)
                return True

            except:
                print("could not parse YAML file:  " + yaml_config_file)
                return False

    def config_root_path(self):
        return "/var/photobot/config/"

    def temp_edit_path(self):
        return self.config_root_path() + "editing/"+self.timestamped_filename()

    def backup_existing_config(self):
        self.mkdir(self.config_file_path +"backups")
        self.do("cp " + self.config_file_path + " " + self.config_root_path() + "backups/" + self.timestamped_filename())

    def timestamped_filename(self):
        base_filename = os.path.basename(self.config_file_path)
        return self.datetime_string() + base_filename

    def datetime_string(self):

        return self.date_time_string

    def copy(self,src,dest,force=False):

        flags =""

        if force:
            flags = " -f "
        self.do("cp " + flags + src + " " + dest)

    def do(self, command, kw=None):
        "print and execute a shell command, exiting on failure"
        if kw:
            command = command.format(**kw)

        print(command)

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
        if not exists:
            self.do("mkdir " + dir)

    def confirm(self, question, allow_no=True):
        "ask user for confirmation to do task, returns result as boolean"
        while True:
            if allow_no:
                #res = input("%s y/n/x >> " % question)
                res = input("%s y/n/x >> " % question)
            else:
                #res = input("%s y/x >> " % question)
                res = input("%s y/x >> " % question)

            if res.lower() == 'x':
                #print("\nEXITING")
                self.exit()
            if res.lower() in ('y','yes'):
                return True
            if res.lower() in ('n','no'):
                return False
            # anything else, we reask the question

    def exit(self):
        print("EXITING")
        sys.exit()
