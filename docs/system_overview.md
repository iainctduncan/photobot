#System Overview
This outlines the basic overview of how the 'Photobot' software works. 

This document focuses on the software over hardware.
## USB Camera Capture
The primary piece in all installations is a high-resolution camera. The CORAL installations use Cannon Rebel T6 and T5 SLR cameras.
A known issue with these cameras is that they have a limited shutter life of about 150,000 photos.

The camera is connected to the Pi via a USB connection. We use the gphoto2 command line interface to libgphoto to communicate with the camera and take photos and save them.

### Dealing with Camera Freezing
Unfortunately, at least with the Cannon Rebel cameras they often freeze after anywhere from 10 minutes to a few hours.
Upgrading the version of gphoto to the latest build instead of the older versions which come in the normal Debian repositories improves this but does not fix it.
The installer script automatically installs the latest version of gphoto. 

Currently the only way to revive the camera after it freezes is to power cycle it. A power relay controlled by the Pi
automatically does this. For more information see the Hardware manual.

## PTZ Network Camera

## Thermal Camera

## AIS Receiver


#Configuration
All configuration values are stored in an ini file at /var/photobot/config/photobot.ini -  There is an interactive configuration script available to write data into that file.
ssh into the pi and run:
`photobot configure`

Note that currently the configuration script doesn't read the saved values so you are starting fresh each time. 
If we continue to use the configuration script it would be nice to rewrite it to read values from the file. 
Or in the future the settings could be controlled via the monitoring panel too.

You can also manually edit the ini file, but note that your changes will get overwritten if someone runs the config script.
The easiest workflow is probably to run the configuration script during initial configuration and then edit it. 

The settings from the file are always accessed via the get_settings_dict() function. That function contains logic to apply default values if they don't exist in the config file, and logic to override settings based on command line flags.
# Scheduling

Currently there are 3 ways that processes are scheduled. In the future they will likely be consolidated to eliminate the crontab version.
## Crontab Execution (legacy)
The USB and PTZ capture processes are called via Root's crontab. They run every minute. 

## Long-running process via Supervisord
The AIS 
## Built In Scheduler Process


