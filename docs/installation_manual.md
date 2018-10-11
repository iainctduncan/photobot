#  Setting up the Raspberry Pi 3 for photo capture

## Requirements:
This document details how to get the Pi 3 working for photo capture.

You will need:
 * A computer running OSX, Windows, or Linux (the host)
 * A raspberry Pi 3
 * An SD card and reader, we will load the SD card from the host and put it in the Pi
 * An ethernet cable and connection for the Pi
 * Internet connection for your host and Pi, we assume you have wireless.
 * A Lorex IP camera

We have only tested these instructions on OSX. They should work (almost) identically on Linux.
It's definitely possible on Windows but the commands and tools are likely different. 

In our instructions:
 * "on your host" means commands exected on your computer (OSX, or Linux)
 * "on the pi":  menas commands exectued on the Pi at a command line prompt that we get to via SSH 

Lines in this document starting with '$' are commands typed at a terminal,
either on the host or the Pi. You don't need to type the '$', that's your prompt.

## Overview of Steps:
1) Setup up Raspberry Pi with Raspbian Jessie 
2) Get wifi working on Pi
3) Download and run the installer script
4) Configure and test


We're going to install the Pi's operating system on an SD card, tweak it a bit,
put it in the Pi, boot up, and SSH into the Pi.

## Download Raspbian Jessie Lite
- on your host computer, download the Raspbian linux OS for the pi: https://www.raspberrypi.org/downloads/raspbian/
- the latest at time of writing is: Rasbian Stretch Lite, June 2018
- we are using Stretch Lite as we will not be plugging a keyboard and monitor into the Pi, 
  we're going to do everything over SSH. ("Stretch" is just the release nickname)

## Burn image on the SD card:
How you do this depends on your operating system. You may be able to do this with a 
graphical tool on your operating system, or you can follow the manual instructions below.
If you know how to burn the image, skip the next step and resume from "Enable SSH"
### OSX image burning instructions.
- put the SD card in your card reader and plug it into the USB port on your host (or 
  directly into your host if you have an SD card reader built in).
- find out the disk number of SD card by opening a terminal and executing:
  
  `$ diskutil list`
- look for the entry that matches the size of your card (so we know it's not your host hard drive)
- for this example, on our machine it was: **/dev/disk2**
- unmount that disk:
 
  `$ diskutil unmountDisk /dev/disk2`
- copy or move the image you downloaded to the current directory, and execute
  the following to copy that image onto your sd card
  
  `$ sudo dd bs=1m if=2017-01-11-raspbian-jessie-lite.img of=/dev/rdisk2`
- note that in the above command, you must replace the name of the image file with your image
  and **/dev/rdisk2** with **/dev/rdisk{X}** where X is your disk number. 
  Note that it is **/dev/rdiskX**, not **/dev/diskX** in this command
### Linux image burning instructions
- Right click on the downloaded raspian image file, and select "open with image writer"
- Select the SD card as the destination, and confirm.
## Enable SSH: Alter the image to enable 
After we have created a Raspbian image, we will alter it to enable networking.
Raspbian, for security reasons, disables SSH by default, so we won't be able to 
log into our Pi unless we enable it.
- Take out your SD card and put it back in. Your OS should automount the drives,
  with the boot sector of our burned image automounting on the host as "Boot".
- We need to put an empty file called 'ssh' in to the boot directory. (The Pi checks to
  see if this empty file was deliberately added before enabling SSH to prevent bot-net-of-things activity)
- In a terminal in your host, cd into the boot directory and execute:
  
  `$ sudo touch ssh`
- Check that it worked:

  `$ ls` 
- You should see the file called 'ssh' in there

## Load into Pi
- Unmount your SD reader, take out the SD card, and put the card into the pi. It slides
  into the metal holder on the underside of the pi, on the opposite end of the USB plugs.
- Plug the Pi into your network with an ethernet cable. We need to use a cable because 
  it doesn't know how to find wireless until we configure wifi.
- Boot the Pi. This happens as soon as you plug in the power.
- On your host, find the ip address of the pi using a portscanning application or through
  your router. On OSX, we used the free application "ipscan" (free download)
- Once we know the IP address, we can ssh in to the pi from the host using the 
  username 'pi' and password 'raspberry'. (Replacing the IP below with the one you found).
  
  `$ ssh pi@192.168.1.68`
- You are now on the PI!

## Setup the Pi (from the Pi)
Now we're going to continue setting up the Pi from the Linux prompt ON the Pi.

### Update System and Install Tools
- update the Debian repository info
  
  `$ sudo apt-get update`
- you might want to install some text editors (optional). If you do, you know what you want. ;-)

  `$ sudo apt-get install vim nano`

### Setup up Wifi
- we have two options: 
   - A) log into PI over ethernet cable and ssh and set it up, what we'll do here
   - B) mount the image file on some host that can read ext3 and edit the filesystem directly
      - this is easy if you have a host system that runs linux, and otherwise it's a pain

### A) setup ON the pi (these commands are executed on the pi, over ssh) ###
- scan for networks to find out the name of your wifi network
  
  `$ sudo iwlist wlan0 scan`
- look for your network, and copy the ESSID ie the same one you use for normal wireless at home
  (at my house it's called "TELUS0001", we're going to pretend my password is "Hunter2")
- we need to edit the wireless config file, using the editor of your choice. I use vim,
  you prob want to use nano if you don't know any linux editors. 
    
  `$ sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`
  
- add in an entry at the bottom of the file for your wifi, with thefollowing format and save the file:

    ```
    network={
      ssid="TELUS0001"
      psk="hunter2"
    }
    ```

- restart networking
  ```
  $sudo ip link set wlan0 down
  $sudo ip link set wlan0 up
  ```

- if you look on your host ip scanner again, the pi should now appear with a second IP address
- test this out by unplugging the ethernet cable, rebooting the pi, and SSH'in with the 
  new (wireless) network IP. 


###B) Setting up by directly accessing the drive
  - on OSX, you can install extfs drivers from https://www.paragon-software.com/home/extfs-mac
    or:
  - start up a linux install. We used VirtualBox and Ubuntu, which are free. We needed to install
  the VirtualBox guest addons and extensions to be able to read the USB drive.
  - put your SD card for the Pi in the reader, mount it from your linux or osx install
  - you should see two drives on there, Boot and the main drive
  - in the main drive, open /etc/wpa_supplicant/wpa_supplicant.conf and add the networking
    entry as detailed above


Install Photobot software on the Pi
------------------------------------------
- From the Pi, download the photobot installer script:
```
$ cd~
$ wget --no-check-certificate --content-disposition https://raw.githubusercontent.com/paddiohara/photobot/master/photobot_installer.py

```
- Run the installation script:
`$ sudo python photobot_installer.py`
### Installation Script Overview
- You should be able to answer yes to all of these questions the first time, except for if they arequestions related to gphoto and you using a lorex ip camera, you don't need to test GPhoto.
- If something goes wrong, you can re-run the script. Just be mindful that any step you have already completed, you should say no to the second time.

## Setting up the Lorex Camera
- Plug the camera into your network, using either a standard ac/dc power adapter, or a power over ethernet adaptor to provide power.
- Edit the lorex config file:
`$ nano /home/pi/photobot/src/photobot_lorex.ini`
- in the config file, ensure:
--'capture_dir' is set to where you want the photos to be stored (should be /mnt/usbstorage/captures)
-- 'lorex_host' is set to the ip on the network where your lorex is. You can find this IP with your port scanner or router. My Lorex had a host name of "ND031711008793" so yours will probably be something similar.
-- 'ensure the 'lorex_user' and 'lorex_password' fields are set correctly. The default is user:admin password:admin


## Testing Photobot
Photobot should be set to run automatically on a cron job already.
To test, you can run it in the foreground with:
`$ /home/pi/photobot/env2/bin/python /home/pi/photobot/src/photobot_lorex.py --settings /home/pi/photobot/src/photobot_lorex.ini`

If everything is working correctly, your capture dir should be filling up with images. You can check with:
`$ ls /mnt/usbstorage/captures`

ALL DONE!

Appendix
-------------------
### CLONING THE PI:
- article:
  https://thepihut.com/blogs/raspberry-pi-tutorials/17789160-backing-up-and-restoring-your-raspberry-pis-sd-card
  http://michaelcrump.net/the-magical-command-to-get-sdcard-formatted-for-fat32/

- to copy an image from the SD card to computer:
  - find out disk number using:
     $ diskutil list
  - unmount disk:
     $ diskutil unmountDisk /dev/disk2
  - copy image
     $ sudo dd if=/dev/disk2 of=~/SDCardBackup.dmg

- to copy image to an SD card:
  - unmount SD disk, find out disk number using diskutil as above:
  - format disk to FAT32 and name it 
    sudo diskutil eraseDisk FAT32 NAME_RASPBIAN MBRFormat /dev/disk2
  - copy the image over, warning this can take a very long time (hours)
    sudo dd if=raspbian_photobot_2017-03-06.dmg of=/dev/disk2

