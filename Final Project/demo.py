"""
Gesture DJ Demo - Web Interface + Core Logic
Uses gesture_dj_core.py for all business logic
"""

from flask import Flask, Response, render_template, jsonify
from flask_socketio import SocketIO
import threading
import time
import random
import math
from gesture_dj_core import GestureDJCore
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
print("="*60)

def generate_camera_frames():
    """Stream camera from core tracker"""
    if not dj_core.hand_tracker or dj_core.hand_tracker.simulation_mode:
        # No camera - blank frame
        while True:
            frame = cv2.zeros((480, 640, 3), dtype='uint8')
            cv2.putText(frame, "Camera not available", (150, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.1)
    else:
        # Stream from core's hand tracker
        print("[Demo] Camera stream started")
        while True:
            try:
                if hasattr(dj_core.hand_tracker, 'last_frame') and dj_core.hand_tracker.last_frame is not None:
                    frame = dj_core.hand_tracker.last_frame.copy()
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                else:
                    time.sleep(0.05)
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
    """Background thread to process gestures from core"""
    while True:
        try:
            # Get hand gesture data
            if dj_core.hand_tracker:
                hand_data = dj_core.hand_tracker.get_data()
                if hand_data:
                    result = dj_core.handle_hand_gesture(hand_data)
                    if result and result.get('type') == 'mood_change':
                        print(f"[Demo] Mood changed: {result['mood']['name']}")
            
            time.sleep(0.02)
        except Exception as e:
            print(f"[Demo] Gesture processing error: {e}")
            time.sleep(0.1)

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
    print("  - Full web visualizations")
    print("  - Camera feed streaming")
    print("\nOpen browser to: http://localhost:5000")
    print("\nGestures:")
    print("  Open Palm (5 fingers) -> Light theme")
    print("  Closed Fist (0 fingers) -> Dark theme")
    print("\nPress Ctrl+C to quit")
    print("="*60 + "\n")
    
    # Start background threads
    gesture_thread = threading.Thread(target=process_gestures, daemon=True)
    gesture_thread.start()
    
    broadcast_thread = threading.Thread(target=broadcast_audio_data, daemon=True)
    broadcast_thread.start()
    
    try:
        # Run Flask-SocketIO server
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n[Demo] Shutting down...")
        dj_core.cleanup()
    except Exception as e:
        print(f"\n[Demo] Error: {e}")
        dj_core.cleanup()