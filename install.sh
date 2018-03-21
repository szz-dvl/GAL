#!/bin/bash

pwd=`pwd`

sed "s|\[PWD\]|$pwd|gi" launch.sh > ./launch.sh
sed "s|\[PWD\]|$pwd|gi" services/pad-listener.service | sudo tee /lib/systemd/system/pad-listener.service
sed "s|\[PWD\]|$pwd|gi" services/gal.service | sudo tee /lib/systemd/system/gal.service
