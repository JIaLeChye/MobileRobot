import cv2
import numpy as np
from RPi_Robot_Hat_Lib import RobotController
from picamera2 import Picamera2
from libcamera import controls, Transform 
import time

tracker = cv2.TrackerKCF_create() 
# cap = cv2.VideoCapture(0)
# frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_width = 640  
frame_height = 480
cap = Picamera2()
cap.configure(cap.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)},transform=Transform(vflip=1)))
cap.set_controls({"AfMode": controls.AfModeEnum.Continuous})
cap.start()

Motor = RobotController()
# enc = Encoder()

vertical = 2
horizontal = 1
Motor.set_servo(vertical, 180)
Motor.set_servo(horizontal, 90)
# All process should be start after the servo @ camera position is set !
time.sleep(1)





def tracking(frame, x,y,w,h):
    
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(frame, "Tracking", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, "Press 'q' to quit", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, f"X:{x} , Y: {y}", (x ,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # Calculate the center of Bounding Box 
    center_x = x + w // 2
    center_y = y + h // 2
    cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)  # Draw a circle at the center
    # Tracking Logic 
    # enc.encoder() 
    if center_y < 220 and center_y > 100:
        if center_x < 300:
            print("Turn Left")
            Motor.move(speed=0, turn=-20) 
        if center_x > 340:
            print("Turn Right")
            Motor.move(speed=0, turn= 20)
        else:
            Motor.Forward(20)
    # Slow Approch        
    elif center_y > 240 and center_y < 440:
        if center_x < 300:
            print("Turn Left")
            Motor.move(speed=0, turn=-10)
        if center_x > 340:
            print("Turn Right")
            Motor.move(speed=0, turn=10)
        else:
            Motor.Forward(10)
    else:
        Motor.Brake()
    
    

def main(): 
    frame = cap.capture_array()
    bbox = cv2.selectROI(frame, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("ROI selector")
 
    # Initialize tracker with first frame and bounding box
    tracker.init(frame, bbox)

    # if not cap.isOpened():
    #     print("Error: Could not open video capture.")
    #     return
    # print(f"Tracking started with ROI: {bbox}")
    
    while True:
        frame = cap.capture_array()  # Read frame
        # Convert the frame from RGBA to BGR (From 4 channel to 1 channel)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # Tracking mode: update the tracker and draw the tracked bounding box
        success, box = tracker.update(frame)  # Update the tracker with the new frame

        if success:
            (x, y, w, h) = [int(v) for v in box]
            tracking(frame, x,y,w,h)
        else:
            cv2.putText(frame, "Tracking failure", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            Motor.Brake() 
        cv2.imshow('Tracking_Area', frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

      # Release the video capture when done

try:
    if __name__ == '__main__':
        main()
except KeyboardInterrupt:
    print("KeyboardInterrupt")
    
finally:
    Motor.cleanup()
    # enc.stop()
    cap.stop()
    cv2.destroyAllWindows()
    print("Program Terminated \nExiting....")