"""
Display Module
Handles PiTFT visual feedback
Owner:
"""

import os
import time
from typing import Optional
import sys

# Try to import display library
try:
    from PIL import Image, ImageDraw, ImageFont
    import digitalio
    import board
    from adafruit_rgb_display import st7789
    DISPLAY_AVAILABLE = True
except ImportError:
    DISPLAY_AVAILABLE = False
    try:
        # PIL may still be available; import for framebuffer mode
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
    except Exception:
        pass
    print("Display libraries not available - running in simulation mode")


class Display:
    def __init__(self, simulation_mode=False, prefer_framebuffer=True):
        """
        Initialize PiTFT display
        simulation_mode: If True, print to console instead
        prefer_framebuffer: If True, use framebuffer instead of SPI (avoids GPIO conflicts)
        """
        self.simulation_mode = simulation_mode
        self._framebuffer_path: Optional[str] = None
        
        if not self.simulation_mode:
            # Try framebuffer first (works with piscreen.service)
            if prefer_framebuffer and self._init_framebuffer():
                return
            
            # Fall back to Adafruit SPI
            if DISPLAY_AVAILABLE:
                try:
                    # Configuration for CS and DC pins (match screen_boot_script.py)
                    cs_pin = digitalio.DigitalInOut(board.D5)
                    dc_pin = digitalio.DigitalInOut(board.D25)
                    reset_pin = None  # No reset pin on this hardware
                    
                    # Config for display baudrate:
                    BAUDRATE = 64000000
                    
                    # Setup SPI bus using hardware SPI:
                    spi = board.SPI()
                    
                    # Create the display (135x240 mini PiTFT)
                    self.disp = st7789.ST7789(
                        spi,
                        width=135,
                        height=240,
                        x_offset=53,
                        y_offset=40,
                        cs=cs_pin,
                        dc=dc_pin,
                        rst=reset_pin,
                        baudrate=BAUDRATE,
                    )
                    self.rotation = 90  # Landscape orientation
                    
                    # Create blank image for drawing (swap for landscape)
                    self.width = self.disp.height  # 240 wide in landscape
                    self.height = self.disp.width  # 135 tall in landscape
                    self.image = Image.new("RGB", (self.width, self.height))
                    self.draw = ImageDraw.Draw(self.image)
                    
                    # Load fonts
                    try:
                        self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                        self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
                        self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                    except:
                        self.font_large = ImageFont.load_default()
                        self.font_medium = ImageFont.load_default()
                        self.font_small = ImageFont.load_default()
                    
                    print("PiTFT display initialized (SPI)")
                    return
                except Exception as e:
                    print(f"Failed to initialize SPI display: {e}")
            
            # Last resort: simulation mode
            print("Falling back to console simulation mode")
            self.simulation_mode = True
        
        self._init_simulation()
    
    def _init_simulation(self):
        """Initialize console simulation mode attributes."""
        self.width = 240
        self.height = 240
    
    def _init_framebuffer(self) -> bool:
        """Initialize direct framebuffer drawing if available."""
        try:
            fb_candidates = ["/dev/fb1", "/dev/fb0"]
            fb = next((p for p in fb_candidates if os.path.exists(p)), None)
            if not fb:
                return False
            
            # Read resolution from sysfs if available
            fb_name = os.path.basename(fb)
            sys_base = f"/sys/class/graphics/{fb_name}"
            width, height = 240, 240
            try:
                with open(os.path.join(sys_base, "virtual_size"), "r") as f:
                    parts = f.read().strip().split(",")
                    if len(parts) == 2:
                        width, height = int(parts[0]), int(parts[1])
            except Exception:
                pass
            
            # Create drawing surface at framebuffer resolution
            self._framebuffer_path = fb
            self.width = width
            self.height = height
            self.image = Image.new("RGB", (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
            
            # Load fonts
            try:
                self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
                self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except Exception:
                self.font_large = ImageFont.load_default()
                self.font_medium = ImageFont.load_default()
                self.font_small = ImageFont.load_default()
            
            print(f"Framebuffer display initialized on {fb} ({self.width}x{self.height})")
            return True
        except Exception as e:
            print(f"Failed to initialize framebuffer display: {e}")
            return False
    
    def _fb_blit(self):
        """Blit current image to framebuffer as RGB565."""
        if not self._framebuffer_path:
            return
        try:
            frame = self.image.convert("RGB")
            data = frame.tobytes("raw", "BGR;16")
            with open(self._framebuffer_path, "wb") as f:
                f.write(data)
        except Exception as e:
            print(f"Framebuffer blit failed: {e}")
    
    def clear(self, color=(0, 0, 0)):
        """Clear the display with a color"""
        if self.simulation_mode:
            return
        
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=color)
    
    def draw_text(self, text, x, y, font=None, color=(255, 255, 255)):
        """Draw text at position"""
        if self.simulation_mode:
            return
        
        if font is None:
            font = self.font_medium
        
        self.draw.text((x, y), text, font=font, fill=color)
    
    def draw_progress_bar(self, x, y, width, height, progress, 
                         bg_color=(50, 50, 50), fg_color=(0, 255, 0)):
        """
        Draw a progress bar
        progress: 0.0 to 1.0
        """
        if self.simulation_mode:
            return
        
        # Draw background
        self.draw.rectangle((x, y, x + width, y + height), 
                          outline=fg_color, fill=bg_color)
        
        # Draw progress
        fill_width = int(width * progress)
        if fill_width > 0:
            self.draw.rectangle((x, y, x + fill_width, y + height), 
                              outline=0, fill=fg_color)
    
    def update_dj_display(self, state):
        """
        Update display with DJ state
        state: dict from audio_engine.get_state()
        """
        if self.simulation_mode:
            self._print_console_display(state)
            return
        
        # Clear screen
        self.clear((0, 0, 0))
        
        # Track info (compact for 240x135 landscape display)
        track_text = f"TRK {state['track_number']}/{state['track_total']}"
        self.draw_text(track_text, 5, 5, self.font_medium, (255, 255, 255))
        
        track_name = state['track_name'][:15]  # Truncate long names
        self.draw_text(track_name, 5, 30, self.font_small, (200, 200, 255))
        
        # Progress bar (real-time from audio engine)
        progress = state.get('progress', 0.0)
        self.draw_progress_bar(5, 50, 230, 10, progress)
        
        # Playback state
        if state['is_playing'] and not state['is_paused']:
            status = ">PLAY"
            status_color = (0, 255, 0)
        elif state['is_paused']:
            status = "||PAUSE"
            status_color = (255, 255, 0)
        else:
            status = "[]STOP"
            status_color = (255, 0, 0)
        
        self.draw_text(status, 5, 70, self.font_small, status_color)
        
        # Volume and Speed on same line (compact)
        volume_text = f"Vol:{state['volume']}%"
        self.draw_text(volume_text, 5, 90, self.font_small, (255, 200, 0))
        
        # Playback Speed (color coded) - right side
        tempo_text = f"Spd:{state['tempo']:.1f}x"
        if state['tempo'] < 1.0:
            tempo_color = (0, 255, 0)  # Green for slow
        elif state['tempo'] == 1.0:
            tempo_color = (255, 255, 255)  # White for normal
        elif state['tempo'] < 2.0:
            tempo_color = (255, 255, 0)  # Yellow for fast
        else:
            tempo_color = (255, 100, 0)  # Orange/red for very fast
        self.draw_text(tempo_text, 120, 90, self.font_small, tempo_color)
        
        # Effects on bottom line
        if state['bass_boost']:
            self.draw_text("[BASS]", 5, 110, self.font_small, (255, 100, 255))
        if state.get('reverb'):
            self.draw_text("[REVERB]", 90, 110, self.font_small, (100, 255, 255))
        
        # Display the image
        if hasattr(self, "disp"):
            self.disp.image(self.image, self.rotation)
        elif self._framebuffer_path:
            self._fb_blit()
    
    def _print_console_display(self, state):
        """Print display state to console for simulation"""
        print("\n" + "=" * 50)
        print(f"  TRACK {state['track_number']}/{state['track_total']}")
        print(f"  {state['track_name']}")
        
        # Progress bar - use ASCII only
        bar_length = 40
        filled = int(bar_length * 0.5)  # Placeholder
        bar = "#" * filled + "-" * (bar_length - filled)
        print(f"  [{bar}]")
        
        print(f"  Volume: {state['volume']}%")
        
        # Status
        if state['is_playing'] and not state['is_paused']:
            print("  > PLAYING")
        elif state['is_paused']:
            print("  || PAUSED")
        else:
            print("  [] STOPPED")
        
        # Playback Speed
        print(f"  Speed: {state['tempo']:.1f}x")
        
        # Effects
        effects = []
        if state['bass_boost']:
            effects.append("BASS")
        if state.get('reverb'):
            effects.append("REVERB")
        
        if effects:
            print(f"  Effects: {', '.join(effects)}")
        
        print("=" * 50)
    
    def show_message(self, message, color=(255, 255, 255)):
        """Show a centered message on screen"""
        if self.simulation_mode:
            print(f"\n>>> {message} <<<\n")
            return
        
        self.clear((0, 0, 0))
        
        # Center the text (approximate)
        text_width = len(message) * 12  # Rough estimate
        x = (self.width - text_width) // 2
        y = self.height // 2 - 20
        
        self.draw_text(message, x, y, self.font_large, color)
        if hasattr(self, "disp"):
            self.disp.image(self.image, self.rotation)
        elif self._framebuffer_path:
            self._fb_blit()
    
    def cleanup(self):
        """Clean up display resources"""
        if not self.simulation_mode:
            self.clear((0, 0, 0))
            if hasattr(self, "disp"):
                self.disp.image(self.image, self.rotation)
            elif self._framebuffer_path:
                self._fb_blit()


if __name__ == "__main__":
    import sys
    
    # Test mode - check for --sim flag
    simulation = '--sim' in sys.argv or '--simulation' in sys.argv
    
    print("=" * 50)
    print("Mini PiTFT Display Test (135x240)")
    print("=" * 50)
    
    if simulation:
        print("Running in SIMULATION mode (console only)")
    else:
        print("Running in HARDWARE mode (trying PiTFT)")
        print("Note: Stop piscreen.service first!")
    
    print()
    
    display = Display(simulation_mode=simulation)
    
    if not display.simulation_mode:
        print("[OK] Display initialized successfully!")
        print(f"    Size: {display.width}x{display.height}")
        if hasattr(display, 'rotation'):
            print(f"    Rotation: {display.rotation} degrees")
    else:
        print("[INFO] Running in simulation mode")
    
    try:
        # Test 1: Color splash
        print("\nTest 1: Color splash messages (6 sec)")
        display.show_message("GESTURE DJ", color=(0, 255, 0))
        time.sleep(2)
        display.show_message("HELLO!", color=(255, 0, 255))
        time.sleep(2)
        display.show_message("READY", color=(0, 255, 255))
        time.sleep(2)
        
        # Test 2: DJ UI - Playing
        print("\nTest 2: DJ UI - PLAYING (3 sec)")
        test_state = {
            "track_number": 1,
            "track_total": 10,
            "track_name": "Track 01",
            "volume": 75,
            "is_playing": True,
            "is_paused": False,
            "tempo": 1.0,
            "bass_boost": False,
            "reverb": False,
            "position": 0.0
        }
        display.update_dj_display(test_state)
        time.sleep(3)
        
        # Test 3: DJ UI - Paused with effects
        print("\nTest 3: DJ UI - PAUSED + EFFECTS (3 sec)")
        test_state["track_number"] = 5
        test_state["track_name"] = "Track 05"
        test_state["is_paused"] = True
        test_state["bass_boost"] = True
        test_state["reverb"] = True
        test_state["volume"] = 90
        display.update_dj_display(test_state)
        time.sleep(3)
        
        # Test 4: DJ UI - Stopped
        print("\nTest 4: DJ UI - STOPPED (3 sec)")
        test_state["is_playing"] = False
        test_state["is_paused"] = False
        test_state["bass_boost"] = False
        test_state["reverb"] = False
        display.update_dj_display(test_state)
        time.sleep(3)
        
        # Test 5: Final message
        print("\nTest 5: Final success message (2 sec)")
        display.show_message("TEST OK!", color=(0, 255, 0))
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user (Ctrl+C)")
    
    finally:
        display.cleanup()
        print("\n" + "=" * 50)
        print("Display test complete!")
        print("=" * 50)