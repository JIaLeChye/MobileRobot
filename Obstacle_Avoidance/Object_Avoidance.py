import cv2 
from picamera2 import Picamera2
from Ultrasonic_sens import Ultrasonic 
from PCA9685_MC import Motor_Controller
from Motor_Encoder import Encoder 
import time 
from libcamera import controls


def init():
    global enc, ultrasonic, Motor, Speed, rotation_speed, threshold, min_thresh_dist, picam2 
    isInit = False

    # picam2 = Picamera2() 
    # picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    # picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    if not isInit: 
        enc = Encoder()
        ultrasonic = Ultrasonic()
        Motor = Motor_Controller()
        Speed = 20
        rotation_speed = 50
        threshold = 30 
        min_thresh_dist = 10

        isInit = True 
    else:
        pass


def obstacle_Avoid(left, front, right):
    global enc, ultrasonic, Motor, Speed, rotation_speed, threshold, min_thresh_dist
    
    # if front > 10:
    #     if right == left:
    #         Motor.Forward(Speed)
    #     elif right > left:
    #         Motor.Clock_Rotate(rotation_speed)
    #         time.sleep(0.1)
    #     elif left > right:
    #         Motor.AntiClock_Rotate(rotation_speed)
    #         time.sleep(0.1)

    if front < threshold :
        if  front <= min_thresh_dist:
            Motor.Backward(Speed)
        elif left < min_thresh_dist and right < min_thresh_dist :
            Motor.Backward(Speed)
            time.sleep(0.1)
        elif left < threshold:
            Motor.Clock_Rotate(rotation_speed)
            time.sleep(0.5)
        elif right < threshold:
            Motor.AntiClock_Rotate(rotation_speed)
            time.sleep(0.5)
        else:
            Motor.Backward(Speed)
            # if right > left:
            #     Motor.Clock_Rotate(rotation_speed)
            #     time.sleep(0.1)
            # elif left > right:
            #     Motor.AntiClock_Rotate(rotation_speed)
            #     time.sleep(0.1)
    
    elif left < threshold:
        Motor.Clock_Rotate(rotation_speed)
        time.sleep(1)
    
    elif right < threshold:
        Motor.AntiClock_Rotate(rotation_speed)  
        time.sleep(1 )

        # if left > right:
        #    Motor.Clock_Rotate(rotation_speed)
        #    time.sleep(0.1)
        # elif right > left:
        #    Motor.AntiClock_Rotate(rotation_speed)
        #    time.sleep(0.1)
        # else:
        #     Motor.Forward(Speed)
        #     time.sleep(0.1)
    
    
    else:
        if right > threshold and left > threshold :
            Motor.Forward(Speed)
        elif right > threshold:
            Motor.Clock_Rotate(rotation_speed)
            time.sleep(0.1)
        elif  left > threshold:
            Motor.AntiClock_Rotate(rotation_speed)
            time.sleep(0.1)
  
            


def main(): 
    global enc, ultrasonic, Motor, Speed, rotation_speed, threshold, min_thresh_dist
    init()
    while True:
        enc.encoder()
        left, front, right = ultrasonic.distances()
        time.sleep(0.1)
        if (left and front and right is not None): 
            print("Left: {:.2f} ".format(left)) 
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
    Motor.Brake()
    enc.stop()
    print("Program Terminated")
    exit
finally: 
    enc.stop()
    print("Program Terminated")
    exit


    
        
    

