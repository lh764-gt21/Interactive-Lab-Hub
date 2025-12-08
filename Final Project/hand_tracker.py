"""
MediaPipe Hand Tracking Module - Simplified
Only tracks: Open Palm (5 fingers) and Closed Fist (0 fingers)
Owner: Zoe (yzt2)
"""

import time
import os

# Disable OpenCV GUI if no display available
if not os.environ.get('DISPLAY'):
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Try to import MediaPipe
try:
    import cv2
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("MediaPipe not available - hand tracking disabled")


class HandTracker:
    """Simplified hand tracker - only palm and fist detection"""
    
    def __init__(self, headless=False):
        """
        Initialize MediaPipe hand tracking
        Args:
            headless: If True, don't show camera window
        """
        self.headless = headless
        self.current_pose = None
        self.gesture_start_time = None
        self.gesture_hold_threshold = 2.5  # 2.5 seconds hold time
        self.simulation_mode = False
        self.last_frame = None  # For web streaming
        
        # Finger pinch detection (thumb + index)
        self.last_pinch_distance = None
        self.pinch_detected = False
        self.pinch_cooldown_time = None
        self.pinch_cooldown_duration = 0.3  # 0.3 seconds between pinches
        self.is_pinching = False
        
        if not MEDIAPIPE_AVAILABLE:
            self.simulation_mode = True
            print("[HandTracker] MediaPipe not available")
            return
        
        try:
            # Initialize MediaPipe Hands
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_draw = mp.solutions.drawing_utils
            
            # Initialize camera
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("[HandTracker] Failed to open camera")
                self.simulation_mode = True
                return
            
            # Lower resolution for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print("[HandTracker] Hand tracking initialized (palm/fist only)")
            
        except Exception as e:
            print(f"[HandTracker] Failed to initialize: {e}")
            self.simulation_mode = True
    
    def detect_finger_pinch(self, landmarks):
        """
        Detect finger pinch gesture (thumb tip + index finger tip)
        Much more reliable than snap!
        Returns: True if pinch just started, False otherwise
        """
        if not landmarks:
            return False
        
        # Check cooldown
        current_time = time.time()
        if self.pinch_cooldown_time and (current_time - self.pinch_cooldown_time) < self.pinch_cooldown_duration:
            return False
        
        # Calculate distance between thumb tip (4) and index finger tip (8)
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        dx = thumb_tip.x - index_tip.x
        dy = thumb_tip.y - index_tip.y
        dz = thumb_tip.z - index_tip.z
        
        distance = (dx**2 + dy**2 + dz**2) ** 0.5
        
        # Pinch threshold - fingers are close together
        pinch_threshold = 0.05  # Very close = pinched
        
        was_pinching = self.is_pinching
        self.is_pinching = distance < pinch_threshold
        
        # Detect pinch start (transition from not pinching to pinching)
        if self.is_pinching and not was_pinching:
            self.pinch_cooldown_time = current_time
            print(f"[Pinch] ✓ INSTANT TRIGGER! Distance: {distance:.3f}")
            return True
        
        return False
    
    def count_fingers(self, landmarks):
        """
        Count extended fingers
        Returns: 0-5
        """
        if not landmarks:
            return 0
        
        fingers = []
        
        # Thumb (compare tip with IP joint)
        if landmarks[4].x < landmarks[3].x:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Other fingers (compare tip with PIP joint)
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks[tip].y < landmarks[pip].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return sum(fingers)
    
    def classify_pose(self, finger_count):
        """
        Classify hand pose - ONLY palm (5) or fist (0)
        Returns: 'palm', 'fist', or 'unknown'
        """
        if finger_count == 5:
            return 'palm'   # Open palm → Light theme
        elif finger_count == 0:
            return 'fist'   # Closed fist → Dark theme
        else:
            return 'unknown'  # Ignore other finger counts
    
    def check_gesture_hold(self, pose):
        """
        Check if gesture held for 2 seconds
        Returns: True if confirmed, False otherwise
        """
        if pose not in ['palm', 'fist']:
            return False
        
        if pose != self.current_pose:
            # New gesture started
            self.current_pose = pose
            self.gesture_start_time = time.time()
            return False
        
        # Same gesture continues
        if self.gesture_start_time:
            hold_duration = time.time() - self.gesture_start_time
            if hold_duration >= self.gesture_hold_threshold:
                # Reset timer after successful hold
                self.gesture_start_time = None
                return True
        
        return False
    
    def get_data(self):
        """
        Process camera frame and return hand data
        Returns: dict with pose info or None
        """
        if self.simulation_mode:
            return None
        
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
        
        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = hand_landmarks.landmark
            
            # Count fingers and classify
            finger_count = self.count_fingers(landmarks)
            pose = self.classify_pose(finger_count)
            gesture_confirmed = self.check_gesture_hold(pose)
            
            # Detect finger pinch for scratching
            pinch_detected = self.detect_finger_pinch(landmarks)
            
            # Draw landmarks on frame
            self.mp_draw.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
            )
            
            # Add text overlay
            cv2.putText(frame, f"Pose: {pose}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Fingers: {finger_count}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Distance: {hand_distance:.2f}", (10, 190),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            # Show scratch intensity
            if scratch_data['should_scratch']:
                scratch_text = "SCRATCHING!"
                cv2.putText(frame, scratch_text, (10, 230),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
            
            if self.gesture_start_time:
                hold_time = time.time() - self.gesture_start_time
                cv2.putText(frame, f"Hold: {hold_time:.1f}s", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            if gesture_confirmed:
                cv2.putText(frame, "THEME CHANGE!", (10, 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 3)
            
            # Show pinch detection
            if pinch_detected:
                cv2.putText(frame, "PINCH!", (10, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 3)
            elif self.is_pinching:
                cv2.putText(frame, "Pinching...", (10, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Save frame for web streaming
            self.last_frame = frame.copy()
            
            # Show window (only if not headless)
            if not self.headless:
                try:
                    cv2.imshow('Hand Tracking', frame)
                    cv2.waitKey(1)
                except:
                    pass
            
            return {
                'pose': pose,
                'finger_count': finger_count,
                'gesture_confirmed': gesture_confirmed,
                'pinch_detected': pinch_detected,
                'is_pinching': self.is_pinching,
                'timestamp': time.time()
            }
        
        # No hand detected - save plain frame
        self.last_frame = frame.copy()
        
            if not self.headless:
                try:
                    cv2.imshow('Hand Tracking', frame)
                    cv2.waitKey(1)
            except:
                pass
        
        return None
    
    def cleanup(self):
        """Release camera resources"""
        if not self.simulation_mode and hasattr(self, 'cap'):
            self.cap.release()
            try:
                cv2.destroyAllWindows()
            except:
                pass


if __name__ == "__main__":
    print("Hand Tracking Test")
    print("=" * 50)
    print("Show gestures:")
    print("  Open Palm (5 fingers) → Light theme")
    print("  Closed Fist (0 fingers) → Dark theme")
    print("Hold gesture for 2 seconds to confirm")
    print("Press Ctrl+C to quit")
    print("=" * 50)
    
    tracker = HandTracker(headless=False)
    
    if tracker.simulation_mode:
        print("\nCamera not available")
    else:
        try:
            while True:
                data = tracker.get_data()
                if data and data['gesture_confirmed']:
                    print(f"✓ Confirmed: {data['pose'].upper()} ({data['finger_count']} fingers)")
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopped")
        finally:
            tracker.cleanup()
