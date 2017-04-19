#!/usr/bin/python

from evdev import InputDevice
import exceptions
import json
import sys
import wx.lib.newevent as NE
import wx
import time
from Xlib.display import Display
import os

UpdateEvent, EVT_UPDT = NE.NewEvent()
EndSessionEvent, EVT_ENDSES = NE.NewEvent()

MASTER_CFG = os.path.dirname(sys.argv[0]) + "/confis.json"

class GamePad():
    def __init__(self, path, keysx, keysd):
        self.path = path
        self.keysx = keysx
        self.keysd = keysd
        
    def get_device(self):
        return InputDevice(self.path)

class CfgMgr(dict):

    def __init__(self):
        
        try:

            with open(MASTER_CFG) as cfg_file:
                super(CfgMgr, self).__init__(json.load(cfg_file))
                self.GamePad = GamePad(self.__getitem__("pad")["path"], self.__getitem__("pad")["keysx"], self.__getitem__("pad")["keysd"])
                
        except NameError as e:
            print "Error loading config file:" + str(e) + ", aborting." 
            sys.exit(1)
            
master_cfg = CfgMgr()
master_dpy = Display()
steam_running = False
PARAMETERS = master_cfg["parameters"]
info = None

class InfoPanel(wx.Frame):
    
    def __init__(self, w=PARAMETERS["INFOWIDTH"], h=PARAMETERS["INFOHEIGHT"], t="Benvingut!", pos=wx.Point(0, 10), urgency=0):
        
      super(InfoPanel, self).__init__(None, style=wx.NO_BORDER|wx.CAPTION|wx.STAY_ON_TOP, size=(w,h), pos=pos)

      self.panel = wx.Panel(self, -1)
      self.panel.SetBackgroundColour(wx.Colour(0, 0, 0))

      self.txt = wx.StaticText(self.panel, -1, t, size=(w, 0), pos=(0, 0))
      
      self.txt.SetForegroundColour(wx.Colour(255, 255, 255))
      
      self.font = wx.Font(22, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD, underline=False, faceName="", encoding=wx.FONTENCODING_DEFAULT)
      self.txt.SetFont(self.font)

      self.amount = 255
      self.delta = 5

      self.hidding = False

      self.Bind(EVT_UPDT, self.set_msg)
      self.tstamp = time.time()
      
      tid = wx.NewId()
      self.timer = wx.Timer(self, tid)
      self.Bind(wx.EVT_TIMER, self.CheckFadeOut, id=tid)
      self.timer.Start(500)

      tid = wx.NewId()
      self.degradat = wx.Timer(self, tid)
      self.Bind(wx.EVT_TIMER, self.FadeOut, id=tid)

    def reset (self):
        self.amount = 255
        self.SetTransparent(self.amount)
        self.panel.SetBackgroundColour(wx.Colour(0, 0, 0))
        
    def set_msg(self, ev):
      
      self.tstamp = time.time()

      if self.hidding:
        self.degradat.Stop()
        time.sleep(0.1)
        self.hidding = False
        self.reset()
          
      if ev.urgency == 1:
          self.panel.SetBackgroundColour(wx.Colour(0, 15, 235))
      elif ev.urgency == 2:
          self.panel.SetBackgroundColour(wx.Colour(234, 211, 64))
      elif ev.urgency == 3:
          self.panel.SetBackgroundColour(wx.Colour(205, 0, 75))
          
      self.txt.SetLabel(ev.msg)                
      self.Update()
        
      if not self.IsShown():
        self.Show()
        
      if not self.IsShownOnScreen():
        self.Raise()

    def CheckFadeOut (self, ev):

      if time.time() - self.tstamp >= 3 and self.IsShown():
        self.hidding = True
        self.degradat.Start(60)      
        
    def FadeOut(self, ev):

      self.amount -= self.delta
      if self.amount <= 0:
        
        self.degradat.Stop()
        self.Hide()
        self.reset()
        self.hidding = False
        
      else:
        self.SetTransparent(self.amount)
        

def create_panel ():
    global info
    
    info = InfoPanel()

def update_info(data, level=0):
    global info
    
    wx.PostEvent(info, UpdateEvent(msg=data, urgency=level))

__all__ = ['CfgMgr', 'GamePad']
