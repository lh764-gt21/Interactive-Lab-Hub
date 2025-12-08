"""
APDS Gesture Module
Handles APDS-9960 gesture sensor for swipe detection
Owner:
"""

import time

# Try to import the actual APDS library
try:
    import board
    import busio
    from adafruit_apds9960.apds9960 import APDS9960
    APDS_AVAILABLE = True
except ImportError:
    APDS_AVAILABLE = False
    print("APDS library not available - running in simulation mode")


class APDSGesture:
    def __init__(self, simulation_mode=False):
        """
        Initialize APDS gesture sensor
        simulation_mode: If True, use keyboard input instead of sensor
        """
        self.simulation_mode = simulation_mode or not APDS_AVAILABLE
        self.last_gesture = None
        self.last_proximity = 0
        
        print(f"[APDS] APDS_AVAILABLE: {APDS_AVAILABLE}, simulation_mode param: {simulation_mode}")
        
        if not self.simulation_mode:
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
                self.sensor = APDS9960(i2c)
                self.sensor.enable_gesture = True
                self.sensor.enable_proximity = True
                print("[APDS] Sensor initialized successfully in HARDWARE mode")
                print(f"[APDS] Gesture enabled: {self.sensor.enable_gesture}")
            except Exception as e:
                print(f"[APDS] Failed to initialize sensor: {e}")
                print("[APDS] Falling back to simulation mode")
                self.simulation_mode = True
        else:
            self.sensor = None
            print("[APDS] Running in SIMULATION mode")
    
    def get_gesture(self):
        """
        Read gesture from sensor
        Returns: 'swipe_left', 'swipe_right', 'swipe_up', 'swipe_down', or None
        """
        if self.simulation_mode:
            return None  # Simulation mode handled externally
        
        try:
            gesture = self.sensor.gesture()
            # Debug: print raw gesture value if non-zero
            if gesture != 0:
                print(f"[APDS DEBUG] Raw gesture value: {gesture} (hex: {hex(gesture)})")
            
            if gesture == 0x01:
                self.last_gesture = 'swipe_up'
            elif gesture == 0x02:
                self.last_gesture = 'swipe_down'
            elif gesture == 0x03:
                self.last_gesture = 'swipe_left'
            elif gesture == 0x04:
                self.last_gesture = 'swipe_right'
            else:
                return None
            
            print(f"Gesture detected: {self.last_gesture}")
            return self.last_gesture
            
        except Exception as e:
            print(f"Error reading gesture: {e}")
            return None
    
    def get_proximity(self):
        """
        Read proximity value from sensor
        Returns: 0-255 (higher = closer)
        """
        if self.simulation_mode:
            return self.last_proximity
        
        try:
            proximity = self.sensor.proximity
            self.last_proximity = proximity
            return proximity
        except Exception as e:
            print(f"Error reading proximity: {e}")
            return 0
    
    def get_data(self):
        """
        Get complete sensor data
        Returns dict with gesture and proximity
        """
        return {
            'gesture': self.get_gesture(),
            'proximity': self.get_proximity(),
            'timestamp': time.time()
        }
    
    def calibrate(self):
        """
        Calibrate the sensor (placeholder for future implementation)
        """
        print("Calibrating APDS sensor...")
        # TODO: Add calibration logic if needed
        time.sleep(1)
        print("Calibration complete")


class APDSSimulator:
    """
    Keyboard simulator for testing without hardware
    Maps arrow keys to gestures
    """
    def __init__(self):
        self.pending_gesture = None
        print("\nAPDS Simulator Active")
        print("Arrow Keys: LEFT/DOWN/UP/RIGHT for swipe gestures")
    
    def inject_gesture(self, gesture):
        """Inject a gesture for simulation"""
        self.pending_gesture = gesture
    
    def get_gesture(self):
        """Get and clear pending gesture"""
        gesture = self.pending_gesture
        self.pending_gesture = None
        return gesture


if __name__ == "__main__":
    # Test mode
    print("APDS Gesture Test Mode")
    print("=" * 40)
    
    apds = APDSGesture(simulation_mode=True)
    
    if apds.simulation_mode:
        print("\nSimulation Mode - Use arrow keys:")
        print("  LEFT  : Swipe Left (previous track)")
        print("  RIGHT : Swipe Right (next track)")
        print("  UP    : Swipe Up (volume up)")
        print("  DOWN  : Swipe Down (volume down)")
        print("  Q     : Quit")
        print()
        
        import sys
        import tty
        import termios
        
        def get_key():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        
        try:
            while True:
                key = get_key()
                
                if key == '\x1b':  # ESC sequence for arrow keys
                    next_key = get_key()
                    if next_key == '[':
                        arrow = get_key()
                        if arrow == 'A':
                            print("UP - Swipe Up")
                        elif arrow == 'B':
                            print("DOWN - Swipe Down")
                        elif arrow == 'C':
                            print("RIGHT - Swipe Right")
                        elif arrow == 'D':
                            print("LEFT - Swipe Left")
                elif key.lower() == 'q':
                    print("Quitting...")
                    break
                
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\nStopped")
    
    else:
        # Real sensor mode - continuous polling
        print("Monitoring APDS sensor... (Ctrl+C to stop)")
        try:
            while True:
                data = apds.get_data()
                if data['gesture']:
                    print(f"Gesture: {data['gesture']}")
                
                # Print proximity if it changes significantly
                if abs(data['proximity'] - apds.last_proximity) > 10:
                    print(f"Proximity: {data['proximity']}")
                
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\nStopped")