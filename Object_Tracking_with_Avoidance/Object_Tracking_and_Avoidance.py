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
# enc = Encoder()
ultrasonic = Ultrasonic()

# Threading synchronization
Frame_lock = threading.Lock()
shutdown_event = threading.Event() 
latest_frame = None


# Set initial servo position
vertical = 2
horizontal = 1
Motor.set_servo(vertical, 150)
Motor.set_servo(horizontal, 90)
# Thresholds
MIN_AREA_THRESHOLD = 10000  # Minimum area to detect color


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
    print("Object Registered")
    cv2.destroyAllWindows()
    Tracking_window = False
    Obstacle_Avoid_Window = False
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
                 # Sort contours by area in descending order
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                # Get the largest contour (first one after sorting)
                largest_contour = contours[0]
                area = cv2.contourArea(largest_contour)
                # x, y, w, h = cv2.boundingRect(largest_contour)
                # cv2.putText(img, "Objact Detected" , (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                # cv2.putText(img, "Area: " + str(area), (x, y + h + 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                if area > MIN_AREA_THRESHOLD:
                    # Check if the window exists
                    if Obstacle_Avoid_Window is True :
                        cv2.destroyWindow("Obstacle Avoidance")
                    else:
                        pass
                    object_detected = True  # Object detected
                    cv2.putText(img, "Object Tracking Mode", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
                    # print("Object Detected")
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.circle(img, (x + w // 2, y + h // 2), 5, (0, 0, 255), -1)
                    cv2.putText(img, "Object", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, "Area: " + str(area), (x, y + h + 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, "Center of Object: (" + str(x + w // 2) + ", " + str(y + h // 2) + ")", (x, y + h + 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

                    center_x = int(x + w // 2)
                    center_y = int(y + h // 2)
                    # print("Center of Object: (" + str(center_x) + ", " + str(center_y) + ")")
                    Tracking_window = True
                    cv2.imshow("Tracking", img)
                    # Motor control based on object's center position
                    if 80 < center_y < 440:
                        if center_y < 370:
                            if 50 < center_x < 240:
                                print("Turn Left")
                                # Motor.move(speed=0, turn=-20)
                                # time.sleep(0.1)
                            elif 400 < center_x < 600:
                                print("Turn Right")
                                # Motor.move(speed=0,turn=20)
                            elif 300 <= center_x <= 400:
                                # Motor.Forward(30)
                                print("Centered")
                                # Motor.Brake()`
                        elif 400> center_y > 370: 
                            Motor.Brake()
                            # threading.Thread(target=play_tone).start()
                            print("Object Found")
                            cv2.putText(img, "Object Found", (100, 200), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
                            # time.sleep(0.5)
                        else:
                            object_detected = False
                            break
                            
                    else:
                        object_detected = False
                        break
                else:
                    object_detected = False
                    # cv2.imshow("Tracking", img)
                    break  # Exit after detecting and processing one object

        elif not object_detected and  area < MIN_AREA_THRESHOLD:
            if Tracking_window is True:
                cv2.destroyWindow("Tracking")
            else:
                pass
            print("No object detected, switching to obstacle avoidance.")
            cv2.putText(img, "Obstacle Avoidance Mode", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)
            Speed =  30
            rotation_speed = 20
            threshold = 20
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
                            Motor.move(speed=0,turn=rotation_speed)
                        elif right < threshold:
                            Motor.move(speed=0, turn=-rotation_speed)
                        else:
                            Motor.Backward(Speed)
                    elif left < threshold:
                        Motor.move(speed=0, turn=rotation_speed)
                    elif right < threshold:
                        Motor.move(speed=0, turn=-rotation_speed)
                else:
                    Motor.Forward(Speed)
            Obstacle_Avoid_Window = True
            cv2.imshow("Obstacle Avoidance", img)

        # Check for user input to quit the program
        if cv2.waitKey(1) == ord('q'):
            print("Shutting down...")
            cv2.destroyAllWindows()
            Motor.cleanup()
            # enc.stop()
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
    shutdown_event.set()
    camera_thread.join()
    cv2.destroyAllWindows()
    Motor.cleanup()
    # enc.stop()
    picam.stop()
    print("Program Terminated \n Exiting....")
    exit()
# finally:
#     shutdown_event.set()
#     camera_thread.join()
#     cv2.destroyAllWindows()
#     Motor.cleanup()
#     # enc.stop()
#     picam.stop()
#     print("Program Terminated \n Exiting....")
#     exit()
