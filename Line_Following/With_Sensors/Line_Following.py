from RPi_Robot_Hat_Lib import RobotController 
import time 



Motor = RobotController() 



def main():
    while True: 
        Line_Sensor = Motor.read_line_sensors()
        outerRight = (Line_Sensor >> 4) & 1
        Right = (Line_Sensor >> 3) & 1
        center = (Line_Sensor >> 2) & 1
        Left = (Line_Sensor >> 1) & 1
        outerLeft = Line_Sensor & 1
        if outerRight == 0 and Right == 0 and center == 0 and Left == 0 and outerLeft == 0:
            Motor.Brake()
            print("Brake")

        if (outerRight == 1 or Right == 1) and center == 0 and Left == 0 and outerLeft == 0:
            print("Turn Right")  # Normal clockwise rotation
            Motor.move(speed=0, turn=30)

        if (outerLeft == 1 or Left == 1) and center == 0 and Right == 0 and outerRight == 0:
            Motor.move(speed=0, turn=-30)
            print("Turn Left")  # Normal anticlockwise rotation

        if (center == 1 and Right == 1 and Left == 1 and outerLeft == 0 and outerRight == 0) or (center == 1 and Right == 0 and Left == 0 and outerRight == 0 and outerLeft == 0):
            Motor.Forward(40)
            print("Forward")

        if center == 1 and Right == 1 and Left == 1 and outerRight == 1 and outerLeft == 1:
            Motor.Brake()
            print("Brake")


try: 
    if __name__ == '__main__': 
        main() 

except KeyboardInterrupt: 
    Motor.cleanup()
    print("Program Stopped")
