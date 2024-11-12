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
Avoidance_event = threading.Event() 

# Declare global variable 
latest_frame = None
Tracking_mode = False 
Avoidance_mode = False 


# Set initial servo position
vertical = 2
horizontal = 1
Motor.set_servo(vertical, 160)
Motor.set_servo(horizontal, 90)
# Thresholds
MIN_AREA_THRESHOLD = 3000 # Minimum area to detect color
threshold = 30 # Threshod for obstacle avoidance 
min_thresh_dist = 10 # Minimum threshoold for obstacle avoidance
print("Initialasition Complete")




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
                continue # Skip the proces if no frame available 
        
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


            
def avoidance_mode():
    global Avoidance_mode,object_detected 

    while not shutdown_event.is_set(): 

        while Avoidance_event.is_set() and not shutdown_event.is_set():

            print("No object detected, switching to obstacle avoidance.")
            Speed = 40
            rotation_speed = 30
            Motor.Brake()
            left,front,right = ultrasonic.distances()
            if left is not None  and front is not None  and right is not None:
                print("left: {:.2f}".format(left))
                print("front: {:.2f}".format(front) )
                print("right: {:.2f}".format(right))
                if front < threshold or left < threshold or right < threshold:
                    if front < threshold:
                        if front <= min_thresh_dist:
                            Motor.Backward(Speed)
                            time.sleep(0.1)
                        elif left < min_thresh_dist and right < min_thresh_dist:
                            Motor.Backward(Speed)
                            time.sleep(0.1)
                        elif left < threshold:
                            Motor.move(speed=0, turn=rotation_speed)
                            time.sleep(0.1)
                        elif right < threshold:
                            Motor.move(speed=0, turn=-rotation_speed)
                            time.sleep(0.1)
                        else:
                            Motor.Backward(Speed)
                    elif left < threshold:
                        Motor.move(speed=0, turn=rotation_speed)
                        time.sleep(0.1)
                    elif right < threshold:
                        Motor.move(speed=0, turn=-rotation_speed)
                        time.sleep(0.1)
                else:
                    Motor.Forward(Speed)
            else:
                print("No data received")
                Motor.Brake()
                time.sleep(1)
            time.sleep(0.5)
        else:
            # print("Avoidance event is not set")
            pass
           

    

# Main function where object tracking and obstacle avoidance happen sequentially
def main():
    global Tracking_mode, Avoidance_mode, object_detected
    lower_bound, upper_bound = colorPicker()  # Get color bounds from the color picker
    cv2.destroyAllWindows()

    while not shutdown_event.is_set():
        # 1. Run color tracker to check for the object
        with Frame_lock:
            if latest_frame is not None:
                img = latest_frame.copy()
            else:
                print("No frame available")
                break  # Skip if no frame available

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        object_detected = False
        if contours:
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            largest_contour = contours[0] 
            area = cv2.contourArea(largest_contour)
            if area > MIN_AREA_THRESHOLD:
                if Avoidance_mode:
                    cv2.destroyWindow("Obstacle Avoidance")
                    Tracking_mode = True
                    Avoidance_mode = False
                    Avoidance_event.clear()

                cv2.putText(img, "Object Tracking Mode", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
                object_detected = True  # Object detected
                x, y, w, h = cv2.boundingRect(largest_contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(img, (x + w // 2, y + h // 2), 5, (0, 0, 255), -1)
                cv2.putText(img, "Object", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(img, "Area: " + str(area), (x, y + h + 20), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(img, "Center of Object: (" + "x: " + str(x + w // 2) + ", " + "y: " + str(y + h // 2) + ")", (10, 60), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                

                center_x = int(x + w // 2)
                center_y = int(y + h // 2)

                # Motor control based on object's center position
                if 80 < center_y < 440:
                    if 50 < center_x < 320:
                        print("Turn Left")
                        Motor.move(speed=0, turn=-30)
                    elif 400 < center_x < 600:
                        print("Turn Right")
                        Motor.move(speed=0, turn=30)
                    elif 320 <= center_x <= 400:
                        Motor.Forward(40)
                        print("Centered")
                    else:
                        Motor.Brake()
                if  (370 < center_y < 400) or area > 30000:
                    Motor.Brake()
                    print("Object Found")
                    cv2.putText(img, "Object Found", (200, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 4)
                else:
                    object_detected = False
                    if not Avoidance_mode:
                        Avoidance_mode = True
                        Avoidance_event.set()
                        print("Switching to Avoidance mode")
                cv2.imshow("Tracking", img)
            else:
                cv2.destroyWindow("Tracking")
                object_detected = False
                if not Avoidance_mode:
                    Avoidance_mode = True
                    Avoidance_event.set()
                    print("Switching to Avoidance mode")
                cv2.putText(img, "Obstacle Avoidance Mode", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)
                cv2.imshow("Obstacle Avoidance", img)
        else:
            if not Avoidance_mode:
                Avoidance_mode = True
                Avoidance_event.set()
                print("Switching to Avoidance mode")
            if Tracking_mode:
                cv2.destroyWindow("Tracking")
                Tracking_mode = False
            cv2.putText(img, "Obstacle Avoidance Mode", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)
            cv2.imshow("Obstacle Avoidance", img)

        # Check for user input to quit the program
        if cv2.waitKey(1) == ord('q'):
            print("Shutting down...")
            cv2.destroyAllWindows()
            Motor.cleanup()
            picam.stop()
            print("Program Terminated \n Exiting....")
            shutdown_event.set()
            
            


try:
    if __name__ == '__main__':
        camera_thread = threading.Thread(target=camera)
        Avoidance_thread = threading.Thread(target=avoidance_mode) 

        camera_thread.start()
        Avoidance_thread.start()

        main()
except KeyboardInterrupt:
    print("KeyboardInterrupt")
finally:
    shutdown_event.set()
    Avoidance_event.clear()
    camera_thread.join()
    cv2.destroyAllWindows()
    Motor.cleanup()
    picam.stop()
    print("Program Terminated \n Exiting....")
    exit()
