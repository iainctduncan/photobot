#System Overview
This outlines the basic overview of how the 'Photobot' software and hardware works. 

###Repository Structure
This software repository is split into two main folders:
photobot_src - which contains all the code which runs on the Pi
and
monitor - which contains all the software that runs on a remote server that the photobots check in with.

##Photobot Control Script
To make controling the functions of a photobot easy, we have created a simple commandline interface to run the most common commands you will need for building and testing photobots.
Once you have finished [installing the photobot software](installation_manual.md) you should be able to SSH in to your bot and run the command:
`photobot` 
This will list all available options.
For example to take a sample photo and upload it use:
`phototobot sample`
or to update the photobot software to the latest version use:
`photobot update`

## USB Camera Capture
The primary piece in all installations is a high-resolution camera. The CORAL installations use Cannon Rebel T6 and T5 SLR cameras.
A known issue with these cameras is that they have a limited shutter life of about 150,000 photos.

The camera is connected to the Pi via a USB connection. We use the gphoto2 command line interface to libgphoto to communicate with the camera and take photos and save them.
To run a PTZ capture session use the command:
`photobot ptzrun`

To campture a single image and use

### Dealing with Camera Freezing
Unfortunately, at least with the Cannon Rebel cameras they often freeze after anywhere from 10 minutes to a few hours.
Upgrading the version of gphoto to the latest build instead of the older versions which come in the normal Debian repositories improves this but does not fix it.
The installer script automatically installs the latest version of gphoto. 

Currently the only way to revive the camera after it freezes is to power cycle it. A power relay controlled by the Pi
automatically does this. For more information see Power Control Relay below.

## PTZ Network Camera
In addition to the USB cameras we have found network security cameras provide another viable camera option. Their resolution isn't as good, but they don't wear out, and they can be remotely panned, tilted ans zoomed.
Using the ONVIF protocol and the [Python onvif module](https://pypi.org/project/onvif/) we are able to capture images directly from ONVIF compatible cameras.

If using a network camera, you should configure the master router that the installation is connected to, to give a fixed local IP address to the camera.
When possible you should also port forward a port (we use port 88) from the external internet to the camera. This will allow you to access it to adjust pan tilt and zoom.

To run a PTZ capture session use the command:
`photobot ptzrun`

## Thermal Camera
We have successfully captured thermal images using a Flir A65 thermal camera. The installer script installs and compiles a custom C program for capturing thermal images.
Thermal captures happen at regular intervals defined in the configuration file and are saved to the standard captures dir. Sample thermal captures are uploaded to the monitor panel aswell.



## AIS Receiver
The AIS receiver module reads data from a USB connected AIS receiver using [gpsd](https://en.wikipedia.org/wiki/Gpsd) and stores the data to a sqllite database at: /mnt/usbstorage/ais/ais_receiver.db
A set of coordinates in the configuration file determine if the information is logged or not, allowing you to ignore distant signals.
To test AIS functionality, and see the raw data it is receiving run:
`photobot ais`

##Power Control Relay
To deal with the need to power cycle frozen cameras we use a power control relay that allows the software to turn the camera off and on again.
We use [this relay](https://www.amazon.ca/Iot-Relay-Enclosed-High-power-Raspberry/dp/B00WV7GMA2/ref=sr_1_fkmr1_1?keywords=pi+power+control+relay+power+bar&qid=1561664063&s=gateway&sr=8-1-fkmr1) connected with [wires like this](https://www.amazon.ca/Premium-Breadboard-Jumper-100-Pack-Hellotronics/dp/B07H7YMGS4/ref=sr_1_5?crid=1K8GXJCS2N8JI&keywords=jumper+wire&qid=1561664227&s=industrial&sprefix=jumper+%2Cindustrial%2C201&sr=1-5)
Note, that you may want to use longer wires depending on where you can place the Pi and the relay in your case. 

Two control wires run from GPIO pins on the Pi to the relay, and when the pi sends a control signal it toggles the relay state. 
Plug the power supply for the camera into the "normally on" plug on the relay. You can use the "always on" plug to power the rest of the components.

Currently the system expects the control wires to be connected as follows:
Pin 21 connects to the + terminal on the relay and the negative terminal on the relay connects to a ground pin, on the Pi. We found the ground directly below pin 21 was the most practical. 
Here is an image showing the layout of the GPIO pins on the pi:
![GPIO Pin Guide](img/gpio-numbers-pi2.png)

We found that connecting the pin from the male end of the control wire to the relay's control port was less reliable than removing the pin, stripping the wire and inserting the bare end of the wire directly.

To test if your replay is working, plug a lamp, or other electrical device into the "normally off" plug on the relay, ssh into the Pi and run the commannd:
`photobot powercycle`
This should cause the device to turn on for 5 seconds and then turn off.

#Configuration
All configuration values are stored in an ini file at /var/photobot/config/photobot.ini -  There is an interactive configuration script available to write data into that file.
ssh into the pi and run:
`photobot configure`

Note that currently the configuration script does not read the saved values so you are starting fresh each time. 
If we continue to use the configuration script it would be nice to rewrite it to read values from the file. 
Or in the future the settings could be controlled via the monitoring panel too.

You can also manually edit the ini file, but note that your changes will get overwritten if someone runs the config script.
The easiest workflow is probably to run the configuration script during initial configuration and then edit it. 

The settings from the file are always accessed via the get_settings_dict() function. That function contains logic to apply default values if they don't exist in the config file, and logic to override settings based on command line flags.
Currently there are a few settings that are only set here because we haven't had need to customize them yet.

# Scheduling

Currently there are 3 ways that processes are scheduled. In the future they will likely be consolidated to eliminate the crontab version.
## Crontab Execution (legacy)
The USB and PTZ capture processes are called via Root's crontab. They run every minute. 

## Long-running process via Supervisord
The AIS module is designed to run continuously, so it is handled via the supervisord utility, which ensures the process is always running.
The conf file at photobot_src/supervisord_conf/ais_receiver.conf is symlinked from /etc/supervisor/conf.d directory by the installer script, which adds it to supervisor's list of processes to maintain.
to check the status of supervisor processes run:
`supervisorctl`
This will show you the status of the processes.

## Built In Scheduler Process
The built in scheduler process is a long running python script, which is also run by supervisor. The process name in supervisor is photobot_scheduler and it is configured in the same file as the AIS process above.
In the future it may be clearer to move this configuration to its own file.
The scheduler script is simply a timer that runs events every X seconds based on values in the configuration script.
Currently the scheduler handles: overall system status pings, sample photo uploads, thermal captures and disk health + space checks.
In the future it would probably make sense to move the USB and PTZ photo captures to be controlled by this script too, because it would allow those processes to run on a custom interval defined in the configuration file, instead of just once per minute as defined in crontab. 

## Day / Night detection
The photobot software is designed to automatically calculate the sunrise and sunset, using code we [found here](https://michelanders.blogspot.com/2010/12/calulating-sunrise-and-sunset-in-python.html). The USB camera and PTZ camera processes automatically abort if they detect it is dark out. 
If you need to know if it is dark out in future code, you can always use the simple is_dark() function which checks if we are between sunrise and sunset.
