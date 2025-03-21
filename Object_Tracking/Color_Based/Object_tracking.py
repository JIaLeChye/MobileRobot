import cv2
from picamera2 import Picamera2
from libcamera import controls, Transform
from RPi_Robot_Hat_Lib import RobotController 
import numpy as np



picam = Picamera2()
config = picam.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)},transform=Transform(vflip=1))
picam.configure(config)
picam.start()
picam.set_controls({"AfMode": controls.AfModeEnum.Continuous})
Motor = RobotController()

vertical = 2
horizontal = 1
Motor.set_servo(vertical, 180)
Motor.set_servo(horizontal, 90)



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
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGRA)
        stacked = np.hstack((mask, img, res))
        cv2.imshow("Color_Picker", cv2.resize(stacked, None, fx=0.4, fy=0.4))
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
    return lower_bound, upper_bound 


def main():
    global picam 
    lower_bound , upper_bound = colorPicker()

    while True:
        img = picam.capture_array()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            for i, contour in enumerate(contours):
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                if area > 1500:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    # cv2.putText(img, f"Object {i + 1}", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

                    center_x = int(x + w // 2)
                    center_y = int(y + h // 2)
                    print("Center X:", center_x)
                    print("Center Y:", center_y)
                    print("Area:", area)

                    cv2.putText(img, f"Center X: {center_x}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, f"Center Y: {center_y}", (10, 60), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, f"Area: {area}", (10, 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

                    if center_y < 400:
                        if 50 < center_x < 320:
                            print("Turn right")
                            Motor.move(speed=0, turn=20)
                        elif 400 < center_x < 600:
                            print("Turn left")
                            Motor.move(speed=0, turn=-20)
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
    cv2.destroyAllWindows()
    print("Program Terminated \n Exiting....")
