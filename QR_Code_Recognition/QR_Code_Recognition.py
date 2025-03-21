import cv2 
from picamera2 import Picamera2 
from libcamera import controls, Transform
import time 
from RPi_Robot_Hat_Lib import RobotController

Motor = RobotController()
vertical = 2
horizontal = 1
Motor.set_servo(horizontal, 80)
Motor.set_servo(vertical, 90)

frame_width = 640 
frame_height = 480 
cam = Picamera2()
cam.configure(cam.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)},transform=Transform(vflip=1))) 
cam.start()
cam.set_controls({"AfMode":controls.AfModeEnum.Continuous})

detector = cv2.QRCodeDetector()

t_start = time.time()
fps = 0


while True :
    frame = cam.capture_array()
    data, bbox, _ = detector.detectAndDecode(frame)
    fps +=1
    mfps = fps/(time.time() - t_start)

    if(bbox is not None):
        for i in range(len(bbox)):
            
            pt1 = (int(bbox[i][0][0]), int(bbox[i][0][1]))
            pt2 = (int(bbox[(i + 1) % len(bbox)][0][0]), int(bbox[(i + 1) % len(bbox)][0][1]))
            
            cv2.line(frame, pt1, pt2, color=(255,
                     0, 0), thickness=2)
            
        cv2.putText(frame, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 250, 120), 2)

        
        
    else:
        print("No Data Found")

    cv2.putText(frame, "FPS : " + str(int(mfps)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.imshow("code detector", frame)

    if cv2.waitKey(1) == ord("q"):
        break 

cam.stop()
Motor.cleanup()
cv2.destroyAllWindows() 
