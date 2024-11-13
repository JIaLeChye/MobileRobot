from RPi_Robot_Hat_Lib import RobotController , Encoder
import time


Motor = RobotController()
Enc = Encoder()

Refresh_time = 2 


def main():
    print("Program Start")
    Motor.reset_encoders()
    # Motor.Forward(30)

   
    while True:
        distance = input("Enter distance: ") 
        speed = input("Enter speed: ")
        Motor.move_distance(int(distance), int(speed))
        Enc.disp_fwd_enc()
        time.sleep(Refresh_time)  # Wait for 1 second
        Enc.clear_disp()
        # display_two_motors_data('LF', 'LB')  # Display data for LF and LB motors
        Enc.disp_bwd_enc()
        time.sleep(Refresh_time)  # Wait for 1 second


try:
    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    Enc.clear_disp()
    Motor.cleanup()
finally:
    Enc.clear_disp()
    Motor.cleanup()
