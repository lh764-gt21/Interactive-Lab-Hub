"""
MPR121 Touch Sensor Module
Handles capacitive touch input for track selection (1-10)

Owner: Zoe Tseng (yzt2), Charlotte Lin (hl2575)
"""

import time

# Try to import the actual MPR121 library
try:
    import board
    import busio
    import adafruit_mpr121
    MPR121_AVAILABLE = True
except ImportError:
    MPR121_AVAILABLE = False
    print("MPR121 library not available")


class MPR121Touch:
    def __init__(self):
        """
        Initialize MPR121 capacitive touch sensor
        Pads 0-9 correspond to tracks 1-10
        Pad 10 = Play/Pause, Pad 11 = Stop
        """
        self.available = MPR121_AVAILABLE
        self.last_touched = 0
        
        if self.available:
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
                self.mpr121 = adafruit_mpr121.MPR121(i2c)
                print("[MPR121] Touch sensor initialized successfully")
            except Exception as e:
                print(f"[MPR121] Failed to initialize: {e}")
                self.available = False
        else:
            self.mpr121 = None
            print("[MPR121] Running without touch sensor")
    
    def get_touched_pad(self):
        """
        Get the currently touched pad number
        Returns: 0-11 for pad number, or None if no pad touched
        """
        if not self.available:
            return None
        
        try:
            current_touched = self.mpr121.touched()
            
            # Check for newly touched pads (rising edge detection)
            for i in range(12):
                pin_bit = 1 << i
                # Check if this pad is newly touched (wasn't touched before, is now)
                if (current_touched & pin_bit) and not (self.last_touched & pin_bit):
                    self.last_touched = current_touched
                    return i
            
            self.last_touched = current_touched
            return None
            
        except Exception as e:
            print(f"[MPR121] Error reading touch: {e}")
            return None
    
    def get_track_number(self):
        """
        Get track number from touch (1-10)
        Returns: 1-10 for track selection, or None if no track pad touched
        """
        pad = self.get_touched_pad()
        if pad is not None and 0 <= pad <= 9:
            return pad + 1  # Pad 0 = Track 1, Pad 9 = Track 10
        return None
    
    def get_control(self):
        """
        Get control action from touch
        Returns: 'play_pause' for pad 10, 'stop' for pad 11, or None
        """
        pad = self.get_touched_pad()
        if pad == 10:
            return 'play_pause'
        elif pad == 11:
            return 'stop'
        return None
    
    def get_action(self):
        """
        Get any action (track selection or control)
        Returns: dict with 'type' and 'value', or None
        """
        pad = self.get_touched_pad()
        if pad is None:
            return None
        
        if 0 <= pad <= 9:
            return {'type': 'track', 'value': pad + 1}
        elif pad == 10:
            return {'type': 'control', 'value': 'play_pause'}
        elif pad == 11:
            return {'type': 'control', 'value': 'stop'}
        
        return None


if __name__ == "__main__":
    print("MPR121 Touch Sensor Test")
    print("=" * 40)
    print("Touch pads 0-9 for tracks 1-10")
    print("Touch pad 10 for Play/Pause")
    print("Touch pad 11 for Stop")
    print("Press Ctrl+C to quit")
    print()
    
    touch = MPR121Touch()
    
    if not touch.available:
        print("MPR121 not available, exiting")
        exit(1)
    
    try:
        while True:
            action = touch.get_action()
            if action:
                if action['type'] == 'track':
                    print(f"Track {action['value']} selected")
                else:
                    print(f"Control: {action['value']}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped")

