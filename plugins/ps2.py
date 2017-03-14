from emulator import Emulator
import time

class PS2_Emulator(Emulator):

    def __init__(self, parent=None, info=None, gamepad=None, source=None, game=None):

        super(PS2_Emulator, self).__init__(parent, gamepad, source, info, game)
        
    #@classmethod
    def getKeys (self, file, keys):
            
        f = open(file, "r")
        ret = {}
        for line in f:
            for key in keys:
                if key in line:
                    nfo = line.split("=")[1].strip()
                    if nfo == "enabled":
                        ret[key] = True
                    else:
                        ret[key] = False
        f.close()

        return ret

    #@classmethod
    def R1_Btn (self):

        push = self.state["FrameSkipEnable"] = not self.state["FrameSkipEnable"]
        mode = "ON" if push else "OFF"
        
        self.infoMsg("Turbo mode " + mode + ".")
        self.window.tap_key('Tab')
        
        return True
    
    #@classmethod
    def L1_Btn (self):

        push = self.state["FrameLimitEnable"] = not self.state["FrameLimitEnable"]
        mode = "ON" if push else "OFF"
            
        self.infoMsg("Framelimmiting mode " + mode + ".")
        self.window.tap_key('F4')
        
        return True
    
    #@classmethod    
    def R2_Btn (self):

        self.infoMsg("Hwd/Swd switch tapped.")
        self.window.tap_key('F9')
        
        return True
        
    #@classmethod
    def L2_Btn (self):
        
        ara = time.strftime("%H:%M:%S", time.gmtime())
        self.infoMsg(ara)

        return True
        
    #@classmethod
    def Save_cmd (self, slot):

        self.infoMsg("Saving slot " + str(slot) + "...")
        
        self.window.tap_key('F2')
        self.window.tap_key('F1')
        
    #@classmethod
    def Load_cmd (self, slot, slot_dest):
        
        if (slot_dest == slot):
         
            self.infoMsg("Loading slot " + str(slot) + "...")
            self.window.tap_key('F3')

        else:
            if slot_dest - slot > 0:
                
                self.window.tap_key('F2', n=(slot_dest - slot))
                self.window.tap_key('F3')
                self.window.multi_key('Shift_L', 'F2', n=(slot_dest - slot), interval=0.3, mod=3)
                
            else:
                
                self.window.multi_key('Shift_L', 'F2', n=(slot - slot_dest), interval=0.3, mod=3)
                self.window.tap_key('F3')
                self.window.tap_key('F2', n=(slot - slot_dest))
                
    
    #@classmethod
    def X_Btn (self, state):
        return False
        
    #@classmethod
    def Square_Btn (self, state):
        return False

    #@classmethod
    def Circle_Btn (self, state):
        return False
        
    #@classmethod
    def Triangle_Btn (self, state):
        return False
    
  
__all__ = ["PS2_Emulator"]
