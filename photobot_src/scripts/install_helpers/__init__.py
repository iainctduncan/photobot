# python script to setup photobot on pi
import subprocess
from datetime import datetime
import time
import sys
import os
import logging
import argparse

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