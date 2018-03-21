#!/usr/bin/python

from evdev import InputDevice
from ctypes import *
import exceptions
import json
import subprocess
import os
import sys

MASTER_CFG = os.path.dirname(sys.argv[0]) + "/../confis.json"

class timeval(Structure):
    _fields_ = [("tv_sec", c_long), ("tv_usec", c_long)]
    
    def tdiff (self, sec, usec):
        return abs ( ( (self.tv_sec - sec) * 1000 ) + ( (self.tv_usec - usec) / 1000 ) )
    
class CfgFile(dict):
    def __init__(self):
        try:
            with open(MASTER_CFG) as cfg_file:
                super(CfgFile, self).__init__(json.load(cfg_file))
                  
        except NameError as e:
            print "Error loading config file:" + str(e) + ", aborting." 
            sys.exit(1)
        

def pad_loop (conf):
    
    ellapsed = timeval(tv_sec=0, tv_usec=0)
    path = conf["pad"]["path"]
    button_x = conf["pad"]["keysx"]["mtr_btn"]
    button_d = conf["pad"]["keysd"]["mtr_btn"]
    onhold = conf["parameters"]["LISTENER_HOLD"]
    ontap = ' '.join(conf["parameters"]["LISTENER_TAB"])
    
    for event in InputDevice(path).read_loop():
        
        # Master button
        if event.code == button_x or event.code == button_d:
            if event.value == 0:
                if ellapsed.tv_usec > 0:
                    if ellapsed.tdiff(event.sec, event.usec) < 1200:
                        subprocess.Popen(ontap, shell=True)
                        break
                    else:
                        subprocess.Popen(onhold, shell=False)
            else:
                ellapsed.tv_usec = event.usec
                ellapsed.tv_sec = event.sec
        
glob_conf = CfgFile()
error = True

while error: 
    try:
        pad_loop(glob_conf)
        error = False
        
    except (IOError, OSError):
        pass
