"""
Gesture DJ - Main Integration System
Combines APDS gestures, MediaPipe hand tracking, audio engine, and display
"""

import time
import sys
import signal
from audio_engine import AudioEngine
from apds_gesture import APDSGesture
from hand_tracker import HandTracker
from display import Display


class GestureDJ:
    def __init__(self, simulation_mode=False):
        """
        Initialize Gesture DJ system
        simulation_mode: If True, use keyboard simulation
        """
        print("Initializing Gesture DJ...")
        print("=" * 50)
        
        self.simulation_mode = simulation_mode
        self.running = False
        
        # Initialize all modules
        self.audio = AudioEngine(tracks_dir="tracks", effects_dir="effects")
        self.apds = APDSGesture(simulation_mode=simulation_mode)
        self.hand_tracker = HandTracker(simulation_mode=simulation_mode)
        # Display: use hardware TFT (with prefer_framebuffer=False to avoid conflicts)
        self.display = Display(simulation_mode=simulation_mode, prefer_framebuffer=False)
        self.last_pose_processed = None
        
        # Load first track
        self.audio.load_track()
        
        # Show welcome message
        self.display.show_message("GESTURE DJ")
        time.sleep(2)
        
        print("\n" + "=" * 50)
        print("Gesture DJ Ready!")
        print("=" * 50)
    
    def handle_apds_gesture(self, gesture):
        """Process APDS gesture and trigger audio action"""
        if not gesture:
            return
        
        print(f"[APDS] {gesture}")
        
        if gesture == 'swipe_right':
            # Next track
            track = self.audio.next_track()
            self.display.show_message(f"-> Track {track['id']}")
            time.sleep(0.5)
        
        elif gesture == 'swipe_left':
            # Previous track (wraps around)
            track = self.audio.prev_track()
            self.display.show_message(f"<- Track {track['id']}")
            time.sleep(0.5)
        
        elif gesture == 'swipe_up':
            # Volume up
            volume = self.audio.volume_up(0.1)  # +10%
            self.display.show_message(f"Volume: {int(volume * 100)}%")
            time.sleep(0.3)
        
        elif gesture == 'swipe_down':
            # Volume down
            volume = self.audio.volume_down(0.1)  # -10%
            self.display.show_message(f"Volume: {int(volume * 100)}%")
            time.sleep(0.3)
    
    def handle_hand_gesture(self, hand_data):
        """Process MediaPipe hand gesture and trigger action"""
        if not hand_data:
            return
        
        pose = hand_data['pose']
        finger_count = hand_data['finger_count']
        gesture_confirmed = hand_data.get('gesture_confirmed', False)
        
        # Only log confirmed gestures to reduce spam
        if gesture_confirmed:
            print(f"[MediaPipe] {pose} ({finger_count} fingers) - CONFIRMED")
        
        # Process confirmed gestures with edge detection
        processed = False
        if gesture_confirmed and pose != self.last_pose_processed:
            # Play/Pause toggle with palm (5 fingers) - requires 2 sec hold
            if pose == 'palm':
                if self.audio.is_paused:
                    self.audio.resume()
                    self.display.show_message("> RESUME")
                elif self.audio.is_playing:
                    self.audio.pause()
                    self.display.show_message("|| PAUSE")
                else:
                    self.audio.play()
                    self.display.show_message("> PLAY")
                time.sleep(0.3)
                processed = True
            
            # Stop + reset with fist (0 fingers) - requires 2 sec hold
            elif pose == 'fist':
                self.audio.stop()
                # Ensure next play starts from beginning
                self.audio.load_track()
                self.display.show_message("[] STOP")
                time.sleep(0.3)
                processed = True
            
            # Update last processed pose (debounce)
            self.last_pose_processed = pose if processed else self.last_pose_processed
        
        # Playback speed control based on finger distance (continuous)
        if 'finger_distance' in hand_data:
            distance = hand_data['finger_distance']
            # Map distance (0-1) to speed (0.5-3.5)
            # Closer fingers = slower (0.5x), wide open = faster (3.5x)
            speed = 0.5 + (distance * 3.0)  # 0.5 + (1.0 * 3.0) = 3.5
            
            # Debug: show what's being detected (every 30 frames to avoid spam)
            if not hasattr(self, '_speed_debug_counter'):
                self._speed_debug_counter = 0
            self._speed_debug_counter += 1
            if self._speed_debug_counter % 30 == 0:
                print(f"[Speed] Distance: {distance:.2f} -> Speed: {speed:.2f}x -> Preset: {self.audio.current_speed_preset}x")
            
            self.audio.set_tempo(speed)
    
    def update_display(self):
        """Update display with current state"""
        state = self.audio.get_state()
        self.display.update_dj_display(state)
    
    def run(self):
        """Main event loop"""
        self.running = True
        
        print("\n" + "=" * 50)
        print("GESTURE DJ CONTROLS")
        print("=" * 50)
        print("\nAPDS Gestures:")
        print("  Swipe RIGHT : Next track")
        print("  Swipe LEFT  : Previous track")
        print("  Swipe UP    : Volume up")
        print("  Swipe DOWN  : Volume down")
        print("\nMediaPipe Hand Gestures:")
        print("  Palm (5 fingers)   : Play/Pause (hold 2 sec)")
        print("  Fist (0 fingers)   : Stop (hold 2 sec)")
        print("  Finger Distance    : Playback speed (continuous)")
        print("\nPress Ctrl+C to quit")
        print("=" * 50 + "\n")
        
        if self.simulation_mode:
            self._run_simulation()
        else:
            self._run_hardware()
    
    def _run_hardware(self):
        """Run with actual hardware sensors"""
        last_display_update = time.time()
        display_update_interval = 0.5  # Update display every 0.5 seconds
        
        try:
            while self.running:
                # Check APDS for gestures
                gesture = self.apds.get_gesture()
                if gesture:
                    self.handle_apds_gesture(gesture)
                
                # Check MediaPipe for hand gestures
                hand_data = self.hand_tracker.get_data()
                if hand_data:
                    self.handle_hand_gesture(hand_data)
                
                # Update display periodically
                if time.time() - last_display_update > display_update_interval:
                    self.update_display()
                    last_display_update = time.time()
                
                time.sleep(0.05)  # 20 FPS polling
        
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
    
    def _run_simulation(self):
        """Run with keyboard simulation"""
        print("\nSIMULATION MODE - Keyboard Controls:")
        print("  Arrow keys: APDS gestures (LEFT/RIGHT/UP/DOWN)")
        print("  Number 0-5: MediaPipe finger count")
        print("  Space: Toggle play/pause")
        print("  Q: Quit")
        print()
        
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
        
        last_display_update = time.time()
        
        try:
            while self.running:
                key = get_key()
                
                # Arrow keys for APDS
                if key == '\x1b':  # ESC sequence
                    next_key = get_key()
                    if next_key == '[':
                        arrow = get_key()
                        if arrow == 'C':
                            self.handle_apds_gesture('swipe_right')
                        elif arrow == 'D':
                            self.handle_apds_gesture('swipe_left')
                        elif arrow == 'A':
                            self.handle_apds_gesture('swipe_up')
                        elif arrow == 'B':
                            self.handle_apds_gesture('swipe_down')
                
                # Number keys for MediaPipe
                elif key.isdigit():
                    finger_count = int(key)
                    poses = {0: 'fist', 1: 'one', 2: 'peace', 3: 'three', 4: 'four', 5: 'palm'}
                    hand_data = {
                        'pose': poses.get(finger_count, 'unknown'),
                        'finger_count': finger_count,
                        'finger_distance': 0.5,
                        'gesture_confirmed': True
                    }
                    self.handle_hand_gesture(hand_data)
                
                # Space for quick play/pause
                elif key == ' ':
                    if self.audio.is_playing:
                        self.audio.pause()
                    else:
                        self.audio.play()
                
                # Quit
                elif key.lower() == 'q':
                    print("Quitting...")
                    break
                
                # Update display periodically
                if time.time() - last_display_update > 1.0:
                    self.update_display()
                    last_display_update = time.time()
                
                time.sleep(0.05)
        
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up all resources"""
        print("\nCleaning up...")
        self.running = False
        
        self.audio.stop()
        
        if hasattr(self.hand_tracker, 'cleanup'):
            self.hand_tracker.cleanup()
        
        if hasattr(self.display, 'cleanup'):
            self.display.cleanup()
        
        print("Goodbye!")


def main():
    """Main entry point"""
    # Check if running in simulation mode
    simulation = '--sim' in sys.argv or '--simulation' in sys.argv
    
    if simulation:
        print("Starting in SIMULATION MODE")
    else:
        print("Starting with HARDWARE")
    
    # Create and run Gesture DJ
    dj = GestureDJ(simulation_mode=simulation)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\nInterrupt received...")
        dj.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the system
    dj.run()


if __name__ == "__main__":
    main()