#!/usr/bin/python

#Speciall thanks: https://github.com/SavinaRoja/PyUserInput/blob/master/pykeyboard/x11.py

import os
import wx
import wx.lib.newevent as NE
from collections import OrderedDict
import threading
import time

import init
from emulator import Gen_Emulator
from plugins import *

CONFIS = init.master_cfg
PARAMETERS = CONFIS["parameters"]

StartSessionEvent, EVT_START = NE.NewEvent()
LKBindingEvent, EVT_LKRESTART = NE.NewEvent()

app = wx.App()
init.master_cfg["parameters"]["SCREEN_X"], init.master_cfg["parameters"]["SCREEN_Y"] = wx.DisplaySize()
init.create_panel()

frame = wx.Frame(None, -1, 'gal.py')
frame.SetSize(wx.Size(PARAMETERS["APPWIDTH"],PARAMETERS["APPHEIGHT"]))
frame.SetTitle('Game Abstraction Layer')
frame.CenterOnScreen()
frame.Show()
frame.Raise()

# def dump(obj):
#   for attr in dir(obj):
#     print "obj.%s = %s" % (attr, getattr(obj, attr))
    
class GameItem:

    def __init__(self, fname, extra=None, instance=None):

        self.file = fname
        self.extra = extra
        self.instance = instance
        
        
class GameList(wx.ListCtrl):

    def __init__(self, panel=None, info=None, w=PARAMETERS["APPWIDTH"], h=PARAMETERS["APPHEIGHT"]):
        
        if (panel is None) or (info is None):
            return None
        
        super(GameList, self).__init__(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL, size=(w, h))
        
        self.lid = info["lid"]
        self.InsertColumn(0, info["title"], width=w) #How to center title?
        self.emulator = info["emu"] if "emu" in info.keys() else None
        self.source = info["source"] if "source" in info.keys() else None
        self.clazz = info["class"] if "class" in info.keys() else None
        
        self.items = []
        self.maxitem = 0
        
        self.font = wx.Font(pointSize=18, family=wx.SWISS, style=wx.NORMAL, weight=wx.FONTWEIGHT_BOLD, underline=False, face="", encoding=wx.FONTENCODING_DEFAULT)
        self.SetFont(self.font)

        if self.source:
            
            for file in os.listdir(self.source):
                if (file.endswith(info["ext"])):
                    
                    item = GameItem(file)
                    extra = info["extra"] if "extra" in info.keys() else None
                    
                    if extra is not None:
                        for key in extra.keys():
                            if key in file:
                                item.extra = extra[key]
                                    
                    self.insert_item(item)  
                    self.maxitem += 1
                    
        elif info["extra"]:
            
            for key_item in info["extra"].keys():
                
                self.insert_item(GameItem(key_item, instance=info["extra"][key_item]))                          
                self.maxitem += 1

        else:
            print "WARNING: Empty List!"
            print (info)
        
        self.Hide()
        
    def get_item(self, idx):
        return self.items[idx]
            
    def insert_item(self, item):
            
        self.items.append(item)
        self.InsertStringItem(self.maxitem, item.file)
            
    
class PagedListMgr(wx.Panel):
     
    def __init__(self, frame=None, lists=[], gamepad=None):

        if frame is None or lists == []: #gamepad too?
            return None
        
        super (PagedListMgr, self).__init__(frame, id=wx.ID_ANY, size=(PARAMETERS["APPWIDTH"], PARAMETERS["APPHEIGHT"]))
        
        self.frame = frame
        self.active = None
        self.session = None
        self.gamepad = gamepad 
            
        self.lists = OrderedDict()
        
        for list in lists:
            self.add_list(list)
            
        self.Bind(init.EVT_ENDSES, self.restart)
        self.Bind(EVT_START, self.start_session)
        self.Bind(EVT_LKRESTART, self.restart)
        
        self.set_active(next(iter(self.lists.keys())))
        
        if self.gamepad is not None:
            threading.Thread(target=self.list_keybinding).start()

    def add_list (self, info):
        
        self.lists[info["lid"]] = GameList(panel=self, info=info)
        return info["lid"]

    def set_active (self, lid):

        if self.active is not None:
            self.lists[self.active].Hide()
        
            while self.lists[self.active].IsShownOnScreen():
                continue
        
        new = self.lists[lid]
        new.Show()
      
        while not new.IsShownOnScreen():
          continue
          
        self.active = lid
        
        return new
    
    def get_active(self):
        return self.lists[self.active]

    def restart (self, ev):
        
        if self.session and not hasattr(ev, 'error'):
            self.session = None

        if self.gamepad is not None:
            threading.Thread(target=self.list_keybinding).start()
        
    def get_prev(self):
        prev, _, _ = self.lists._OrderedDict__map[self.active]

        if prev[2] is None:
            return next(reversed(self.lists.keys()))
        else:
            return prev[2]
        
    def get_next(self):
        _, nxt, _ = self.lists._OrderedDict__map[self.active]

        if nxt[2] is None:
            return next(iter(self.lists.keys()))
        else:
            return nxt[2]
        
    def next_activate (self):
        return self.set_active(self.get_next())

    def prev_activate (self):
        return self.set_active(self.get_prev())
        
    def start_session(self, ev):

      lst = self.get_active()
      item = ev.item

      # If we got item.extra we will have a lst.emulator but we won't have an item.instance ...
      if item.extra is not None: 
          lst.emulator["opt"] += item.extra

      nfo = item.instance if item.instance is not None else lst.emulator

      # ... and we need either an item.instance or a lst.emulator
      if not nfo:
          return
        
      if item.instance is not None and "class" in item.instance.keys():
        clazz = item.instance["class"]
      elif lst.clazz:
        clazz = lst.clazz
      else:
        clazz = 'Gen_Emulator'

      self.session = eval(clazz)(
          parent = self,
          info = nfo,
          source = lst.source or "",
          gamepad = self.gamepad,
          game = item.file)
      
    def list_keybinding (self):
  
      visible = self.get_active()

      try:

        pad = self.gamepad.get_device()
        keys = self.gamepad.keysx
      
        for event in pad.read_loop():
        
          if self.session is not None:
            break
        
          # Up/Down arrows
          if event.code == keys['ud_arrows']:
            actual = visible.GetFirstSelected()
            if actual == -1:
              visible.Select(0)
            else:    
              if event.value == -1:
                visible.Select(actual - 1)
              
              elif event.value == 1:
                if ((actual + 1) >= visible.maxitem):
                  visible.Select(0)
                else:
                  visible.Select(actual + 1)
                          
          # Left/Right arrows
          if event.code == keys['lr_arrows']:
 
            if event.value == -1:
              visible = self.prev_activate()
            elif event.value == 1:
              visible = self.next_activate()
                    
          # X button                
          elif (event.code == keys['X'] and event.value == 0):
            itm = visible.GetFirstSelected()

            if itm != -1:
              wx.PostEvent(self, StartSessionEvent(item=visible.get_item(itm)))

      except (IOError, OSError):
        wx.PostEvent(self, LKBindingEvent(error=True))
        init.update_info("Re-binding Pad!", 1)
        
# Testing purposes. (to be used in a dedicated X session)          
if PARAMETERS["NICE_WDW"]:
    subprocess.Popen(["hsetroot", "-solid", "\"#000000\""], shell=False)
    subprocess.Popen(["xcompmgr", "-c", "-C", "-f", "-F"], shell=False)

PagedListMgr(frame, lists=CONFIS["lists"], gamepad=CONFIS.GamePad)

app.MainLoop()

__name__ = '__main__'
