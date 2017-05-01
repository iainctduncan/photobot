# python script to setup photobot on pi
import subprocess
from datetime import datetime
import time
import sys
import os
import logging
import argparse


class PhotobotInstaller(object):

    def __init__(self, args):
        self.args = args
        self.wpa_file = args.wpa_file or "/etc/wpa_supplicant/wpa_supplicant.conf"
        self.cron_file = args.cron_file or "/etc/crontab"


    def do(self, command, kw=None):
        "print and execute a shell command, exiting on failure"
        if kw:
            command = command.format(**kw)
        print(command)
        if not args.dry_run:
            try:
                subprocess.check_call(command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True) 
            except:
                print("\nERROR executing command: '%s'" % command)
                if self.confirm("continue anyway?"):
                    return
                else:
                    sys.exit() 


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


    def setup_wifi(self):
        # get network settings    
        # TODO check if the network is already in there
        while True:
            network_name = raw_input("Network name: ")
            network_password = raw_input("Network password: ")
            if self.confirm("Patch %s with network '%s' and password '%s'?" % 
                (self.wpa_file, network_name, network_password) ):
                break
        # patch file
        patch = """
  network={
    ssid="%s"
    psk="%s"
  }
""" % (network_name, network_password)
        if not self.args.dry_run:
            with open(self.wpa_file, "a") as wpa_file:
                wpa_file.write(patch)
        if self.confirm("wpa file patched, restart networking?"):
            self.do("ifdown wlan0")
            self.do("ifup wlan0")
        self.confirm("select 'y' to continue or 'x' to exit so you can reboot your pi")


    def install_packages(self):
        print("running apt-get update, installing nano, vim, gphoto2...")
        self.do("apt-get update")
        self.do("apt-get install nano vim")
        self.do("apt-get install gphoto2")
        if self.confirm("test gphoto2 to see camera? (plug in camera)"):
            self.do("gphoto2 --list-config")
            self.confirm("camera found, continue?", allow_no=False)    


    def setup_drive(self):
        print("setting up external USB drive")
        if self.confirm("create dir /mnt/usbstorage"):
            self.do("mkdir /mnt/usbstorage")
        self.confirm("plug in USB drive and continue", allow_no=False)
        print("checking drive ID with 'blkid'")
        self.do("blkid")
        while True:
            dev_num = int( raw_input("Enter drive number: ") )
            if self.confirm("Drive number is '%i' " % dev_num):
                break
        print("mounting /dev/sda%i" % dev_num)
        self.do("mount dev/sda%i /mnt/usbstorage")
        self.do("chmod 755 /mnt/usbstorage")        
        if self.confirm("edit fstab file to automount drive as ext3?"):
            patch = "/dev/sda%i /mnt/usbstorage /ext3 defaults 0 0"
            # patch the fstab file and test 
            if not self.args.dry_run:
                with open(self.fstab_file, "a") as fstab_file:
                    fstab_file.write(patch)
            print("Testing fstab file. WARNING: do not reboot if this errors, Pi will hang.")
            self.do("mount -a")
            self.confirm("press y to continue, x for exit", allow_no=False)


    def setup_code(self):
        print("downloading photobot.py...")
        self.do("wget https://raw.githubusercontent.com/paddiohara/photobot/master/src/photobot.py")

    def setup_directories(self):
        if self.confirm("create directory on pi: /home/pi/captures ?"):
            self.do("mkdir /home/pi/captures")
        if self.confirm("create directory on USB drive: /mnt/usbstorage/captures ?"):
            self.do("mkdir /mnt/usbstorage/captures")


    def take_test_photo(self):
        "take a photo with the camera"
        print("Taking test photo with gphoto2...")
        self.do("gphoto2 --wait-event=1s --set-config eosremoterelease=2 --wait-event=1s "
            "--set-config eosremoterelease=4 --wait-event-and-download=2s "
            "--force-overwrite --get-all-files --delete-all-files "
            "--filename=/home/pi/captures/test_photo.jpg")
        print("Moving test photo to /mnt/usbstorage/captures...")
        self.do("mv /home/pi/captures/test_photo.jpg /mnt/usbstorage/captures/")


    def setup_cron(self):
        patch = "\n* * * * * root python /home/pi/photobot.py"
        if self.confirm("patching %s with patch: '%s'\n?" % (self.cron_file, patch) ):
            if not self.args.dry_run:
                with open(self.cron_file, "a") as cron_file:
                    cron_file.write(patch)
        if self.confirm("reload cron to test? "):
            self.do("restart cron")     


    def setup_witty(self):
        print("downloading witty pi installer")
        self.do("wget http://www.uugear.com/repo/WittyPi/installWittyPi.sh")
        self.do("sh installWittyPi.sh")


    # main install process
    def main(self):
        print("Running photobot installer")

        if not self.confirm("Did you execute this as sudo?"):
            self.exit()

        if self.confirm("setup wifi configuration?"):
            self.setup_wifi()

        if self.confirm("Install packages?"):
            self.install_packages()             

        if self.confirm("Setup USB drive?"):
            self.setup_drive()
  
        if self.confirm("Download photobot.py from github?"):
            self.setup_code()
        
        if self.confirm("Create directories for captures?"):
            self.setup_directories()
        
        if self.confirm("Take test photo? (Attach and power on camera before continuing) "):
            self.take_test_photo()
        
        if self.confirm("Setup cronjob for capture every minute?"):
            self.setup_cron()

        if self.confirm("Download and install Witty Pi software?"):
            self.setup_witty()


        print("\nDONE SETUP\n")


if __name__=="__main__":
  
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action="store_true", help="print commands but don't run them")
    parser.add_argument('--wpa-file', help="alternate networking file to patch")
    parser.add_argument('--fstab-file', help="alternate fstab file to patch")
    parser.add_argument('--cron-file', help="alternate fstab file to patch")
    args = parser.parse_args()

    print("running with args: %s" % args)
    installer = PhotobotInstaller(args) 
    installer.main()