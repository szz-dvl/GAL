from emulator import Emulator
import time

#Example for Mupen64Plus emulator:

class N64_Emulator(Emulator):

    def __init__(self, parent=None, info=None, gamepad=None, source=None, game=None):

        super(N64_Emulator, self).__init__(parent, gamepad, source, info, game)
        
    def getKeys (self, file, keys):
        return None
  
    def R1_Btn (self):

        self.infoMsg("Speed +5%")
        
        self.window.tap_key('F11')
        
        return True
    
    def L1_Btn (self):
        
        self.infoMsg("Speed -5%")
        
        self.window.tap_key('F10')
        
        return True
    
    def R2_Btn (self):
        return False
        
    def L2_Btn (self):
        return False

    def Save_cmd (self, slot):
        
        self.infoMsg("Saving slot " + str(slot) + "...")

        self.window.tap_key(str(slot))
        self.window.tap_key('F5')
    
    def Load_cmd (self, slot, slot_dest):

        self.infoMsg("Loading slot " + str(slot_dest) + " current: " + str(slot) + "...")
        
        if (slot_dest != slot):
            self.window.tap_key(str(slot_dest))
        else:
            self.window.tap_key(str(slot))
            
        self.window.tap_key('F7')

        if (slot_dest != slot):
            self.window.tap_key(str(slot))
        
    
    def X_Btn (self):
        return False
        
    def Square_Btn (self):
        return False

    def Circle_Btn (self):
        return False
        
    def Triangle_Btn (self):
        return False
    
__all__ = ["N64_Emulator"]
