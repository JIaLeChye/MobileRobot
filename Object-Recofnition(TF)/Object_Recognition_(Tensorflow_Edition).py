
## Object detection and image processing 
import tensorflow as tf 
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils 

## Required files validation
import os

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
path_to_labels = os.path.join(model_folder + '/data/mscoco_label_map.pbtxt')
number_Class = 90

## Check location of the files
isCKPTexist = os.path.isfile(path_To_ckpt)
isLabelexist = os.path.isfile(path_to_labels)
if isCKPTexist: 
    print('Model Found at:', path_To_ckpt)
else:
    print('Model Not Found')
if isLabelexist:
    print('Label File Found at:', path_to_labels)
else:
    print('Label File Not Found')

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

