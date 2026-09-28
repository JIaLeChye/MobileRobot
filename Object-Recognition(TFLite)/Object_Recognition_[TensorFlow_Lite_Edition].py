## TensorFlow Lite Object Detection
## Uses ai_edge_litert (new LiteRT package) with fallback to tf.lite.Interpreter
try:
    from ai_edge_litert.interpreter import Interpreter as LiteInterpreter
except ImportError:
    # Fallback: tf.lite.Interpreter (available in tensorflow>=2.x)
    import tensorflow as tf
    LiteInterpreter = tf.lite.Interpreter

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

## To get the accurate time
import time

## Control the Servo Pan Tilt HAT
from RPi_Robot_Hat_Lib import RobotController


## ─── Model & label paths ─────────────────────────────────────────────────────
model_folder = 'tensorflow_lite_examples'
model_file   = 'mobilenet_v2.tflite'
model_path   = os.path.join(model_folder, model_file)
label_file   = 'coco_labels.txt'
label_path   = os.path.join(model_folder, label_file)

# Remote base URL (raw GitHub — picamera2 example assets)
remote_base = 'https://github.com/raspberrypi/picamera2/raw/main/examples/tensorflow'

SCORE_THRESHOLD = 0.5   # Minimum confidence to display a detection


## ─── File download helper ────────────────────────────────────────────────────

def download_if_missing(local_path, remote_name):
    """Download remote_name from remote_base to local_path if it doesn't exist."""
    if os.path.exists(local_path):
        print(f"Found: {local_path}")
        return True

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    remote_url = f"{remote_base}/{remote_name}"
    print(f"File not found locally: {local_path}\nDownloading from: {remote_url}")
    try:
        with urllib.request.urlopen(remote_url) as response, open(local_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"Downloaded {remote_name} to {local_path}")
        return True
    except Exception as e:
        print(f"Failed to download {remote_name}: {e}")
        return False


## ─── Ensure model and label files are present ────────────────────────────────

ok_model = download_if_missing(model_path, model_file)
ok_label = download_if_missing(label_path, label_file)

if not ok_model:
    print("Model file missing and could not be downloaded. Exiting.")
    exit(1)

if not ok_label:
    print("Label file missing and could not be downloaded. Exiting.")
    exit(1)


## ─── Label loader ────────────────────────────────────────────────────────────

def load_labels(path):
    """Parse the label file and return a dict {class_id: label_name}."""
    labels = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                try:
                    labels[int(parts[0])] = parts[1]
                except ValueError:
                    pass
            else:
                next_idx = max(labels.keys()) + 1 if labels else 0
                labels[next_idx] = parts[0]
    return labels


labels = load_labels(label_path)


## ─── Motor and servo initialisation ─────────────────────────────────────────

Motor = RobotController()

vertical   = 2
horizontal = 1
Motor.set_servo(vertical,   80)
Motor.set_servo(horizontal, 90)


## ─── Camera setup ────────────────────────────────────────────────────────────

frame_height = 480
frame_width  = 640

cam = Picamera2()
cam.configure(cam.create_preview_configuration(
    main={"format": 'RGB888', "size": (frame_width, frame_height)},
    transform=Transform(vflip=1)
))
cam.start()
cam.set_controls({"AfMode": controls.AfModeEnum.Continuous})


## ─── Object detection function ───────────────────────────────────────────────

def object_detection():
    # Use ai_edge_litert (LiteRT) — the successor to tf.lite.Interpreter
    interpreter = LiteInterpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_details  = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    model_height = input_details[0]['shape'][1]
    model_width  = input_details[0]['shape'][2]
    is_float     = (input_details[0]['dtype'] == np.float32)

    print('Starting object detection (TFLite). Press q to quit.')
    t_start = time.time()
    frame_count = 0

    while True:
        ## Capture frame
        # picamera2 RGB888 stores pixels in BGR order in memory — same as OpenCV
        frame = cam.capture_array()              # BGR (ready for OpenCV display/drawing)

        ## Resize and convert BGR → RGB for TFLite model input
        resized     = cv2.resize(frame, (model_width, model_height))
        frame_rgb   = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        input_data  = np.expand_dims(frame_rgb, axis=0)

        ## Normalise to [-1, 1] for float models; uint8 models expect raw [0, 255]
        if is_float:
            input_data = (np.float32(input_data) - 127.5) / 127.5

        ## Run inference
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        ## Retrieve outputs
        detected_boxes   = interpreter.get_tensor(output_details[0]['index'])[0]  # [N, 4]
        detected_classes = interpreter.get_tensor(output_details[1]['index'])[0]  # [N]
        detected_scores  = interpreter.get_tensor(output_details[2]['index'])[0]  # [N]
        num_boxes        = int(interpreter.get_tensor(output_details[3]['index'])[0])

        ## Process detections
        for i in range(num_boxes):
            if detected_scores[i] < SCORE_THRESHOLD:
                continue

            ymin, xmin, ymax, xmax = detected_boxes[i]
            im_height, im_width, _ = frame.shape
            left   = int(xmin * im_width)
            right  = int(xmax * im_width)
            top    = int(ymin * im_height)
            bottom = int(ymax * im_height)

            center_x = (left + right) // 2
            center_y = (top  + bottom) // 2

            class_id = int(detected_classes[i])
            label    = labels.get(class_id, 'Unknown')
            score    = detected_scores[i]

            print(f"Object: {label}  Score: {score:.2f}  X: {center_x}  Y: {center_y}")

            ## Draw bounding box and label on the BGR frame
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, f'{label} {score:.0%}', (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        ## Compute rolling FPS (frames since start / elapsed seconds)
        frame_count += 1
        elapsed = time.time() - t_start
        fps = frame_count / elapsed if elapsed > 0 else 0
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        ## Display annotated BGR frame
        cv2.imshow("Object Detection (TFLite)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


## ─── Cleanup & entry point ───────────────────────────────────────────────────

def cleanup():
    """Release all resources cleanly."""
    try:
        Motor.cleanup()
    except Exception:
        pass
    try:
        cam.stop()
        cam.close()
    except Exception:
        pass
    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        object_detection()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()