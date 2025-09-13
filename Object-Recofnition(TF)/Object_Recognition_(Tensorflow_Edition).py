
## Object detection and image processing 
import tensorflow as tf 
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils 
import object_detection as od_pkg

# TensorFlow 2.x compatibility for TF1-style code used by Object Detection API utils
if not hasattr(tf, 'gfile'):
    tf.gfile = tf.io.gfile  # type: ignore

## Required files validation
import os
import tarfile
import urllib.request

## To get the accurate time 
import time

## Image aquation and atftyer processing process 
import cv2
import numpy as np
from picamera2 import Picamera2 
from libcamera import controls, Transform 



## define global variables 
frame_height = 480 
frame_width = 640

## Load the Model Folder 
model_folder = 'object_detection'
model_Name = '/ssdlite_mobilenet_v2_coco_2018_05_09'
path_To_ckpt = model_folder + model_Name + '/frozen_inference_graph.pb'

# Prefer the label map bundled with the installed object_detection package
try:
    _pkg_dir = os.path.dirname(od_pkg.__file__)
    path_to_labels = os.path.join(_pkg_dir, 'data', 'mscoco_label_map.pbtxt')
except Exception:
    # Fallback to local relative path if package resource lookup fails
    path_to_labels = os.path.join(model_folder, 'data', 'mscoco_label_map.pbtxt')

number_Class = 90

MODEL_BASE_URL = 'http://download.tensorflow.org/models/object_detection/'
MODEL_ARCHIVE = 'ssdlite_mobilenet_v2_coco_2018_05_09.tar.gz'
LABEL_MAP_URL = 'https://raw.githubusercontent.com/tensorflow/models/master/research/object_detection/data/mscoco_label_map.pbtxt'

def ensure_label_map_present():
    """Ensure the COCO label map exists locally; download if missing."""
    nonlocal_path = path_to_labels
    # If the package path doesn't exist, write to local object_detection/data
    if not os.path.isfile(nonlocal_path):
        local_labels_dir = os.path.join(model_folder, 'data')
        os.makedirs(local_labels_dir, exist_ok=True)
        local_labels_path = os.path.join(local_labels_dir, 'mscoco_label_map.pbtxt')
        try:
            print('Label map not found. Downloading COCO label map...')
            urllib.request.urlretrieve(LABEL_MAP_URL, local_labels_path)
            print('Label map saved to:', local_labels_path)
            return local_labels_path
        except Exception as e:
            print('Failed to download label map:', e)
            return nonlocal_path
    return nonlocal_path

def ensure_model_present():
    """Download and extract the TF1 SSDLite MobileNet v2 model if missing."""
    os.makedirs(model_folder, exist_ok=True)
    if os.path.isfile(path_To_ckpt):
        return True
    archive_path = os.path.join(model_folder, MODEL_ARCHIVE)
    try:
        print('Model not found locally. Downloading:', MODEL_ARCHIVE)
        urllib.request.urlretrieve(MODEL_BASE_URL + MODEL_ARCHIVE, archive_path)
        print('Download complete. Extracting...')
        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(model_folder)
        try:
            os.remove(archive_path)
        except OSError:
            pass
        return os.path.isfile(path_To_ckpt)
    except Exception as e:
        print('Failed to download model:', e)
        return False

## Check location of the files
isCKPTexist = os.path.isfile(path_To_ckpt)
isLabelexist = os.path.isfile(path_to_labels)
if isCKPTexist: 
    print('Model Found at:', path_To_ckpt)
else:
    print('Model Not Found')
    # Try to fetch the model automatically
    if ensure_model_present():
        isCKPTexist = True
        print('Model downloaded to:', path_To_ckpt)
if isLabelexist:
    print('Label File Found at:', path_to_labels)
else:
    print('Label File Not Found')
    # Try to fetch the label map automatically
    new_path = ensure_label_map_present()
    path_to_labels = new_path
    isLabelexist = os.path.isfile(path_to_labels)
    if isLabelexist:
        print('Label File Downloaded to:', path_to_labels)
    else:
        # If the package resource wasn't found, give a hint
        if 'site-packages' not in path_to_labels:
            print('Tip: Install tensorflow-object-detection-api or place mscoco_label_map.pbtxt under object_detection/data/')

# Final guard before proceeding
if not isCKPTexist:
    raise FileNotFoundError(f"Missing model file: {path_To_ckpt}. Check your network and rerun, or provide the model locally.")
if not isLabelexist:
    raise FileNotFoundError(f"Missing label map: {path_to_labels}. Ensure TensorFlow Object Detection API is installed or provide the file locally.")

## load the Tensorflow Detection Graph
print("Loading tensorflow Graph....")
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.compat.v1.GraphDef()
    with tf.io.gfile.GFile(path_To_ckpt, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

label_map = label_map_util.load_labelmap(path_to_labels)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=number_Class, use_display_name=True)
category_index = label_map_util.create_category_index(categories)
print("Graph Loading Process Complete!")

## Initialize Picamera2 Library 

cam = Picamera2()

cam.configure(cam.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)},transform=Transform(vflip=1)))
cam.start()
cam.set_controls({"AfMode":controls.AfModeEnum.Continuous}) # Enable auto focus 
 
## Object detection Function
def object_detect(): 
    
     with detection_graph.as_default():
        with tf.compat.v1.Session(graph=detection_graph) as sess:
            while True:
                ## Start the capturing the frame 
                frame = cam.capture_array()
                bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                ## tidy up the captured frame array 
                image_np_expanded = np.expand_dims(bgr, axis=0)
                ## start detection 
                image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                boxes_tensor = detection_graph.get_tensor_by_name('detection_boxes:0')
                scores_tensor = detection_graph.get_tensor_by_name('detection_scores:0')
                classes_tensor = detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections_tensor = detection_graph.get_tensor_by_name('num_detections:0')

                (boxes, scores, classes, num_detections) = sess.run(
                                                                    [boxes_tensor, scores_tensor, classes_tensor, num_detections_tensor],
                                                                    feed_dict={image_tensor: image_np_expanded})
                
                ## When Object detected
                for i in range(0,10):
                    if scores[0][i] > 0.5:
                        
                        print("Object:", category_index[classes[0][i]]['name'])
                        print("Score:", scores[0][i])
                        
                        ## Draw boxes for the detected object
                        viz_utils.visualize_boxes_and_labels_on_image_array(
                                bgr,
                                np.squeeze(boxes),
                                np.squeeze(classes).astype(np.int32),
                                np.squeeze(scores),
                                category_index,
                                use_normalized_coordinates=True,
                                line_thickness=2)
                        ## get the coordinates of the detected object
                        box = boxes[0][i]
                        ymin, xmin, ymax, xmax = box
                        im_height, im_width, _ = frame.shape 
                        left = int(xmin * im_width)
                        right = int(xmax * im_width)
                        top = int(ymin * im_height)
                        bottom = int(ymax * im_height)
                        center_y = int((left + right) // 2)
                        center_x = int((top + bottom) // 2)
                        print("Coordinates: ", "\nX: ", center_x, "\nY: ", center_y)
                  

                        ## When the specific object is selected  
                        if category_index[classes[0][i]]['name'] == 'bottle':
                            coordinates = [center_y, center_x] 

                            # movement(coordinates)
                            object_detected = True
                        else:
                            object_detected = False


                    frame = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                    cv2.imshow("main", frame)

                    if cv2.waitKey(1) == ord('q'):
                        break


def main():
    object_detect()



try:
    if __name__ == '__main__':
        main()

except KeyboardInterrupt:
    pass
 
finally:
    cam.close() 
    exit()

