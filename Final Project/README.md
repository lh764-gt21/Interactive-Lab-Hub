# Gesture DJ 🎵

A multi-modal DJ controller for Raspberry Pi that uses gesture sensors, touch input, and voice commands to control music playback.

## Features

- **APDS-9960 Gesture Control**: Swipe gestures to navigate tracks and control volume
- **MPR121 Touch Pads**: Capacitive touch pads to select specific tracks (1-10)
- **Voice Control**: Say "play" or "pause" to control playback using offline speech recognition
- **TFT Display**: Retro vaporwave-style visual feedback on PiTFT display
- **Web Visualization**: Real-time audio visualizations accessible from any browser
  - Waveform display with beat detection
  - Frequency spectrum analyzer
  - Audience mode with RGB bars
  - Particle effects
- **10 Track Support**: Load up to 10 MP3 tracks for seamless switching

## Hardware Requirements

### Required
- Raspberry Pi 5 (or Pi 4)
- APDS-9960 Gesture Sensor (I2C address: 0x39)
- PiTFT Display (SPI)
- USB Microphone (for voice control)
- Speakers or headphones (3.5mm audio output)
- MPR121 Capacitive Touch Sensor (I2C address: 0x5A)

## Wiring

### APDS-9960 (I2C)
| APDS-9960 | Raspberry Pi |
|-----------|--------------|
| VCC       | 3.3V         |
| GND       | GND          |
| SDA       | GPIO 2 (SDA) |
| SCL       | GPIO 3 (SCL) |

### MPR121 (I2C) - Optional
| MPR121    | Raspberry Pi |
|-----------|--------------|
| VCC       | 3.3V         |
| GND       | GND          |
| SDA       | GPIO 2 (SDA) |
| SCL       | GPIO 3 (SCL) |



## Installation

### 1. Clone the Repository
```bash
cd ~/Interactive-Lab-Hub
cd "Final Project"
```

### 2. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a Python virtual environment (`.venv`)
- Install all required Python packages
- Download the Vosk speech recognition model
- Create `tracks/` and `effects/` directories

### 3. Add Music Files

Place your MP3 tracks in the `tracks/` directory:
```
tracks/
├── track01.mp3
├── track02.mp3
├── track03.mp3
├── track04.mp3
├── track05.mp3
├── track06.mp3
├── track07.mp3
├── track08.mp3
├── track09.mp3
└── track10.mp3
```

Optionally, add sound effects in `effects/`:
```
effects/
├── beep.mp3    (track change sound)
├── click.mp3   (volume change sound)
└── whoosh.mp3  (effect toggle sound)
```

### 4. Enable I2C
```bash
sudo raspi-config
# Navigate to: Interface Options -> I2C -> Enable
```

### 5. Verify Sensors
```bash
sudo i2cdetect -y 1
```
You should see:
- `39` - APDS-9960 gesture sensor
- `5a` - MPR121 touch sensor (if connected)

## Usage

### Start the Application
```bash
cd ~/Interactive-Lab-Hub/Final\ Project
source .venv/bin/activate
python gesture_dj.py
```

### Start with Web Visualization
```bash
python gesture_dj.py --web
```
Then open `http://<raspberry-pi-ip>:5000` in any browser to see the visualizations.

### Controls

#### APDS-9960 Gesture Controls
| Gesture      | Action              |
|--------------|---------------------|
| Swipe RIGHT  | Next track (auto-play) |
| Swipe LEFT   | Previous track (auto-play) |
| Swipe UP     | Volume up (+10%)    |
| Swipe DOWN   | Volume down (-10%)  |

#### MPR121 Touch Controls (Optional)
| Pad      | Action              |
|----------|---------------------|
| Pad 0-9  | Select track 1-10   |
| Pad 10   | Play/Pause toggle   |
| Pad 11   | Stop playback       |

#### Voice Commands
| Command  | Action              |
|----------|---------------------|
| "play"   | Start/resume playback |
| "pause"  | Pause playback      |

Alternative words also work:
- Play: "start", "go", "resume"
- Pause: "stop", "wait", "hold"

### Web Visualization Modes

When running with `--web`, access the visualizer at `http://<pi-ip>:5000`:

| Mode      | Description |
|-----------|-------------|
| WAVEFORM  | Real-time waveform with beat-reactive glow |
| SPECTRUM  | Frequency spectrum analyzer with color gradient |
| AUDIENCE  | RGB bars bouncing with bass, party mode |
| PARTICLES | Pulsing rings with particle burst effects |

**Features:**
- 🎵 Track waveform visualization - see beats and peaks
- 📊 Frequency spectrum with bass/mid/high analysis
- 🎨 RGB bars bounce with bass levels
- ✨ Reactive particle effects on beat detection
- 🖱️ Click and drag on waveform to "scratch"
- 📱 Works on mobile browsers too

### Stop the Application
Press `Ctrl+C` to exit gracefully.

## File Structure

```
Final Project/
├── gesture_dj.py       # Main application
├── audio_engine.py     # Audio playback and track management
├── apds_gesture.py     # APDS-9960 gesture sensor interface
├── mpr121_touch.py     # MPR121 touch sensor interface
├── voice_control.py    # Vosk-based voice recognition
├── hand_tracker.py     # MediaPipe hand tracking (disabled)
├── display.py          # PiTFT display interface
├── requirements.txt    # Python dependencies
├── setup.sh            # Setup script
├── README.md           # This file
├── tracks/             # MP3 track files
│   └── track01-10.mp3
└── effects/            # Sound effect files
    ├── beep.mp3
    ├── click.mp3
    └── whoosh.mp3
```

## Module Descriptions

### `gesture_dj.py`
Main integration module that combines all input methods and controls audio playback.

### `audio_engine.py`
Handles audio playback using pygame:
- Track loading and switching
- Play, pause, stop, resume controls
- Volume control
- Playback speed adjustment (via mixer frequency)

### `apds_gesture.py`
Interface for APDS-9960 gesture sensor:
- Swipe detection (up, down, left, right)
- Proximity sensing

### `mpr121_touch.py`
Interface for MPR121 capacitive touch sensor:
- 12 touch pads (0-11)
- Rising edge detection for reliable touch input

### `voice_control.py`
Offline speech recognition using Vosk:
- Uses USB microphone
- Recognizes "play" and "pause" commands
- Runs in background thread

### `display.py`
PiTFT display interface:
- Shows track number and name
- Displays volume level
- Shows playback status (playing/paused/stopped)
- Progress bar visualization

## Troubleshooting

### APDS Sensor Not Working
1. Check I2C connection: `sudo i2cdetect -y 1` (should show `39`)
2. Ensure I2C is enabled in raspi-config
3. Check wiring (VCC, GND, SDA, SCL)

### Voice Control Not Working
1. Check microphone is connected: `arecord -l`
2. Test microphone: `arecord -d 3 test.wav && aplay test.wav`
3. Ensure Vosk model is downloaded (check `~/.cache/vosk/`)

### No Audio Output
1. Check speaker/headphone connection
2. Set audio output: `sudo raspi-config` -> System Options -> Audio
3. Test audio: `speaker-test -t wav`

### Display Not Showing
1. Ensure PiTFT is properly installed
2. Check SPI is enabled in raspi-config
3. Verify display driver is loaded

### MPR121 Not Detected
1. Check I2C connection: `sudo i2cdetect -y 1` (should show `5a`)
2. MPR121 is optional - system works without it

## Dependencies

See `requirements.txt` for full list. Key dependencies:
- `pygame` - Audio playback
- `adafruit-circuitpython-apds9960` - APDS gesture sensor
- `adafruit-circuitpython-mpr121` - MPR121 touch sensor
- `vosk` - Offline speech recognition
- `sounddevice` - Microphone input
- `pillow` - Image processing for display
- `lgpio` - GPIO for Raspberry Pi 5

