from RPi_Robot_Hat_Lib import RobotController 
import time 

Motor = RobotController()

def main():
    print("Program Start")
    Motor.reset_encoders()
    motor_list = ['RF', 'RB', 'LF', 'LB']  # Using a different name for the motor list

    while True:
        Motor.move(30, 0)  # Assuming move(30, 0) is the command to start movement
        print()
        for motor in motor_list:
            # Get encoder value and ensure it's not impacted by negative counts
            encoder_value = Motor.get_encoder(motor)
            distance = abs(Motor.get_distance(motor))  # Use absolute value for distance if direction isn’t needed
            rpm = abs(Motor.get_rpm(motor))  # Take absolute value to prevent negative RPM
            
            # Print debug information to verify each step
            print(f"Motor: {motor} - Distance: {distance:.2f} cm, Encoder Value: {encoder_value}, RPM: {rpm:.2f}")

        time.sleep(1)

try: 
    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    Motor.cleanup()
finally:
    Motor.cleanup()
