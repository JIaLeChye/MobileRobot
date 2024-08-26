from PCA9685_MC import Motor_Controller 
from Motor_Encoder import Encoder 
import time 
import RPi.GPIO as GPIO 

def init():  
    global Motor, enc, D1, D2, D3, D4, D5
    Motor = Motor_Controller()
    enc = Encoder(debug = True) 
    GPIO.setmode(GPIO.BCM)
    D1 = 6 
    D2 = 11
    D3 = 13
    D4 = 17 
    D5 = 19 

    GPIO.setup(D1, GPIO.IN)
    GPIO.setup(D2, GPIO.IN)
    GPIO.setup(D3, GPIO.IN)
    GPIO.setup(D4, GPIO.IN)
    GPIO.setup(D5, GPIO.IN)
    print("GPIO Setup Complete")



def main():
    global Motor, enc, D1, D2, D3, D4, D5
    init()
    while True: 
        enc.encoder()
        # GPIO.setup(D1, GPIO.IN)
        # GPIO.setup(D2, GPIO.IN)
        # GPIO.setup(D3, GPIO.IN)
        # GPIO.setup(D4, GPIO.IN)
        # GPIO.setup(D5, GPIO.IN)
        outerRight = GPIO.input(D1)
        Right = GPIO.input(D2)
        center =  GPIO.input(D3)
        Left  = GPIO.input(D4)
        outerLeft = GPIO.input(D5) 
        if outerRight == 0 and Right == 0 and center == 0 and Left == 0 and outerLeft == 0:
            Motor.Brake()
            print("Brake")

        if (outerRight == 1 or Right == 1) and center == 0 and Left == 0 and outerLeft == 0:
            if outerRight == 1 :
               Motor.Clock_Rotate(20)
               print("Turn sharp Right")  # Turn faster if only outerRight is detected
            else:
                print("Turn Right")  # Normal clockwise rotation
                Motor.Clock_Rotate(20)

        if (outerLeft == 1 or Left == 1) and center == 0 and Right == 0 and outerRight == 0:
            if outerLeft == 1: 
                print("Turn sharp Left")  # Turn faster if only outerLeft is detected
                Motor.AntiClock_Rotate(20)
            else:
                Motor.AntiClock_Rotate(20)
                print("Turn Left")  # Normal anticlockwise rotation

        if (center == 1 and Right == 1 and Left == 1 and outerLeft == 0 and outerRight == 0) or (center == 1 and Right == 0 and Left == 0 and outerRight == 0 and outerLeft == 0):
            Motor.Forward(15)
            print("Forward")

        if center == 1 and Right == 1 and Left == 1 and outerRight == 1 and outerLeft == 1:
            Motor.Brake()
            print("Brake")

        if center == 0 and Right == 0 and Left == 0 and (outerRight == 1 or outerLeft == 1):
            if outerRight == 1 and outerLeft == 0:
                Motor.Clock_Rotate(20)  # Prioritize turning clockwise with higher speed
                print("Turn Right") 
            elif outerLeft == 1 and outerRight == 0:
                Motor.AntiClock_Rotate(20)  # Prioritize turning anticlockwise with higher speed
                print("Turn Left")

try: 
    if __name__ == '__main__': 
        main() 

except KeyboardInterrupt: 
    Motor.cleanup()
    enc.stop()
    print("Program Stopped")
