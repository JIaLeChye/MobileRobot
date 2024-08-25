import cv2 
import time 
from picamera2 import Picamera2 
from libcamera import controls

def init(): 
    global picam 
    picam = Picamera2()
    picam.configure(picam.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    