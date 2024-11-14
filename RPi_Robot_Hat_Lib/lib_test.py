from RPi_Robot_Hat_Lib import RobotController 
import time


Motor = RobotController()
Refresh_time = 2 


def main():
    print("Program Start")
    Motor.reset_encoders()
    # Motor.Forward(30)

   
    while True:
        distance = input("Enter distance: ") 
        speed = input("Enter speed: ")
        Motor.move_distance(int(distance), int(speed))
        Motor.disp_fwd_enc()
        time.sleep(Refresh_time)  # Wait for 1 second
        Motor.clear_disp()
        # display_two_motors_data('LF', 'LB')  # Display data for LF and LB motors
        Motor.disp_bwd_enc()
        time.sleep(Refresh_time)  # Wait for 1 second


try:
    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    Motor.clear_disp()
    Motor.cleanup()
finally:
    Motor.clear_disp()
    Motor.cleanup()
    exit()
