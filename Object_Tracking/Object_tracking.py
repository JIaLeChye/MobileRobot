import cv2 
import time 
from picamera2 import Picamera2 
from libcamera import controls

from PCA9685_MC import Motor_Controller 
from Motor_Encoder import Encoder
import threading  
import numpy as np 
def init(): 
    global picam , Motor, enc 
    picam = Picamera2()
    picam.configure(picam.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam.start()
    picam.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    Motor = Motor_Controller()
    enc = Encoder() 

    
def main(): 
    init()
    lower_bound = input("Enter lower bound: ")
    upper_bound = input("Enter upper bound: ")
    lower_bound = np.array([int(x) for x in lower_bound.split(",")])
    upper_bound = np.array([int(x) for x in upper_bound.split(", ")])
    while True:
        img = picam.capture_array()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contour_ids = [None] * len(contours)

        if contours is not None: 
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img, "Object " + str(i + 1), (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                contour_ids[1] = (x + w // 2, y + h // 2)
                print(contour_ids)


                center_x = int(x + w // 2)
                center_y = int(y + h // 2) 
                area = cv2.contourArea(contour)
                print("Center X: " , center_x)
                print("Center Y: ", center_y)
                print("Area: ", area)

                cv2.putText(img, "Center X: " + str(center_x), (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(img, "Center Y: " + str(center_y), (10, 60), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(img, "Area: " + str(area), (10, 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2) 
                if area > 1500: 
                    if center_y <300: 
                        if center_x     < 320 and center_x > 50:
                            print("Turn right")
                        elif center_x < 600 and center_x > 400:
                            print("Turn left")
                        elif center_x >320 and center_x < 400:
                            print("Centered")
                        else: 
                            print("Out of range")
                    else:
                        print("Out of range")

        cv2.imshow("Camera", mask)
        if cv2.waitKey(1) == ord('q'):
            break




try: 
    if __name__ == '__main__':
        main()

except KeyboardInterrupt:
    print("KeyboardInterrupt")
    picam.stop()
    cv2.destroyAllWindows() 

finally:
    picam.stop()
    Motor.cleanup()
    enc.stop()
    print("Program Terminated \n Exiting....")
    exit