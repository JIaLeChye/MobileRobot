
## Object detection using full TensorFlow 2.x (SavedModel API)
## Contrast: The TFLite edition uses tflite_runtime.interpreter (lightweight, quantized)
##           This edition uses tf.saved_model.load() (full TF2, float32, higher accuracy)
import tensorflow as tf
import tensorflow_hub as hub

## Required files validation
import os
import urllib.request

## To get the accurate time
import time

## Image acquisition and after processing
import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls, Transform


## ─── Global settings ────────────────────────────────────────────────────────
frame_height = 480
frame_width  = 640

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR    = os.path.join(SCRIPT_DIR, 'tf_saved_model')

## SSD MobileNet V2 320x320 — full TF2 SavedModel from TensorFlow Hub
## (same architecture as the TFLite edition, but full float32 precision)
TFHUB_MODEL_URL = 'https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2'

## COCO label map (90 classes, index 1-based to match model output)
LABELS_URL  = 'https://raw.githubusercontent.com/tensorflow/models/master/research/object_detection/data/mscoco_label_map.pbtxt'
LABELS_PATH = os.path.join(MODEL_DIR, 'mscoco_label_map.pbtxt')

SCORE_THRESHOLD = 0.5    # Only show detections above this confidence
TARGET_OBJECT   = 'bottle'  # The object to trigger robot action


## ─── Label loading ───────────────────────────────────────────────────────────

def ensure_labels_present():
    """Download the COCO label map pbtxt if not already on disk."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    if os.path.isfile(LABELS_PATH):
        return
    print('Downloading COCO label map...')
    urllib.request.urlretrieve(LABELS_URL, LABELS_PATH)
    print('Labels saved to:', LABELS_PATH)


def load_labels_from_pbtxt(path):
    """Parse a .pbtxt label map and return a dict {id: display_name}."""
    labels = {}
    current_id = None
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('id:'):
                current_id = int(line.split(':')[1].strip())
            elif line.startswith('display_name:') and current_id is not None:
                name = line.split(':', 1)[1].strip().strip('"')
                labels[current_id] = name
    return labels


## ─── Model loading ───────────────────────────────────────────────────────────

def load_model():
    """Load SSD MobileNet V2 SavedModel from TF Hub (cached locally after first run)."""
    # TF Hub caches the model in TFHUB_CACHE_DIR (default: /tmp/tfhub_modules)
    # Set cache dir next to the script for persistence across reboots
    os.environ.setdefault('TFHUB_CACHE_DIR', MODEL_DIR)
    print('Loading TF2 SavedModel from TF Hub (first run downloads ~67 MB)...')
    model = hub.load(TFHUB_MODEL_URL)
    print('Model loaded.')
    return model


## ─── Drawing helper ──────────────────────────────────────────────────────────

def draw_detection(frame, box, label, score, color=(0, 255, 0)):
    """Draw a bounding box and label on the BGR frame."""
    h, w = frame.shape[:2]
    ymin, xmin, ymax, xmax = box
    left   = int(xmin * w)
    right  = int(xmax * w)
    top    = int(ymin * h)
    bottom = int(ymax * h)

    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    text = f'{label}: {score:.0%}'
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.rectangle(frame, (left, top - text_size[1] - 4), (left + text_size[0], top), color, -1)
    cv2.putText(frame, text, (left, top - 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    return left, right, top, bottom


## ─── Initialization ──────────────────────────────────────────────────────────

ensure_labels_present()
labels = load_labels_from_pbtxt(LABELS_PATH)

## Load the full TF2 SavedModel (infer function accepts uint8 image tensors)
detector = load_model()
detect_fn = detector.signatures['serving_default']

## ─── Camera setup ────────────────────────────────────────────────────────────

cam = Picamera2()
cam.configure(cam.create_preview_configuration(
    main={"format": 'RGB888', "size": (frame_width, frame_height)},
    transform=Transform(vflip=1)
))
cam.start()
cam.set_controls({"AfMode": controls.AfModeEnum.Continuous})


## ─── Main detection loop ─────────────────────────────────────────────────────

def object_detect():
    print('Starting object detection (TF2 SavedModel). Press q to quit.')
    fps_counter = 0
    t_start = time.time()

    while True:
        ## Capture frame from camera
        # picamera2 RGB888 stores pixels in BGR order in memory — same as OpenCV
        frame = cam.capture_array()              # BGR (ready for OpenCV display)

        ## TF2 SavedModel expects uint8 RGB tensor [1, H, W, 3]
        # Convert BGR → RGB only for the inference input
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_tensor = tf.convert_to_tensor(rgb)             # uint8 RGB
        input_tensor = input_tensor[tf.newaxis, ...]         # add batch dim

        ## Run inference
        detections = detect_fn(input_tensor)

        ## Extract results (remove batch dimension)
        boxes   = detections['detection_boxes'][0].numpy()   # [N, 4]  ymin,xmin,ymax,xmax
        classes = detections['detection_classes'][0].numpy().astype(int)  # [N]
        scores  = detections['detection_scores'][0].numpy()  # [N]

        ## Process detections
        for i in range(len(scores)):
            if scores[i] < SCORE_THRESHOLD:
                continue

            class_id = classes[i]
            label = labels.get(class_id, f'id:{class_id}')
            score = scores[i]

            print(f'Object: {label}  Score: {score:.2f}')

            ## Draw bounding box on BGR frame (frame is already BGR)
            left, right, top, bottom = draw_detection(frame, boxes[i], label, score)

            ## Compute object centre
            center_x = (left + right) // 2
            center_y = (top + bottom) // 2
            print(f'Coordinates:  X={center_x}  Y={center_y}')

            ## Target-specific action
            if label == TARGET_OBJECT:
                coordinates = [center_x, center_y]
                object_detected = True
                # motor_command(coordinates)   # ← hook in robot movement here
            else:
                object_detected = False

        ## Compute and display FPS
        fps_counter += 1
        elapsed = time.time() - t_start
        fps = fps_counter / elapsed if elapsed > 0 else 0
        cv2.putText(frame, f'FPS: {fps:.1f}', (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        ## Show annotated frame (frame is BGR — correct for cv2.imshow)
        cv2.imshow('Object Detection (TF2 SavedModel)', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


## ─── Cleanup & entry point ───────────────────────────────────────────────────

def cleanup():
    """Release all resources cleanly."""
    try:
        cam.stop()
        cam.close()
    except Exception:
        pass
    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        object_detect()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
