"""
Gesture DJ - Main Integration System
Combines APDS gestures, MPR121 touch, voice control, audio engine, and display
With optional web visualization interface
"""

import time
import sys
import signal
import threading
from audio_engine import AudioEngine
from apds_gesture import APDSGesture
from mpr121_touch import MPR121Touch
from voice_control import VoiceControl
from display import Display

# MediaPipe imports (kept but disabled)
# from hand_tracker import HandTracker

# Web server (optional)
try:
    import web_server
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False


class GestureDJ:
    def __init__(self):
        """
        Initialize Gesture DJ system
        """
        print("Initializing Gesture DJ...")
        print("=" * 50)
        
        self.running = False
        
        # Initialize all modules
        self.audio = AudioEngine(tracks_dir="tracks", effects_dir="effects")
        self.apds = APDSGesture()
        self.mpr121 = MPR121Touch()
        self.voice = VoiceControl()
        
        # MediaPipe hand tracker (disabled)
        # self.hand_tracker = HandTracker(headless=False)
        # self.last_pose_processed = None
        
        # Display: use hardware TFT
        self.display = Display(prefer_framebuffer=False)
        
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
            # Next track and auto-play
            self.audio.stop()
            track = self.audio.next_track()
            self.audio.play()
            self.display.show_message(f"-> Track {track['id']}")
            self._update_web_state()
            time.sleep(0.5)
        
        elif gesture == 'swipe_left':
            # Previous track and auto-play
            self.audio.stop()
            track = self.audio.prev_track()
            self.audio.play()
            self.display.show_message(f"<- Track {track['id']}")
            self._update_web_state()
            time.sleep(0.5)
        
        elif gesture == 'swipe_up':
            # Volume up
            volume = self.audio.volume_up(0.1)
            self.display.show_message(f"Volume: {int(volume * 100)}%")
            self._update_web_state()
            time.sleep(0.3)
        
        elif gesture == 'swipe_down':
            # Volume down
            volume = self.audio.volume_down(0.1)
            self.display.show_message(f"Volume: {int(volume * 100)}%")
            self._update_web_state()
            time.sleep(0.3)
    
    def handle_mpr121_touch(self, action):
        """Process MPR121 touch and trigger audio action"""
        if not action:
            return
        
        if action['type'] == 'track':
            track_num = action['value']
            print(f"[MPR121] Track {track_num} selected")
            self.audio.stop()
            track = self.audio.select_track(track_num)
            if track:
                self.audio.play()
                self.display.show_message(f"Track {track['id']}")
            self._update_web_state()
            time.sleep(0.3)
        
        elif action['type'] == 'control':
            if action['value'] == 'play_pause':
                print("[MPR121] Play/Pause")
                if self.audio.is_paused:
                    self.audio.resume()
                    self.display.show_message("> RESUME")
                elif self.audio.is_playing:
                    self.audio.pause()
                    self.display.show_message("|| PAUSE")
                else:
                    self.audio.play()
                    self.display.show_message("> PLAY")
                self._update_web_state()
                time.sleep(0.3)
            
            elif action['value'] == 'stop':
                print("[MPR121] Stop")
                self.audio.stop()
                self.audio.load_track()
                self.display.show_message("[] STOP")
                self._update_web_state()
                time.sleep(0.3)
    
    def handle_voice_command(self, command):
        """Process voice command and trigger audio action (play/pause only)"""
        if not command:
            return
        
        print(f"[Voice] Command: {command}")
        
        if command == 'play':
            if not self.audio.is_playing or self.audio.is_paused:
                if self.audio.is_paused:
                    self.audio.resume()
                else:
                    self.audio.play()
                self.display.show_message("> PLAY")
            self._update_web_state()
            time.sleep(0.3)
        
        elif command == 'pause':
            if self.audio.is_playing and not self.audio.is_paused:
                self.audio.pause()
                self.display.show_message("|| PAUSE")
            self._update_web_state()
            time.sleep(0.3)
    
    # MediaPipe hand gesture handler (kept but disabled)
    # def handle_hand_gesture(self, hand_data):
    #     """Process MediaPipe hand gesture and trigger action"""
    #     if not hand_data:
    #         return
    #     
    #     pose = hand_data['pose']
    #     finger_count = hand_data['finger_count']
    #     gesture_confirmed = hand_data.get('gesture_confirmed', False)
    #     
    #     if gesture_confirmed:
    #         print(f"[MediaPipe] {pose} ({finger_count} fingers) - CONFIRMED")
    #     
    #     processed = False
    #     if gesture_confirmed and pose != self.last_pose_processed:
    #         if pose == 'palm':
    #             if self.audio.is_paused:
    #                 self.audio.resume()
    #                 self.display.show_message("> RESUME")
    #             elif self.audio.is_playing:
    #                 self.audio.pause()
    #                 self.display.show_message("|| PAUSE")
    #             else:
    #                 self.audio.play()
    #                 self.display.show_message("> PLAY")
    #             time.sleep(0.3)
    #             processed = True
    #         
    #         elif pose == 'fist':
    #             self.audio.stop()
    #             self.audio.load_track()
    #             self.display.show_message("[] STOP")
    #             time.sleep(0.3)
    #             processed = True
    #         
    #         self.last_pose_processed = pose if processed else self.last_pose_processed
    #     
    #     if 'finger_distance' in hand_data:
    #         distance = hand_data['finger_distance']
    #         speed = 0.5 + (distance * 3.0)
    #         self.audio.set_tempo(speed)
    
    def update_display(self):
        """Update display with current state"""
        state = self.audio.get_state()
        self.display.update_dj_display(state)
    
    def _update_web_state(self):
        """Immediately update web interface with current state"""
        if hasattr(self, 'web_enabled') and self.web_enabled and WEB_AVAILABLE:
            state = self.audio.get_state()
            web_server.update_state(state)
    
    def run(self, enable_web=False):
        """Main event loop"""
        self.running = True
        self.web_enabled = enable_web
        
        print("\n" + "=" * 50)
        print("GESTURE DJ CONTROLS")
        print("=" * 50)
        print("\nAPDS Gestures:")
        print("  Swipe RIGHT : Next track")
        print("  Swipe LEFT  : Previous track")
        print("  Swipe UP    : Volume up")
        print("  Swipe DOWN  : Volume down")
        print("\nMPR121 Touch Pads:")
        print("  Pads 0-9    : Select track 1-10")
        print("  Pad 10      : Play/Pause")
        print("  Pad 11      : Stop")
        print("\nVoice Commands:")
        print("  'play'      : Start playback")
        print("  'pause'     : Pause playback")
        
        if enable_web and WEB_AVAILABLE:
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            print(f"\nWeb Visualizer:")
            print(f"  http://{ip}:5000")
            print(f"  http://localhost:5000")
        
        print("\nPress Ctrl+C to quit")
        print("=" * 50 + "\n")
        
        # Start voice control in background
        self.voice.start(callback=self.handle_voice_command)
        
        # Start web server in background if enabled
        if enable_web and WEB_AVAILABLE:
            import webbrowser
            import socket
            
            web_server.set_audio_engine(self.audio)
            self._web_thread = threading.Thread(
                target=web_server.run_server,
                kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False},
                daemon=True
            )
            self._web_thread.start()
            print("[Web] Visualization server started")
            
            # Auto-open browser after short delay
            time.sleep(2)
            try:
                # Try to get local IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                url = f"http://{local_ip}:5000"
            except:
                url = "http://localhost:5000"
            
            print(f"[Web] Opening browser: {url}")
            webbrowser.open(url)
        
        self._run_hardware()
    
    def _run_hardware(self):
        """Run with actual hardware sensors"""
        last_display_update = time.time()
        last_web_update = time.time()
        display_update_interval = 0.5
        web_update_interval = 0.1  # 10 FPS for web
        
        try:
            while self.running:
                # Check APDS for gestures
                gesture = self.apds.get_gesture()
                if gesture:
                    self.handle_apds_gesture(gesture)
                
                # Check MPR121 for touch input
                action = self.mpr121.get_action()
                if action:
                    self.handle_mpr121_touch(action)
                
                # Voice commands are handled via callback in background thread
                
                # MediaPipe hand tracking (disabled)
                # hand_data = self.hand_tracker.get_data()
                # if hand_data:
                #     self.handle_hand_gesture(hand_data)
                
                # Check APDS again
                gesture = self.apds.get_gesture()
                if gesture:
                    self.handle_apds_gesture(gesture)
                
                # Update display periodically
                if time.time() - last_display_update > display_update_interval:
                    self.update_display()
                    last_display_update = time.time()
                
                # Update web server state
                if self.web_enabled and WEB_AVAILABLE:
                    if time.time() - last_web_update > web_update_interval:
                        state = self.audio.get_state()
                        web_server.update_state(state)
                        last_web_update = time.time()
                
                time.sleep(0.02)
        
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up all resources"""
        print("\nCleaning up...")
        self.running = False
        
        self.audio.stop()
        
        # Stop voice control
        if hasattr(self, 'voice'):
            self.voice.stop()
        
        # MediaPipe cleanup (disabled)
        # if hasattr(self, 'hand_tracker') and hasattr(self.hand_tracker, 'cleanup'):
        #     self.hand_tracker.cleanup()
        
        if hasattr(self.display, 'cleanup'):
            self.display.cleanup()
        
        print("Goodbye!")


def main():
    """Main entry point"""
    # Check for --web flag
    enable_web = '--web' in sys.argv
    
    print("Starting Gesture DJ with HARDWARE")
    if enable_web:
        if WEB_AVAILABLE:
            print("Web visualization ENABLED")
        else:
            print("Warning: Web server not available (missing dependencies)")
            enable_web = False
    
    # Create and run Gesture DJ
    dj = GestureDJ()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\nInterrupt received... Exiting.")
        dj.running = False
        dj.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the system
    dj.run(enable_web=enable_web)


if __name__ == "__main__":
    main()
