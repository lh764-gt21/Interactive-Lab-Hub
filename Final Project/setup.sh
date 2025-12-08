#!/bin/bash
# Setup script for Gesture DJ project
# Run this script once to set up everything

set -e  # Exit on error

echo "=========================================="
echo "       Gesture DJ Setup Script"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Create virtual environment
echo "[1/5] Creating Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "      Virtual environment created."
else
    echo "      Virtual environment already exists."
fi

# Activate virtual environment
source .venv/bin/activate

# 2. Install Python dependencies
echo ""
echo "[2/5] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Install lgpio (required for Raspberry Pi 5)
echo ""
echo "[3/5] Installing lgpio for Raspberry Pi 5..."
pip install lgpio 2>/dev/null || echo "      lgpio already installed or not needed."

# 4. Download Vosk speech recognition model
echo ""
echo "[4/5] Downloading Vosk speech recognition model..."
VOSK_MODEL_PATH="$HOME/.cache/vosk/vosk-model-small-en-us-0.15"
if [ ! -d "$VOSK_MODEL_PATH" ]; then
    python3 -c "from vosk import Model; Model(lang='en-us')" 2>/dev/null || echo "      Model will download on first run."
    echo "      Vosk model downloaded."
else
    echo "      Vosk model already cached."
fi

# 5. Create directories and placeholder files
echo ""
echo "[5/5] Setting up project directories..."
mkdir -p tracks
mkdir -p effects

# Create tracks README
cat > tracks/README.md << 'EOF'
# Tracks Directory

Place your 10 MP3 track files here with the following naming:
- track01.mp3
- track02.mp3
- track03.mp3
- track04.mp3
- track05.mp3
- track06.mp3
- track07.mp3
- track08.mp3
- track09.mp3
- track10.mp3

## Suggested Track Sources:
- Free Music Archive (https://freemusicarchive.org/)
- Incompetech (https://incompetech.com/music/)
- YouTube Audio Library
- Bensound (https://www.bensound.com/)

## Track Guidelines:
- Format: MP3
- Length: 10-60 seconds (shorter is better for DJ loops)
- Quality: 128kbps or higher
- License: Royalty-free or Creative Commons
EOF

# Create effects README
cat > effects/README.md << 'EOF'
# Effects Directory

Place your sound effect MP3 files here:
- beep.mp3 (track change confirmation)
- click.mp3 (volume change confirmation)
- whoosh.mp3 (effect toggle confirmation)

## Suggested Effect Sources:
- Freesound (https://freesound.org/)
- Zapsplat (https://www.zapsplat.com/)
- SoundBible (http://soundbible.com/)

## Effect Guidelines:
- Format: MP3
- Length: 0.1-0.5 seconds (very short)
- Volume: Moderate (not too loud)
- License: Royalty-free or Creative Commons
EOF

echo ""
echo "=========================================="
echo "           Setup Complete!"
echo "=========================================="
echo ""
echo "Directory structure:"
echo "  tracks/     - Place 10 MP3 tracks (track01.mp3 - track10.mp3)"
echo "  effects/    - Place sound effects (beep.mp3, click.mp3, whoosh.mp3)"
echo ""
echo "To run the Gesture DJ:"
echo "  1. Activate virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python gesture_dj.py"
echo ""
echo "Controls:"
echo "  APDS-9960 Gestures:"
echo "    - Swipe RIGHT: Next track"
echo "    - Swipe LEFT:  Previous track"
echo "    - Swipe UP:    Volume up"
echo "    - Swipe DOWN:  Volume down"
echo ""
echo "  MPR121 Touch Pads (if connected):"
echo "    - Pads 0-9:    Select track 1-10"
echo "    - Pad 10:      Play/Pause"
echo "    - Pad 11:      Stop"
echo ""
echo "  Voice Commands:"
echo "    - Say 'play':  Start playback"
echo "    - Say 'pause': Pause playback"
echo ""
echo "Done!"
