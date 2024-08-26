import cv2
import time
from picamera2 import Picamera2
from libcamera import controls
from PCA9685_MC import Motor_Controller
from Motor_Encoder import Encoder
import numpy as np



picam = Picamera2()
picam.configure(picam.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam.start()
picam.set_controls({"AfMode": controls.AfModeEnum.Continuous})
Motor = Motor_Controller()
enc = Encoder()

def colorPicker(): 
    global picam 
    def nothing(x):
        pass    
    cv2.namedWindow("Color_Picker")
    cv2.createTrackbar("Lower Hue", "Color_Picker", 0, 179, nothing)
    cv2.createTrackbar("Lower Saturation", "Color_Picker", 0, 255, nothing)
    cv2.createTrackbar("Lower Value", "Color_Picker", 0, 255, nothing)
    cv2.createTrackbar("Upper Hue", "Color_Picker", 179, 179, nothing)
    cv2.createTrackbar("Upper Saturation", "Color_Picker", 255, 255, nothing)
    cv2.createTrackbar("Upper Value", "Color_Picker", 255, 255, nothing)
    while True:
        img = picam.capture_array()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        l_h = cv2.getTrackbarPos("Lower Hue", "Color_Picker")
        l_s = cv2.getTrackbarPos("Lower Saturation", "Color_Picker")
        l_v = cv2.getTrackbarPos("Lower Value", "Color_Picker")
        u_h = cv2.getTrackbarPos("Upper Hue", "Color_Picker")
        u_s = cv2.getTrackbarPos("Upper Saturation", "Color_Picker")
        u_v = cv2.getTrackbarPos("Upper Value", "Color_Picker")
        lower_bound = np.array([l_h, l_s, l_v])
        upper_bound = np.array([u_h, u_s, u_v])
        mask = cv2.inRange(hsv, lower_bound, upper_bound) 
        res = cv2.bitwise_and(img, img, mask=mask)

        cv2.imshow("Color_Picker", mask)
        cv2.imshow("Color_Picker", img)
        cv2.imshow("Color_Picker", res)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
    return lower_bound, upper_bound 


def main():
    global picam 
    lower_bound , upper_bound = colorPicker()
    lower_bound = np.array([int(x) for x in lower_bound.split(",")])
    upper_bound = np.array([int(x) for x in upper_bound.split(",")])

    while True:
        img = picam.capture_array()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area > 1500:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(img, f"Object {i + 1}", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

                    center_x = int(x + w // 2)
                    center_y = int(y + h // 2)
                    print("Center X:", center_x)
                    print("Center Y:", center_y)
                    print("Area:", area)

                    cv2.putText(img, f"Center X: {center_x}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, f"Center Y: {center_y}", (10, 60), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, f"Area: {area}", (10, 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

                    if center_y < 300:
                        if 50 < center_x < 320:
                            print("Turn right")
                            Motor.Clock_Rotate(20)
                        elif 400 < center_x < 600:
                            print("Turn left")
                            Motor.AntiClock_Rotate(20)
                        elif 320 <= center_x <= 400:
                            Motor.Forward(20)
                            print("Centered")
                        else:
                            print("Out of range")
                            Motor.Brake() 
                    else:
                        print("Out of range")
                        Motor.Brake()

        cv2.imshow("Camera", mask)
        cv2.imshow("Result", img)
        if cv2.waitKey(1) == ord('q'):
            break

try:
    if __name__ == '__main__':
        main()
except KeyboardInterrupt:
    print("KeyboardInterrupt")
finally:
    picam.stop()
    Motor.cleanup()
    enc.stop()
    cv2.destroyAllWindows()
    print("Program Terminated \n Exiting....")
