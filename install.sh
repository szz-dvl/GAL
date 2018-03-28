#!/bin/bash

pwd=`pwd`

sed -i "s|\[PWD\]|$pwd|gi" launch.sh
sed "s|\[PWD\]|$pwd|gi" services/pad-listener.service | sudo tee /lib/systemd/system/pad-listener.service > /dev/null
sed "s|\[PWD\]|$pwd|gi" services/gal.service | sudo tee /lib/systemd/system/gal.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable pad-listener

sudo apt-get install -y python python-pip psmisc python-wxgtk3.0 alsa libasound2-dev
sudo pip install evdev python-xlib pyalsaaudio psutil pyjon.events

sudo systemctl start pad-listener
