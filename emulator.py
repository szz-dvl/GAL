#!/usr/bin/python

import init
import wx
from ctypes import *
from Xlib import X, Xutil, protocol
import Xlib.XK
import Xlib.keysymdef.xkb
from abc import abstractmethod
import os
import threading
import time
import subprocess
from multiprocessing import Process, Pipe
from evdev import InputDevice
import signal
import alsaaudio
import psutil
import re
import logging
from pyjon.events import EventDispatcher

PARAMETERS = init.master_cfg["parameters"]
    
class timeval(Structure):
    _fields_ = [("tv_sec", c_long), ("tv_usec", c_long)]
        
    def tdiff (self, sec, usec):
      return abs ( ( (self.tv_sec - sec) * 1000 ) + ( (self.tv_usec - usec) / 1000 ) ) 

class BaseWdw():

    __metaclass__ = EventDispatcher

    def __init__(self, name, process=None):

        self.display = init.master_dpy
        self.windows = []
        
        threading.Timer(3, self.get_windows, args=[name]).start()
        
    def get_windows(self, name):
  
        root_win = self.display.screen().root 
        window_list = [root_win]
        
        while len(window_list) != 0:
            try:
                win = window_list.pop(0)
                if win.get_wm_name() == None:
                    children = win.query_tree().children
                    if children != None:
                        window_list += children
                        continue
                    
                clazz = win.get_wm_class()
                search_str = win.get_wm_name() or ""
                search_str += clazz[0] if clazz is not None else ""
                search_str += clazz[1] if clazz is not None else ""
                     
                if re.search(name, search_str, re.IGNORECASE):
                    
                    if win not in self.windows:
                        self.windows.append(win)
                else:

                    children = win.query_tree().children
                    if children != None:
                        window_list += children
                        
            except (Xlib.error.BadWindow, TypeError, RuntimeError):
                pass
        
        if self.windows:
            self.emit_event('wdws', name)
        else:
            self.emit_event('NOwdws', name)
                
        
class HiddenWindow(BaseWdw):

    def __init__(self, name, limit=7):

        self.limit = limit
        self.count = {'act': 0, 'last': 0, 'check': 0}

        Process(target=self.hide, args=(name,)).start()
                
        super(HiddenWindow, self).__init__(name)

        self.add_listener('NOwdws', self.__empty_wdws_event)
        self.add_listener('wdws', self.__wdws_event)
           
    def __wdws_event(self, name):
        
        self.count['act'] = len(self.windows)    

        for wdw in self.windows:
            self.minimize(wdw)
            
        if self.count['act'] != self.count['last']:
                    
            self.count['last'] = self.count['act']
            self.count['check'] = 0
                
            threading.Timer(1, self.get_windows, args=[name]).start()
            
        elif self.count['check'] <= self.limit:
                
            self.count['check'] += 1
            
            threading.Timer(1, self.get_windows, args=[name]).start()
            
        elif self.count['check'] > self.limit:
            
            self.emit_event('hidden', name)
            
    def __empty_wdws_event(self, name):
        
        threading.Timer(1, self.get_windows, args=[name]).start()
        
    def minimize (self, wdw):
        
        try:

            self.display.screen().root.send_event(
                protocol.event.ClientMessage(
                    window = wdw,
                    client_type = self.display.intern_atom("_NET_ACTIVE_WINDOW", only_if_exists=1),
                    data = (32, [2, X.CurrentTime,0,0,0])
                ),
                
                event_mask=X.SubstructureRedirectMask
            )
        
            
            self.display.flush()
            
            self.display.screen().root.send_event(
            
                protocol.event.ClientMessage (
                    window = wdw,
                    client_type = self.display.intern_atom('WM_CHANGE_STATE', only_if_exists=1),
                    data = (32, [Xutil.IconicState,0,0,0,0])
                ),
                
                event_mask = X.SubstructureRedirectMask|X.SubstructureNotifyMask
            )

            wdw.get_wm_state()
            
        except Xlib.error.BadWindow:
            pass
        
    @staticmethod
    def hide (name):
        subprocess.Popen([name], shell=False)
        
class GameWindow(BaseWdw):

    def __init__(self, name):

        self.name = name
        
        super(GameWindow, self).__init__(name)

        self.add_listener('NOwdws', self.__empty_wdws_event)
        self.add_listener('wdws', self.__wdws_event)
        self.__ready = False
                
    def __empty_wdws_event(self, name):

        threading.Timer(1, self.get_windows, args=[name]).start()
        # self.emit_event('busy', name)
        
    def __wdws_event(self, name):
      
        self.__ready = True            
        self.emit_event('ready', name)
                
    def __reset (self, name):

        if self.__ready:
            self.__ready = False
            self.windows = []
            self.get_windows(self.name)
        
    def __lookup_character_keycode(self, character):
    
        """
        Looks up the keysym for the character then returns the keycode mapping
        for that keysym.
        """
        
        keysym = Xlib.XK.string_to_keysym(character)
        if not keysym:
            try:
                keysym = getattr(Xlib.keysymdef.xkb, 'XK_' + character, 0)
            except:
                keysym = 0
                        
        return self.display.keysym_to_keycode(keysym)

    def __handle_key(self, character, event, modifiers):

        #INFO: http://stackoverflow.com/questions/38157453/send-keys-to-an-inactive-window-using-python-xlib
    
        """ Handles either a key press or release, depending on ``event``.
        :param character: The key to handle. See :meth:`press_key` and
        :meth:`release_key` for information about this parameter.
        :param event: The *Xlib* event. This should be either
        :attr:`Xlib.X.KeyPress` or :attr:`Xlib.X.KeyRelease`
        """
        
        keyCode = self.__lookup_character_keycode(character)
        
        for wdw in self.windows:
            
            wdw.grab_keyboard(True,
                              X.GrabModeAsync,
                              X.GrabModeAsync,
                              X.CurrentTime)
        
            if event == X.KeyPress:
                
                keyEvent = Xlib.protocol.event.KeyPress(
                    detail=keyCode,
                    time=X.CurrentTime,
                    root=self.display.screen().root,
                    window=wdw,
                    child=X.NONE,
                    root_x=1,
                    root_y=1,
                    event_x=1,
                    event_y=1,
                    state=modifiers,
                    same_screen=1
                )
                
            elif event == X.KeyRelease:
                
                keyEvent = Xlib.protocol.event.KeyRelease(
                    detail=keyCode,
                    time=X.CurrentTime,
                    root=self.display.screen().root,
                    window=wdw,
                    child=X.NONE,
                    root_x=1,
                    root_y=1,
                    event_x=1,
                    event_y=1,
                    state=modifiers,
                    same_screen=1
                )
                
            wdw.send_event(keyEvent)
                
    def press_key(self, character='', mod=0):
        """
        Press a given character key. Also works with character keycodes as
        integers, but not keysyms.
        """
        try:
            self.__handle_key(character, X.KeyPress, mod)
        except:
            self.__reset()
            pass
        
    def release_key(self, character='', mod=0):
        """
        Release a given character key. Also works with character keycodes as
        integers, but not keysyms.
        """
        try:
            self.__handle_key(character, X.KeyRelease, mod)
        except:
            self.__reset()
            pass
        
    def tap_key(self, character='', n=1, interval=0.25, mod=0):
        """Press and release a given character key n times."""

        if not self.__ready:
            return
        
        for i in range(n):
            self.press_key(character, mod)
            self.release_key(character, mod)
            time.sleep(interval)

    def multi_key(self, hold='', tap='',n=1, interval=0, mod=0):
        """Press and release a given "character combo keys" n times."""

        if not self.__ready:
            return
        
        for i in range(n):
            self.press_key(hold)
            time.sleep(interval/2)
            self.press_key(tap, mod)
            time.sleep(interval/2)
            self.release_key(hold)
            time.sleep(interval/2)
            self.release_key(tap)
            time.sleep(interval)
        
class Emulator(object):

    def __init__(self, parent=None, gamepad=None, source=None, nfo=None, game=None):
        
        if (nfo is None) or (parent is None) or (source is None) or (game is None):

            if (parent):
                wx.PostEvent(parent, init.EndSessionEvent())

            return None
        
        elif "name" not in nfo.keys() or "bin" not in nfo.keys():

            wx.PostEvent(self.parent, init.EndSessionEvent())
            return None
        
        self.gamepad = gamepad
        self.source = source
        self.parent = parent
        
        self.name = nfo["name"]
        self.bin = nfo["bin"]

        self.opt = nfo["opt"] if "opt" in nfo.keys() else None
        self.mode = nfo["mode"] if "mode" in nfo.keys() else "x"
        self.panel = nfo["panel"] if "panel" in nfo.keys() else True
        self.killd = {'R1': False, 'L1': False, 'L2': False, 'R2': False}
        
        self.session = None
        self.flag = False
        
        if "ini_file" in nfo.keys():
            self.state = self.getKeys(nfo["ini_file"], nfo["ini_kwd"])
        else:
            self.state = None
            
        if "steam" in nfo.keys():
          if not init.steam_running:
            
              self.steam = HiddenWindow("steam")
              self.steam.add_listener("hidden", self.__run_game, game)
              init.steam_running = True
            
          else:
          
              self.steam = True
              self.__run_game(game)
            
        else:
            self.steam = False
            self.__run_game(game)
            
    def __run_game (self, game):
        
        pconn, cconn = Pipe()
        
        Process(target=self.__run, args=(game,cconn,)).start()
        self.session = pconn.recv()
        pconn.close()
            
        self.window = GameWindow(self.name)
        
        self.window.add_listener("ready", self.__win_ready)
        
    def __win_ready (self, game, name=None):
        
        if self.gamepad and not self.flag:
            threading.Thread(target=self.upsession_bindings, kwargs={'init_slot': 0}).start()
        
    def __run (self, game, conn):
            
        cmd = [self.bin]

        if self.opt:
            for option in self.opt:
                cmd.append(option)

        if self.source != "":
            cmd.append(self.source + game)
            
        conn.send(subprocess.Popen(cmd, shell=False).pid)
        conn.close()
    
    def restart_keys (self, slot):
        threading.Thread(target=self.upsession_bindings, kwargs={'init_slot': slot}).start()
        
    #@abstractmethod
    def getKeys (self, file, keys):
        pass
    
    #@abstractmethod
    def R1_btn (self, edge):
        pass
        
    #@abstractmethod
    def L1_btn (self, edge):
        pass

    #@abstractmethod
    def R2_btn (self, edge):
        pass
        
    #@abstractmethod
    def L2_btn (self, edge):
        pass
      
    #@abstractmethod
    def X_btn (self, edge):
        pass
      
    #@abstractmethod
    def Square_btn (self, edge):
        pass

    #@abstractmethod
    def Circle_btn (self, edge):
        pass
        
    #@abstractmethod
    def Triangle_btn (self, edge):
        pass

    #@abstractmethod
    def Save_cmd (self, slot):
        pass

    #@abstractmethod
    def Load_cmd (self, slot, slot_dest):
        pass

    def kill_session (self):

        try:
            
            os.kill(self.session, signal.SIGTERM)
        
            if psutil.pid_exists(self.session):
                time.sleep(0.5)

                if psutil.pid_exists(self.session):
                    os.kill(self.session, signal.SIGKILL)

            exename = os.path.split(self.bin)[1].split(".")[0]
        
            for proc in psutil.process_iter():
                pname = proc.as_dict()['name']

                if pname.find(exename) != -1:
                    proc.kill()

                elif self.steam and not PARAMETERS["STEAM_KEEP_ALIVE"]:
                    if pname.find("steam") != -1:
                        proc.kill()
                        init.steam_running = False
                    
        except OSError:
            pass
            
        self.session = None
        wx.PostEvent(self.parent, init.EndSessionEvent())
            
    def onlyOne (self, mykey):
      
      res = True
      
      for key in self.killd.keys():
        if key == mykey:
          res = res and self.killd[key]
        else:
          res = res and not self.killd[key]
          
      return res
        
    def allPressed (self):
                
      res = True
        
      for key in self.killd.keys():
        res = res and self.killd[key]
            
      return res

    def infoMsg (self, data, level=0):
      
      if self.panel:
        init.update_info(data, level)
        
    def upsession_bindings (self, init_slot=0):

      sound = alsaaudio.Mixer()
      slot = init_slot
      slot_diff = slot
      tini = timeval(tv_sec=0, tv_usec=0)
      action = False
      master_btn = False

      self.flag = True

      try:

        pad = self.gamepad.get_device()
        keys = self.gamepad.keysx if self.mode == "x" else self.gamepad.keysd
        
        for event in pad.read_loop():

            if event.code == 0:
                continue

            if self.session is None:
                break

            # "Master" Button
            if event.code == keys['mtr_btn']:
                
                if event.value == 1:

                    tini.tv_usec = event.usec
                    tini.tv_sec = event.sec
                    
                    action = False
                    master_btn = True
                    
                elif event.value == 0:
            
                    master_btn = False
                    
                    for key in self.killd:
                        self.killd[key] = False
            
                    if not action:

                        tdiff = tini.tdiff(event.sec, event.usec) # millis.
                      
                        if (tdiff <= 1000) and slot_diff == slot:
                            
                            slot = (slot + 1) % 10
                            self.Save_cmd(slot)
                    
                        elif (tdiff > 1000):
                            self.Load_cmd(slot, slot_diff)
                        
                slot_diff = slot
                                
            elif master_btn: # <--- "Master" Button is pressed here!
              
                # L1 Button
                if event.code == keys['L1']:
                    if event.value == 1:
                        self.killd['L1'] = True
                    elif event.value == 0:
                        if self.onlyOne('L1'):
                            action = self.L1_Btn() or action
                            
                        self.killd['L1'] = False
                  
                # R1 Button
                elif event.code == keys['R1']:
                    if event.value == 1:
                        self.killd['R1'] = True
                    elif event.value == 0:
                        if self.onlyOne('R1'):
                            action = self.R1_Btn() or action
                  
                        self.killd['R1'] = False
                  

                # L2 Button
                elif event.code == keys['L2']:
                    if event.value >= 1:
                        self.killd['L2'] = True
                    elif event.value == 0:
                        if self.onlyOne('L2'):
                            action = self.L2_Btn() or action

                        self.killd['L2'] = False

                # R2 Button
                elif event.code == keys['R2']:
                    if event.value  >= 1:
                        self.killd['R2'] = True
                    elif event.value == 0: 
                        if self.onlyOne('R2'):
                            action = self.R2_Btn() or action
                        
                        self.killd['R2'] = False

                # X Button 
                elif event.code == keys['X']:
                    if event.value == 0: 
                        action = self.X_Btn() or action

                # Square Button 
                elif event.code == keys['Sqre']:
                    if event.value == 0: 
                        action = self.Square_Btn() or action

                # Circle Button 
                elif event.code == keys['Circ']:
                    if event.value == 0: 
                        action = self.Circle_Btn() or action

                # Triangle Button 
                elif event.code == keys['Tri']:
                    if event.value == 0: 
                        action = self.Triangle_Btn() or action
                        
                # Up / Down arrows
                elif event.code == keys['ud_arrows']:

                    vol = int(sound.getvolume()[0])
                    
                    if event.value == -1:
                    
                        if (vol + 5 >= 100):
                            vol = 100;
                        else:
                            vol += 5
                
                    elif event.value == 1:
                    
                        if (vol - 5 <= 0):
                            vol = 0
                        else:
                            vol -= 5
                
                    self.infoMsg("Volume: " + str(vol))
                    sound.setvolume(vol)
                    action = True

                # Left / Right arrows
                elif event.code == keys['lr_arrows']:
                
                    if event.value != 0:
                        slot_diff += event.value 

                    if slot_diff < 0:
                        slot_diff = 10 + slot_diff
                    elif slot_diff > 9:
                        slot_diff = slot_diff - 10
                  
                    self.infoMsg("Loading slot " + str(slot_diff) + " ...")

                # Kill command detection
                if self.allPressed():
                    
                    self.kill_session()
                    action = True
                    
      except (IOError, OSError):
          self.restart_keys(slot)
          self.infoMsg("Re-binding Pad!", 1)
          
      except AttributeError:
          # Not Implemented Button responses
          pass
      
class Gen_Emulator(Emulator):

    def __init__(self, parent=None, info=None, gamepad=None, source=None, game=None):

        super(Gen_Emulator, self).__init__(parent, gamepad, source, info, game)

        
__all__ = ['Emulator', 'Gen_Emulator']
