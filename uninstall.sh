#!/bin/bash

sudo rm -f /lib/systemd/system/gal.service
sudo rm -f /lib/systemd/system/pad-listener.service

sudo systemctl daemon-reload
