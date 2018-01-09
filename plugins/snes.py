from emulator import Emulator
import time

#Example for ZSNES emulator:

class ZSNES_Emulator(Emulator):
    
    def __init__(self, parent=None, info=None, gamepad=None, source=None, game=None):

        super(ZSNES_Emulator, self).__init__(parent, gamepad, source, info, game)

        self.slot_mode = False
        self.menu_mode = False
        self.menu_cnt = 0
        self.menu_max_depth = 2
        
    def getKeys (self, file, keys):
        return None

    def zsnes_tap(self, key):
        self.window.press_key(key)
        time.sleep(0.05)
        self.window.release_key(key)
        time.sleep(0.05)
        self.window.release_key(key)
        
    def R1_Btn (self):

        # sometimes things gets a little bit messy ... =S.

        self.slot_mode = False
        self.menu_mode = False
        self.nav_mode = False
        self.menu_cnt = 0

        return True
    
    def L1_Btn (self):

        if not self.menu_mode:
            if not self.slot_mode: 
                self.zsnes_tap('F3')
                self.slot_mode = True
            else:
                self.zsnes_tap('Escape')
                self.slot_mode = False
                
            self.nav_mode = not self.nav_mode

        return True

    def R2_Btn (self):
        return False
    
    def L2_Btn (self):
        
        if not self.slot_mode:
            self.zsnes_tap('Escape')
            
            if self.menu_mode:    
                self.menu_cnt -= 1

                if self.menu_cnt == 0:
                    self.menu_mode = False
                    self.nav_mode = False
                
            else:
                self.menu_cnt += 1 
                self.menu_mode = True
                self.nav_mode = True
                
        return True

    def Save_cmd (self, slot):
        
        self.zsnes_tap('F2')
    
    def Load_cmd (self, slot, slot_dest):

        self.zsnes_tap('F4')

    def X_Btn (self):

        if self.slot_mode or self.menu_mode:
            self.zsnes_tap('Return')

            if self.menu_mode:
                if self.menu_cnt < self.menu_max_depth:
                    self.menu_cnt += 1

            elif self.slot_mode:
                self.slot_mode = False
                self.nav_mode = False
                
        return True
        
    def Square_Btn (self):

        if self.menu_mode:
            self.zsnes_tap('SpaceBar')
            
        return False

    def Circle_Btn (self):

        if self.menu_mode:
            self.window.multi_key('Alt_L', 'E') # Enable / Disable sound =P.
            
            return True
        
    def Triangle_Btn (self):
        
        if self.slot_mode or self.menu_mode:
            self.zsnes_tap('Escape')

            if self.slot_mode:
                self.slot_mode = False
                self.nav_mode = False
                
            elif self.menu_mode:
                self.menu_cnt -= 1

                if self.menu_cnt == 0:
                    self.menu_mode = False
                    self.nav_mode = False
                    
        return True

    # Navigate mode.
    def Navigate (self, dire):
        self.zsnes_tap(dire);
        
__all__ = ["ZSNES_Emulator"]
