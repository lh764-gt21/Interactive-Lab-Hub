"""
Gesture DJ Core Logic
Handles audio, gestures, voice control, and mood lighting.
No display or web server logic.
"""

import time
import cv2
import mediapipe as mp
from audio_engine import AudioEngine
from apds_gesture import APDSGesture
from mpr121_touch import MPR121Touch
from voice_control import VoiceControl
from mood_lighting import MoodLighting


class SimpleHandTracker:
    """Simplified hand tracker - hands only"""
    def __init__(self, headless=False):
        self.headless = headless
        self.current_pose = None
        self.gesture_start_time = None
        self.gesture_hold_threshold = 2.5
        self.simulation_mode = False
        self.last_frame = None
        
        # Peace sign detection
        self.peace_detected = False
        self.peace_cooldown_time = None
        self.peace_cooldown_duration = 0.5
        
        try:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_draw = mp.solutions.drawing_utils
            
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("[HandTracker] Failed to open camera")
                self.simulation_mode = True
                return
            
            # Lower resolution for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Test frame
            ret, test_frame = self.cap.read()
            if not ret or test_frame is None:
                print("[HandTracker] Camera opened but cannot read frames")
                self.simulation_mode = True
                return
                
        except Exception as e:
            print(f"[HandTracker] Failed to initialize: {e}")
            self.simulation_mode = True
    
    def detect_peace_sign(self, landmarks, finger_count):
        """Detect peace sign gesture (✌️ two fingers up)"""
        if not landmarks:
            return False
        
        current_time = time.time()
        if self.peace_cooldown_time and (current_time - self.peace_cooldown_time) < self.peace_cooldown_duration:
            return False
        
        # Peace sign = exactly 2 fingers extended
        if finger_count == 2:
            # Verify index and middle fingers are up
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            index_pip = landmarks[6]
            middle_pip = landmarks[10]
            
            index_up = index_tip.y < index_pip.y
            middle_up = middle_tip.y < middle_pip.y
            
            if index_up and middle_up:
                self.peace_cooldown_time = current_time
                return True
        
        return False
    
    def count_fingers(self, landmarks):
        if not landmarks:
            return 0
        fingers = []
        # Thumb
        if landmarks[4].x < landmarks[3].x:
            fingers.append(1)
        else:
            fingers.append(0)
        # Other fingers
        for tip, pip in [(8,6), (12,10), (16,14), (20,18)]:
            if landmarks[tip].y < landmarks[pip].y:
                fingers.append(1)
            else:
                fingers.append(0)
        return sum(fingers)
    
    def classify_pose(self, finger_count):
        if finger_count == 5:
            return 'palm'
        elif finger_count == 0:
            return 'fist'
        else:
            return 'unknown'
    
    def check_gesture_hold(self, pose):
        if pose not in ['palm', 'fist']:
            return False
        if pose != self.current_pose:
            self.current_pose = pose
            self.gesture_start_time = time.time()
            return False
        if self.gesture_start_time:
            hold_duration = time.time() - self.gesture_start_time
            if hold_duration >= self.gesture_hold_threshold:
                self.gesture_start_time = None
                return True
        return False
    
    def get_data(self):
        if self.simulation_mode:
            return None
        
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = hand_landmarks.landmark
            
            finger_count = self.count_fingers(landmarks)
            pose = self.classify_pose(finger_count)
            gesture_confirmed = self.check_gesture_hold(pose)
            peace_detected = self.detect_peace_sign(landmarks, finger_count)
            
            # ALWAYS draw landmarks (for streaming)
            height, width, _ = frame.shape
            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            cv2.putText(frame, f"Pose: {pose}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Fingers: {finger_count}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if peace_detected:
                cv2.putText(frame, "PEACE SIGN!", (10, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 3)
            
            if self.gesture_start_time:
                hold_time = time.time() - self.gesture_start_time
                cv2.putText(frame, f"Hold: {hold_time:.1f}s", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            if gesture_confirmed:
                cv2.putText(frame, "CONFIRMED!", (10, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
            
            # Save frame AFTER drawing
            self.last_frame = frame.copy()
            
            # Show window only if not headless
            if not self.headless:
                try:
                    cv2.imshow('Hand Tracking', frame)
                    cv2.waitKey(5)
                except:
                    pass
            
            return {
                'pose': pose,
                'finger_count': finger_count,
                'gesture_confirmed': gesture_confirmed,
                'peace_detected': peace_detected,
                'timestamp': time.time()
            }
        
        # No hand - save plain frame
        self.last_frame = frame.copy()
        
        if not self.headless:
            try:
                cv2.imshow('Hand Tracking', frame)
                cv2.waitKey(5)
            except:
                pass
        
        return None
    
    def cleanup(self):
        if not self.simulation_mode and hasattr(self, 'cap'):
            self.cap.release()
            try:
                cv2.destroyAllWindows()
            except:
                pass


class GestureDJCore:
    """Core business logic for Gesture DJ - no UI/display code"""
    
    def __init__(self, enable_camera=True, headless_camera=False):
        """
        Initialize core Gesture DJ logic
        Args:
            enable_camera: Enable MediaPipe hand tracking
            headless_camera: Run camera without window
        """
        print("[Core] Initializing Gesture DJ Core...")
        
        self.running = False
        self.last_pose_processed = None
        
        # Audio engine
        self.audio = AudioEngine(tracks_dir="tracks", effects_dir="effects")
        
        # Hardware controls
        self.apds = APDSGesture()
        self.mpr121 = MPR121Touch()
        self.voice = VoiceControl()
        
        # MediaPipe hand tracking
        if enable_camera:
            self.hand_tracker = SimpleHandTracker(headless=headless_camera)
            if not self.hand_tracker.simulation_mode:
                print("[Core] Hand tracking enabled")
            else:
                self.hand_tracker = None
                print("[Core] Hand tracking disabled (camera failed)")
        else:
            self.hand_tracker = None
            print("[Core] Hand tracking disabled")
        
        # Mood lighting
        self.mood_lighting = MoodLighting()
        
        # Load first track
        self.audio.load_track()
        
        print("[Core] Initialization complete")
    
    def handle_apds_gesture(self, gesture):
        """Process APDS gesture"""
        if not gesture:
            return None
        
        print(f"[APDS] {gesture}")
        
        if gesture == 'swipe_right':
            self.audio.stop()
            track = self.audio.next_track()
            self.audio.play()
            return {'type': 'track_change', 'track': track, 'action': 'next'}
        
        elif gesture == 'swipe_left':
            self.audio.stop()
            track = self.audio.prev_track()
            self.audio.play()
            return {'type': 'track_change', 'track': track, 'action': 'prev'}
        
        elif gesture == 'swipe_up':
            volume = self.audio.volume_up(0.1)
            return {'type': 'volume_change', 'volume': volume, 'action': 'up'}
        
        elif gesture == 'swipe_down':
            volume = self.audio.volume_down(0.1)
            return {'type': 'volume_change', 'volume': volume, 'action': 'down'}
        
        return None
    
    def handle_mpr121_touch(self, action):
        """Process MPR121 touch"""
        if not action:
            return None
        
        if action['type'] == 'track':
            track_num = action['value']
            print(f"[MPR121] Track {track_num}")
            self.audio.stop()
            track = self.audio.select_track(track_num)
            if track:
                self.audio.play()
            return {'type': 'track_select', 'track': track}
        
        elif action['type'] == 'control':
            if action['value'] == 'play_pause':
                if self.audio.is_paused:
                    self.audio.resume()
                    return {'type': 'playback', 'action': 'resume'}
                elif self.audio.is_playing:
                    self.audio.pause()
                    return {'type': 'playback', 'action': 'pause'}
                else:
                    self.audio.play()
                    return {'type': 'playback', 'action': 'play'}
            
            elif action['value'] == 'stop':
                self.audio.stop()
                self.audio.load_track()
                return {'type': 'playback', 'action': 'stop'}
        
        return None
    
    def handle_voice_command(self, command):
        """Process voice command"""
        if not command:
            return None
        
        print(f"[Voice] {command}")
        
        if command == 'play':
            if not self.audio.is_playing or self.audio.is_paused:
                if self.audio.is_paused:
                    self.audio.resume()
                else:
                    self.audio.play()
                return {'type': 'playback', 'action': 'play'}
        
        elif command == 'pause':
            if self.audio.is_playing and not self.audio.is_paused:
                self.audio.pause()
                return {'type': 'playback', 'action': 'pause'}
        
        return None
    
    def handle_hand_gesture(self, hand_data):
        """Process MediaPipe hand gesture for mood lighting or scratch"""
        if not hand_data:
            return None
        
        pose = hand_data.get('pose')
        gesture_confirmed = hand_data.get('gesture_confirmed', False)
        peace_detected = hand_data.get('peace_detected', False)
        
        # Priority 1: Check for peace sign (scratch effect)
        if peace_detected:
            print(f"[Gesture] PEACE SIGN detected! Playing scratch effect...")
            self.audio.play_scratch_effect()
            return {'type': 'scratch_event', 'action': 'peace'}
        
        # Priority 2: Check for theme change gestures (palm/fist)
        if gesture_confirmed and pose != self.last_pose_processed:
            if pose in ['palm', 'fist']:
                print(f"[Gesture] {pose.upper()} confirmed")
                
                mood_changed = self.mood_lighting.set_mood_from_gesture(pose)
                
                if mood_changed:
                    # Play swoosh sound effect on theme change
                    self.audio.play_effect("swoosh")
                    print(f"[Audio] Playing swoosh effect for theme change")
                    
                    mood = self.mood_lighting.get_current_mood()
                    self.last_pose_processed = pose
                    
                    return {
                        'type': 'mood_change',
                        'pose': pose,
                        'mood': mood,
                        'mood_state': self.mood_lighting.get_state()
                    }
        
        return None
    
    def get_state(self):
        """Get current state of all systems"""
        audio_state = self.audio.get_state()
        mood_state = self.mood_lighting.get_state()
        
        # Get peace sign detection if available
        peace_detected = False
        if self.hand_tracker and not self.hand_tracker.simulation_mode:
            peace_detected = self.hand_tracker.peace_detected
        
        return {
            **audio_state,
            'mood': mood_state,
            'peace_detected': peace_detected
        }
    
    def cleanup(self):
        """Clean up resources"""
        print("[Core] Cleaning up...")
        self.running = False
        
        self.audio.stop()
        
        if hasattr(self, 'voice'):
            self.voice.stop()
        
        if self.hand_tracker:
            self.hand_tracker.cleanup()
        
        print("[Core] Cleanup complete")

