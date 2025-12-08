# DJ Scratch Effect - Quick Start

## What Changed?

✅ **NEW**: Finger snap to trigger scratch!  
✅ **Much simpler** - just snap your fingers 👌  
✅ **Better performance** - camera feed is now smooth  
✅ Music pauses during scratch, resumes automatically 🎧

## Full Demo

```bash
python demo.py
```

Then open `http://localhost:5000` in your browser.

## How to Scratch

1. **Show your hand** to the camera
2. **Snap your fingers** (thumb + middle finger)
3. **Watch and listen**:
   - Camera shows "SNAP!" overlay
   - Vinyl indicator flashes
   - Music pauses
   - Random scratch sound plays
   - Music automatically resumes

## What You'll See

### Camera Feed (Top-Right)
- Hand tracking with landmarks
- **"SNAP!"** when finger snap detected
- Smooth performance (no more lag!)

### Scratch Indicator (Bottom-Left)
- Vinyl record visual
- **Flashes briefly** when you snap

### Status Bar (Bottom)
- **SCRATCH**: Shows `SNAP!` briefly, then `--`

## Snap Techniques

1. **Quick Snap**: Fast snap for instant scratch
2. **Double Snap**: Snap twice quickly (0.5s cooldown between)
3. **Rhythm Snaps**: Snap to the beat of the music
4. **Combo**: Mix snaps with theme changes (palm/fist)

## Sound Behavior

- **Random scratch sound** (1 of 4 samples)
- **Music pauses** during scratch
- **Auto-resumes** when scratch ends
- **Cooldown**: 0.5 seconds between snaps

## Still Works

- ✋ **Open Palm** (5 fingers, hold 2.5 sec) → Light theme + swoosh
- ✊ **Closed Fist** (0 fingers, hold 2.5 sec) → Dark theme + swoosh
- 🎵 **All music controls** still functional
- 🎶 **Music pauses during scratch** and resumes from same position

## Troubleshooting

**Snap not triggering?**
- Actually **touch** thumb and middle finger together
- Snap more **deliberately**
- Wait 0.5 seconds between snaps (cooldown)
- Make sure hand is visible to camera

**No sound?**
- Click the page first (browser autoplay policy)
- Check `effects/swoosh.mp3` exists
- Check browser volume

## Performance Improvements

✅ **Camera resolution**: 640x480 → 480x360 (44% fewer pixels)  
✅ **JPEG quality**: 85 → 70 (smaller files)  
✅ **Frame skipping**: Every other frame (50% reduction)  
✅ **Result**: Smooth, responsive camera feed!

## Technical Details

See `PERFORMANCE_IMPROVEMENTS.md` for:
- Complete implementation details
- Finger snap detection algorithm
- Performance tuning options
- Troubleshooting guide

---

**Have fun scratching! 🎶✨**
