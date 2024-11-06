from RPi_Robot_Hat_Lib import RobotController 
import time 
import RPi.GPIO as GPIO 


Motor = RobotController() 
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
    while True: 
        # enc.encoder()
        Line_Sensor = Motor.read_line_sensors()
        outerRight = Line_Sensor[0]
        Right = Line_Sensor[1]
        center =  Line_Sensor[2]
        Left  = Line_Sensor[3]
        outerLeft = Line_Sensor[4]
        if outerRight == 0 and Right == 0 and center == 0 and Left == 0 and outerLeft == 0:
            Motor.Brake()
            print("Brake")

        if (outerRight == 1 or Right == 1) and center == 0 and Left == 0 and outerLeft == 0:
            print("Turn Right")  # Normal clockwise rotation
            Motor.move(speed=0, turn=-20)

        if (outerLeft == 1 or Left == 1) and center == 0 and Right == 0 and outerRight == 0:
            Motor.move(speed=0, turn=20)
            print("Turn Left")  # Normal anticlockwise rotation

        if (center == 1 and Right == 1 and Left == 1 and outerLeft == 0 and outerRight == 0) or (center == 1 and Right == 0 and Left == 0 and outerRight == 0 and outerLeft == 0):
            Motor.Forward(15)
            print("Forward")

        if center == 1 and Right == 1 and Left == 1 and outerRight == 1 and outerLeft == 1:
            Motor.Brake()
            print("Brake")


try: 
    if __name__ == '__main__': 
        main() 

except KeyboardInterrupt: 
    Motor.cleanup()
    # enc.stop()
    print("Program Stopped")
