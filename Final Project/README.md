# 🎵 Gesture DJ 

A multi-modal DJ controller for Raspberry Pi that uses gesture sensors, touch input, voice commands, and hand tracking to control music playback with real-time web visualizations.

**Project Team:**
- Eva Huang (lh764)
- Zoe Tseng (yzt2)
- Charlotte Lin (hl2575)

# 📹 Demo Video

*▶️ Click below to watch someone using Gesture DJ!*

| Video Description | Video link |
|-------------------|------------|
|Final Presentation |<a href="https://youtube.com/shorts/_Esceg73g3c"><img src="https://img.youtube.com/vi/_Esceg73g3c/hqdefault.jpg" alt="Demo Video" width="500"></a>|
|Switch tracks with `ADPS sensor` + Choose tracks with `MPR121 touch sensor` + Control UI and Sound effects with `MediaPipe`| <a href="https://youtube.com/shorts/_wjvhvSJUlQ"><img src="https://img.youtube.com/vi/_wjvhvSJUlQ/hqdefault.jpg" alt="Demo Video" width="500"></a>|
|Details on `Media pipe` gestures controls| https://youtube.com/shorts/9XZ2AFxADyA?feature=share



# 📸 Project Photos

### The Complete Device
<!-- Add photo of your finished device -->
<img src="https://hackmd.io/_uploads/rJWBAaTfZl.jpg" alt="Gesture DJ Device" width="400">

## Hardware Setup
<img src="https://hackmd.io/_uploads/HkKSvJRfWg.png" alt="Full Setup" width="400">




## Web Interface Screenshots
| Light Theme | Dark Theme |
|-------------|------------|
| <img src="https://hackmd.io/_uploads/BJjHPxRMbe.png" alt="Dark Theme" width="500">| <img src="https://hackmd.io/_uploads/Sy0avApfZe.png" alt="Dark Theme" width="500"> |


# Deliverables

| Deliverable | Link/Status |
|-------------|-------------|
| 📋 Project Plan | [View Plan](https://github.com/zyt02/Interactive-Lab-Hub/blob/Fall2025/final_project_plan.md) |
| 📝 Design Documentation | See [Design Documentation](#design-documentation) below |
| 💻 Code Archive | This repository |

## Design Documentation

### Design Process

<details>
<summary>Click to expand Initial idea </summary>
<img src="https://hackmd.io/_uploads/SkhPiR6Mbe.jpg" alt="Gesture DJ Device" width="300">
    
Early concept for the Gesture DJ
    
</details>details>

#### Prototype Iterations

| Version | Changes Made |
|---------|--------------|
| **v1** | MediaPipe hand tracking for play/pause control + APDS gesture sensor + USB camera |
| **v2** | Removed MediaPipe (conflicted with APDS) + Added voice control for play/pause + APDS + Removed camera + Added web interface |
| **v3 (Current)** | Re-added MediaPipe for UI theme switching & scratch effects + Voice control + APDS + MPR121 touch pads + Web interface + PiTFT display + Camera (for hand tracking) |


#### Physical Device Design Process
<!-- Add photos of your physical enclosure design process -->
| Stage | Photo |
|-------|-------|
| Design sketch | <img src="https://hackmd.io/_uploads/HktUWkCfbl.png" width="600"> |
| CAD/Design | <img src="https://hackmd.io/_uploads/rJglpA6fWl.png" width="600"> |
| Laser Cutting | <img src="https://hackmd.io/_uploads/BkuyXkRfZg.png" height = "400" width="600"> |
| Finished |  <img src="https://hackmd.io/_uploads/B1o4Vy0z-l.png"  width="600"> |



## Features

### 1. APDS-9960 Gesture Sensor
Navigate music library intuitively with proximity-based gesture control:
- **Swipe gestures** to skip between tracks
- **Distance-based volume control** for hands-free adjustment

### 2.MPR121 Capacitive Touch Pads
Direct track selection at your fingertips:
- **10 touch-sensitive pads** for instant access to individual tracks
- Quick switching between your favorite songs

### 3. Voice Commands
Control playback with simple voice commands using offline speech recognition:
- Say **"play"** to start playback
- Say **"pause"** to stop playback
- No internet connection required


### 4. MediaPipe Hand Gesture Recognition
Advanced computer vision-based controls using hand poses:

#### Theme Control
- **Light/Dark Mode Toggle**: Hold palm open or make a fist for 2.5 seconds to switch between interface themes
- Seamless visual transitions

#### DJ Effects
- **Scratch Effect**: Trigger real-time DJ scratch sounds with a peace sign gesture
- Professional audio manipulation with hand movements


### 5. PiTFT Display
Immersive visual feedback directly on the device:
- **Retro vaporwave aesthetic** with nostalgic 80s-inspired graphics
- Real-time track information and system status

### 6. Web Interface
Access music system from any device on your network:
- **Real-time camera feed** showing hand gesture recognition
- **Playback controls** for play/pause functionality
- **Volume slider** for precise audio level adjustment

#### Dynamic Audio Visualizations
Multiple visualization modes that respond to music:
- **Waveform Display**: Real-time audio amplitude with beat detection
- **Frequency Spectrum Analyzer**: Visual representation of frequency content
- **Audience Mode**: RGB bar visualization simulating crowd response
- **Particle Effects**: Dynamic animations synchronized to the music
- All visualizations adapt based on active control inputs and audio characteristics



## Hardware Requirements

### Required
- Raspberry Pi 5 (or Pi 4)
- APDS-9960 Gesture Sensor (I2C address: 0x39)
- PiTFT Display (SPI)
- USB Microphone (for voice control)
- USB Camera (for MediaPipe hand tracking)
- Speakers or headphones (3.5mm audio output)
- MPR121 Capacitive Touch Sensor (I2C address: 0x5A)
- Desktop or Laptop for Web Interface
- Wood boards and arcrylic materials for physical device design 

### Wiring

| Raspberry Pi | MPR121   | APDS-9960 |
|--------------|----------|-----------|
| 3.3V         |VCC       | VCC       | 
| GND          |GND       |GND       |
| GPIO 2 (SDA) |SDA       | SDA       | 
| GPIO 3 (SCL) |SCL       | SCL       | 




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
├── beep.mp3       (track change sound)
├── click.mp3      (volume change sound)
├── swoosh.mp3     (theme change sound)
├── scratch1.mp3   (DJ scratch effect)
├── scratch2.mp3   (DJ scratch effect)
├── scratch3.mp3   (DJ scratch effect)
└── scratch4.mp3   (DJ scratch effect)
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

<details>
<summary> User Guide Poster </summary>


![Screenshot 2025-12-15 at 16.16.02](https://hackmd.io/_uploads/HyfC9xCzZl.png)
</details>details>

#### APDS-9960 Gesture Controls
| Gesture      | Action              |
|--------------|---------------------|
| Swipe RIGHT  | Next track (auto-play) |
| Swipe LEFT   | Previous track (auto-play) |
| Swipe UP     | Volume up (+10%)    |
| Swipe DOWN   | Volume down (-10%)  |

#### MPR121 Touch Controls
| Pad      | Action              |
|----------|---------------------|
| Pad 0-9  | Select track 1-10   |

#### MediaPipe Hand Gestures (Camera Required)
| Gesture | Fingers | Action | Hold Time |
|---------|---------|--------|-----------|
| ✋ OPEN PALM | 5 | Light theme (baby blue UI) | 2.5 seconds |
| ✊ CLOSED FIST | 0 | Dark theme (midnight UI) | 2.5 seconds |
| ✌️ PEACE SIGN | 2 | DJ scratch effect | Instant |


<details>
<summary>Click to see Tips detail</summary>
    
**Tips:**
- Hold palm/fist gestures for **2.5 seconds** to change theme
- Peace sign triggers immediately (no hold required)
- Keep hand 1-2 feet from camera for best detection
- Use good lighting for accurate gesture recognition
- Camera feed visible in web UI (top-right corner)
- Scratch effect plays random scratch sound over music
    
</details>details>

#### Voice Commands
| Command  | Action              |
|----------|---------------------|
| "play"   | Start/resume playback |
| "pause"  | Pause playback      |


<details>
<summary>Click to see Alternatives detail</summary>
    
Alternative words also work:
- Play: "start", "go", "resume"
- Pause: "stop", "wait", "hold"

    
</details>details>


### Web Visualization Modes

When running with `--web`, access the visualizer at `http://<pi-ip>:5000`:

| Mode      | Description | Features |
|-----------|-------------|-------------|
| WAVEFORM  | Real-time waveform with beat-reactive glow | see beats and peaks |
| SPECTRUM  | Frequency spectrum analyzer with color gradient | spectrum with bass/mid/high analysis|
| AUDIENCE  | RGB bars bouncing with bass, party mode | bounce with bass levels |
| PARTICLES | Pulsing rings with particle burst effects |  effects on beat detection |


### Stop the Application
Press `Ctrl+C` to exit gracefully.

## File Structure

<details>
<summary>Click to expand file structure</summary>

```
Final Project/
│
├── README.md                    # Main project documentation and usage guide
├── requirements.txt             # Python package dependencies
├── setup.sh                     # Setup script (creates venv, installs dependencies)
│
├── Core Application Files
│   ├── gesture_dj.py              # Main entry point with display integration
│   ├── gesture_dj_core.py         # Core business logic and system integration
│   ├── demo.py                    # Demo mode with web interface
│   └── web_server.py              # Flask web server for visualizations
│
├── Audio Module
│   └── audio_engine.py            # Audio playback, track management, effects
│
├── Input Modules
│   ├── apds_gesture.py            # APDS-9960 gesture sensor interface
│   ├── mpr121_touch.py            # MPR121 capacitive touch sensor interface
│   ├── voice_control.py           # Vosk-based offline speech recognition
│   └── hand_tracker.py            # MediaPipe hand tracking and gesture recognition
│
├── Output Modules
│   ├── display.py                 # PiTFT display interface and rendering
│   └── mood_lighting.py           # Mood-based lighting control
│
├── Web Interface
│   └── web/
│       └── index.html             # Web visualization interface (Flask template)
│
├── Media Assets
│   ├── tracks/                    # Music track files (MP3)
│   │   ├── README.md
│   │   ├── track01.mp3
│   │   ├── track02.mp3
│   │   ├── track03.mp3
│   │   ├── track04.mp3
│   │   ├── track05.mp3
│   │   ├── track06.mp3
│   │   ├── track07.mp3
│   │   ├── track08.mp3
│   │   ├── track09.mp3
│   │   └── track10.mp3
│   │
│   └── effects/                   # Sound effect files (MP3)
│       ├── README.md
│       ├── beep.mp3               # Track change notification
│       ├── click.mp3              # Volume change feedback
│       ├── swoosh.mp3             # Theme change sound
│       ├── scratch1.mp3           # DJ scratch effect
│       ├── scratch2.mp3           # DJ scratch effect
│       ├── scratch3.mp3           # DJ scratch effect
│       └── scratch4.mp3           # DJ scratch effect
│
└── Generated Files (not in repo)
    └── .venv/                     # Python virtual environment (created by setup.sh)
        └── ...                    # Installed packages and dependencies
```
    
</details>

## Module dependency 
```
gesture_dj.py / demo.py
    │
    ├── gesture_dj_core.py (core logic)
    │   │
    │   ├── audio_engine.py (audio playback)
    │   ├── apds_gesture.py (gesture sensor)
    │   ├── mpr121_touch.py (touch sensor)
    │   ├── voice_control.py (speech recognition)
    │   ├── hand_tracker.py (MediaPipe hand tracking)
    │   └── mood_lighting.py (lighting control)
    │
    ├── display.py (PiTFT display)
    │
    └── web_server.py (web interface)
        └── web/index.html (web UI)
```
    


## System Architectue

![Decision Path Selection Flow-2025-12-15-030217](https://hackmd.io/_uploads/H1MfoeazWx.png)

## Module Descriptions

### `gesture_dj.py`
> **Owner:** Eva Huang (lh764), Zoe Tseng (yzt2), Charlotte Lin (hl2575)

Main application entry point that handles display and web interface integration:
- Initializes GestureDJCore for business logic
- Manages PiTFT display updates
- Coordinates web server (optional)
- Main event loop for all input methods
- Graceful shutdown handling

### `gesture_dj_core.py`
> **Owner:** Eva Huang (lh764), Zoe Tseng (yzt2), Charlotte Lin (hl2575)

Core business logic module that orchestrates all input/output components:
- Integrates all input modules (APDS, MPR121, voice, hand tracking)
- Coordinates audio engine and mood lighting
- Handles gesture-to-action mappings
- Provides unified state management
- Contains SimpleHandTracker implementation for MediaPipe hand tracking
- No display or web server dependencies

### `audio_engine.py`
> **Owner:** Eva Huang (lh764)

Handles audio playback and management using pygame:
- Track loading and switching (supports up to 10 MP3 tracks)
- Play, pause, stop, resume controls
- Volume control (0-100%) with sound feedback
- DJ scratch effect (overlays random scratch sound on music)
- Theme change swoosh sound effect
- Playback speed adjustment (via mixer frequency presets)
- Sound effect management (beep, click, swoosh, scratch sounds)

### `apds_gesture.py`
> **Owner:** Charlotte Lin (hl2575), Zoe Tseng (yzt2)

Interface for APDS-9960 gesture sensor:
- Swipe detection (up, down, left, right)
- Proximity sensing
- Gesture debouncing and reliability

### `mpr121_touch.py`
> **Owner:** Zoe Tseng (yzt2), Charlotte Lin (hl2575)

Interface for MPR121 capacitive touch sensor:
- 12 touch pads (0-11)
- Rising edge detection for reliable touch input
- Pad 0-9: Direct track selection (1-10)
- Pad 10: Play/Pause toggle
- Pad 11: Stop playback

### `voice_control.py`
> **Owner:** Zoe Tseng (yzt2), Charlotte Lin (hl2575)

Offline speech recognition using Vosk:
- Uses USB microphone input
- Recognizes "play" and "pause" commands (with alternatives: start/go/resume, stop/wait/hold)
- Runs in background thread for non-blocking operation
- Continuous listening with keyword detection

### `hand_tracker.py`
> **Owner:** Eva Huang (lh764)

MediaPipe hand tracking module for gesture control:
- Palm detection (5 fingers extended) → Light theme trigger
- Fist detection (0 fingers extended) → Dark theme trigger
- Peace sign detection (2 fingers: index + middle) → DJ scratch effect
- 2.5 second hold requirement for theme changes
- Real-time finger counting and pose classification
- Headless mode support for web streaming
- Live camera feed with gesture overlays
- Gesture cooldown to prevent rapid re-triggering

### `display.py`
> **Owner:** Eva Huang (lh764), Zoe Tseng (yzt2), Charlotte Lin (hl2575)

PiTFT display interface with retro vaporwave aesthetic:
- Shows track number and name
- Displays volume level
- Shows playback status (playing/paused/stopped)
- Progress bar visualization
- Gesture feedback with emojis
- Color-coded mood indicators
- Supports both SPI and framebuffer modes
- Simulation mode for development without hardware

### `mood_lighting.py`
> **Owner:** Eva Huang (lh764)

Manages mood-based visual themes and color schemes:
- Light theme (baby blue gradient) triggered by palm gesture
- Dark theme (midnight/cyberpunk) triggered by fist gesture
- Theme configuration with gradients, colors, and UI elements
- Provides mood state for web UI and display
- RGB color mapping for display feedback
- Theme change detection and timing

### `web_server.py`
> **Owner:** Eva Huang (lh764), Zoe Tseng (yzt2), Charlotte Lin (hl2575)

Flask web server providing real-time audio visualizations:
- WebSocket-based real-time updates
- Waveform visualization mode
- Frequency spectrum analyzer
- Audience mode with RGB bars
- Particle effects visualization
- Camera feed streaming (hand tracking overlay)
- Mood-based dynamic theming
- Accessible from any browser on the network

### `demo.py`
> **Owner:** Eva Huang (lh764), Zoe Tseng (yzt2), Charlotte Lin (hl2575)

Enhanced demo mode with web interface for presentations:
- Combines GestureDJCore with Flask web server
- Optimized for demonstrations and testing
- Full web visualization suite
- Real-time gesture feedback on web UI
- Camera stream integration

## Troubleshooting


**APDS Sensor Not Working**
1. Check I2C connection: `sudo i2cdetect -y 1` (should show `39`)
2. Ensure I2C is enabled in raspi-config
3. Check wiring (VCC, GND, SDA, SCL)

**Voice Control Not Working**
1. Check microphone is connected: `arecord -l`
2. Test microphone: `arecord -d 3 test.wav && aplay test.wav`
3. Ensure Vosk model is downloaded (check `~/.cache/vosk/`)

**No Audio Output**
1. Check speaker/headphone connection
2. Set audio output: `sudo raspi-config` -> System Options -> Audio
3. Test audio: `speaker-test -t wav`

**Display Not Showing**
1. Ensure PiTFT is properly installed
2. Check SPI is enabled in raspi-config
3. Verify display driver is loaded

**MPR121 Not Detected**
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
- `mediapipe` -  MediaPipe framework for hand gesture recognition 



## Improvements and iteration documentations

- **user voice input** : We didn't originally plan to include voice input in our device. During the functional check, Professor Ju suggested adding voice control for music playback, such as play and pause commands. We ran some trials with voice input and speech recognition, and initially it seemed to work pretty well. However, we hadn't really thought about background noise and other people talking nearby. As a result, at the final presentation, sometimes the microphone struggled to pick up voice commands accurately and respond quickly because of all the ambient sound in the room.
- **user gesture controls (adps)**: We used the APDS gesture sensor for two functions: switching tracks (next or previous) and volume control. The track switching worked well because it's a simple and discrete action as one swipe clearly moves to the next song. Volume control, however, was less successful. Each upward swipe increased the volume by 10%, but the change wasn't always noticeable to the user. Additionally, if someone wanted to raise the volume by 30%, they'd have to swipe up three separate times, which felt cumbersome. Looking back, a volume dial might have been a better choice for volume control since it would allow for smoother, more continuous adjustments.
- **user gesture recognition (media pipe)** : MediaPipe hand tracking was one of the most challenging parts of our project. Initially, we tried to use it for play/pause control, but it conflicted with the APDS gesture sensor. We ended up removing MediaPipe entirely to simplify the system. But later, we added it back but with a completely different purpose: UI theme switching (palm/fist gestures) and DJ scratch sound effects (peace sign). The most difficult technical challenge was making MediaPipe work simultaneously with all the other sensors (APDS, MPR121, voice) without conflicts. We had to carefully design the event handling system so that each input method had distinct responsibilities and wouldn't interfere with each other, which took us a lot of time working on multiple iterations of testing and debugging to ensure smooth multi-modal interaction.

- **web interface** : Initially, the web interface was just a backup plan. We designed it only as a visualization tool to give users clearer visual feedback. However, when testing with the PiTFT display, we realized it alone wasn't enough for users to easily see what was happening or interact with the device effectively. After a few design iterations, we settled on a neon theme for the interface to align with the DJ aesthetic of our project. We also added gesture control to let users switch between light and dark themes, giving them the flexibility to adjust the display based on their environment and personal preference without needing to navigate through menus.

- **physical device design** : For the physical design, our vision was to create a DJ board aesthetic using laser-cut wooden panels assembled into a box-like structure. We wanted the device to feel like an actual DJ controller, which would make the interaction more intuitive and engaging. The main challenge we faced was making it immediately clear to users where and how to interact with the device. Since gesture sensors and other components aren't as visually obvious as physical buttons or knobs, we had to carefully consider the placement of components and add visual cues like labels, icons, or designated interaction zones to guide users toward the right areas and help them understand which gestures to use. Looking ahead, there are many things we'd like to improve. For instance, the decorative elements on the DJ panel could actually be functional instead of just decorations, they could serve as interactive controls.
