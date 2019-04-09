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

class PhotobotInstaller(InstallHelper):

    def __init__(self, args):
        self.args = args
        self.wpa_file = args.wpa_file or "/etc/wpa_supplicant/wpa_supplicant.conf"
        self.cron_file = "/etc/crontab"

        self.defaults = {
            "install_path" : "/home/pi/photobot"
        }

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
        print("running apt-get update, installing nano, vim, git, gphoto2, gpsd, virtualenv, supervisor ...")
        self.do("apt-get update")
        self.do("apt-get install -y nano vim git")

        print("######################")
        print("Installing Latest Gphoto Software")
        print("Select Install latest stable version (option 2)")
        print("######################")
        self.do("wget https://raw.githubusercontent.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh && chmod +x gphoto2-updater.sh && sudo ./gphoto2-updater.sh")
        #self.do("apt-get install gphoto2")
        self.do("apt-get install -y imagemagick")
        self.do("apt-get install -y gpsd")
        self.do("apt-get install -y python-virtualenv")
        self.do("apt-get install -y supervisor")
        self.do("apt-get install -y sqlite3")
        self.do("apt-get install -y ntfs-3g")
        self.do("apt-get install -y tcpdump")
        self.do("apt-get install -y nmap")
        self.do("apt-get install -y python-dev")

        #if self.confirm("test gphoto2 to see camera? (plug in camera)"):
        #    self.do("gphoto2 --list-config")
        #    self.confirm("camera found, continue?", allow_no=False)


    # TODO: fix this sucker
    def setup_drive(self):
        print("setting up external USB drive")
        if self.confirm("create dir /mnt/usbstorage"):
            self.do("mkdir /mnt/usbstorage")
        self.confirm("plug in USB drive and continue", allow_no=False)
        print("checking drive ID with lsblk, look for sdaX where X is the drive number and the size matches")
        self.do("lsblk")
        while True:
            drive_input = raw_input("Enter drive number: ")
            if not drive_input.isdigit():
                print ("\n OOPS! Please enter just a number, with no other characters. \n restarting drive setup.\n")
                return self.setup_drive()
            dev_num = int( drive_input )
            if self.confirm("Drive number is '%i' " % dev_num):
                break
        print("mounting /dev/sda%i" % dev_num)
        self.do("mount /dev/sda%i /mnt/usbstorage" % dev_num)
        self.do("chmod 755 /mnt/usbstorage")        
        # no longer mounting with fstab, doing it in the init_script
        #if self.confirm("edit fstab file to automount drive as ext3?"):
        #    patch = "/dev/sda%i /mnt/usbstorage /ext3 defaults 0 0"
        #    # patch the fstab file and test
        #    if not self.args.dry_run:
        #        with open(self.fstab_file, "a") as fstab_file:
        #            fstab_file.write(patch)
        #    print("Testing fstab file. WARNING: do not reboot if this errors, Pi will hang.")
        #    self.do("mount -a")
        #    self.confirm("press y to continue, x for exit", allow_no=False)

    def setup_symlinks(self):
        default_path = self.defaults['install_path']
        install_path= raw_input("installation directory ["+default_path+"]: ")

        if install_path == '':
            install_path=default_path

        print ("Installing to" + default_path)

        print("To make things easy and portable we will set up symbolic links in your filesystem.")
        self.mkdir(install_path)
        self.mkdir(install_path + "/logs")
        self.do("ln -s " + install_path + " /var/photobot")


        #cwd = os.path.dirname(os.path.abspath(__file__))
        #print("/var/photobot_src  will contain the source it will point to:" + cwd)

    def setup_code(self):
        print("cloning photobot repository into /var/photobot/repo")
        self.do("git clone https://github.com/iainctduncan/photobot.git /var/photobot/repo")
        self.do("ln -s /var/photobot/repo/photobot_src /var/photobot/src")

    def setup_directories(self):
        #if self.confirm("create directory on pi: /var/photobot/captures ?"):
         #   self.mkdir("/var/photobot/captures")
        if self.confirm("create directory on USB drive: /mnt/usbstorage/captures ?"):
            self.mkdir("/mnt/usbstorage/captures")
        #if self.confirm("create directory on pi: /var/photobot/lorex ?"):
        #    self.mkdir("/var/photobot/lorex")
        #if self.confirm("create directory on USB drive: /mnt/usbstorage/lorex ?"):
            #self.mkdir("/mnt/usbstorage/lorex")


    def take_test_photo(self):
        "take a photo with the camera"
        print("Taking test photo with gphoto2...")
        self.do("gphoto2 --wait-event=1s --set-config eosremoterelease=2 --wait-event=1s "
            "--set-config eosremoterelease=4 --wait-event-and-download=2s "
            "--force-overwrite --get-all-files --delete-all-files "
            "--filename=/var/photobot/test_photo.jpg")
        print("Moving test photo to /mnt/usbstorage/captures...")
        self.do("mv /var/photobot/test_photo.jpg /mnt/usbstorage/captures/")


    def setup_cron(self):
        lorex_comment="\n"
        gphoto_comment="\n"

        if not self.enable_lorex:
            lorex_comment="\n# uncomment to enable PTZ network camera \n#"
        if not self.enable_gphoto:
            gphoto_comment = "\n# uncomment to enable USB (GPHOTO) camera \n#"
        patch = (
            "\n@reboot root /var/photobot/env2/bin/python /var/photobot/src/photobot_reboot.py --settings /var/photobot/config/photobot.ini "

            "" +gphoto_comment+"* * * * * root /var/photobot/env2/bin/python /var/photobot/src/photobot.py --settings /var/photobot/config/photobot.ini"

            "" +lorex_comment+"* * * * * root /var/photobot/env2/bin/python /var/photobot/src/photobot_lorex.py --settings /var/photobot/config/photobot.ini\n\n")
        if self.confirm("patching %s with patch: '%s'\n?" % (self.cron_file, patch) ):
            if not self.args.dry_run:
                with open(self.cron_file, "a") as cron_file:
                    cron_file.write(patch)
        if self.confirm("reload cron to test? "):
            self.do("sudo service cron reload")

    def setup_supervisor(self):
        print("Creating symlink at /etc/supervisord/conf.d/ais_receiver.conf")
        self.do("ln -s /var/photobot/src/supervisord_conf/ais_receiver.conf /etc/supervisor/conf.d/ais_receiver.conf")
        self.do("supervisorctl reread")
        self.do("supervisorctl update")

    def setup_python_envs(self):
        print("Creating python 2 and 3 virtualenvs, and installing dependencies")
        self.do("virtualenv -p python2 /var/photobot/env2")
        self.do("/var/photobot/env2/bin/pip install -r /var/photobot/src/requirements2.txt")
        self.do("virtualenv -p python3 /var/photobot/env3")
        self.do("sudo /var/photobot/env3/bin/pip install -r /var/photobot/src/requirements3.txt")

    def run_configuration_script(self):
        self.do("sudo python /var/photobot/src/scripts/photobot_config.py")

    def setup_thermal(self):
        self.do("apt-get update")
        self.do("apt-get install -y libglib2.0-dev glib-2.0 libxml2-dev ")
        self.do("sudo apt-get upgrade -y intltool")
        self.do("cp -dpr /var/photobot/repo/3rd_party/aravis-0.4.0 /usr/local/src")
        os.chdir("/usr/local/src/aravis-0.4.0")
        self.do("sudo ./configure")
        self.do("sudo make")
        self.do("sudo make install")
        self.do("sudo ldconfig")
        self.do("sudo timedatectl set-timezone UTC")
        os.chdir("/var/photobot/repo/3rd_party/flircap")
        self.do("sudo make")
        self.do("sudo cp FLIRA65-Capture /usr/local/bin")


    def setup_ais(self):
        print("Setting up ais directory and initializing database")
        self.mkdir("/mnt/usbstorage/ais")
        self.do("/var/photobot/env3/bin/python /var/photobot/src/ais_receiver.py "
                "--init-db --settings /var/photobot/config/photobot.ini")
        print("disabling auto start of gpsd")
        self.do("systemctl stop gpsd.socket")
        self.do("systemctl disable gpsd.socket")

    def chown_files(self):
        print("Setting ownership for all photobot files and /mnt/usbstorage to pi:pi")
        self.do("chown -R pi:pi /var/photobot")
        self.do("chown -R pi:pi /mnt/usbstorage")

    def setup_lanscan_script(self):
        print("setting up lanscan script helper. to use type 'lanscan scan'")
        self.do("cp /var/photobot/src/scripts/lanscan /usr/local/bin")
        self.do("chmod +x /usr/local/bin/lanscan")
    def setup_photo_sample_uploads(self):
        print("This will set up SSH-keys to allow connection to the samples account on the monitor sever. You will need to type the password once now to authorize future connections.")
        self.do("apt-get install imagemagick")
        self.do("sudo -H -u root bash -c 'ssh-keygen'")
        self.do("sudo -H -u root bash -c 'ssh-copy-id samples@photobots.info'")
    # main install process
    def main(self):
        print("Running photobot installer")

        if not self.confirm("Did you execute this as sudo?"):
            self.exit()

        if self.confirm("Set up symlinks and master directory structure?"):
            self.setup_symlinks()
            # we switched to configuring networking pre installation
        #if self.confirm("setup wifi configuration?"):
        #    self.setup_wifi()

        if self.confirm("Install packages?"):
            self.install_packages()             

        if self.confirm("Setup USB drive?"):
            self.setup_drive()
  
        if self.confirm("Clone photobot repository?"):
            self.setup_code()

        if self.confirm("Create python environments?"):
            self.setup_python_envs()

        if self.confirm("Install Lanscan Script?"):
            self.setup_lanscan_script()

        if self.confirm("Create directories for captures?"):
            self.setup_directories()

        self.enable_lorex = False
        if self.confirm("Do you want to enable a PTZ Network camera"):
            self.enable_lorex = True

        self.enable_gphoto = False
        if self.confirm("Do you want to enable and test a USB (Canon) camera"):
            self.enable_gphoto = True

        if(self.enable_gphoto):
            if self.confirm("Take test photo? (Attach and power on camera before continuing) "):
                self.take_test_photo()
        
        if self.confirm("Setup cronjobs for reboot and capture every minute?"):
            self.setup_cron()

        if self.confirm("Create symlink for ais_receiver supervisord conf file?"):
            self.setup_supervisor()

        if self.confirm("Run configuration script"):
            self.run_configuration_script();

        if self.confirm("Set up photo sample uploads? (Requires password to samples upload account)"):
            self.setup_photo_sample_uploads();

        if self.confirm("Create ais directory, initialize ais db, and prepare gpsd?"):
            self.setup_ais()

        if self.confirm("Set up a Thermal Camera (FLIR A65)"):
            self.setup_thermal()

        if self.confirm("Set ownership of touched files to user pi?"):
            self.chown_files()



        print("\nSetup Complete. You will need to run the configruation script\n")
        print("To set/adjust configuration Run:")
        print("sudo python /var/photobot/src/scripts/photobot_config.py")


if __name__=="__main__":
  
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action="store_true", help="print commands but don't run them")
    parser.add_argument('--wpa-file', help="alternate networking file to patch")
    args = parser.parse_args()

    installer = PhotobotInstaller(args)
    installer.main()
