## Tensorflow Lite Library
import tflite_runtime.interpreter as tflite

## For Image processing 
import cv2
import numpy as np

## To capture the frames from the camera
from picamera2 import Picamera2
from libcamera import controls, Transform

## For validation of the model and label files 
import os
import urllib.request
import shutil
import errno

## To get the accurate time 
import time 

## Control the Servo Pan Tilt HAT 
from RPi_Robot_Hat_Lib import RobotController 
# Verify the model and label files
model_folder = 'tensorflow_lite_examples'
model_file = 'mobilenet_v2.tflite'
model_path = os.path.join(model_folder, model_file)
label_file = 'coco_labels.txt'
label_path = os.path.join(model_folder, label_file)

# Remote base URL (raw GitHub)
remote_base = 'https://github.com/raspberrypi/picamera2/raw/main/examples/tensorflow'

def ensure_dir_exists(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def download_if_missing(local_path, remote_name):
    """Download remote_name from remote_base to local_path if it doesn't exist."""
    if os.path.exists(local_path):
        print(f"Found: {local_path}")
        return True

    ensure_dir_exists(os.path.dirname(local_path))
    remote_url = f"{remote_base}/{remote_name}"
    print(f"File not found locally: {local_path}\nAttempting to download from: {remote_url}")
    try:
        with urllib.request.urlopen(remote_url) as response, open(local_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"Downloaded {remote_name} to {local_path}")
        return True
    except Exception as e:
        print(f"Failed to download {remote_name}: {e}")
        return False

# Ensure both files exist (try download if missing)
ok_model = download_if_missing(model_path, model_file)
ok_label = download_if_missing(label_path, label_file)

if not ok_model:
    print("Model file missing and could not be downloaded. Exiting.")
    exit(1)

if not ok_label:
    print("Label file missing and could not be downloaded. Exiting.")
    exit(1)

# Decode the label file
def load_labels(path):
    labels = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                try:
                    idx = int(parts[0])
                    labels[idx] = parts[1]
                except ValueError:
                    # Not starting with index, try to use incremental indexing
                    pass
            else:
                # If the file doesn't contain numeric prefixes, build a list-like mapping
                # keep adding with next index
                next_idx = max(labels.keys()) + 1 if labels else 0
                labels[next_idx] = parts[0]
    return labels

labels = load_labels(label_path)


## Initialise the Motor Controler Library 
Motor = RobotController() 

##  Control the Pna Tilt HAT using the motor controller
# Set PanTilt and servo channels
vertical = 2
horizontal = 1
Motor.set_servo(vertical, 80)
Motor.set_servo(horizontal, 90)

# Start the camera
frame_height = 480
frame_width = 640
cam = Picamera2()
cam.configure(cam.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)},transform=Transform(vflip=1)))
cam.start()
cam.set_controls({"AfMode": controls.AfModeEnum.Continuous})



# Object Detection function
def object_detection():
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    
    
    while True:
        frame = cam.capture_array()
        t_start = time.time()
        fps = 0
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
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

        for i in range(num_boxes):
            if detected_scores[i] > 0.5:
                ymin, xmin, ymax, xmax = detected_boxes[i]
                im_height, im_width, _ = frame.shape
                left = int(xmin * im_width)
                right = int(xmax * im_width)
                top = int(ymin * im_height)
                bottom = int(ymax * im_height)

                center_x = int((left + right) // 2)
                center_y = int((top + bottom) // 2)
                print("Coordinates: ", "\nX: ", center_x, "\nY: ", center_y)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                # Ensure detected class index is within the range of labels
                class_id = int(detected_classes[i])
                if class_id in labels:
                    label = labels[class_id]
                else:
                    label = 'Unknown'

                # Debugging output to verify label and class index
                print(f"Detected class ID: {class_id}, Label: {label}, Score: {detected_scores[i]}")

                cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2) 

        fps += 1
        mfps = fps / (time.time() - t_start)
        cv2.putText(frame, "FPS : " + str(int(mfps)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow("main", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

try:
    if __name__ == '__main__':
        object_detection()
except KeyboardInterrupt:
    cam.stop()
    Motor.cleanup()
    print("Exiting")
    exit()