"""
Voice Control Module
Uses Vosk for offline speech recognition to detect "play" and "pause" commands
Based on Lab 3 speech recognition examples

Owner: Zoe Tseng (yzt2), Charlotte Lin (hl2575)
"""

import os
import queue
import json
import threading
import time

# Try to import vosk and sounddevice
try:
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    print("vosk or sounddevice not available - voice control disabled")


class VoiceControl:
    def __init__(self):
        """
        Initialize voice control with microphone using Vosk
        Recognizes: "play", "pause"
        """
        self.available = VOSK_AVAILABLE
        self.running = False
        self.last_command = None
        self.command_callback = None
        self._thread = None
        self._audio_queue = queue.Queue()
        
        if self.available:
            try:
                # Check for vosk model in cache
                cache_model_path = os.path.expanduser("~/.cache/vosk/vosk-model-small-en-us-0.15")
                
                if os.path.exists(cache_model_path):
                    print("[Voice] Loading Vosk model from cache...")
                    self.model = Model(cache_model_path)
                else:
                    print("[Voice] Downloading Vosk model (first time only)...")
                    self.model = Model(lang="en-us")
                
                # Get default microphone sample rate
                device_info = sd.query_devices(kind="input")
                self.sample_rate = int(device_info["default_samplerate"])
                
                print(f"[Voice] Voice control initialized (sample rate: {self.sample_rate})")
            except Exception as e:
                print(f"[Voice] Failed to initialize: {e}")
                self.available = False
        else:
            print("[Voice] Running without voice control")
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio input stream"""
        if status:
            print(f"[Voice] Audio status: {status}")
        self._audio_queue.put(bytes(indata))
    
    def _listen_loop(self):
        """Background thread for continuous listening"""
        recognizer = KaldiRecognizer(self.model, self.sample_rate)
        
        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=self._audio_callback
            ):
                print("[Voice] Listening for 'play' and 'pause'...")
                
                while self.running:
                    try:
                        data = self._audio_queue.get(timeout=0.5)
                    except queue.Empty:
                        continue
                    
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").lower().strip()
                        
                        if text:
                            print(f"[Voice] Heard: '{text}'")
                            command = self._parse_command(text)
                            if command:
                                self.last_command = command
                                print(f"[Voice] Command: {command}")
                                if self.command_callback:
                                    self.command_callback(command)
        
        except Exception as e:
            print(f"[Voice] Error in listen loop: {e}")
    
    def _parse_command(self, text):
        """Parse text for voice commands (play and pause only)"""
        text = text.lower().strip()
        
        # Play commands
        if any(word in text for word in ['play', 'start', 'go', 'resume']):
            return 'play'
        
        # Pause commands
        if any(word in text for word in ['pause', 'stop', 'wait', 'hold']):
            return 'pause'
        
        return None
    
    def start(self, callback=None):
        """Start listening for voice commands in background"""
        if not self.available:
            print("[Voice] Voice control not available")
            return False
        
        if self.running:
            return True
        
        self.command_callback = callback
        self.running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        return True
    
    def stop(self):
        """Stop listening for voice commands"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
        print("[Voice] Stopped listening")
    
    def get_command(self):
        """Get the last recognized command and clear it"""
        cmd = self.last_command
        self.last_command = None
        return cmd


if __name__ == "__main__":
    print("Voice Control Test (Vosk)")
    print("=" * 40)
    print("Say: 'play' or 'pause'")
    print("Press Ctrl+C to quit")
    print()
    
    def on_command(cmd):
        print(f">>> Command received: {cmd}")
    
    voice = VoiceControl()
    
    if not voice.available:
        print("Voice control not available")
        print("Install with: pip install vosk sounddevice")
        exit(1)
    
    voice.start(callback=on_command)
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
        voice.stop()
