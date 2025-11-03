# Observant Systems


#### Collaborators: Charlotte Lin (hl2575), Zoe Tseng (yzt2), Le-En Huang (lh764) 
#### Use of AI for this lab: Claude Sonnet4 for image creation and debugging instructions for the code.


For lab this week, we focus on creating interactive systems that can detect and respond to events or stimuli in the environment of the Pi, like the Boat Detector we mentioned in lecture. 
Your **observant device** could, for example, count items, find objects, recognize an event or continuously monitor a room.

This lab will help you think through the design of observant systems, particularly corner cases that the algorithms need to be aware of.


### Deliverables for this lab are:
1. Show pictures, videos of the "sense-making" algorithms you tried.
1. Show a video of how you embed one of these algorithms into your observant system.
1. Test, characterize your interactive device. Show faults in the detection and how the system handled it.

## Overview
Building upon the paper-airplane metaphor (we're understanding the material of machine learning for design), here are the four sections of the lab activity:

A) [Play](#part-a)

B) [Fold](#part-b)

C) [Flight test](#part-c)

D) [Reflect](#part-d)

---

### Part A
### Play with different sense-making algorithms.

### 1. Testing Teachable Machine
Class 1: Heart emoji
![Screenshot 2025-11-02 at 10.28.14 PM](https://hackmd.io/_uploads/SJxjZjrJWg.png)

Class 2: Thumbs up
![Screenshot 2025-11-02 at 10.27.43 PM](https://hackmd.io/_uploads/ryDi-iHk-l.png)

[Video demo](https://youtu.be/MrGmYIaht3A)

### 2. Testing Moondream

**1. When does it do what it is supposed to do?**

The system performs as intended when: The webcam captures a clear, well-lit image of a single hand showing a thumbs-up or thumbs-down gesture.
The background is uncluttered, and the hand is centered in the frame.Under these conditions, Moondream is generally able to interpret the gesture correctly.

**2. When and why does it fail?**

The system fails under several conditions:
- Camera-level issues: It can be difficult to capture only the hand gesture, especially if the camera position is not ideal.
- Model-level issues:
    - The model sometimes fails to interpret the image or produces incomplete responses. For example, hands that are partially out of frame often lead to uncertain classifications.
![moondream_error copy](https://hackmd.io/_uploads/H11kpsB1Zg.png)

    - The Raspberry Pi occasionally shuts down due to high processing load or memory limits. This could be due to model latency or overload.
![pi_shutdown copy](https://hackmd.io/_uploads/rkTdhiBkWx.png)


**3. Other scenarios that could cause problems**
Additional sources of error include:
- Multiple hands or people in the frame, leading to ambiguity about which hand to classify.
- Unusual camera angles, such as a side view of the thumb, which confuse the model.
- Non-human hands (e.g., statues, drawings, or printed images) that can lead to misclassification.

**4. Optimizations to the sense-making algorithm**
- One potential improvement involves refining the prompt design.
- We experimented with zero-shot classification phrasing, such as:
```
“Classify this image into exactly one category: [‘thumbs up’, ‘thumbs down’, ‘none’]. Respond with one of these words only.”
```
However, even with simplified prompts, the model frequently returned no output or an empty response (the terminal simply printed “done”).
This suggests that prompt tuning alone is insufficient to achieve reliable results for this type of visual classification.

**5. How we modified the system to address these issues**

During testing, we found that while Moondream could understand and describe visual scenes, it has high latency and is very likely to misclassification when applied to simple gesture recognition tasks. Because our task involves detecting a specific, well-defined visual pattern, we decided to use lighter, more specialized models that offer faster response times and higher interpretive accuracy.

- **Teachable Machine** allows quick training and deployment of custom gesture classifiers with less latency.
- **MediaPipe** is more efficient, on-device hand-landmark detection that can reliably infer gestures without requiring cloud inference or text-based reasoning.

We think the interactive system becomes more responsive, deterministic, and robust under real-time conditions if we use the above 2 models instead of `moondream`.

### Part B
### Construct a simple interaction.

* Pick one of the models you have tried, and experiment with prototyping an interaction.
* This can be as simple as the boat detector shown in lecture.
* Try out different interaction outputs and inputs.

**\*\*\*Describe and detail the interaction, as well as your experimentation here.\*\*\***

Model: MediaPipe
Demo video: [link](https://youtu.be/ZWbaBjM_1b8)
How to run: 
```
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python balloon.py
```
Description: 

A simple Balloon popping game with your finger!
There are different colors of balloon, try getting as many points as you can without popping the "toxic" balloon with black X on it. 

If you lose all your points, you can always retry for chances of winning more points.


### Part C
### Test the interaction prototype

Now flight test your interactive prototype and **note down your observations**:
For example:
1. When does it what it is supposed to do?
2. When does it fail?
3. When it fails, why does it fail?
4. Based on the behavior you have seen, what other scenarios could cause problems?


#### Happy Case
- Works well in consistent, moderate lighting conditions
- Accurately detects finger position when hand is clearly visible and within 1-2 feet of camera
- Collision detection is responsive when finger clearly overlaps with balloon
- Score tracking and balloon respawning work consistently

#### Tricky Case
- Fails to detect finger when lighting is too dim or too bright
- **Misses collisions** when finger **moves very quickly** across balloons
- Blue balloons move so fast that they're difficult to hit, sometimes passing by before system can register collision

#### Failure analysis
- **Lighting issues**: MediaPipe's hand detection model is trained on well-lit conditions
- **Latency**: Small delay between hand movement, detection, processing, and collision check
- **Tracking loss**: MediaPipe temporarily loses hand pointers during fast movements

#### Potential issues
- Multiple hands in frame could confuse which finger to track
- Similar skin-toned objects in background might interfere with hand detection
- Camera angle/position changes would affect calibration
- Reflective surfaces or windows in background could create false detections
- User wearing gloves or hand accessories might reduce detection accuracy

---
<!-- 
**\*\*\*Think about someone using the system. Describe how you think this will work.\*\*\***
1. Are they aware of the uncertainties in the system?
2. How bad would they be impacted by a miss classification?
3. How could change your interactive system to address this?
4. Are there optimizations you can try to do on your sense-making algorithm.
 -->
 
#### 1. Are they aware of the uncertainties in the system?
Currently, users may not fully understand the system's limitations:
- No visual/audio feedback when hand tracking is lost
- No indication when lighting conditions are suboptimal
- Unclear why some apparent hits don't register

#### 2. How bad would they be impacted by a misclassification?
This is a gameplay where there are hardly ever harms that users will be experiencing.
However, there are likely things that will discourage users from playing more:
- **Missed collision**: Frustrating but minor - user just tries again
- **False collision**: More problematic - could lose points if it's a toxic balloon (-15 points)

#### 3. How could you change your interactive system to address this?

**Visual Feedback Improvements:**
- Add visual feedback for successful hits (particle effects, sound)
- Display "Hand Lost" warning when tracking fails
- Show collision radius around finger pointer for transparency

**Collision Detection Refinements:**
- Add confirmation requirement (hold finger on balloon for 0.2s)

**Gameplay Adjustments:**
- Implement combo system - consecutive hits reward bonus points

#### 4. Are there optimizations you can try on your sense-making algorithm?

**Detection Improvements:**
- Use multiple hand landmarks (not just fingertip) to improve collision accuracy
- Add temporal averaging - only register collision if detected for 2+ consecutive frames
- Dynamically adjust collision radius based on balloon speed
- Scale difficulty based on user's success rate

**Comprehensive Gameplay Adjustments:**
- Consider using both index finger AND thumb pinch gesture for more deliberate popping
- Add gesture controls (e.g., open palm = pause, fist = shield)
- Implement two-handed mode for advanced players

---

### Part D
### Characterize your own Observant system

Now that you have experimented with one or more of these sense-making systems **characterize their behavior**.
During the lecture, we mentioned questions to help characterize a material:
* What can you use X for?
* What is a good environment for X?
* What is a bad environment for X?
* When will X break?
* When it breaks how will X break?
* What are other properties/behaviors of X?
* How does X feel?

**\*\*\*Include a short video demonstrating the answers to these questions.\*\*\***

#### Teachable Machine
| **Question** | **Your Observations** |
|--------------|----------------------|
| **What can you use X for?** | Object classification, Gesture classification |
| **What is a good environment for X?** | Static, controlled, not dynamic, generally where object in question can be placed front and center without a lot of noise. |
| **What is a bad environment for X?** | People are walking around, more than one objects present, not enough light or too much light - see this [short clip](https://youtu.be/6_ayZN7uc_o) where the light is shadowing some gestures. |
| **When will X break? How will it break?** | **1. Complexity:** The model works pretty well when there are only two classes - thumbs up and heart emoji. When I added two more classes, thumbs down and ok, the model starts having confusions between different classes. There are some possible explanations of this, one could be that the newly added gestures are more complex in nature. One could also argue having more classes generally adds complexity to the trained model. See this [video](https://youtu.be/DPIkheJOZJA) that shows some of that confusion and less confidence in classifying gestures.<br><br>**2. Data bias:** When I first trained the model, I noticed it worked best when I recorded my gestures front and center, and avoid showing face/clothes or any other background that could add to the confusion. I tried adding *some* pictures in the "ok" gesture class with my face showing and my jacket. See this [video](https://youtu.be/FgUPexjaoDQ) that demonstrates how this will break the model because whenever I gesture with this jacket, no matter what I do, it will automatically be classified as "ok".<br><br>**3. Not enough data:** I noticed when I add a class to the model, if I only recorded my gesture from a certain angle, there is a high chance if I rotate it 90 degrees or hold it at a distance that's closer/further from the camera, it will break the classification. |
| **What are other properties/behaviors of X?** | **Visual/Sensory affordance:** ![Screenshot 2025-11-02 at 11.21.07 PM (2)](https://hackmd.io/_uploads/SygApjrJZx.png)<br>I discovered there are some emojis/gestures that would trigger an actual emoji visual effect on screen. This is pretty neat.<br><br>**Perceptible affordance:** There is also a nice results visualization section where instant feedback is given to the user interacting with the system. User should be able to learn what works and what doesn't in a natural way. |
| **How does X feel?** | Teachable Machine feels pleasant, interactive, iterative, and positive. It encourages user to interact with a model, train a model, and adjust it based on feedback. Impressive stuff! |

### Part 2.

Following exploration and reflection from Part 1, finish building your interactive system, and demonstrate it in use with a video.

**\*\*\*Include a short video demonstrating the finished result.\*\*\***