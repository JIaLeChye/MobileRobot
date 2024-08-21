import RPi.GPIO as GPIO 
from PCA9685_MC import  Motor_Controller  
import time 
from Motor_Encoder import Encoder 



def init(): 
    global Leftsensor, Rightsensor, motor, enc
    Leftsensor = 13
    Rightsensor  = 11 
    GPIO.setmode(GPIO.BCM) 
    
    motor = Motor_Controller() 
    enc = Encoder()

def main(): 
    init()
    
    while True:
        GPIO.setup(Leftsensor, GPIO.IN)
        GPIO.setup(Rightsensor, GPIO.IN)
        Rightstat = GPIO.input(Leftsensor)
        Leftstat = GPIO.input(Rightsensor)
        print(f"Left Sensor: {Leftstat}, Right Sensor: {Rightstat}")
        enc.encoder() 
        if (Leftstat and Rightstat) is not None: 
            if Leftstat == 0 and Rightstat == 0:
                motor.Forward(15)
            elif Leftstat == 0 and Rightstat == 1:
                motor.Clock_Rotate(50) 
                time.sleep(0.5)
            elif Leftstat == 1 and Rightstat == 0:
                motor.AntiClock_Rotate(50)
                time.sleep(0.5)
            else:
                motor.Brake()
        else:
            motor.Brake()
            

try:

    if __name__ == "__main__":
        main() 
except KeyboardInterrupt:
    motor.Brake() 
    enc.stop()
    GPIO.cleanup() 
