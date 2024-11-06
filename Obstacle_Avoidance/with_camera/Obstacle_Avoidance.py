import threading 
import cv2 
from picamera2 import Picamera2
from Ultrasonic_sens import Ultrasonic 
from RPi_Robot_Hat_Lib import RobotController 
import time 
from libcamera import controls


 # enc = Encoder(ODISPLAY=True)
ultrasonic = Ultrasonic()
Motor = RobotController()
vertical = 1
horizontal = 2
Motor.set_servo(vertical, 80)
Motor.set_servo(horizontal, 90)

Speed = 20
rotation_speed = 50
threshold = 30 
min_thresh_dist = 10 
picam2 = Picamera2() 
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
frame_lock = threading.Lock()
capture_thread = threading.Thread(target=capture_frame)  # Start the capture frame thread
shutdown_event = threading.Event()
isInit = True 


# Capture and Display Frame 
def capture_frame():
    global picam2, frame_lock, shutdown_event
    while not shutdown_event.is_set():
        with frame_lock:
            frame = picam2.capture_array()
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            shutdown_event.set()  # Signal to stop the program
            break 
    cv2.destroyAllWindows()  # Cleanup the OpenCV windows


def obstacle_Avoid(left, front, right):
    if front < threshold:
        if front <= min_thresh_dist:
            print("Reversing")
            Motor.Backward(Speed)
            time.sleep(0.1)
            Motor.Brake()
        elif left < min_thresh_dist and right < min_thresh_dist:
            print("Reversing")
            Motor.Backward(Speed)
            time.sleep(0.1)
            Motor.Brake()
        elif left < threshold:
            print("Turning Right") 
            Motor.move(speed=0, turn=-rotation_speed)
            time.sleep(0.5)
            Motor.Brake()
        elif right < threshold:
            print("Turning Left") 
            Motor.move(speed=0, turn=rotation_speed)
            time.sleep(0.5)
            Motor.Brake()
        else:
            print("Reversing")
            Motor.Backward(Speed)
            time.sleep(0.1)
            Motor.Brake()
    
    elif left < threshold:
        print("Turning Right")
        Motor.move(speed=0, turn=-rotation_speed)
        time.sleep(1)
        Motor.Brake()
    
    elif right < threshold:
        print("Turning Left") 
        Motor.move(speed=0, turn=rotation_speed)  
        time.sleep(1)
        Motor.Brake()
    
    else:
        if right > threshold and left > threshold:
            print("Forward") 
            Motor.Forward(Speed)
        elif right > threshold:
            print("Turning Right")
            Motor.move(speed=0, turn=-rotation_speed)
            time.sleep(0.1)
            Motor.Brake()
        elif left > threshold:
            print("Turning Left")
            Motor.move(speed=0, turn=rotation_speed)
            time.sleep(0.1)
            Motor.Brake()


def main(): 
    print("Program Started")
    capture_thread.start()
    while not shutdown_event.is_set():
        # enc.encoder()
        left, front, right = ultrasonic.distances()
        time.sleep(0.1)
        if left is not None and front is not None and right is not None: 
            print("Left: {:.2f}".format(left)) 
            print("Front: {:.2f}".format(front))
            print("Right: {:.2f}".format(right)) 
            print(" ")
            obstacle_Avoid(left, front, right)
            time.sleep(0.1)
        else:
            print("No data received")
            Motor.Brake()
            time.sleep(1)
    
    



try:
    if __name__ == "__main__":
        main()
            

except KeyboardInterrupt:
    shutdown_event.set()
    Motor.cleanup()
    # enc.stop()
    print("Program Terminated")

finally: 
    shutdown_event.set()
    # enc.stop()
    capture_thread.join()
    cv2.destroyAllWindows()
    exit()
    print("Program Terminated")