"""
Audio Engine Module
Handles audio playback, track management, volume control, and effects
Owner: Eva Huang (lh764)
"""

import pygame
import time
import random
from pathlib import Path

class AudioEngine:
    def __init__(self, tracks_dir="tracks", effects_dir="effects"):
        """Initialize the audio engine with pygame mixer"""
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        self.tracks_dir = Path(tracks_dir)
        self.effects_dir = Path(effects_dir)
        
        # Track management
        self.tracks = self._load_tracks()
        self.current_track_index = 0
        self.is_playing = False
        self.is_paused = False
        
        # Audio state
        self.volume = 0.75  # 75% default
        self.playback_speed = 1.0  # Normal speed
        self.current_speed_preset = 1.0  # Current active preset
        self.bass_boost = False
        self.reverb = False
        
        # Speed presets (discrete levels for playback)
        self.speed_presets = [0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        
        # Scratch state
        self.scratching = False
        self.pause_position = 0  # Store position when scratching starts
        self.was_playing_before_scratch = False
        
        # Effect sounds
        self.effects = self._load_effects()
        
        print(f"Audio Engine initialized with {len(self.tracks)} tracks")
    
    def _load_tracks(self):
        """Load all track metadata"""
        tracks = []
        for i in range(1, 11):  # 10 tracks
            track = {
                "id": i,
                "name": f"Track {i}",
                "file": self.tracks_dir / f"track{i:02d}.mp3",
                "bpm": 120,  # Default, can be customized
            }
            tracks.append(track)
        return tracks
    
    def _load_effects(self):
        """Load sound effects for feedback"""
        effects = {}
        effect_files = {
            "beep": "beep.mp3",      # Track change
            "click": "click.mp3",    # Volume change
            "swoosh": "swoosh.mp3",  # Theme change
        }
        
        for name, filename in effect_files.items():
            filepath = self.effects_dir / filename
            if filepath.exists():
                effects[name] = pygame.mixer.Sound(str(filepath))
            else:
                print(f"Warning: Effect file not found: {filepath}")
                effects[name] = None
        
        # Load scratch sounds
        scratch_sounds = []
        for i in range(1, 5):  # scratch1.mp3 through scratch4.mp3
            scratch_file = self.effects_dir / f"scratch{i}.mp3"
            if scratch_file.exists():
                scratch_sounds.append(pygame.mixer.Sound(str(scratch_file)))
            else:
                print(f"Warning: Scratch file not found: {scratch_file}")
        
        if scratch_sounds:
            effects['scratch_sounds'] = scratch_sounds
            print(f"Loaded {len(scratch_sounds)} scratch sounds")
        
        return effects
    
    def get_current_track(self):
        """Get current track information"""
        return self.tracks[self.current_track_index]
    
    def next_track(self):
        """Move to next track (wraps around)"""
        self.current_track_index = (self.current_track_index + 1) % len(self.tracks)
        self.load_track()
        self.play_effect("beep")
        return self.get_current_track()
    
    def prev_track(self):
        """Move to previous track (wraps around)"""
        self.current_track_index = (self.current_track_index - 1) % len(self.tracks)
        self.load_track()
        self.play_effect("beep")
        return self.get_current_track()
    
    def select_track(self, track_number):
        """Jump to specific track by number (1-10)"""
        if 1 <= track_number <= len(self.tracks):
            self.current_track_index = track_number - 1
            self.load_track()
            self.play_effect("beep")
            return self.get_current_track()
        return None
    
    def load_track(self):
        """Load the current track into pygame mixer"""
        track = self.get_current_track()
        if track["file"].exists():
            pygame.mixer.music.load(str(track["file"]))
            pygame.mixer.music.set_volume(self.volume)
            print(f"Loaded: {track['name']}")
        else:
            print(f"Warning: Track file not found: {track['file']}")
    
    def play(self):
        """Start playing from beginning"""
        if not self.is_playing:
            # Ensure mixer is at correct speed before playing
            self._ensure_correct_frequency()
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            print("Playing")
    
    def _ensure_correct_frequency(self):
        """Ensure mixer is initialized at the correct frequency for current speed"""
        base_freq = 44100
        target_freq = int(base_freq * self.current_speed_preset)
        
        # Reinitialize if frequency doesn't match
        pygame.mixer.quit()
        pygame.mixer.init(frequency=target_freq, size=-16, channels=2, buffer=512)
        
        # Reload current track
        track = self.get_current_track()
        if track["file"].exists():
            pygame.mixer.music.load(str(track["file"]))
            pygame.mixer.music.set_volume(self.volume)
    
    def pause(self):
        """Pause playback"""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            print("Paused")
    
    def resume(self):
        """Resume from pause"""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            print("Resumed")
    
    def stop(self):
        """Stop playback"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        print("Stopped")
    
    def volume_up(self, amount=0.1):
        """Increase volume by amount (default 10%)"""
        self.volume = min(1.0, self.volume + amount)
        pygame.mixer.music.set_volume(self.volume)
        self.play_effect("click")
        print(f"Volume: {int(self.volume * 100)}%")
        return self.volume
    
    def volume_down(self, amount=0.1):
        """Decrease volume by amount (default 10%)"""
        self.volume = max(0.0, self.volume - amount)
        pygame.mixer.music.set_volume(self.volume)
        self.play_effect("click")
        print(f"Volume: {int(self.volume * 100)}%")
        return self.volume
    
    def set_tempo(self, speed):
        """
        Adjust playback speed using discrete presets
        speed: 0.5 to 3.5 (input from finger distance)
        Maps to nearest preset and adjusts speed without restarting
        """
        self.playback_speed = max(0.5, min(3.5, speed))
        
        # Find nearest preset
        nearest_preset = min(self.speed_presets, key=lambda x: abs(x - speed))
        
        # Only change if preset changed significantly
        if abs(nearest_preset - self.current_speed_preset) > 0.2:
            old_preset = self.current_speed_preset
            self.current_speed_preset = nearest_preset
            
            # If currently playing, adjust speed smoothly
            if self.is_playing and not self.is_paused:
                self._adjust_playback_speed(nearest_preset)
                print(f"Speed: {old_preset:.1f}x -> {nearest_preset}x")
        
        return self.playback_speed
    
    def _adjust_playback_speed(self, speed):
        """
        Adjust playback speed without restarting
        Uses pygame mixer frequency adjustment
        """
        # Calculate frequency multiplier (higher freq = faster playback)
        base_freq = 44100
        new_freq = int(base_freq * speed)
        
        # Save current state
        was_paused = self.is_paused
        current_volume = self.volume
        
        # Reinitialize mixer with new frequency (this is unavoidable with pygame)
        pygame.mixer.quit()
        pygame.mixer.init(frequency=new_freq, size=-16, channels=2, buffer=512)
        
        # Reload and immediately play (continuation feels smoother than saving position)
        track = self.get_current_track()
        if track["file"].exists():
            pygame.mixer.music.load(str(track["file"]))
            pygame.mixer.music.set_volume(current_volume)
            
            # Continue playback immediately (no start position - plays from current mixer buffer)
            pygame.mixer.music.play()
            
            if was_paused:
                pygame.mixer.music.pause()
                self.is_paused = True
            else:
                self.is_paused = False
            
            self.is_playing = True
    
    def toggle_bass_boost(self):
        """Toggle bass boost effect"""
        self.bass_boost = not self.bass_boost
        self.play_effect("whoosh")
        print(f"Bass Boost: {'ON' if self.bass_boost else 'OFF'}")
        # TODO: Implement actual bass boost (may need audio processing)
        return self.bass_boost
    
    def toggle_reverb(self):
        """Toggle reverb effect (placeholder)"""
        self.reverb = not self.reverb
        self.play_effect("whoosh")
        print(f"Reverb: {'ON' if self.reverb else 'OFF'}")
        # TODO: Implement actual reverb if needed
        return self.reverb
    
    def play_effect(self, effect_name):
        """Play a sound effect"""
        if effect_name in self.effects and self.effects[effect_name]:
            self.effects[effect_name].play()
    
    def play_scratch_effect(self):
        """
        Play DJ scratch effect - overlays on top of music without pausing
        Plays a random scratch sound simultaneously with the music
        """
        scratch_sounds = self.effects.get('scratch_sounds', [])
        if not scratch_sounds:
            print("[Scratch] No scratch sounds available")
            return
        
        # Play random scratch sound over the music
        scratch_sound = random.choice(scratch_sounds)
        scratch_sound.set_volume(self.volume * 1.0)  # Full volume for punch
        
        scratch_index = scratch_sounds.index(scratch_sound) + 1
        print(f"[Scratch] Playing scratch{scratch_index}.mp3 (overlay)")
        
        scratch_sound.play()  # Plays on a separate channel, doesn't interrupt music
    
    
    def get_playback_position(self):
        """Get current playback position in seconds"""
        if self.is_playing:
            return pygame.mixer.music.get_pos() / 1000.0  # Convert ms to seconds
        return 0.0
    
    def get_track_duration(self):
        """Get approximate track duration (placeholder - would need mutagen or similar)"""
        # TODO: Use mutagen library to read actual MP3 duration
        # For now, return a placeholder or use a lookup table
        return 180.0  # Assume 3 minute tracks for now
    
    def get_progress(self):
        """Get playback progress as 0.0-1.0"""
        if not self.is_playing:
            return 0.0
        position = self.get_playback_position()
        duration = self.get_track_duration()
        if duration > 0:
            return min(1.0, max(0.0, position / duration))
        return 0.0
    
    def get_state(self):
        """Get complete audio engine state for display"""
        track = self.get_current_track()
        return {
            "track_number": self.current_track_index + 1,
            "track_total": len(self.tracks),
            "track_name": track["name"],
            "volume": int(self.volume * 100),
            "is_playing": self.is_playing,
            "is_paused": self.is_paused,
            "tempo": self.current_speed_preset,  # Show actual active preset, not raw value
            "bass_boost": self.bass_boost,
            "reverb": self.reverb,
            "position": self.get_playback_position(),
            "progress": self.get_progress()
        }


if __name__ == "__main__":
    # Test mode with keyboard simulation
    print("Audio Engine Test Mode")
    print("=" * 40)
    
    engine = AudioEngine()
    engine.load_track()
    
    print("\nKeyboard Controls:")
    print("Space: Play/Pause")
    print("Left/Right Arrow: Previous/Next track")
    print("Up/Down Arrow: Volume up/down")
    print("1-9,0: Select track directly")
    print("B: Toggle bass boost")
    print("Q: Quit")
    print()
    
    # Simple keyboard test loop
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
            state = engine.get_state()
            print(f"\r[{state['track_number']}/{state['track_total']}] {state['track_name']} | "
                  f"Vol: {state['volume']}% | "
                  f"{'Playing' if state['is_playing'] else 'Stopped'} | "
                  f"Bass: {'ON' if state['bass_boost'] else 'OFF'}", end="", flush=True)
            
            key = get_key()
            
            if key == ' ':
                if engine.is_paused:
                    engine.resume()
                elif engine.is_playing:
                    engine.pause()
                else:
                    engine.play()
            elif key == '\x1b':  # Arrow keys
                next_key = get_key()
                if next_key == '[':
                    arrow = get_key()
                    if arrow == 'C':  # Right arrow
                        engine.next_track()
                    elif arrow == 'D':  # Left arrow
                        engine.prev_track()
                    elif arrow == 'A':  # Up arrow
                        engine.volume_up()
                    elif arrow == 'B':  # Down arrow
                        engine.volume_down()
            elif key.isdigit():
                track_num = int(key) if key != '0' else 10
                engine.select_track(track_num)
            elif key.lower() == 'b':
                engine.toggle_bass_boost()
            elif key.lower() == 'q':
                print("\nQuitting...")
                break
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nStopped")
    
    pygame.quit()