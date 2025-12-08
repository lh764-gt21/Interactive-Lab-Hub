#!/usr/bin/env python3
"""
Demo script for MediaPipe Mood Lighting System
Test gesture detection and mood changes without full DJ system
"""

import time
import sys
from hand_tracker import HandTracker, MEDIAPIPE_AVAILABLE
from mood_lighting import MoodLighting
from display import Display

def print_banner():
    """Print demo banner"""
    print("\n" + "=" * 60)
    print("  MEDIAPIPE MOOD LIGHTING DEMO")
    print("=" * 60)
    print("\nThis demo tests hand gesture detection and mood changes")
    print("without running the full DJ system.\n")

def print_instructions():
    """Print gesture instructions"""
    print("\n" + "-" * 60)
    print("HAND GESTURES:")
    print("-" * 60)
    print("  OPEN PALM (5 fingers)  -> Light theme (day)")
    print("  CLOSED FIST (0 fingers) -> Dark theme (night)")
    print("")
    print("MOUTH GESTURES:")
    print("  BLOW (open mouth wide) -> Activate bubbles")
    print("-" * 60)
    print("\nHold hand gestures for 2 seconds to confirm")
    print("Open mouth VERY wide to trigger blow detection")
    print("Press Ctrl+C to quit\n")

def run_demo():
    """Run the mood lighting demo"""
    print_banner()
    
    # Check if MediaPipe is available
    if not MEDIAPIPE_AVAILABLE:
        print("[!] MediaPipe not available!")
        print("Install with: pip install mediapipe opencv-python")
        print("\nRunning in SIMULATION mode (no camera required)")
        print("Press number keys 0-5 to simulate gestures")
        simulation = True
    else:
        print("[OK] MediaPipe available - using camera")
        simulation = False
    
    print_instructions()
    
    # Initialize components
    print("Initializing components...")
    
    # Check if running over VNC/SSH (no real display)
    import os
    is_remote = not os.environ.get('DISPLAY') or os.environ.get('SSH_CONNECTION')
    
    if is_remote:
        print("[INFO] Remote session detected - running in headless mode")
        print("[INFO] Camera window will not be shown")
    
    hand_tracker = HandTracker(simulation_mode=simulation, headless=is_remote)
    mood_lighting = MoodLighting()
    display = Display(simulation_mode=True)  # Console mode for demo
    
    print("[OK] Ready!\n")
    
    if not is_remote:
        print("[INFO] Look for the 'Hand Tracking' window to see camera feed")
    else:
        print("[INFO] Watch console output for gesture detection")
    
    # Demo loop
    try:
        gesture_count = 0
        last_mood = None
        
        while True:
            # Get hand data
            hand_data = hand_tracker.get_data()
            
            if hand_data and hand_data.get('gesture_confirmed'):
                pose = hand_data['pose']
                finger_count = hand_data['finger_count']
                
                print(f"\n[*] GESTURE DETECTED: {pose.upper()} ({finger_count} fingers)")
                gesture_count += 1
                
                # Handle palm and fist gestures only
                if pose in ['palm', 'fist']:
                    mood_changed = mood_lighting.set_mood_from_gesture(pose)
                    
                    if mood_changed:
                        mood = mood_lighting.get_current_mood()
                        # No emojis in console output (encoding issues)
                        print(f"   [*] Theme changed to: {mood['name']}")
                        print(f"   [*] Primary color: {mood['primary']}")
                        print(f"   [*] Gradient: {mood['gradient']}")
                        print(f"   [*] Description: {mood.get('description', '')}")
                        
                        # NO emoji in display message - ASCII only
                        display.show_message(f"{mood['name'].upper()} THEME")
                        
                        last_mood = mood['name']
                
                print(f"   [*] Total gestures: {gesture_count}")
                
                time.sleep(0.5)
            
            # Show current state periodically
            if simulation:
                time.sleep(0.1)
            else:
                time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("DEMO SUMMARY")
        print("=" * 60)
        print(f"Total gestures detected: {gesture_count}")
        # No emoji in console output
        print(f"Final theme: {mood_lighting.get_mood_name()}")
        print(f"Bubbles active: {mood_lighting.bubbles_active}")
        print("\nDemo completed successfully!")
        print("=" * 60 + "\n")
    
    finally:
        # Cleanup
        if hasattr(hand_tracker, 'cleanup'):
            hand_tracker.cleanup()

if __name__ == "__main__":
    run_demo()

