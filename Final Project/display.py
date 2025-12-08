"""
Display Module
Handles PiTFT visual feedback with retro vaporwave aesthetic

Owner: Eva Huang (lh764), Zoe Tseng (yzt2), Charlotte Lin (hl2575)
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


# Retro color palette (vaporwave/Windows 95 style)
COLORS = {
    'pink_frame': (255, 182, 193),      # Light pink window frame
    'pink_dark': (219, 112, 147),       # Darker pink for borders
    'teal_bg': (127, 205, 205),         # Teal/turquoise background
    'teal_dark': (95, 158, 160),        # Darker teal for borders
    'navy': (25, 25, 60),               # Dark navy for progress bar
    'pink_progress': (219, 112, 147),   # Pink for remaining progress
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'text_dark': (40, 40, 80),          # Dark text
    'button_dark': (25, 25, 60),        # Button color
}


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
                    
                    self._load_fonts()
                    print("PiTFT display initialized (SPI)")
                    return
                except Exception as e:
                    print(f"Failed to initialize SPI display: {e}")
            
            # Last resort: simulation mode
            print("Falling back to console simulation mode")
            self.simulation_mode = True
        
        self._init_simulation()
    
    def _load_fonts(self):
        """Load fonts for display"""
        try:
            self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
            self.font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        except:
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font_tiny = ImageFont.load_default()
    
    def _init_simulation(self):
        """Initialize console simulation mode attributes."""
        self.width = 240
        self.height = 135
    
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
            width, height = 240, 135
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
            
            self._load_fonts()
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
    
    def _draw_retro_window(self):
        """Draw the retro window frame"""
        # Outer pink frame
        self.draw.rectangle((0, 0, self.width-1, self.height-1), 
                           fill=COLORS['pink_frame'])
        
        # Inner border (darker pink)
        self.draw.rectangle((3, 3, self.width-4, self.height-4), 
                           outline=COLORS['pink_dark'], width=2)
        
        # Window title bar area (top pink section)
        self.draw.rectangle((5, 5, self.width-6, 22), 
                           fill=COLORS['pink_frame'])
        
        # Window buttons (minimize, maximize, close) - right side
        btn_y = 8
        btn_size = 12
        btn_spacing = 16
        
        # Minimize button (-)
        btn_x = self.width - 55
        self.draw.rectangle((btn_x, btn_y, btn_x + btn_size, btn_y + btn_size), 
                           outline=COLORS['pink_dark'], fill=COLORS['pink_frame'], width=1)
        self.draw.line((btn_x + 2, btn_y + 6, btn_x + btn_size - 2, btn_y + 6), 
                      fill=COLORS['pink_dark'], width=1)
        
        # Maximize button (□)
        btn_x += btn_spacing
        self.draw.rectangle((btn_x, btn_y, btn_x + btn_size, btn_y + btn_size), 
                           outline=COLORS['pink_dark'], fill=COLORS['pink_frame'], width=1)
        self.draw.rectangle((btn_x + 2, btn_y + 2, btn_x + btn_size - 2, btn_y + btn_size - 2), 
                           outline=COLORS['pink_dark'], width=1)
        
        # Close button (X)
        btn_x += btn_spacing
        self.draw.rectangle((btn_x, btn_y, btn_x + btn_size, btn_y + btn_size), 
                           outline=COLORS['pink_dark'], fill=COLORS['pink_frame'], width=1)
        self.draw.line((btn_x + 2, btn_y + 2, btn_x + btn_size - 2, btn_y + btn_size - 2), 
                      fill=COLORS['pink_dark'], width=1)
        self.draw.line((btn_x + 2, btn_y + btn_size - 2, btn_x + btn_size - 2, btn_y + 2), 
                      fill=COLORS['pink_dark'], width=1)
        
        # Main content area (teal background)
        content_top = 25
        content_bottom = self.height - 35
        self.draw.rectangle((6, content_top, self.width-7, content_bottom), 
                           fill=COLORS['teal_bg'])
        self.draw.rectangle((6, content_top, self.width-7, content_bottom), 
                           outline=COLORS['teal_dark'], width=1)
        
        # Bottom control area (pink)
        self.draw.rectangle((5, content_bottom + 2, self.width-6, self.height-6), 
                           fill=COLORS['pink_frame'])
    
    def _draw_progress_bar_retro(self, x, y, width, height, progress):
        """Draw retro-style progress bar"""
        # Background (dark navy)
        self.draw.rectangle((x, y, x + width, y + height), 
                           fill=COLORS['navy'])
        
        # Progress fill
        fill_width = int(width * progress)
        if fill_width > 0:
            self.draw.rectangle((x, y, x + fill_width, y + height), 
                               fill=COLORS['navy'])
        
        # Remaining (pink)
        if fill_width < width:
            self.draw.rectangle((x + fill_width, y, x + width, y + height), 
                               fill=COLORS['pink_progress'])
        
        # Slider handle
        handle_x = x + fill_width - 3
        handle_x = max(x, min(handle_x, x + width - 6))
        self.draw.rectangle((handle_x, y - 2, handle_x + 6, y + height + 2), 
                           fill=COLORS['teal_bg'], outline=COLORS['teal_dark'])
    
    def _draw_play_button(self, x, y, size, filled=False):
        """Draw play triangle button"""
        points = [(x, y), (x, y + size), (x + size, y + size // 2)]
        if filled:
            self.draw.polygon(points, fill=COLORS['button_dark'])
        else:
            self.draw.polygon(points, outline=COLORS['button_dark'])
    
    def _draw_pause_button(self, x, y, size):
        """Draw pause button (two bars)"""
        bar_width = size // 4
        self.draw.rectangle((x, y, x + bar_width, y + size), fill=COLORS['button_dark'])
        self.draw.rectangle((x + size - bar_width, y, x + size, y + size), fill=COLORS['button_dark'])
    
    def _draw_next_button(self, x, y, size):
        """Draw next/skip button"""
        # Two triangles
        half = size // 2
        points1 = [(x, y), (x, y + size), (x + half, y + half)]
        points2 = [(x + half, y), (x + half, y + size), (x + size, y + half)]
        self.draw.polygon(points1, fill=COLORS['button_dark'])
        self.draw.polygon(points2, fill=COLORS['button_dark'])
    
    def _draw_volume_bars(self, x, y, level):
        """Draw volume indicator bars"""
        bar_width = 3
        bar_spacing = 5
        max_bars = 5
        active_bars = int(level / 100 * max_bars)
        
        for i in range(max_bars):
            bar_height = 8 + i * 3
            bar_y = y + 20 - bar_height
            color = COLORS['button_dark'] if i < active_bars else COLORS['pink_dark']
            self.draw.rectangle((x + i * bar_spacing, bar_y, 
                                x + i * bar_spacing + bar_width, y + 20), 
                               fill=color)
    
    def update_dj_display(self, state):
        """
        Update display with DJ state in retro style
        state: dict from audio_engine.get_state()
        """
        if self.simulation_mode:
            self._print_console_display(state)
            return
        
        # Draw retro window frame
        self._draw_retro_window()
        
        # Track info in content area
        content_top = 30
        
        # Track number and name
        track_text = f"TRACK {state['track_number']}/{state['track_total']}"
        self.draw.text((15, content_top), track_text, 
                      font=self.font_medium, fill=COLORS['text_dark'])
        
        track_name = state['track_name'][:18]
        self.draw.text((15, content_top + 18), track_name, 
                      font=self.font_small, fill=COLORS['text_dark'])
        
        # Status icon in center
        status_x = self.width // 2 - 10
        status_y = content_top + 35
        
        if state['is_playing'] and not state['is_paused']:
            # Show play icon or "playing" indicator
            self._draw_play_button(status_x, status_y, 20, filled=True)
        elif state['is_paused']:
            # Show pause icon
            self._draw_pause_button(status_x, status_y, 20)
        else:
            # Show stop (square)
            self.draw.rectangle((status_x, status_y, status_x + 20, status_y + 20), 
                               fill=COLORS['button_dark'])
        
        # Progress bar
        progress = state.get('progress', 0.5)
        bar_y = self.height - 33
        self._draw_progress_bar_retro(8, bar_y, self.width - 16, 8, progress)
        
        # Bottom controls area
        ctrl_y = self.height - 22
        
        # Play button
        self._draw_play_button(15, ctrl_y, 14, filled=True)
        
        # Pause button
        self._draw_pause_button(35, ctrl_y, 14)
        
        # Next button
        self._draw_next_button(55, ctrl_y, 14)
        
        # Volume bars on right
        self._draw_volume_bars(self.width - 35, ctrl_y - 5, state['volume'])
        
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
        filled = int(bar_length * state.get('progress', 0.5))
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
        print("=" * 50)
    
    def show_message(self, message, color=None):
        """Show a centered message on screen with retro style"""
        if self.simulation_mode:
            print(f"\n>>> {message} <<<\n")
            return
        
        # Draw retro window
        self._draw_retro_window()
        
        # Center the text in content area
        content_center_y = (25 + self.height - 35) // 2 + 10
        
        # Get text size for centering
        try:
            bbox = self.draw.textbbox((0, 0), message, font=self.font_large)
            text_width = bbox[2] - bbox[0]
        except:
            text_width = len(message) * 12
        
        x = (self.width - text_width) // 2
        
        # Use custom color if provided, otherwise use default
        text_color = color if color else COLORS['text_dark']
        
        self.draw.text((x, content_center_y), message, 
                      font=self.font_large, fill=text_color)
        
        if hasattr(self, "disp"):
            self.disp.image(self.image, self.rotation)
        elif self._framebuffer_path:
            self._fb_blit()
    
    def show_gesture_feedback(self, gesture_name, mood_color=None, emoji=""):
        """
        Show gesture feedback with mood color
        gesture_name: Name of the gesture (e.g., "ENERGETIC", "CHILL")
        mood_color: RGB tuple for the mood color
        emoji: Emoji to display
        """
        if self.simulation_mode:
            print(f"\n>>> {emoji} {gesture_name} <<<\n")
            return
        
        # Draw retro window
        self._draw_retro_window()
        
        # Content area center
        content_center_y = (25 + self.height - 35) // 2
        
        # Draw emoji if provided (larger)
        if emoji:
            try:
                emoji_bbox = self.draw.textbbox((0, 0), emoji, font=self.font_large)
                emoji_width = emoji_bbox[2] - emoji_bbox[0]
            except:
                emoji_width = 30
            
            emoji_x = (self.width - emoji_width) // 2
            self.draw.text((emoji_x, content_center_y - 15), emoji, 
                          font=self.font_large, fill=COLORS['text_dark'])
        
        # Draw gesture name below emoji
        try:
            text_bbox = self.draw.textbbox((0, 0), gesture_name, font=self.font_medium)
            text_width = text_bbox[2] - text_bbox[0]
        except:
            text_width = len(gesture_name) * 10
        
        text_x = (self.width - text_width) // 2
        text_y = content_center_y + 15
        
        # Use mood color if provided
        text_color = mood_color if mood_color else COLORS['text_dark']
        
        self.draw.text((text_x, text_y), gesture_name, 
                      font=self.font_medium, fill=text_color)
        
        # Add a colored indicator bar at the bottom of content area
        if mood_color:
            bar_y = self.height - 40
            bar_height = 4
            self.draw.rectangle((10, bar_y, self.width - 10, bar_y + bar_height), 
                               fill=mood_color)
        
        if hasattr(self, "disp"):
            self.disp.image(self.image, self.rotation)
        elif self._framebuffer_path:
            self._fb_blit()
    
    def cleanup(self):
        """Clean up display resources"""
        if not self.simulation_mode:
            self.clear(COLORS['pink_frame'])
            if hasattr(self, "disp"):
                self.disp.image(self.image, self.rotation)
            elif self._framebuffer_path:
                self._fb_blit()


if __name__ == "__main__":
    import sys
    
    # Test mode - check for --sim flag
    simulation = '--sim' in sys.argv or '--simulation' in sys.argv
    
    print("=" * 50)
    print("Retro Display Test")
    print("=" * 50)
    
    if simulation:
        print("Running in SIMULATION mode (console only)")
    else:
        print("Running in HARDWARE mode (trying PiTFT)")
    
    print()
    
    display = Display(simulation_mode=simulation)
    
    try:
        # Test 1: Welcome message
        print("\nTest 1: Welcome message (3 sec)")
        display.show_message("GESTURE DJ")
        time.sleep(3)
        
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
            "progress": 0.65
        }
        display.update_dj_display(test_state)
        time.sleep(3)
        
        # Test 3: DJ UI - Paused
        print("\nTest 3: DJ UI - PAUSED (3 sec)")
        test_state["is_paused"] = True
        test_state["track_number"] = 5
        test_state["track_name"] = "Summer Vibes"
        test_state["progress"] = 0.3
        display.update_dj_display(test_state)
        time.sleep(3)
        
        # Test 4: DJ UI - Stopped
        print("\nTest 4: DJ UI - STOPPED (3 sec)")
        test_state["is_playing"] = False
        test_state["is_paused"] = False
        test_state["progress"] = 0.0
        display.update_dj_display(test_state)
        time.sleep(3)
        
        # Test 5: Final message
        print("\nTest 5: Final message (2 sec)")
        display.show_message("READY!")
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted (Ctrl+C)")
    
    finally:
        display.cleanup()
        print("\nDisplay test complete!")
