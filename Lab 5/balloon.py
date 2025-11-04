import cv2
import time
import numpy as np
import HandTrackingModule as htm
import random
import math

################################
wCam, hCam = 640, 480
################################

class Balloon:
    def __init__(self, x, y, balloon_type):
        self.x = x
        self.y = y
        self.balloon_type = balloon_type
        self.popped = False
        self.grabbed = False
        self.action_timer = 0
        
        if balloon_type == "red":
            self.color = (0, 0, 255)  # Red - need to POP
            self.points_correct = 3  # Points for popping
            self.points_wrong = -5   # Penalty for grabbing
            self.speed = random.uniform(1.2, 2.2)
            self.radius = 35
            self.action_text = "POP ME!"
        elif balloon_type == "blue":
            self.color = (255, 0, 0)  # Blue - need to GRAB
            self.points_correct = 3  # Points for grabbing
            self.points_wrong = -5   # Penalty for popping
            self.speed = random.uniform(1.0, 2.0)
            self.radius = 35
            self.action_text = "GRAB ME!"
        elif balloon_type == "black":
            self.color = (0, 0, 0)  # Black - avoid!
            self.points_correct = -5  # Always penalty
            self.points_wrong = -5
            self.speed = random.uniform(1.5, 2.5)
            self.radius = 35
            self.action_text = "AVOID!"
    
    def update(self):
        if not self.popped and not self.grabbed:
            self.y -= self.speed
            
            if self.y < -self.radius:
                self.reset()
        else:
            self.action_timer -= 1
            if self.action_timer <= 0:
                self.reset()
    
    def reset(self):
        self.x = random.randint(self.radius + 50, wCam - self.radius - 50)
        self.y = hCam + random.randint(0, 200)
        self.popped = False
        self.grabbed = False
        self.action_timer = 0
        
        # Weighted probabilities
        rand = random.random()
        if rand < 0.45:  # 45% red
            self.balloon_type = "red"
            self.color = (0, 0, 255)
            self.points_correct = 3
            self.points_wrong = -5
            self.speed = random.uniform(1.2, 2.2)
            self.radius = 35
            self.action_text = "POP ME!"
        elif rand < 0.90:  # 45% blue
            self.balloon_type = "blue"
            self.color = (255, 0, 0)
            self.points_correct = 3
            self.points_wrong = -5
            self.speed = random.uniform(1.0, 2.0)
            self.radius = 35
            self.action_text = "GRAB ME!"
        else:  # 10% black
            self.balloon_type = "black"
            self.color = (0, 0, 0)
            self.points_correct = -5
            self.points_wrong = -5
            self.speed = random.uniform(1.5, 2.5)
            self.radius = 35
            self.action_text = "AVOID!"
    
    def draw(self, img):
        if not self.popped and not self.grabbed:
            # Draw balloon body
            cv2.circle(img, (int(self.x), int(self.y)), self.radius, self.color, -1)
            
            # Draw X on black balloons
            if self.balloon_type == "black":
                x_size = 20
                cv2.line(img, 
                        (int(self.x - x_size), int(self.y - x_size)),
                        (int(self.x + x_size), int(self.y + x_size)),
                        (255, 255, 255), 4)
                cv2.line(img, 
                        (int(self.x + x_size), int(self.y - x_size)),
                        (int(self.x - x_size), int(self.y + x_size)),
                        (255, 255, 255), 4)
            else:
                # Draw balloon shine
                cv2.circle(img, (int(self.x - 10), int(self.y - 10)), 8, (255, 255, 255), -1)
            
            # Draw balloon string
            string_end_y = min(int(self.y + self.radius + 40), hCam)
            cv2.line(img, (int(self.x), int(self.y + self.radius)), 
                    (int(self.x), string_end_y), (100, 100, 100), 2)
            
            # Draw action hint text
            text_size = cv2.getTextSize(self.action_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            text_x = int(self.x - text_size[0] / 2)
            text_y = int(self.y - self.radius - 10)
            cv2.putText(img, self.action_text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
        elif self.action_timer > 0:
            # Draw action feedback
            if self.popped:
                cv2.circle(img, (int(self.x), int(self.y)), self.radius + (30 - self.action_timer), 
                          self.color, 2)
                cv2.putText(img, "POP!", (int(self.x - 30), int(self.y)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.color, 2)
            elif self.grabbed:
                # Draw grab effect - shrinking circle
                shrink_size = int(self.radius * (self.action_timer / 30))
                cv2.circle(img, (int(self.x), int(self.y)), shrink_size, self.color, -1)
                cv2.putText(img, "GRAB!", (int(self.x - 35), int(self.y)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.color, 2)
    
    def check_collision(self, finger_x, finger_y):
        if not self.popped and not self.grabbed:
            distance = np.sqrt((self.x - finger_x)**2 + (self.y - finger_y)**2)
            if distance < self.radius + 20:
                return True
        return False
    
    def pop(self):
        if not self.popped and not self.grabbed:
            self.popped = True
            self.action_timer = 30
    
    def grab(self):
        if not self.popped and not self.grabbed:
            self.grabbed = True
            self.action_timer = 30


def detect_gesture(lmList):
    if len(lmList) == 0:
        return "none"
    
    thumb_tip = lmList[4]
    index_tip = lmList[8]
    middle_tip = lmList[12]
    ring_tip = lmList[16]
    pinky_tip = lmList[20]
    
    index_base = lmList[5]
    middle_base = lmList[9]
    ring_base = lmList[13]
    pinky_base = lmList[17]
    wrist = lmList[0]
    
    def is_finger_extended(tip, base):
        return tip[2] < base[2]
    
    # Check thumb extension (different logic - horizontal)
    thumb_extended = abs(thumb_tip[1] - wrist[1]) > abs(index_base[1] - wrist[1])
    
    index_extended = is_finger_extended(index_tip, index_base)
    middle_extended = is_finger_extended(middle_tip, middle_base)
    ring_extended = is_finger_extended(ring_tip, ring_base)
    pinky_extended = is_finger_extended(pinky_tip, pinky_base)
    
    # Count extended fingers (excluding thumb for now)
    extended_fingers = sum([index_extended, middle_extended, ring_extended, pinky_extended])
    
    # Open palm: 4+ fingers extended (all fingers open)
    if extended_fingers >= 4:
        return "palm"
    # Point: only index finger extended
    elif index_extended and not middle_extended and not ring_extended and not pinky_extended:
        return "point"
    else:
        return "other"


# Initialize
print("Initializing camera...")
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

if not cap.isOpened():
    print("ERROR: Could not open camera")
    exit()

print("Camera opened successfully!")
pTime = 0

print("Initializing hand detector...")
hand_detector = htm.handDetector()
print("Hand detector ready!")

# Create balloons
balloon_types = ["red", "red", "red", "blue", "blue", "blue", "black"]
balloons = []
num_balloons = 7

print("Creating balloons...")
for i in range(num_balloons):
    x = random.randint(80, wCam - 80)
    y = hCam + i * 100
    balloon_type = random.choice(balloon_types)
    balloons.append(Balloon(x, y, balloon_type))

score = 10
last_action_time = 0
game_active = True
game_over = False
paused = False

current_gesture = "none"

print("\n=== Balloon Pop & Grab Game ===")
print("GESTURES:")
print("  POINT (index finger only) = Pop red balloons")
print("  OPEN PALM (all fingers extended) = Grab blue balloons")
print("\nRULES:")
print("  Red balloons: POINT to pop = +3 points")
print("  Blue balloons: PALM to grab = +3 points")
print("  Black balloons: AVOID! = -5 points")
print("  Wrong action = -5 points penalty!")
print("\nPress 'q' to quit, 'r' to restart, 'p' to pause")
print("\nStarting game...")

frame_count = 0
feedback_message = ""
feedback_timer = 0
feedback_color = (255, 255, 255)

while True:
    success, img = cap.read()
    if not success:
        continue
    
    frame_count += 1
    img = cv2.flip(img, 1)
    
    if not game_over and not paused:
        # Find hands
        img = hand_detector.findHands(img, draw=False)
        lmList = hand_detector.findPosition(img, draw=False)
        
        # Detect hand gesture
        if len(lmList) != 0:
            current_gesture = detect_gesture(lmList)
            
            if current_gesture == "point":
                # Pointing - for popping RED balloons
                finger_pos = (lmList[8][1], lmList[8][2])
                indicator_color = (0, 255, 0)
                
                # Draw finger indicator
                cv2.circle(img, finger_pos, 20, indicator_color, 3)
                cv2.circle(img, finger_pos, 5, (255, 255, 255), -1)
                cv2.putText(img, "POP", (finger_pos[0] - 20, finger_pos[1] - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, indicator_color, 2)
                
                # Check collisions
                current_time = time.time()
                if current_time - last_action_time > 0.4:
                    for balloon in balloons:
                        if balloon.check_collision(finger_pos[0], finger_pos[1]):
                            balloon.pop()
                            
                            # Scoring logic
                            if balloon.balloon_type == "red":
                                score += balloon.points_correct
                                feedback_message = f"+{balloon.points_correct} CORRECT!"
                                feedback_color = (0, 255, 0)
                                print(f"Popped red balloon: +{balloon.points_correct}")
                            elif balloon.balloon_type == "blue":
                                score += balloon.points_wrong
                                feedback_message = f"{balloon.points_wrong} WRONG ACTION!"
                                feedback_color = (0, 0, 255)
                                print(f"Popped blue balloon (should grab): {balloon.points_wrong}")
                            else:  # black
                                score += balloon.points_correct
                                feedback_message = f"{balloon.points_correct} HIT BLACK!"
                                feedback_color = (0, 0, 255)
                                print(f"Hit black balloon: {balloon.points_correct}")
                            
                            feedback_timer = 60
                            last_action_time = current_time
                            
                            if score <= 0:
                                score = 0
                                game_over = True
                                print("GAME OVER!")
                            break
            
            elif current_gesture == "palm":
                # Open palm - for grabbing BLUE balloons
                palm_center = (lmList[9][1], lmList[9][2])
                indicator_color = (255, 100, 255)
                
                # Draw palm indicator - larger circle
                cv2.circle(img, palm_center, 40, indicator_color, 3)
                cv2.circle(img, palm_center, 10, (255, 255, 255), -1)
                cv2.putText(img, "GRAB", (palm_center[0] - 30, palm_center[1] - 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, indicator_color, 2)
                
                # Draw extended fingers for visual feedback
                for finger_tip in [lmList[8], lmList[12], lmList[16], lmList[20]]:
                    cv2.circle(img, (finger_tip[1], finger_tip[2]), 8, indicator_color, -1)
                
                # Check collisions
                current_time = time.time()
                if current_time - last_action_time > 0.4:
                    for balloon in balloons:
                        if balloon.check_collision(palm_center[0], palm_center[1]):
                            balloon.grab()
                            
                            # Scoring logic
                            if balloon.balloon_type == "blue":
                                score += balloon.points_correct
                                feedback_message = f"+{balloon.points_correct} CORRECT!"
                                feedback_color = (0, 255, 0)
                                print(f"Grabbed blue balloon: +{balloon.points_correct}")
                            elif balloon.balloon_type == "red":
                                score += balloon.points_wrong
                                feedback_message = f"{balloon.points_wrong} WRONG ACTION!"
                                feedback_color = (0, 0, 255)
                                print(f"Grabbed red balloon (should pop): {balloon.points_wrong}")
                            else:  # black
                                score += balloon.points_correct
                                feedback_message = f"{balloon.points_correct} HIT BLACK!"
                                feedback_color = (0, 0, 255)
                                print(f"Hit black balloon: {balloon.points_correct}")
                            
                            feedback_timer = 60
                            last_action_time = current_time
                            
                            if score <= 0:
                                score = 0
                                game_over = True
                                print("GAME OVER!")
                            break
        
        # Update balloons
        for balloon in balloons:
            balloon.update()
            balloon.draw(img)
        
        # Draw UI
        cv2.rectangle(img, (10, 10), (220, 100), (0, 0, 0), -1)
        cv2.rectangle(img, (10, 10), (220, 100), (255, 255, 255), 2)
        cv2.putText(img, f'Score: {score}', (20, 55), cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (0, 255, 0), 3)
        
        # Gesture indicator
        gesture_display = "Point" if current_gesture == "point" else "Palm" if current_gesture == "palm" else "None"
        cv2.putText(img, f'Action: {gesture_display}', (wCam - 200, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Feedback message
        if feedback_timer > 0:
            text_size = cv2.getTextSize(feedback_message, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
            text_x = (wCam - text_size[0]) // 2
            cv2.putText(img, feedback_message, (text_x, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, feedback_color, 3)
            feedback_timer -= 1
        
    elif paused:
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (wCam, hCam), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, img, 0.5, 0, img)
        
        cv2.putText(img, 'PAUSED', (wCam//2 - 80, hCam//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4)
        cv2.putText(img, "Press 'P' to continue", (wCam//2 - 120, hCam//2 + 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    else:
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (wCam, hCam), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
        
        cv2.putText(img, 'GAME OVER!', (wCam//2 - 180, hCam//2 - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
        cv2.putText(img, f'Final Score: {score}', (wCam//2 - 150, hCam//2 + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        cv2.putText(img, "Press 'R' to restart", (wCam//2 - 150, hCam//2 + 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(img, "Press 'Q' to quit", (wCam//2 - 130, hCam//2 + 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, hCam - 20), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (200, 200, 200), 2)
    
    cv2.imshow("Balloon Pop & Grab Game", img)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("\nQuitting...")
        break
    elif key == ord('r'):
        score = 10
        game_over = False
        feedback_message = ""
        feedback_timer = 0
        for i, balloon in enumerate(balloons):
            balloon.y = hCam + i * 100
            balloon.reset()