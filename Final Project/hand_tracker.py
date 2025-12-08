"""
MediaPipe Hand Tracking Module
Handles camera-based hand pose recognition
Owner: Zoe (yzt2)
"""

import time
import math
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
    print("MediaPipe not available - running in simulation mode")


class HandTracker:
    def __init__(self, simulation_mode=False, headless=None):
        """
        Initialize MediaPipe hand and face tracking
        simulation_mode: If True, use keyboard instead of camera
        headless: If True, don't show camera window (auto-detect if None)
        """
        print(f"[HandTracker] MEDIAPIPE_AVAILABLE: {MEDIAPIPE_AVAILABLE}, simulation_mode param: {simulation_mode}")
        self.simulation_mode = simulation_mode or not MEDIAPIPE_AVAILABLE
        
        # Auto-detect headless mode
        if headless is None:
            headless = not bool(os.environ.get('DISPLAY'))
        self.headless = headless
        
        # Hand state
        self.current_pose = None
        self.finger_count = 0
        self.hand_rotation = 0.0
        self.finger_distance = 0.0
        self.gesture_start_time = None
        self.gesture_hold_threshold = 2.0  # 2 seconds hold time for palm/fist
        
        # Mouth blow detection state
        self.mouth_open_ratio = 0.0
        self.blow_detected = False
        self.last_blow_time = 0
        
        if not self.simulation_mode:
            try:
                # Initialize hand tracking
                self.mp_hands = mp.solutions.hands
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=1,
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.5
                )
                
                # Initialize face mesh for mouth detection
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                
                self.mp_draw = mp.solutions.drawing_utils
                
                # Initialize camera - always use index 0
                self.cap = cv2.VideoCapture(0)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                print("MediaPipe hand + face tracking initialized")
            except Exception as e:
                print(f"Failed to initialize MediaPipe: {e}")
                print("Falling back to simulation mode")
                self.simulation_mode = True
        else:
            print("MediaPipe running in simulation mode")
    
    def count_fingers(self, landmarks):
        """
        Count extended fingers based on landmarks
        Returns: 0-5
        """
        if not landmarks:
            return 0
        
        fingers = []
        
        # Thumb (compare tip with IP joint)
        if landmarks[4].x < landmarks[3].x:  # Right hand assumption
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
    
    def get_finger_distance(self, landmarks, image_width=640, image_height=480):
        """
        Calculate distance between thumb and index finger tips
        Used for playback speed control (wider = faster, narrower = slower)
        Returns: 0.0-1.0 normalized distance
        """
        if not landmarks:
            return 0.0
        
        # Get thumb tip (landmark 4) and index finger tip (landmark 8) in pixel coordinates
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        # Convert normalized coordinates to pixel coordinates
        thumbX = int(thumb_tip.x * image_width)
        thumbY = int(thumb_tip.y * image_height)
        indexX = int(index_tip.x * image_width)
        indexY = int(index_tip.y * image_height)
        
        # Calculate Euclidean distance in pixels
        distance = math.hypot(indexX - thumbX, indexY - thumbY)
        
        # Normalize to 0-1 range (50-300 pixels typical range from hand_pose.py)
        # 50 pixels = close (0.0), 300 pixels = far (1.0)
        min_dist = 50
        max_dist = 300
        normalized = (distance - min_dist) / (max_dist - min_dist)
        
        # Clamp to 0-1 range
        return max(0.0, min(1.0, normalized))
    
    def classify_pose(self, finger_count):
        """
        Classify hand pose based on finger count - SIMPLIFIED
        Only palm (light theme) and fist (dark theme)
        """
        if finger_count == 5:
            return 'palm'  # Open palm - Light/day theme
        elif finger_count == 0:
            return 'fist'  # Closed fist - Dark/night theme
        else:
            return 'unknown'  # Ignore other gestures
    
    def check_gesture_hold(self, pose):
        """
        Check if a gesture has been held long enough (2 seconds for palm/fist)
        Returns: True if held long enough, False otherwise
        """
        # Require hold for palm and fist
        requires_hold = pose in ['palm', 'fist']
        
        if not requires_hold:
            return False  # Don't process unknown gestures
        
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
    
    def detect_mouth_blow(self, face_landmarks, image_width, image_height):
        """
        Detect if mouth is open (blowing gesture)
        Uses mouth landmarks to calculate open ratio
        Returns: True if blow detected
        """
        if not face_landmarks:
            return False
        
        try:
            # Mouth landmarks indices (MediaPipe Face Mesh)
            # Upper lip: 13, Lower lip: 14
            # Mouth corners: 61 (left), 291 (right)
            upper_lip = face_landmarks.landmark[13]
            lower_lip = face_landmarks.landmark[14]
            left_corner = face_landmarks.landmark[61]
            right_corner = face_landmarks.landmark[291]
            
            # Calculate vertical mouth opening
            mouth_height = abs(lower_lip.y - upper_lip.y) * image_height
            
            # Calculate horizontal mouth width
            mouth_width = abs(right_corner.x - left_corner.x) * image_width
            
            # Calculate aspect ratio (height/width)
            if mouth_width > 0:
                self.mouth_open_ratio = mouth_height / mouth_width
            else:
                self.mouth_open_ratio = 0
            
            # Detect blow - mouth is relatively wide open (high ratio)
            # Threshold: > 0.5 indicates mouth is open for blowing
            current_time = time.time()
            cooldown = 3.0  # 3 second cooldown between blows
            
            if self.mouth_open_ratio > 0.5 and (current_time - self.last_blow_time) > cooldown:
                self.last_blow_time = current_time
                return True
            
            return False
            
        except Exception as e:
            print(f"[HandTracker] Error detecting mouth blow: {e}")
            return False
    
    def process_frame(self):
        """
        Process one camera frame and extract hand data
        Returns: dict with pose, finger_count, confidence, etc.
        """
        if self.simulation_mode:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Get frame dimensions
        height, width, _ = frame.shape
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process hands with MediaPipe
        hand_results = self.hands.process(rgb_frame)
        
        # Process face with MediaPipe
        face_results = self.face_mesh.process(rgb_frame)
        
        # Check for mouth blow first
        blow_detected = False
        if face_results.multi_face_landmarks:
            face_landmarks = face_results.multi_face_landmarks[0]
            blow_detected = self.detect_mouth_blow(face_landmarks, width, height)
            
            if blow_detected:
                # Draw visual feedback for blow
                cv2.putText(frame, "BLOW DETECTED!", (10, 230),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
        
        if hand_results.multi_hand_landmarks:
            hand_landmarks = hand_results.multi_hand_landmarks[0]
            landmarks = hand_landmarks.landmark
            
            # Count fingers
            finger_count = self.count_fingers(landmarks)
            
            # Classify pose
            pose = self.classify_pose(finger_count)
            
            # Calculate finger distance for playback speed (pass image dimensions)
            finger_distance = self.get_finger_distance(landmarks, width, height)
            
            # Check if gesture held long enough
            gesture_confirmed = self.check_gesture_hold(pose)
            
            # Draw landmarks on frame (for debugging)
            self.mp_draw.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
            )
            
            # Get thumb and index finger positions for visual feedback
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            thumbX = int(thumb_tip.x * width)
            thumbY = int(thumb_tip.y * height)
            indexX = int(index_tip.x * width)
            indexY = int(index_tip.y * height)
            
            # Draw circles on thumb and index finger
            cv2.circle(frame, (thumbX, thumbY), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (indexX, indexY), 15, (255, 0, 255), cv2.FILLED)
            
            # Draw line between thumb and index
            cv2.line(frame, (thumbX, thumbY), (indexX, indexY), (255, 0, 255), 3)
            
            # Calculate center point and distance for display
            cx, cy = (thumbX + indexX) // 2, (thumbY + indexY) // 2
            pixel_distance = math.hypot(indexX - thumbX, indexY - thumbY)
            
            # Display info on frame
            cv2.putText(frame, f"Pose: {pose}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Fingers: {finger_count}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Distance: {int(pixel_distance)}px", (10, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
            cv2.putText(frame, f"Speed: {finger_distance:.2f}", (10, 190),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
            
            if self.gesture_start_time:
                hold_time = time.time() - self.gesture_start_time
                cv2.putText(frame, f"Hold: {hold_time:.1f}s", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            # Show frame (only if not headless)
            if not self.headless:
                try:
                    cv2.imshow('Hand Tracking', frame)
                    cv2.waitKey(1)
                except:
                    pass  # Display error
            
            return {
                'pose': pose,
                'finger_count': finger_count,
                'finger_distance': finger_distance,
                'gesture_confirmed': gesture_confirmed,
                'blow_detected': blow_detected,
                'mouth_open_ratio': self.mouth_open_ratio,
                'confidence': 1.0,
                'timestamp': time.time()
            }
        else:
            # No hand detected, but check for blow
            if blow_detected:
                # Show frame (only if not headless)
                if not self.headless:
                    try:
                        cv2.imshow('Hand Tracking', frame)
                        cv2.waitKey(1)
                    except:
                        pass  # Display error
                
                return {
                    'pose': None,
                    'finger_count': 0,
                    'finger_distance': 0.0,
                    'gesture_confirmed': False,
                    'blow_detected': blow_detected,
                    'mouth_open_ratio': self.mouth_open_ratio,
                    'confidence': 1.0,
                    'timestamp': time.time()
                }
            
            # Nothing detected
            if not self.headless:
                try:
                    cv2.imshow('Hand Tracking', frame)
                    cv2.waitKey(1)
                except:
                    pass  # Display error
            return None
    
    def get_data(self):
        """
        Get current hand tracking data
        """
        return self.process_frame()
    
    def cleanup(self):
        """Release camera resources"""
        if not self.simulation_mode:
            if hasattr(self, 'cap'):
                self.cap.release()
            if not self.headless:
                try:
                    cv2.destroyAllWindows()
                except:
                    pass


class HandTrackingSimulator:
    """
    Keyboard simulator for testing without camera
    """
    def __init__(self):
        self.pending_pose = None
        self.finger_count = 0
        print("\nMediaPipe Simulator Active")
        print("Number keys 0-5: Set finger count")
        print("P: Palm (play)")
        print("F: Fist (resume)")
    
    def inject_pose(self, pose, finger_count):
        """Inject a pose for simulation"""
        self.pending_pose = pose
        self.finger_count = finger_count
    
    def get_data(self):
        """Get simulated hand data"""
        if self.pending_pose:
            data = {
                'pose': self.pending_pose,
                'finger_count': self.finger_count,
                'finger_distance': 0.5,
                'gesture_confirmed': True,  # Instant confirmation in sim
                'confidence': 1.0,
                'timestamp': time.time()
            }
            self.pending_pose = None
            return data
        return None


if __name__ == "__main__":
    # Test mode
    print("MediaPipe Hand Tracking Test Mode")
    print("=" * 40)
    
    tracker = HandTracker(simulation_mode=not MEDIAPIPE_AVAILABLE)
    
    if tracker.simulation_mode:
        print("\nSimulation Mode - Number keys to simulate:")
        print("  0: Fist (resume)")
        print("  1: One finger (track 1)")
        print("  2: Peace sign (effect toggle)")
        print("  3: Three fingers")
        print("  4: Four fingers")
        print("  5: Palm (play)")
        print("  Q: Quit")
        print()
        
        import sys
        import tty
        import termios
        
        def get_key():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        
        try:
            while True:
                key = get_key()
                
                if key.isdigit():
                    count = int(key)
                    if count == 5:
                        print("PALM - (5 fingers) Play")
                    elif count == 0:
                        print("FIST - (0 fingers) Resume")
                    elif count == 1:
                        print("ONE - (1 finger)")
                    elif count == 2:
                        print("PEACE - (2 fingers)")
                    elif count == 3:
                        print("THREE - (3 fingers)")
                    elif count == 4:
                        print("FOUR - (4 fingers)")
                
                elif key.lower() == 'q':
                    print("Quitting...")
                    break
                
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\nStopped")
    
    else:
        # Real camera mode
        print("Monitoring camera... Show hand gestures (Ctrl+C to stop)")
        print("Hold gesture for 3 seconds to confirm")
        try:
            while True:
                data = tracker.get_data()
                if data and data['gesture_confirmed']:
                    print(f"[OK] Confirmed: {data['pose']} ({data['finger_count']} fingers)")
                
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\nStopped")
        finally:
            tracker.cleanup()