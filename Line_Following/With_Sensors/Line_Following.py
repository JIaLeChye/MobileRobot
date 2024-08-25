from PCA9685_MC import Motor_Controller 
from Motor_Encoder import Encoder 
import time 
import RPi.GPIO as GPIO 

def int():  
    global Motor, enc, D1, D2, D3, D4, D5
    Motor = Motor_Controller()
    enc = Encoder() 
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



def main():
    int()



try: 
    if __name__ == 'main': 
        main() 

except KeyboardInterrupt: 
    Motor.cleanup()

