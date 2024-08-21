import threading 
import cv2 
from picamera2 import Picamera2
from Ultrasonic_sens import Ultrasonic 
from PCA9685_MC import Motor_Controller
from Motor_Encoder import Encoder 
import time 
from libcamera import controls


def init():
    global enc, ultrasonic, Motor, Speed, rotation_speed, threshold, min_thresh_dist, picam2, frame_lock, shutdown_event, isInit
    isInit = False

    if not isInit: 
        picam2 = Picamera2() 
        picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
        picam2.start()
        picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        enc = Encoder(ODISPLAY=True)
        ultrasonic = Ultrasonic()
        Motor = Motor_Controller()
        Speed = 20
        rotation_speed = 50
        threshold = 30 
        min_thresh_dist = 10 
        frame_lock = threading.Lock()
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
    global enc, ultrasonic, Motor, Speed, rotation_speed, threshold, min_thresh_dist
    
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
            Motor.Clock_Rotate(rotation_speed)
            time.sleep(0.5)
            Motor.Brake()
        elif right < threshold:
            print("Turning Left") 
            Motor.AntiClock_Rotate(rotation_speed)
            time.sleep(0.5)
            Motor.Brake()
        else:
            print("Reversing")
            Motor.Backward(Speed)
            time.sleep(0.1)
            Motor.Brake()
    
    elif left < threshold:
        print("Turning Right")
        Motor.Clock_Rotate(rotation_speed)
        time.sleep(1)
        Motor.Brake()
    
    elif right < threshold:
        print("Turning Left") 
        Motor.AntiClock_Rotate(rotation_speed)  
        time.sleep(1)
        Motor.Brake()
    
    else:
        if right > threshold and left > threshold:
            print("Forward") 
            Motor.Forward(Speed)
        elif right > threshold:
            print("Turning Right")
            Motor.Clock_Rotate(rotation_speed)
            time.sleep(0.1)
            Motor.Brake()
        elif left > threshold:
            print("Turning Left")
            Motor.AntiClock_Rotate(rotation_speed)
            time.sleep(0.1)
            Motor.Brake()


def main(): 
    global enc, ultrasonic, Motor, Speed, rotation_speed, threshold, min_thresh_dist, picam2, shutdown_event
    
    init()
    print("Program Started")
    
    capture_thread = threading.Thread(target=capture_frame)  # Start the capture frame thread
    capture_thread.start()
    
    try:
        while not shutdown_event.is_set():
            enc.encoder()
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

    except KeyboardInterrupt:
        shutdown_event.set()
        Motor.Brake()
        enc.stop()
        print("Program Terminated")

    finally: 
        shutdown_event.set()
        enc.stop()
        capture_thread.join()
        cv2.destroyAllWindows()
        exit()
        print("Program Terminated")


if __name__ == "__main__":
    main()
