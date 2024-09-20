from PCA9685_MC import Motor_Controller
from Motor_EncoderV2 import Encoder
import time

def init():
    global enc, Motor
    Motor = Motor_Controller() 
    enc = Encoder() 

def move_to_distance(target_distance, target_speed):
    global Motor, enc
    Motor.Forward(target_speed)

    while True:
        # Get the encoder counts and current distance
        left_enc, right_enc = enc.encoder()
        left_distance, right_distance = enc.distance()

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
    enc.stop()

def main():
    target_distance = float(input("Enter the target distance (in meters): "))
    target_speed = float(input("Enter the target spee (1 - 100): "))
    move_to_distance(target_distance, target_speed )
if __name__ == '__main__':
    try:
        init()
        main()
    except KeyboardInterrupt:
        print("Shutting down")
        cleanup()
