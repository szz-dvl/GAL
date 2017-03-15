from emulator import Emulator
import time

# Poor example for Xonotic:

class Xonotic (Emulator):

    def __init__(self, parent=None, info=None, gamepad=None, source=None, game=None):

        super(Xonotic, self).__init__(parent, gamepad, source, info, game)
        
    def getKeys (self, file, keys):
        return None
  
    def R1_Btn (self):
        return False
    
    def L1_Btn (self):

        self.window.tap_key('Escape')
        return True
    
    def R2_Btn (self):
        return False
        
    def L2_Btn (self):
        return False

    def Save_cmd (self, slot):
        
        self.window.tap_key('F1')
    
    def Load_cmd (self, slot, slot_dest):

        self.window.tap_key('F2')        
    
    def X_Btn (self):
        return False
        
    def Square_Btn (self):
        return False

    def Circle_Btn (self):
        return False
        
    def Triangle_Btn (self):
        return False
    
__all__ = ["Xonotic"]
