import cv2
import time
import numpy as np
from picamera2 import Picamera2
from libcamera import controls
from RPi_Robot_Hat_Lib import RobotController
from Ultrasonic_sens import Ultrasonic
import threading 


# Initialize camera, motor, encoder, and ultrasonic sensor
picam = Picamera2()
picam.configure(picam.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam.start()
picam.set_controls({"AfMode": controls.AfModeEnum.Continuous})
Motor = RobotController()
ultrasonic = Ultrasonic()

# Threading synchronization
Frame_lock = threading.Lock()
shutdown_event = threading.Event() 
latest_frame = None

# Set initial servo position
vertical = 2
horizontal = 1
Motor.set_servo(vertical, 130)
Motor.set_servo(horizontal, 1050)
# Thresholds
MIN_AREA_THRESHOLD = 1500  # Minimum area to detect color



def camera():
    global latest_frame 
    picam.start() 
    while not shutdown_event.is_set():
        with Frame_lock:
            latest_frame = picam.capture_array()
        time.sleep(0.01) # Prevent high CPU usage
    picam.stop()

# Color Picker for object tracking
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
        with Frame_lock:
            if latest_frame is not None:
                img = latest_frame.copy() # Copy the image from the camera thread
            else:
                continue # Skip the proces if no prame available 
        
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
            cv2.destroyAllWindows()
            break
    return lower_bound, upper_bound

# Main function where object tracking and obstacle avoidance happen sequentially
def main():
    lower_bound, upper_bound = colorPicker()  # Get color bounds from the color picker
    cv2.destroyAllWindows()

    while not shutdown_event.is_set():
        # 1. Run color tracker to check for the object
        with Frame_lock:
            if latest_frame is not None:
                img = latest_frame.copy()
            else:
                continue # Skip if no frame available

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        object_detected = False
        if contours:
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > MIN_AREA_THRESHOLD:
                    object_detected = True  # Object detected
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.circle(img, (x + w // 2, y + h // 2), 5, (0, 0, 255), -1)
                    cv2.putText(img, "Object", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, "Area: " + str(area), (x, y + h + 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, "Center of Object: (" + str(x + w // 2) + ", " + str(y + h // 2) + ")", (x, y + h + 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

                    center_x = int(x + w // 2)
                    center_y = int(y + h // 2)

                    # Motor control based on object's center position
                    if 80 < center_y < 440:
                        if 50 < center_x < 320:
                            print("Turn Left")
                            Motor.move(sped= 0,  turn=20)
                        if 400 < center_x < 600:
                            print("Turn Right")
                            Motor.move(speed=0, turn=-20)
                        if 320 <= center_x <= 400:
                            Motor.Forward(20)
                            print("Centered")
                        else:
                            Motor.Brake()
                    else:
                        object_detected = False
                else:
                    object_detected = False
                    cv2.imshow("Tracking", img)
                    break  # Exit after detecting and processing one object

        elif not object_detected and (not contours or area < MIN_AREA_THRESHOLD):
            print("No object detected, switching to obstacle avoidance.")
            cv2.putText(img, "Obstacle Avoidance Mode", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)
            Speed = 20
            rotation_speed = 15
            threshold = 30
            min_thresh_dist = 10

            left, front, right = ultrasonic.distances()
            if left and front and right is not None:
                if front < threshold or left < threshold or right < threshold:
                    if front < threshold:
                        if front <= min_thresh_dist:
                            Motor.Backward(Speed)
                        elif left < min_thresh_dist and right < min_thresh_dist:
                            Motor.Backward(Speed)
                        elif left < threshold:
                            Motor.move(speed=0,turn=-rotation_speed)
                        elif right < threshold:
                            Motor.move(speed=0, turn=rotation_speed)
                        else:
                            Motor.Backward(Speed)
                    elif left < threshold:
                        Motor.move(speed=0, turn=-rotation_speed)
                    elif right < threshold:
                        Motor.move(sped=0, turn=rotation_speed)
                else:
                    Motor.Forward(Speed)
            cv2.imshow("Obstacle Avoidance", img)

        # Check for user input to quit the program
        if cv2.waitKey(1) == ord('q'):
            print("Shutting down...")
            cv2.destroyAllWindows()
            Motor.cleanup()
            picam.stop()
            print("Program Terminated \n Exiting....")
            break

try:
    if __name__ == '__main__':
        camera_thread = threading.Thread(target=camera)
        camera_thread.start()
        main()
except KeyboardInterrupt:
    print("KeyboardInterrupt")
finally:
    shutdown_event.set()
    camera_thread.join()
    cv2.destroyAllWindows()
    Motor.cleanup()
    picam.stop()
    print("Program Terminated \n Exiting....")
