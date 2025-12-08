"""
Gesture DJ Demo - Web Interface + Core Logic
Uses gesture_dj_core.py for all business logic

Owner: Eva Huang (lh764), Zoe Tseng (yzt2), Charlotte Lin (hl2575)

"""

from flask import Flask, Response, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO
import threading
import time
import random
import math
from gesture_dj_core import GestureDJCore
from display import Display
import cv2

# Use the web folder for templates
app = Flask(__name__, template_folder='web', static_folder='web/static')
app.config['SECRET_KEY'] = 'demo-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Gesture DJ Core (headless camera for web streaming)
print("="*60)
print("  GESTURE DJ DEMO - Initializing")
print("="*60)
dj_core = GestureDJCore(enable_camera=True, headless_camera=True)

# Initialize PiTFT Display (use SPI directly, no framebuffer on this Pi)
print("[Demo] Initializing PiTFT display...")
pitft_display = Display(simulation_mode=False, prefer_framebuffer=False)
print("="*60)


def on_voice_command(command):
    """Callback for voice commands - connected to gesture_dj_core"""
    try:
        result = dj_core.handle_voice_command(command)
        if result:
            print(f"[Demo] Voice command executed: {result}")
            # Broadcast state update to clients
            socketio.emit('audio_update', dj_core.get_state())
    except Exception as e:
        print(f"[Demo] Voice command error: {e}")

def generate_camera_frames():
    """Stream camera from core tracker with optimized performance"""
    if not dj_core.hand_tracker or dj_core.hand_tracker.simulation_mode:
        # No camera - blank frame
        while True:
            frame = cv2.zeros((360, 480, 3), dtype='uint8')
            cv2.putText(frame, "Camera not available", (100, 180),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.1)
    else:
        # Stream from core's hand tracker
        print("[Demo] Camera stream started")
        frame_skip = 0
        while True:
            try:
                if hasattr(dj_core.hand_tracker, 'last_frame') and dj_core.hand_tracker.last_frame is not None:
                    # Skip every other frame for better performance
                    frame_skip += 1
                    if frame_skip % 2 == 0:
                        frame = dj_core.hand_tracker.last_frame
                        # Lower JPEG quality for better performance
                        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                        if ret:
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                time.sleep(0.05)  # ~20 FPS (with frame skipping = ~10 FPS effective)
            except Exception as e:
                print(f"[Demo] Camera stream error: {e}")
                time.sleep(0.1)

def generate_fake_audio_data():
    """Generate simulated audio visualization data"""
    t = time.time()
    
    # Simulate waveform (64 points)
    waveform = []
    for i in range(64):
        base = math.sin(t * 2 + i * 0.2) * 0.3
        noise = random.uniform(-0.2, 0.2)
        beat_pulse = math.sin(t * 8) * 0.4 if random.random() > 0.7 else 0
        waveform.append(max(-1, min(1, base + noise + beat_pulse)))
    
    # Simulate frequency bands (32 bands)
    frequencies = []
    for i in range(32):
        if i < 8:
            base = 0.5 + math.sin(t * 4) * 0.3
        elif i < 20:
            base = 0.3 + math.sin(t * 6 + i * 0.3) * 0.2
        else:
            base = 0.2 + random.uniform(0, 0.3)
        frequencies.append(max(0, min(1, base + random.uniform(-0.1, 0.1))))
    
    bass_level = sum(frequencies[:8]) / 8
    mid_level = sum(frequencies[8:20]) / 12
    high_level = sum(frequencies[20:]) / 12
    beat_detected = bass_level > 0.6 and random.random() > 0.5
    
    return {
        'waveform': waveform,
        'frequencies': frequencies,
        'bass_level': bass_level,
        'mid_level': mid_level,
        'high_level': high_level,
        'beat_detected': beat_detected,
    }

def process_gestures():
    """Background thread to process MediaPipe hand gestures from core"""
    while True:
        try:
            # Get hand gesture data
            if dj_core.hand_tracker:
                hand_data = dj_core.hand_tracker.get_data()
                if hand_data:
                    # Handle mood change gestures
                    result = dj_core.handle_hand_gesture(hand_data)
                    if result:
                        if result.get('type') == 'mood_change':
                            print(f"[Demo] Mood changed: {result['mood']['name']}")
                        elif result.get('type') == 'scratch_event':
                            print(f"[Demo] Scratch effect triggered!")
                        # Broadcast state update
                        socketio.emit('audio_update', dj_core.get_state())
            
            time.sleep(0.05)
        except Exception as e:
            print(f"[Demo] Gesture processing error: {e}")
            time.sleep(0.1)


def process_apds_gestures():
    """Background thread to process APDS-9960 swipe gestures"""
    while True:
        try:
            if dj_core.apds and not dj_core.apds.simulation_mode:
                gesture = dj_core.apds.get_gesture()
                if gesture:
                    result = dj_core.handle_apds_gesture(gesture)
                    if result:
                        print(f"[Demo] APDS gesture: {gesture} -> {result}")
                        # Broadcast state update to clients
                        socketio.emit('audio_update', dj_core.get_state())
            
            time.sleep(0.05)
        except Exception as e:
            print(f"[Demo] APDS gesture error: {e}")
            time.sleep(0.1)


def process_mpr121_touch():
    """Background thread to process MPR121 capacitive touch"""
    while True:
        try:
            if dj_core.mpr121 and dj_core.mpr121.available:
                action = dj_core.mpr121.get_action()
                if action:
                    result = dj_core.handle_mpr121_touch(action)
                    if result:
                        print(f"[Demo] MPR121 touch: {action} -> {result}")
                        # Broadcast state update to clients
                        socketio.emit('audio_update', dj_core.get_state())
            
            time.sleep(0.05)
        except Exception as e:
            print(f"[Demo] MPR121 touch error: {e}")
            time.sleep(0.1)


def update_pitft_display():
    """Background thread to update the PiTFT display"""
    # Show welcome message first
    try:
        pitft_display.show_message("GESTURE DJ")
        time.sleep(1)
    except Exception as e:
        print(f"[Demo] Display welcome error: {e}")
    
    while True:
        try:
            # Get current state from core
            state = dj_core.get_state()
            
            # Update the display with DJ state
            pitft_display.update_dj_display(state)
            
            time.sleep(0.2)  # Update at ~5 FPS (display doesn't need high refresh)
        except Exception as e:
            print(f"[Demo] Display update error: {e}")
            time.sleep(0.5)


def broadcast_audio_data():
    """Background thread to broadcast audio data"""
    while True:
        try:
            # Get state from core
            state = dj_core.get_state()
            
            # Add simulated visualizat data
            viz_data = generate_fake_audio_data()
            data = {**state, **viz_data}
            
            socketio.emit('audio_update', data)
            time.sleep(0.05)  # 20 FPS
        except Exception as e:
            print(f"[Demo] Broadcast error: {e}")
            time.sleep(0.1)

@app.route('/')
def index():
    """Main page - uses the same template as gesture_dj.py"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_camera_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/state')
def get_state():
    """Get current state from core"""
    return jsonify(dj_core.get_state())

@app.route('/hand_status')
def hand_status():
    """Get hand tracking status"""
    tracker = dj_core.hand_tracker
    if tracker and not tracker.simulation_mode:
        return jsonify({"tracking": True, "available": True})
    return jsonify({"tracking": False, "available": False})


@app.route('/api/sensors')
def sensor_status():
    """Get status of all sensors and display"""
    return jsonify({
        'voice': {
            'available': dj_core.voice.available if dj_core.voice else False,
            'running': dj_core.voice.running if dj_core.voice else False
        },
        'apds': {
            'available': not dj_core.apds.simulation_mode if dj_core.apds else False
        },
        'mpr121': {
            'available': dj_core.mpr121.available if dj_core.mpr121 else False
        },
        'hand_tracker': {
            'available': dj_core.hand_tracker is not None and not dj_core.hand_tracker.simulation_mode
        },
        'display': {
            'available': not pitft_display.simulation_mode,
            'type': 'framebuffer' if pitft_display._framebuffer_path else 'spi' if hasattr(pitft_display, 'disp') else 'simulation'
        }
    })


@app.route('/effects/<path:filename>')
def serve_effect(filename):
    """Serve effect sound files"""
    return send_from_directory('effects', filename)

@app.route('/api/test/scratch', methods=['POST'])
def test_scratch():
    """Test scratch effect - trigger manually"""
    try:
        print("[Demo] Test scratch button clicked")
        dj_core.audio.play_scratch_effect()
        return jsonify({'status': 'ok', 'message': 'Scratch effect triggered'})
    except Exception as e:
        print(f"[Demo] Scratch test error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/control/<action>', methods=['POST'])
def control(action):
    """Control audio playback - connected to gesture_dj_core"""
    try:
        if action == 'play':
            result = dj_core.audio.play()
            print(f"[Demo] Play button clicked")
        elif action == 'pause':
            result = dj_core.audio.pause()
            print(f"[Demo] Pause button clicked")
        elif action == 'stop':
            result = dj_core.audio.stop()
            print(f"[Demo] Stop button clicked")
        elif action == 'next':
            dj_core.audio.stop()
            track = dj_core.audio.next_track()
            dj_core.audio.play()
            print(f"[Demo] Next track: {track['name']}")
        elif action == 'prev':
            dj_core.audio.stop()
            track = dj_core.audio.prev_track()
            dj_core.audio.play()
            print(f"[Demo] Previous track: {track['name']}")
        elif action == 'volume_up':
            volume = dj_core.audio.volume_up(0.1)
            print(f"[Demo] Volume up: {int(volume * 100)}%")
        elif action == 'volume_down':
            volume = dj_core.audio.volume_down(0.1)
            print(f"[Demo] Volume down: {int(volume * 100)}%")
        
        # Get updated state
        state = dj_core.get_state()
        return jsonify({'status': 'ok', 'state': state})
    except Exception as e:
        print(f"[Demo] Control error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('[Demo] Client connected')
    socketio.emit('audio_update', dj_core.get_state())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('[Demo] Client disconnected')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  GESTURE DJ DEMO - Full Web Interface")
    print("="*60)
    print("\nStarting demo with:")
    print("  - MediaPipe hand tracking (via core)")
    print("  - Voice control (Vosk speech recognition)")
    print("  - APDS-9960 gesture sensor (swipes)")
    print("  - MPR121 capacitive touch (track selection)")
    print("  - PiTFT display (retro vaporwave UI)")
    print("  - Full web visualizations")
    print("  - Camera feed streaming")
    print("\nOpen browser to: http://localhost:5000")
    print("\nControls:")
    print("  Voice: Say 'play' or 'pause'")
    print("  APDS Gestures:")
    print("    - Swipe Left/Right -> Previous/Next track")
    print("    - Swipe Up/Down -> Volume up/down")
    print("  MPR121 Touch Pads:")
    print("    - Pads 0-9 -> Select tracks 1-10")
    print("    - Pad 10 -> Play/Pause")
    print("    - Pad 11 -> Stop")
    print("  Hand Gestures (Camera):")
    print("    - Open Palm (5 fingers) held -> Light theme")
    print("    - Closed Fist (0 fingers) held -> Dark theme")
    print("    - Peace Sign (2 fingers) -> Scratch effect")
    print("\nPress Ctrl+C to quit")
    print("="*60 + "\n")
    
    # Start voice control (if available)
    if dj_core.voice and dj_core.voice.available:
        dj_core.voice.start(callback=on_voice_command)
        print("[Demo] Voice control started - say 'play' or 'pause'")
    else:
        print("[Demo] Voice control not available")
    
    # Start background threads
    gesture_thread = threading.Thread(target=process_gestures, daemon=True)
    gesture_thread.start()
    print("[Demo] MediaPipe hand gesture thread started")
    
    apds_thread = threading.Thread(target=process_apds_gestures, daemon=True)
    apds_thread.start()
    print("[Demo] APDS gesture thread started")
    
    mpr121_thread = threading.Thread(target=process_mpr121_touch, daemon=True)
    mpr121_thread.start()
    print("[Demo] MPR121 touch thread started")
    
    # Start PiTFT display thread
    display_thread = threading.Thread(target=update_pitft_display, daemon=True)
    display_thread.start()
    print("[Demo] PiTFT display thread started")
    
    broadcast_thread = threading.Thread(target=broadcast_audio_data, daemon=True)
    broadcast_thread.start()
    print("[Demo] Audio broadcast thread started")
    
    try:
        # Run Flask-SocketIO server
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n[Demo] Shutting down...")
        pitft_display.cleanup()
        dj_core.cleanup()
    except Exception as e:
        print(f"\n[Demo] Error: {e}")
        pitft_display.cleanup()
        dj_core.cleanup()