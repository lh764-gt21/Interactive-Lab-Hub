"""
Mood Lighting System
Controls visual themes and color schemes for web UI and display
Owner: Eva Huang (lh764)
"""

import time
from typing import Dict, Tuple


class MoodLighting:
    """Manages mood/theme state based on gestures"""
    
    # Simplified mood definitions - Light and Dark themes only
    MOODS = {
        'light': {
            'name': 'Light',
            # Baby blue gradient for light mode
            'gradient': ['#a8d8ea', '#c7e9f5', '#e3f4f9'],
            
            # Vibrant blue primary accent
            'primary': '#2196F3',
            
            # Warm orange secondary accent
            'secondary': '#FF9800',
            
            # Text colors
            'text': '#212529',              # Dark charcoal for main text
            'text_secondary': '#6c757d',    # Medium gray for secondary
            
            # UI elements
            'border': '#7fb3d5',            # Soft blue borders
            'panel_bg': 'rgba(255, 255, 255, 0.85)',  # Semi-transparent white
            'glow': 'rgba(33, 150, 243, 0.4)',
            
            'description': 'Clean daylight theme',
            'emoji': ''  # Emoji removed for console safety
        },
        'dark': {
            'name': 'Dark',
            # True black to dark navy gradient
            'gradient': ['#000000', '#0a0a1f', '#0f1419'],
            
            # Neon pink primary accent
            'primary': '#ff0080',
            
            # Electric cyan secondary accent
            'secondary': '#00ffff',
            
            # Text colors
            'text': '#ffffff',              # Pure white for main text
            'text_secondary': '#e0e0e0',    # Light gray for secondary
            
            # UI elements
            'border': '#1a1f2e',            # Dark blue borders
            'panel_bg': 'rgba(10, 10, 20, 0.7)',
            'glow': 'rgba(255, 0, 128, 0.5)',
            
            'description': 'Cyberpunk midnight theme',
            'emoji': ''  # Emoji removed for console safety
        }
    }
    
    # Gesture to mood mapping - simplified
    GESTURE_MOOD_MAP = {
        'palm': 'light',      # Open palm (5 fingers)
        'fist': 'dark',       # Closed fist (0 fingers)
    }
    
    def __init__(self):
        """Initialize mood lighting system"""
        self.current_mood = 'dark'  # Start with dark theme
        self.previous_mood = None
        self.mood_changed_time = time.time()
        self.bubbles_active = False  # Activated by mouth blow
        
    def set_mood_from_gesture(self, gesture: str) -> bool:
        """
        Set mood based on gesture
        Returns: True if mood changed, False otherwise
        """
        if gesture in self.GESTURE_MOOD_MAP:
            new_mood = self.GESTURE_MOOD_MAP[gesture]
            if new_mood != self.current_mood:
                self.previous_mood = self.current_mood
                self.current_mood = new_mood
                self.mood_changed_time = time.time()
                print(f"[MoodLighting] Changed to '{new_mood}' mood via {gesture} gesture")
                return True
        
        return False
    
    def activate_bubbles(self, duration=5.0):
        """Activate bubble effect (triggered by mouth blow)"""
        self.bubbles_active = True
        self.bubble_start_time = time.time()
        self.bubble_duration = duration
        print(f"[MoodLighting] Bubbles activated for {duration}s")
        return True
    
    def check_bubbles(self):
        """Check if bubbles should still be active"""
        if self.bubbles_active:
            elapsed = time.time() - self.bubble_start_time
            if elapsed >= self.bubble_duration:
                self.bubbles_active = False
        return self.bubbles_active
    
    def get_current_mood(self) -> Dict:
        """Get current mood configuration"""
        mood_config = self.MOODS[self.current_mood].copy()
        mood_config['mood_name'] = self.current_mood
        mood_config['bubbles_active'] = self.check_bubbles()
        mood_config['changed_time'] = self.mood_changed_time
        return mood_config
    
    def get_state(self) -> Dict:
        """Get complete state for web/display"""
        return {
            'mood': self.current_mood,
            'mood_config': self.get_current_mood(),
            'bubbles_active': self.check_bubbles(),
            'changed_time': self.mood_changed_time
        }
    
    def get_display_color(self) -> Tuple[int, int, int]:
        """
        Get RGB color for OLED display based on current mood
        Returns: (R, G, B) tuple
        """
        color_map = {
            'light': (74, 144, 226),    # Blue (daytime)
            'dark': (255, 0, 128)       # Pink (nighttime)
        }
        return color_map.get(self.current_mood, (255, 0, 128))
    
    def get_mood_emoji(self) -> str:
        """Get emoji representing current mood"""
        return self.MOODS[self.current_mood].get('emoji', '')
    
    def get_mood_name(self) -> str:
        """Get display name of current mood"""
        return self.MOODS[self.current_mood]['name']


if __name__ == "__main__":
    # Test mood lighting system
    print("Testing Simplified Mood Lighting System")
    print("=" * 50)
    
    lighting = MoodLighting()
    
    # Test gesture mappings
    test_gestures = ['palm', 'fist']
    
    for gesture in test_gestures:
        print(f"\nGesture: {gesture}")
        changed = lighting.set_mood_from_gesture(gesture)
        if changed:
            mood = lighting.get_current_mood()
            print(f"  Mood: {mood['name']} {mood.get('emoji', '')}")
            print(f"  Primary: {mood['primary']}")
            print(f"  Gradient: {mood['gradient']}")
            print(f"  Display RGB: {lighting.get_display_color()}")
    
    # Test bubbles activation
    print("\n" + "=" * 50)
    print("Testing bubbles activation (mouth blow):")
    lighting.activate_bubbles(duration=3.0)
    print(f"  Bubbles active: {lighting.check_bubbles()}")
    import time
    time.sleep(3.5)
    print(f"  After 3.5s, bubbles active: {lighting.check_bubbles()}")
    
    print("\n" + "=" * 50)
    print("Complete state:")
    import json
    print(json.dumps(lighting.get_state(), indent=2, default=str))

