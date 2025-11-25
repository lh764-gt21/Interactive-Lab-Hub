#!/bin/bash
# Setup script for Gesture DJ project
# Creates necessary directories and placeholder files

echo "Setting up Gesture DJ project structure..."
echo "=========================================="

# Create directories
echo "Creating directories..."
mkdir -p tracks
mkdir -p effects

# Create placeholder track files info
echo "Creating placeholder info..."
cat > tracks/README.md << EOF
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

cat > effects/README.md << EOF
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
echo "Directory structure created!"
echo ""
echo "Next steps:"
echo "1. Add 10 MP3 tracks to the 'tracks/' directory"
echo "2. Add 3 sound effects to the 'effects/' directory"
echo "3. Install dependencies: pip install pygame opencv-python mediapipe --break-system-packages"
echo "4. Test in simulation mode: python gesture_dj.py --sim"
echo "5. Run with hardware: python gesture_dj.py"
echo ""
echo "Done!"
