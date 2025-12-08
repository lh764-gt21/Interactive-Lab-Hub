"""
Gesture DJ - Main Application with OLED Display
Uses gesture_dj_core.py for logic, handles display and web interface
"""

import time
import sys
import signal
import threading
from display import Display
from gesture_dj_core import GestureDJCore

# Web server (optional)
try:
    import web_server
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False


class GestureDJ:
    def __init__(self, web_mode=False):
        """
        Initialize Gesture DJ with display
        Args:
            web_mode: If True, run camera in headless mode (browser only)
        """
        print("Initializing Gesture DJ...")
        print("=" * 50)
        
        self.running = False
        self.web_mode = web_mode
        
        # Initialize core logic
        self.core = GestureDJCore(
            enable_camera=True, 
            headless_camera=web_mode
        )
        
        # Display: use hardware TFT (OLED)
        self.display = Display(prefer_framebuffer=False)
        
        # Show welcome message
        self.display.show_message("GESTURE DJ")
        time.sleep(2)
        
        print("\n" + "=" * 50)
        print("Gesture DJ Ready!")
        print("=" * 50)
    
    def _update_web_state(self):
        """Update web interface with current state"""
        if hasattr(self, 'web_enabled') and self.web_enabled and WEB_AVAILABLE:
            state = self.core.get_state()
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
        print("\nMediaPipe Hand Gestures:")
        if self.core.hand_tracker:
            print("  PALM (5)    : Light/day theme (hold 2s)")
            print("  FIST (0)    : Dark/night theme (hold 2s)")
            if self.web_mode:
                print("  >> Camera feed visible in browser only")
            else:
                print("  >> Camera window visible in VNC")
        else:
            print("  (MediaPipe not available)")
        
        if enable_web and WEB_AVAILABLE:
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            print(f"\nWeb Visualizer:")
            print(f"  http://{ip}:5000")
            print(f"  http://localhost:5000")
        
        print("\nPress Ctrl+C to quit")
        print("=" * 50 + "\n")
        
        # Start voice control
        self.core.voice.start(callback=lambda cmd: self._handle_voice(cmd))
        
        # Start web server if enabled
        if enable_web and WEB_AVAILABLE:
            self._start_web_server()
        
        self._run_hardware()
    
    def _start_web_server(self):
        """Start web server in background"""
        import webbrowser
        import socket
        
        web_server.set_audio_engine(self.core.audio)
        
        if self.core.hand_tracker:
            web_server.set_hand_tracker(self.core.hand_tracker)
            print("[Web] Camera streaming enabled")
        
        self._web_thread = threading.Thread(
            target=web_server.run_server,
            kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False},
            daemon=True
        )
        self._web_thread.start()
        print("[Web] Visualization server started")
        
        time.sleep(1)
        
        # Auto-open browser (skip if --no-browser)
        if '--no-browser' not in sys.argv:
            time.sleep(1)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                url = f"http://{local_ip}:5000"
            except:
                url = "http://localhost:5000"
            
            print(f"[Web] Opening browser: {url}")
            webbrowser.open(url)
        else:
            print("[Web] Browser auto-open disabled")
    
    def _handle_voice(self, command):
        """Handle voice command and update display"""
        result = self.core.handle_voice_command(command)
        if result:
            if result['action'] == 'play':
                self.display.show_message("> PLAY")
            elif result['action'] == 'pause':
                self.display.show_message("|| PAUSE")
            self._update_web_state()
    
    def _run_hardware(self):
        """Run main hardware loop"""
        last_display_update = time.time()
        last_web_update = time.time()
        display_update_interval = 0.5
        web_update_interval = 0.1
        
        print("\n[Main Loop] Starting...")
        
        try:
            while self.running:
                # APDS gestures
                gesture = self.core.apds.get_gesture()
                if gesture:
                    result = self.core.handle_apds_gesture(gesture)
                    if result:
                        if result['type'] == 'track_change':
                            track = result['track']
                            self.display.show_message(f"{result['action'].upper()} Track {track['id']}")
                        elif result['type'] == 'volume_change':
                            volume = int(result['volume'] * 100)
                            self.display.show_message(f"Volume: {volume}%")
                        self._update_web_state()
                
                # MPR121 touch
                action = self.core.mpr121.get_action()
                if action:
                    result = self.core.handle_mpr121_touch(action)
                    if result:
                        if result['type'] == 'track_select':
                            track = result['track']
                            if track:
                                self.display.show_message(f"Track {track['id']}")
                        elif result['type'] == 'playback':
                            if result['action'] == 'play':
                                self.display.show_message("> PLAY")
                            elif result['action'] == 'pause':
                                self.display.show_message("|| PAUSE")
                            elif result['action'] == 'stop':
                                self.display.show_message("[] STOP")
                        self._update_web_state()
                
                # MediaPipe hand tracking
                if self.core.hand_tracker:
                    hand_data = self.core.hand_tracker.get_data()
                    if hand_data:
                        result = self.core.handle_hand_gesture(hand_data)
                        if result and result['type'] == 'mood_change':
                            mood = result['mood']
                            self.display.show_message(f"{mood['name'].upper()} THEME")
                            self._update_web_state()
                
                # Update OLED display
                if time.time() - last_display_update > display_update_interval:
                    state = self.core.get_state()
                    self.display.update_dj_display(state)
                    last_display_update = time.time()
                
                # Update web
                if self.web_enabled and WEB_AVAILABLE:
                    if time.time() - last_web_update > web_update_interval:
                        self._update_web_state()
                        last_web_update = time.time()
                
                time.sleep(0.02)
        
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        self.running = False
        
        self.core.cleanup()
        
        if hasattr(self.display, 'cleanup'):
            self.display.cleanup()
        
        print("Goodbye!")


def main():
    """Main entry point"""
    enable_web = '--web' in sys.argv
    
    print("Starting Gesture DJ with HARDWARE")
    if enable_web:
        if WEB_AVAILABLE:
            print("Web visualization ENABLED (camera streams to browser)")
        else:
            print("Warning: Web server not available")
            enable_web = False
    
    # Create and run
    dj = GestureDJ(web_mode=enable_web)
    
    # Handle Ctrl+C
    def signal_handler(sig, frame):
        print("\nInterrupt received... Exiting.")
        dj.running = False
        dj.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start
    dj.run(enable_web=enable_web)


if __name__ == "__main__":
    main()
