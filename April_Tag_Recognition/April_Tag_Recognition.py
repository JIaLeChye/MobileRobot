import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls
import apriltag
import time

cam = Picamera2()
cam.configure(cam.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
cam.start()
cam.set_controls({"AfMode":controls.AfModeEnum.Continuous})

# t_start = time.time()
# fps = 0

while True:
   
    frame = cam.capture_array()
    # fps += 1
    # mfps = fps / (time.time() - t_start)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = apriltag.Detector()
    detections = detector.detect(gray)
    # cv2.putText(frame, "FPS : " + str(int(mfps)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    for detect in detections:
        print("tag_id: %s, center: %s" % (detect.tag_id, detect.center)) 
        cv2.putText(frame, "AprilTag Detected", (30, 480), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cam.stop()
cv2.destroyAllWindows()

