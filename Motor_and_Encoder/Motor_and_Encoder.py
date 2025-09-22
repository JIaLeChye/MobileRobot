from RPi_Robot_Hat_Lib import RobotController
import time

def init():
    global Motor, enc
    Motor = RobotController(wheel_diameter=98)  # diameter in mm
    enc = Motor  # Use same object for encoder functions

def move_to_distance(target_distance, target_speed):
    global Motor, enc
    if target_distance >= 0:
        Motor.Forward(target_speed)  # Move forward
    else:
        Motor.Backward(target_speed)  # Move backward
        target_distance = abs(target_distance)  # Use absolute value for comparison

    while True:
        # Get the encoder counts and current distance
        left_distance = enc.get_distance('LF')
        right_distance = enc.get_distance('RF')
        
        # Get encoder values for display
        left_enc = enc.get_encoder('LF')
        right_enc = enc.get_encoder('RF')

        # Display encoder values and distances
        print("Left Encoder: {:.2f}".format(left_enc))
        print("Right Encoder: {:.2f}".format(right_enc))
        print("Left Distance: {:.2f}m".format(left_distance))
        print("Right Distance: {:.2f}m".format(right_distance))

        # Stop the motor once the target distance is reached
        if right_distance >= target_distance and left_distance >= target_distance:
            Motor.Brake()
            break

        time.sleep(0.1)

def cleanup():
    global Motor, enc
    Motor.cleanup()

def main():
    target_distance = float(input("Enter the target distance (in meters, negative for backward): "))
    target_speed = float(input("Enter the target speed (1 - 100): "))
    move_to_distance(target_distance, target_speed)

if __name__ == '__main__':
    try:
        init()
        main()
    except KeyboardInterrupt:
        print("Shutting down")
        cleanup()