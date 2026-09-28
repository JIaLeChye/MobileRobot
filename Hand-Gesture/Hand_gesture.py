import cv2
import mediapipe as mp
import numpy as np
import os
import time
import urllib.request
from picamera2 import Picamera2
from libcamera import controls, Transform 
from RPi_Robot_Hat_Lib import RobotController

# ─── MediaPipe 1.x Tasks API ────────────────────────────────────────────────
# MediaPipe 1.0+ uses mp.tasks instead of mp.solutions
BaseOptions        = mp.tasks.BaseOptions
HandLandmarker     = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode  = mp.tasks.vision.RunningMode

# Hand landmark indices (same as before)
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),          # Thumb
    (0,5),(5,6),(6,7),(7,8),          # Index
    (5,9),(9,10),(10,11),(11,12),     # Middle
    (9,13),(13,14),(14,15),(15,16),   # Ring
    (13,17),(17,18),(18,19),(19,20),  # Pinky
    (0,17)                            # Palm base
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"


def download_model():
    """Download the hand landmarker model if not already present."""
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading hand landmarker model to {MODEL_PATH} ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded.")
    else:
        print("Hand landmarker model already present.")


def init(): 
    """
    Initialize motor controller, encoder, mediapipe hands and camera 
    """
    global landmarker, cap, Motor

    Motor = RobotController()

    # Download model if needed
    download_model()

    # Initialize MediaPipe HandLandmarker (new Tasks API)
    # VIDEO mode uses timestamps for temporal smoothing → much better accuracy
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )
    landmarker = HandLandmarker.create_from_options(options)

    # Start video capture
    cap = Picamera2(0)
    cap.configure(cap.create_preview_configuration(
        main={"format": 'XRGB8888', "size": (640, 480)},
        transform=Transform(vflip=1)
    ))
    cap.start()
    cap.set_controls({"AfMode": controls.AfModeEnum.Continuous})

    vertical   = 2
    horizontal = 1
    Motor.set_servo(vertical,   40)
    Motor.set_servo(horizontal, 92)


def draw_landmarks(frame_bgr, hand_landmarks_list):
    """Draw hand landmarks and connections on the frame (replaces mp_drawing)."""
    h, w = frame_bgr.shape[:2]
    for hand_landmarks in hand_landmarks_list:
        # Convert normalised coords to pixel coords
        pts = [
            (int(lm.x * w), int(lm.y * h))
            for lm in hand_landmarks
        ]
        # Draw connections
        for start, end in HAND_CONNECTIONS:
            cv2.line(frame_bgr, pts[start], pts[end], (0, 255, 0), 2)
        # Draw landmark dots
        for pt in pts:
            cv2.circle(frame_bgr, pt, 4, (255, 0, 0), -1)


# Define function to control the robot car
def control_car(hand_landmarks):
    global Motor
    # Extract the position of landmark 9
    landmark_9 = hand_landmarks[9]
        
    # Get normalized coordinates of landmark 9
    landmark_9_x = landmark_9.x
    landmark_9_y = landmark_9.y
        
    # Calculate direction and distance based on landmark 9 position
    # Example: Determine if landmark 9 is to the left, right, or center
    motorFreq = 30  # set the speed of the motor to 30
    if landmark_9_x < 0.3:
        direction = "right"
    elif landmark_9_x > 0.7:
        direction = "left"
    else:
        direction = "center"
        
    # Example: Determine if landmark 9 is closer or farther away
    if landmark_9_y < 0.4:
        distance = "close"
    elif landmark_9_y > 0.6:
        distance = "far"
    else:
        distance = "medium"
        
    # Map direction and distance to control commands for the car
    # Example: Adjust speed and steering based on direction and distance
    if direction == "left":
        print("Turn left")
        Motor.move(speed=0, turn=-30)
    elif direction == "right":
        print("Turn right")
        Motor.move(speed=0, turn=30)
    else:
        # Move the car forward or stop based on distance
        if distance == "close":
            print("Stop")
            Motor.Brake()
        else:
            print("Move forward")
            Motor.Forward(motorFreq)


def main():
    init()
    global landmarker, cap, Motor

    # Main loop for robot car control
    start_time = time.monotonic()
    while True:
        # Read frame from video capture
        frame = cap.capture_array()

        # XRGB8888 from picamera2 is 4-channel (B,G,R,X order).
        # Slice off the X channel and force a contiguous copy (required by OpenCV 5).
        frame_bgr = np.ascontiguousarray(frame[:, :, :3])  # B,G,R — contiguous

        # MediaPipe needs an RGB image — flip channel order
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        # Convert to MediaPipe Image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb
        )

        # VIDEO mode requires a monotonically increasing timestamp in ms
        timestamp_ms = int((time.monotonic() - start_time) * 1000)

        # Detect hand landmarks using MediaPipe HandLandmarker
        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        # Draw hand landmarks on the frame and control the car
        if result.hand_landmarks:
            draw_landmarks(frame_bgr, result.hand_landmarks)
            for hand_landmarks in result.hand_landmarks:
                control_car(hand_landmarks)
        else:
            Motor.Brake()

        # Display the frame with hand landmarks
        cv2.imshow('Hand Gesture Control', frame_bgr)

        # Exit loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def cleanup():
    """Explicit cleanup — must be called before Python shuts down modules."""
    global landmarker, cap, Motor
    try:
        Motor.Brake()
        Motor.cleanup()
    except Exception:
        pass
    try:
        landmarker.close()   # Prevents MediaPipe __del__ NoneType error
    except Exception:
        pass
    try:
        cap.stop()
    except Exception:
        pass
    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
