"""
Web Server for Gesture DJ Visualizations
Provides real-time waveform and audience visualization via WebSocket
"""

import os
import json
import threading
import time
import random
import math
from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

# Create Flask app
app = Flask(__name__, template_folder='web', static_folder='web/static')
app.config['SECRET_KEY'] = 'gesture-dj-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Audio state (shared with main app)
audio_state = {
    'track_number': 1,
    'track_total': 10,
    'track_name': 'Track 01',
    'volume': 75,
    'is_playing': False,
    'is_paused': False,
    'tempo': 1.0,
    'progress': 0.0,
    'position': 0.0,
    # Visualization data
    'waveform': [],
    'frequencies': [],
    'bass_level': 0,
    'mid_level': 0,
    'high_level': 0,
    'beat_detected': False,
}

# Reference to audio engine (set by main app)
audio_engine = None


def set_audio_engine(engine):
    """Set the audio engine reference"""
    global audio_engine
    audio_engine = engine


def generate_fake_audio_data():
    """Generate simulated audio visualization data"""
    t = time.time()
    
    # Simulate waveform (64 points)
    waveform = []
    for i in range(64):
        # Create a dynamic waveform based on time
        base = math.sin(t * 2 + i * 0.2) * 0.3
        noise = random.uniform(-0.2, 0.2)
        beat_pulse = math.sin(t * 8) * 0.4 if random.random() > 0.7 else 0
        waveform.append(max(-1, min(1, base + noise + beat_pulse)))
    
    # Simulate frequency bands (32 bands)
    frequencies = []
    for i in range(32):
        # Bass frequencies (0-7) are higher
        if i < 8:
            base = 0.5 + math.sin(t * 4) * 0.3
        # Mid frequencies (8-20)
        elif i < 20:
            base = 0.3 + math.sin(t * 6 + i * 0.3) * 0.2
        # High frequencies (20-32)
        else:
            base = 0.2 + random.uniform(0, 0.3)
        
        frequencies.append(max(0, min(1, base + random.uniform(-0.1, 0.1))))
    
    # Bass, mid, high levels
    bass_level = sum(frequencies[:8]) / 8
    mid_level = sum(frequencies[8:20]) / 12
    high_level = sum(frequencies[20:]) / 12
    
    # Beat detection (simple threshold)
    beat_detected = bass_level > 0.6 and random.random() > 0.5
    
    return {
        'waveform': waveform,
        'frequencies': frequencies,
        'bass_level': bass_level,
        'mid_level': mid_level,
        'high_level': high_level,
        'beat_detected': beat_detected,
    }


def broadcast_audio_data():
    """Background thread to broadcast audio data"""
    while True:
        if audio_state.get('is_playing') and not audio_state.get('is_paused'):
            # Get visualization data
            viz_data = generate_fake_audio_data()
            
            # Update audio state with visualization
            data = {
                **audio_state,
                **viz_data,
            }
            
            socketio.emit('audio_update', data)
        
        time.sleep(0.05)  # 20 FPS updates


@app.route('/')
def index():
    """Main visualization page"""
    return render_template('index.html')


@app.route('/api/state')
def get_state():
    """Get current audio state"""
    return jsonify(audio_state)


@app.route('/api/control/<action>', methods=['POST'])
def control(action):
    """Control audio playback"""
    global audio_engine
    
    if audio_engine:
        if action == 'play':
            audio_engine.play()
            audio_state['is_playing'] = True
            audio_state['is_paused'] = False
        elif action == 'pause':
            audio_engine.pause()
            audio_state['is_paused'] = True
        elif action == 'stop':
            audio_engine.stop()
            audio_state['is_playing'] = False
            audio_state['is_paused'] = False
        elif action == 'next':
            audio_engine.stop()
            track = audio_engine.next_track()
            audio_engine.play()
            audio_state['track_number'] = track['id']
            audio_state['track_name'] = track['name']
            audio_state['is_playing'] = True
        elif action == 'prev':
            audio_engine.stop()
            track = audio_engine.prev_track()
            audio_engine.play()
            audio_state['track_number'] = track['id']
            audio_state['track_name'] = track['name']
            audio_state['is_playing'] = True
        elif action == 'volume_up':
            audio_engine.volume_up(0.1)
            audio_state['volume'] = int(audio_engine.volume * 100)
        elif action == 'volume_down':
            audio_engine.volume_down(0.1)
            audio_state['volume'] = int(audio_engine.volume * 100)
    
    return jsonify({'status': 'ok', 'state': audio_state})


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('[Web] Client connected')
    emit('audio_update', audio_state)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('[Web] Client disconnected')


@socketio.on('scratch')
def handle_scratch(data):
    """Handle scratch gesture from web interface"""
    direction = data.get('direction', 0)
    print(f'[Web] Scratch: {direction}')
    # Could adjust playback position here


def update_state(new_state):
    """Update audio state from main app"""
    global audio_state
    audio_state.update(new_state)


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run the web server"""
    # Start background thread for audio data broadcast
    broadcast_thread = threading.Thread(target=broadcast_audio_data, daemon=True)
    broadcast_thread.start()
    
    print(f"[Web] Starting server at http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    # Create web directories if they don't exist
    os.makedirs('web/static', exist_ok=True)
    
    # Test mode - simulate playing
    audio_state['is_playing'] = True
    
    run_server(debug=True)



