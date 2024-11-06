from Ultrasonic_sens import Ultrasonic 
from RPi_Robot_Hat_Lib import RobotController
import time 



        
# enc = Encoder(debug=True)
ultrasonic = Ultrasonic(debug=True)
Motor = RobotController()
Speed = 20
rotation_speed = 15
threshold = 30 
min_thresh_dist = 10 
isInit = True 


def obstacle_Avoid(left, front, right):
    
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
            Motor.move(speed=0, turn=-rotation_speed)
            time.sleep(0.5)
            Motor.Brake()
        elif right < threshold:
            Motor.move(speed=0, turn=rotation_speed)
            time.sleep(0.5)
            Motor.Brake()
        else:
            Motor.Backward(Speed)
            time.sleep(0.1)
            Motor.Brake()
    
    elif left < threshold:
        Motor.move(speed=0, turn=-rotation_speed)
        time.sleep(1)
        Motor.Brake()
    
    elif right < threshold:
        Motor.move(speed=0, turn=rotation_speed)  
        time.sleep(1)
        Motor.Brake()
    
    elif right < threshold and left < threshold and front > threshold :
            Motor.Forward(Speed)
            time.sleep(0.1)
            Motor.Brake()
    else:
        Motor.Brake()
            


def main():  
    while True: 
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
    Motor.Brake()
    # enc.stop()
    print("Program Terminated")
finally:
    # enc.stop()
    Motor.cleanup()
    print("Program Terminated")

