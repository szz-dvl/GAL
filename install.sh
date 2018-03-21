#!/bin/bash

pwd=`pwd`

sed "s|\[PWD\]|$pwd|gi" launch.sh
sed "s|\[PWD\]|$pwd|gi" services/pad-listener.service
sed "s|\[PWD\]|$pwd|gi" services/gal.service
