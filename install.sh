#!/bin/bash

pwd=`pwd`

sed -i "s|\[PWD\]|$pwd|gi" launch.sh
sed "s|\[PWD\]|$pwd|gi" services/pad-listener.service 1&>2 | sudo tee /lib/systemd/system/pad-listener.service
sed "s|\[PWD\]|$pwd|gi" services/gal.service 1&>2 | sudo tee /lib/systemd/system/gal.service
