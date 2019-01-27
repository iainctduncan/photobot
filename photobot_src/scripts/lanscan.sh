#!/usr/bin/env bash
sudo su root
source /var/photobot/env3/bin/activate
lanscan scan
echo "Look for the device with the following open ports: 80, 554, 5000, 49152 - that one will be the lorex "
