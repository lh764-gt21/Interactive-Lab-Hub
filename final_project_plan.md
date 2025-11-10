# Final Project Plan

### Resources

[final project instructions link](https://github.com/IRL-CT/Developing-and-Designing-Interactive-Devices/blob/2025Fall/FinalProject.md)
[past projects link](https://github.com/IRL-CT/Developing-and-Designing-Interactive-Devices/wiki/Previous-Final-Projects)

#### Collaborators: Charlotte Lin (hl2575), Zoe Tseng (yzt2), Le-En Huang (lh764) 
#### Use of AI for this lab: Claude Sonnet4 for code development, debugging, and project planning.

---

## Proposed Work Split

| Team Member | Primary Module | Hardware Components | Key Responsibilities | Deliverables |
|-------------|---------------|---------------------|---------------------|--------------|
| **Charlotte Lin (hl2575)** | APDS Gesture Control | APDS-9960 sensor | • Gesture recognition (swipe left/right/up/down)<br>• Proximity sensing for continuous effects<br>• Sensor calibration and debouncing<br>• Map gestures to audio parameters | • Gesture event handler<br>• Clean API for gesture data<br>• Testing/simulation mode |
| **Zoe Tseng (yzt2)** | MediaPipe Hand Pose | Pi Camera | • Real-time hand tracking<br>• Pose classification (open/fist/counting)<br>• Hand rotation detection<br>• Performance optimization | • Hand state data output<br>• Pose recognition API<br>• Keyboard fallback mode |
| **Eva Huang (lh764)** | Audio Engine + Visual Feedback | PiTFT display + speakers + LEDs + browser interface | • Audio sample management & playback<br>• Real-time mixing and effects<br>• Multi-modal feedback (display/LED/audio)<br>• System integration coordinator | • Audio output system<br>• Visual feedback interface<br>• Integration framework |

---

## Big Idea

Create **"Gesture DJ"** – a hand-controlled sound toy that combines APDS gesture sensing and MediaPipe hand-pose recognition to create an embodied music interaction experience. Users control sound loops, effects, and mixing through intuitive hand movements and gestures, with **multi-modal feedback** including visual display, LED indicators, and audio cues that respond immediately to gestures.

**Core Concept:** Transform physical gestures into musical expression—swipe to switch tracks, raise your hand to increase volume, make a fist to add distortion, open your palm to trigger effects. The system responds with immediate audio changes and **rich, clear feedback** through multiple channels, creating an intuitive, playful DJ experience.

### Interaction Flow
1. **Start System** → Display shows ready state with available loops/sounds, LEDs indicate system status
2. **APDS Gestures** → Quick swipes and proximity control for discrete actions (track selection, volume)
3. **Hand Poses** → Expressive control for continuous effects (filters, pitch, reverb)
4. **Multi-Modal Feedback:**
   - **PiTFT Display:** Current track/mode/gesture recognition
   - **LED Indicators:** Real-time beat visualization, active effects, gesture confirmation
   - **Audio Feedback:** Confirmation sounds for successful gestures
   - **Browser Interface (fallback):** Larger visualization if PiTFT proves too small
5. **Audio Output** → Layered loops and effects respond immediately to gestures

![Untitled diagram-2025-11-09-203615](https://hackmd.io/_uploads/B18vouAJWl.png)

---

## Timeline

### Week 1: Component Development & Early Experimentation (INSTRUCTOR FEEDBACK: Test input methods early!)

1. **Days 1-2:** Parts check and **input method comparison**
   - Verify all hardware works independently
   - **CRITICAL: Test both APDS and MediaPipe early to determine which works better for DJ control**
   - Set up shared code repository structure
   - Define integration interfaces (data formats, shared state)

2. **Days 3-5:** Module development + **feedback system prototyping**
   - **APDS Module:** Get gesture recognition working, calibrate sensitivity
   - **MediaPipe Module:** Implement hand tracking, test pose classification
   - **Audio Module:** Set up pygame.mixer, load sample sounds, test playback
   - **Feedback Module:** Prototype LED patterns and PiTFT display layouts

3. **Days 6-7:** Individual testing with simulation modes + **input method decision**
   - Each person creates keyboard fallbacks for testing
   - Document module APIs and data outputs
   - **DECIDE: Which input method (APDS vs MediaPipe) feels more natural for DJ control?**
   - May choose to focus on one primary input with the other as secondary/fallback

### Week 2: Integration & Refinement

4. **Days 8-9:** Pairwise integration
   - Primary gesture input → Audio connection
   - Secondary gesture input → Audio connection
   - Test gesture-to-sound mappings
   - **Add LED feedback for gesture confirmation**

5. **Days 10-11:** Full system integration + **feedback enhancement**
   - Combine all three modules
   - Resolve timing conflicts and performance issues
   - Add visual feedback for all gestures on PiTFT
   - **Test if PiTFT is sufficient or if browser interface is needed**

6. **Days 12-13:** User experience polish + **feedback optimization**
   - Refine gesture sensitivity and response
   - **Improve feedback clarity across all channels (LED, display, audio)**
   - Test visibility of feedback in demo lighting conditions
   - Add "DJ modes" or preset configurations
   - Implement browser interface if PiTFT proves too small

### Week 3: Final Testing & Documentation

7. **Days 14-15:** Build physical enclosure/setup
   - Clean cable management
   - Position sensors and camera optimally
   - **Optimize LED placement for visibility**
   - Make system demo-ready

8. **Days 16-17:** User testing and refinement
   - Test with at least 3-5 users
   - **Specifically test feedback clarity: Can users tell what's happening?**
   - Gather feedback on intuitiveness
   - Make final adjustments

9. **Day 18:** Final documentation and demo prep
   - Record demo video
   - Finalize project documentation
   - Prepare presentation

---

## Parts Needed

**Already Have:**
* Raspberry Pi 4
* PiTFT display (ST7789)
* APDS-9960 gesture sensor
* Pi Camera (for MediaPipe)
* Speakers/audio output

**Need to Acquire:**
* **LEDs (NeoPixel strip or individual LEDs)** - for enhanced visual feedback
* Breadboard/jumper wires for LED connections

**Optional Enhancements:**
* USB microphone (for audio sampling - stretch goal)
* External monitor/screen if browser interface is needed

---

## Technical Architecture

### Module 1: APDS Gesture Control
**Inputs:** APDS-9960 sensor data

**Outputs:** 
```python
{
  'gesture': 'swipe_left' | 'swipe_right' | 'swipe_up' | 'swipe_down',
  'proximity': 0-255,
  'timestamp': float
}
```

**Gesture Mappings:**
- Swipe Left/Right: Previous/Next track
- Swipe Up/Down: Volume up/down
- Proximity: Filter cutoff frequency (closer = more filter)

**Note:** Based on early testing, this may become primary or secondary input method.

### Module 2: MediaPipe Hand Pose
**Inputs:** Pi Camera video stream

**Outputs:**
```python
{
  'pose': 'open' | 'fist' | 'counting',
  'finger_count': 0-5,
  'hand_rotation': -180 to 180,
  'confidence': 0.0-1.0,
  'timestamp': float
}
```

**Pose Mappings:**
- Open Palm: Play/resume
- Closed Fist: Pause + distortion effect
- Finger Count: Select loop layer (1-5)
- Hand Rotation: Pitch bend or reverb amount

**Note:** Based on early testing, this may become primary or secondary input method.

### Module 3: Audio Engine + Multi-Modal Feedback
**Inputs:** Gesture data from both modules

**Outputs:** 
- Audio output (mixed loops + effects)
- PiTFT display (current state, gesture recognition)
- LED indicators (beat visualization, active effects)
- Browser interface (optional, if PiTFT too small)
- Audio confirmation sounds

**Responsibilities:**
- Maintain audio state (active loops, effect levels)
- Mix multiple audio streams in real-time
- Render feedback across multiple channels:
  - **PiTFT Display:** Text/graphics showing current track, mode, detected gestures
  - **LED Feedback:** Color-coded status (e.g., red=recording, green=playing, blue=effect active), beat-reactive patterns
  - **Audio Cues:** Short confirmation sounds when gestures are recognized
  - **Browser Interface (fallback):** Flask server serving larger visualization
- Coordinate timing between modules

**Feedback Design Principles (addressing instructor concern):**
- **Immediate:** Feedback appears within 100ms of gesture
- **Clear:** Multiple channels ensure DJ always knows system state
- **Scalable:** Can switch to browser interface if PiTFT insufficient
- **Visible:** LED placement optimized for demo viewing angles

---

## Risks/Contingencies

### Technical Risks

1. **Input Method Uncertainty:** Not sure whether APDS or MediaPipe works better for DJ control
   - **Mitigation:** **TEST BOTH EARLY (Days 1-2)** to determine which feels more natural
   - **Fallback:** Use one as primary input, other as secondary/enhancement

2. **PiTFT Too Small for Feedback:** Display may not be visible enough for demo/DJ use
   - **Mitigation:** Add LED indicators and audio cues as primary feedback
   - **Fallback:** Implement browser-based interface with Flask server for larger display

3. **Performance Issues:** Running MediaPipe + audio processing + multiple feedback channels may strain the Pi
   - **Mitigation:** Optimize frame rate, use lower resolution for hand tracking, simplify LED patterns
   - **Fallback:** Reduce to one primary input method, simplify visual feedback

4. **Gesture Conflicts:** APDS and hand movements might interfere with each other
   - **Mitigation:** Early testing will help determine if both can coexist
   - **Fallback:** Choose one primary input method based on Day 1-2 testing

5. **Audio Latency:** Delay between gesture and sound response
   - **Mitigation:** Use lightweight audio library, pre-load all samples
   - **Fallback:** Accept some latency, make it feel "intentional"

6. **Integration Complexity:** Three separate modules + multiple feedback channels may be difficult to synchronize
   - **Mitigation:** Regular integration checkpoints, shared state manager
   - **Fallback:** Simplify to 2-module system with single feedback channel

### Hardware Risks

7. **Camera Lighting Dependency:** MediaPipe requires good lighting
   - **Mitigation:** Test in demo environment early, add LED if needed
   - **Fallback:** If MediaPipe unreliable, use APDS as primary input

8. **Sensor Placement:** Finding optimal position for both sensors + camera + LEDs
   - **Mitigation:** Prototype enclosure early, test different configurations
   - **Fallback:** Separate stations (user moves between sensors)

9. **LED Visibility:** LEDs may not be bright enough or positioned poorly
   - **Mitigation:** Test LED brightness and placement early
   - **Fallback:** Use browser interface as primary feedback

---

## Fall-back Plan

**Level 1 - Input Method Simplification:**
Based on early testing (Days 1-2), choose the more reliable input method (APDS or MediaPipe) as primary, use the other as secondary enhancement only.

**Level 2 - Feedback Channel Reduction:**
If multi-modal feedback proves too complex, focus on 2 channels: LEDs (primary visual) + Audio (confirmation), with PiTFT showing minimal state info.

**Level 3 - Browser Interface Only:**
If PiTFT proves too small and LED implementation is problematic, focus all visual feedback on a browser-based interface served from the Pi.

**Level 4 - Single Input, Single Output:**
Simplify to one gesture input method (likely APDS for reliability) + Audio output + simple browser visualization.


**Success Criteria:** We consider the project successful if:
- Users can control at least 3 distinct audio parameters through gestures
- System responds within 200ms of gesture recognition
- **DJ receives clear, immediate feedback through at least 2 channels (visual + audio)**
- **Input method decision made by Day 2 based on real testing**
- Demo runs reliably for 3+ minutes without crashes

---

## Deliverables
- [x] Project plan: Big idea, timeline, parts needed, fall-back plan.
- [ ] Functioning project: The finished project should be a device, system, interface, etc. that people can interact with.
- [ ] Documentation of design process
- [ ] Archive of all code, design patterns, etc. used in the final design. (As with labs, the standard should be that the documentation would allow you to recreate your project if you woke up with amnesia.)
- [ ] Video of someone using your project
- [ ] Reflections on process (What have you learned or wish you knew at the start?)
- [ ] Group work distribution questionnaire
