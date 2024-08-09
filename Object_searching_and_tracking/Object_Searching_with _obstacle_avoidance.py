import threading
import queue
import tflite_runtime.interpreter as tflite
import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls
import os
import time

from PCA9685_MC import Motor_Controller
from Motor_Encoder import Encoder
from Ultrasonic_sens import Ultrasonic 

# Initialize the libraries for the movements of the robot
motor = Motor_Controller()
enc = Encoder(ODISPLAY=True)
usonic = Ultrasonic()

# Set Camera Position
horizontal = 1
vertical = 0

motor.servoPulse(horizontal, 1250)
motor.servoPulse(vertical, 1050)

# Verify the model and label files 
model_folder = 'tensorflow_lite_examples'
model_file = '/mobilenet_v2.tflite'
model_path = model_folder + model_file
label_file = '/coco_labels.txt'
label_path = model_folder + label_file

if not os.path.exists(model_path):
    print("Model file not found")
    exit()
else:
    print("Model file found at:", model_path)

if not os.path.exists(label_path):
    print("Label file not found")
    exit()
else:
    print("Label file found at:", label_path)

# Decode the label file
with open(label_path, 'r') as f:
    lines = f.readlines()
    labels = {int(line.strip().split(maxsplit=1)[0]): line.strip().split(maxsplit=1)[1] for line in lines}

# Start the camera
frame_height = 240
frame_width = 320
cam = Picamera2()
cam.configure(cam.create_preview_configuration(main={"format": 'XRGB8888', "size": (frame_width, frame_height)}))
cam.start()
print("Camera started")

# Continuous Auto Focus
cam.set_controls({"AfMode": controls.AfModeEnum.Continuous})

obstacle_avoid = threading.Event() 
shutdown_event = threading.Event()
cleanup_event = threading.Event()

interpreter = tflite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

detected_objects_info = []
tracking_object = None
object_queue = queue.Queue()

# Initialize the tracker globally
tracker = cv2.TrackerKCF_create()
init_tracker = False
tracking_failed = False
frame_lock = threading.Lock()
frame_rgb = None
tracking_object_features = None  # Track object features for comparison

def detect_objects(frame, update_queue=True):
    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if rgb_frame.size == 0:
            raise ValueError("Empty frame received")
        resized_frame = cv2.resize(rgb_frame, (width, height))
        input_data = np.expand_dims(resized_frame, axis=0)

        if input_details[0]['dtype'] == np.float32:
            input_data = (np.float32(input_data) - 127.5) / 127.5

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        detected_boxes = interpreter.get_tensor(output_details[0]['index'])[0]
        detected_classes = interpreter.get_tensor(output_details[1]['index'])[0]
        detected_scores = interpreter.get_tensor(output_details[2]['index'])[0]
        num_boxes = int(interpreter.get_tensor(output_details[3]['index'])[0])

        detected_objects = []
        for i in range(num_boxes):
            if detected_scores[i] > 0.5:
                ymin, xmin, ymax, xmax = detected_boxes[i]
                im_height, im_width, _ = frame.shape
                left = int(xmin * im_width)
                right = int(xmax * im_width)
                top = int(ymin * im_height)
                bottom = int(ymax * im_height)
                class_id = int(detected_classes[i])
                label = labels.get(class_id, 'Unknown')
                detected_objects.append((label, (left, top, right, bottom)))
                cv2.rectangle(rgb_frame, (left, top), (right, bottom), (255, 0, 0), 2)
                cv2.imshow("Object Detection", rgb_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                

        if update_queue:
            object_queue.put(detected_objects)

       
        return detected_objects
   
        
    except Exception as e:
        print(f"Error in detect_objects: {e}")
        return []

def extract_features(frame, bbox):
    """Extract features from the bounding box in the frame."""
    x, y, w, h = bbox
    roi = frame[y:y+h, x:x+w]
    hist = cv2.calcHist([roi], [0, 1, 2], None, [16, 16, 16], [0, 256, 0, 256, 0, 256])
    return hist.flatten()

def match_features(features1, features2, threshold=0.7):
    """Compare features using correlation to check if they match."""
    correlation = cv2.compareHist(features1, features2, cv2.HISTCMP_CORREL)
    return correlation >= threshold

def capture_and_detect():
    global detected_objects_info, tracking_object, init_tracker, tracking_failed, frame_rgb, tracker, tracking_object_features
    print("Starting frame capture and object detection")
    frame_count = 0
    start_time = time.time()

    while not shutdown_event.is_set():
        obstacle_avoid.clear()
        try:
            frame = cam.capture_array()
            if frame.size == 0:
                continue
            frame_count += 1
            with frame_lock:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Call detect_objects to update queue
            detect_objects(frame_rgb, update_queue=True)

            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time
            cv2.putText(frame_rgb, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            if tracking_object and not tracking_failed:
                try:
                    with frame_lock:
                        success, box = tracker.update(frame_rgb)
                    if success:
                        left, top, w, h = [int(v) for v in box]
                        right = left + w
                        bottom = top + h
                        with frame_lock:
                            cv2.rectangle(frame_rgb, (left, top), (right, bottom), (255, 0, 0), 2)
                            cv2.putText(frame_rgb, tracking_object[0], (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                            centerPoint = (int((left + right) / 2), int((top + bottom) / 2))
                            cv2.circle(frame_rgb, centerPoint, 5, (0, 0, 255), -1)

                    else:
                        print("Tracking failed, waiting for object to re-enter frame")
                        tracking_failed = True
                except cv2.error as e:
                    print(f"OpenCV error: {e}")
                    tracking_failed = True

            if tracking_failed:
                detected_objects_info = detect_objects(frame_rgb, update_queue=False)
                for label, (left, top, right, bottom) in detected_objects_info:
                    if label == tracking_object[0]:
                        print(f"Similar Object {label} re-entered the frame")
                        new_features = extract_features(frame_rgb, (left, top, right-left, bottom-top))
                        if tracking_object_features is not None and match_features(new_features, tracking_object_features):
                            with frame_lock:
                                tracker = cv2.TrackerKCF_create()
                                tracker.init(frame_rgb, (left, top, right-left, bottom-top))
                            tracking_failed = False
                            break

            disp_frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            cv2.imshow("Object Detection and Tracking", disp_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(f"Error in capture_and_detect: {e}")
            break

    print("Stopped frame capture and object detection")
    cleanup_event.set()  # Signal the cleanup event

def user_input_listener():
    global detected_objects_info, tracking_object, init_tracker, tracking_failed, frame_rgb, tracker, tracking_object_features
    while not shutdown_event.is_set():
        input("Press Enter to display detected objects...")
        detected_objects_info = object_queue.get()
        if detected_objects_info:
            print("Detected Objects:")
            for idx, obj in enumerate(detected_objects_info):
                print(f"{idx}: {obj[0]}")
            choice = input("Enter the object number to track (or 'q' to quit): ")
            if choice.isdigit() and int(choice) < len(detected_objects_info):
                idx = int(choice)
                tracking_object = detected_objects_info[idx]
                init_tracker = False
                tracking_failed = False
                print(f"Now tracking: {tracking_object[0]}")
                label, (left, top, right, bottom) = tracking_object
                with frame_lock:
                    tracker = cv2.TrackerKCF_create()
                    tracker.init(frame_rgb, (left, top, right-left, bottom-top))
                    tracking_object_features = extract_features(frame_rgb, (left, top, right-left, bottom-top))
            elif choice.lower() == 'q':
                shutdown_event.set()
                break

def obstacle_avoidance():
    Speed = 25
    rotation_speed = 20
    threshold = 30
    min_thresh_dist = 15

    while not shutdown_event.is_set():
        if not obstacle_avoid.is_set():
            motor.Brake()
            continue

        left, front, right = usonic.distances()
        time.sleep(0.1)
        if left is not None and front is not None and right is not None:
            if front < threshold:
                if front <= min_thresh_dist:
                    motor.Backward(Speed)
                elif left < threshold and right < threshold:
                    motor.Backward(Speed)
                    time.sleep(0.1)
                elif left < threshold:
                    motor.Clock_Rotate(rotation_speed)
                    time.sleep(0.1)
                elif right < threshold:
                    motor.AntiClock_Rotate(rotation_speed)
                    time.sleep(0.1)
                else:
                    if right > left:
                        motor.Clock_Rotate(rotation_speed)
                        time.sleep(0.1)
                    elif left > right:
                        motor.AntiClock_Rotate(rotation_speed)
                        time.sleep(0.1)
            elif left < threshold:
                motor.Clock_Rotate(Speed)
            elif right < threshold:
                motor.AntiClock_Rotate(Speed)
            else:
                motor.Forward(Speed)
        else:
            print("No data received")
            motor.Brake()
            time.sleep(1)

def cleanup():
    print("Performing cleanup...")
    cam.stop()
    cv2.destroyAllWindows()
    motor.Brake()  # Ensure you have a cleanup method for Motor_Controller
    exit()

# Start the threads
capture_thread = threading.Thread(target=capture_and_detect)
input_thread = threading.Thread(target=user_input_listener)
obstacle_thread = threading.Thread(target=obstacle_avoidance)

capture_thread.start()
input_thread.start()
obstacle_thread.start()

try:
    capture_thread.join()
    input_thread.join()
    obstacle_thread.join()
except KeyboardInterrupt:
    shutdown_event.set()

finally:
    cleanup_event.wait()
    cleanup()
    exit()
