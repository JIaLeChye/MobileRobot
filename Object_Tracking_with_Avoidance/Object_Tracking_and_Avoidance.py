import cv2
import time
from picamera2 import Picamera2
from libcamera import controls
from PCA9685_MC import Motor_Controller
from Motor_Encoder import Encoder
import numpy as np
import threading
from Ultrasonic_sens import Ultrasonic

picam = Picamera2()
picam.configure(picam.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam.start()
picam.set_controls({"AfMode": controls.AfModeEnum.Continuous})
Motor = Motor_Controller()
enc = Encoder()
ultrasonic = Ultrasonic()
Frame_Lock = threading.Lock()
shutdown_event = threading.Event()
avoidance_event = threading.Event()


vertical = 0
horizontal = 1
Motor.servoPulse(horizontal, 1250)
Motor.servoPulse(vertical, 1050)



# Thresholds
MIN_AREA_THRESHOLD = 1500  # Minimum area to detect color


def colorPicker():
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


def color_tracker(lower_bound, upper_bound):
    while not shutdown_event.is_set():
        img = picam.capture_array()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


        if contours:
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > MIN_AREA_THRESHOLD:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    center_x = int(x + w // 2)
                    center_y = int(y + h // 2)
                    print("Center X:", center_x)
                    print("Center Y:", center_y)
                    print("Area:", area)

                    cv2.putText(img, f"Center X: {center_x}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, f"Center Y: {center_y}", (10, 60), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, f"Area: {area}", (10, 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1)

                    object_detected = True  # Object detected

                    if 80 < center_y < 440:
                        if 50 < center_x < 320:
                            print("Turn right")
                            Motor.AntiClock_Rotate(20)
                        elif 400 < center_x < 600:
                            print("Turn left")
                            Motor.Clock_Rotate(20)
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


        else:
            print("No object detected, switching to obstacle avoidance.")
            cv2.destroyAllWindows()
            avoidance_event.set()
            break

        
        if cv2.waitKey(1) == ord('q'):
            shutdown_event.set()
            break


def obstacle_avoidance():
    Speed = 20
    rotation_speed = 15
    threshold = 30
    min_thresh_dist = 10

    while avoidance_event.is_set() and not shutdown_event.is_set():
        left, front, right = ultrasonic.distances()
        if left and front and right is not None: 
            if front < threshold or left < threshold or right < threshold:
                print("Obstacle detected, avoiding...")
                if front < threshold:
                    if front <= min_thresh_dist:
                        Motor.Backward(Speed)
                        time.sleep(0.1)
                        Motor.Brake()
                    elif left < min_thresh_dist and right < min_thresh_dist:
                        Motor.Backward(Speed)
                        time.sleep(0.1)
                        Motor.Brake()
                    elif left < threshold:
                        Motor.Clock_Rotate(rotation_speed)
                        time.sleep(0.5)
                        Motor.Brake()
                    elif right < threshold:
                        Motor.AntiClock_Rotate(rotation_speed)
                        time.sleep(0.5)
                        Motor.Brake()
                    else:
                        Motor.Backward(Speed)
                        time.sleep(0.1)
                        Motor.Brake()

                elif left < threshold:
                    Motor.Clock_Rotate(rotation_speed)
                    time.sleep(1)
                    Motor.Brake()

                elif right < threshold:
                    Motor.AntiClock_Rotate(rotation_speed)
                    time.sleep(1)
                    Motor.Brake()

        else:
            print("No ultrasonic sensors detected.")
            print("Check Ultrasonic Cable")
            break

def main():
    lower_bound, upper_bound = colorPicker()

    while not shutdown_event.is_set():
        if not avoidance_event.is_set():
            print("Tracking mode.")
            color_tracker(lower_bound, upper_bound)
        if avoidance_event.is_set():
            print("Switching to obstacle avoidance.")
            obstacle_avoidance()


try:
    if __name__ == '__main__':
        main_thread = threading.Thread(target=main)
        main_thread.start()
        main_thread.join()

except KeyboardInterrupt:
    print("KeyboardInterrupt")
finally:
    shutdown_event.set()
    picam.stop()
    Motor.cleanup()
    enc.stop()
    cv2.destroyAllWindows()
    print("Program Terminated \n Exiting....")
