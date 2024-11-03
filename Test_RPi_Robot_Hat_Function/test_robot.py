from RPi_Robot_Hat_Lib import RobotController
import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# Mario tune notes (frequency in Hz)
MARIO_MELODY = [
    (660, 0.2), (660, 0.2), (0, 0.2), (660, 0.2), (0, 0.2), (523, 0.2), (660, 0.2),
    (0, 0.2), (784, 0.2), (0, 0.2), (392, 0.2), (0, 0.2), (523, 0.2), (0, 0.2),
    (392, 0.2), (0, 0.2), (330, 0.2), (0, 0.2), (440, 0.2), (0, 0.2), (494, 0.2),
    (466, 0.2), (440, 0.2), (0, 0.2), (392, 0.2), (0, 0.2), (660, 0.2), (784, 0.2),
    (880, 0.2), (0, 0.2), (698, 0.2), (784, 0.2), (0, 0.2), (660, 0.2), (0, 0.2),
    (523, 0.2), (587, 0.2), (494, 0.2)
]

def initialize_oled():
    """Initialize OLED display"""
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        disp.fill(0)
        disp.show()
        image = Image.new("1", (disp.width, disp.height))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        return disp, image, draw, font
    except Exception as e:
        print(f"Error initializing OLED: {e}")
        return None, None, None, None

def test_menu():
    print("\nRobot Test Menu:")
    print("1. Basic movements test")
    print("2. Distance movement test")
    print("3. Square pattern")
    print("4. Circle pattern")
    print("5. Speed test")
    print("6. Encoder test")
    print("7. Line following test")
    print("8. Battery voltage test")
    print("9. Servo test")
    print("10. Buzzer test (Mario theme)")
    print("11. Horizontal movements test")
    print("0. Exit")

def test_basic_movements(robot):
    print("\nTesting basic movements...")
    
    # Forward
    print("\nTesting Forward...")
    robot.Forward(50)
    time.sleep(2)
    robot.stop()
    time.sleep(1)
    
    # Backward
    print("Testing Backward...")
    robot.Backward(50)
    time.sleep(2)
    robot.stop()
    time.sleep(1)
    
    # Turn Right
    print("Testing Right Turn...")
    robot.move(speed=0, turn=50)  # Positive turn for right
    time.sleep(2)
    robot.stop()
    time.sleep(1)
    
    # Turn Left
    print("Testing Left Turn...")
    robot.move(speed=0, turn=-50)  # Negative turn for left
    time.sleep(2)
    robot.stop()
    time.sleep(1)

def test_horizontal_movement(robot, shift_pos, speed):
    
    print("\nTesting horizontal movements...") 
    # Shift Left 
    if shift_pos == 'L':
        print("Testing Shift Left...")
        robot.set_motor('LF', -speed)
        robot.set_motor('RF', speed)
        robot.set_motor('LB', speed)
        robot.set_motor('RB', -speed)
    
    # Shift Right
    if shift_pos == 'R':
        print("Testing Shift Right...")
        robot.set_motor('LF', speed)
        robot.set_motor('RF', -speed)
        robot.set_motor('LB', -speed)
        robot.set_motor('RB', speed)

    else:
        print("Invalid Shift Position")
        return

def test_distance_movement(robot, oled_objects):
    print("\nTesting distance movements...")
    distance = float(input("Enter distance in meters: "))
    speed = int(input("Enter speed (1-100): "))
    
    disp, image, draw, font = oled_objects
    if all([disp, image, draw, font]):
        draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
        draw.text((0, 0), f"Moving {abs(distance)*100:.0f}cm", font=font, fill=255)
        draw.text((0, 20), f"Speed: {speed}%", font=font, fill=255)
        disp.image(image)
        disp.show()
    
    robot.move_distance(distance, speed)
    
def test_square(robot):
    print("\nDriving in square pattern...")
    for _ in range(2):
        # Move forward
        robot.Forward(30)
        time.sleep(2)
        robot.stop()
        time.sleep(0.5)
        # Turn right
        robot.move(speed=0, turn=30)
        time.sleep(1)
        robot.stop()
        time.sleep(0.5)

def test_circle(robot):
    print("\nDriving in circle...")
    duration = 5
    start_time = time.time()
    while time.time() - start_time < duration:
        robot.move(speed=20, turn=30)  # Forward with constant turn
        time.sleep(0.1)
    robot.stop()

def test_speeds(robot):
    print("\nTesting different speeds...")
    for speed in [20, 40, 60, 80, 100]:
        print(f"Testing speed: {speed}%")
        robot.Forward(speed)
        time.sleep(2)
        robot.stop()
        time.sleep(1)

def test_encoders(robot):
    print("\nTesting encoders...")
    # Get initial values
    start_values = {
        'RF': robot.get_encoder('RF'),
        'RB': robot.get_encoder('RB'),
        'LF': robot.get_encoder('LF'),
        'LB': robot.get_encoder('LB')
    }
    
    # Move forward briefly
    print("Moving forward...")
    robot.Forward(50)
    time.sleep(2)
    robot.stop()
    
    # Get final values
    end_values = {
        'RF': robot.get_encoder('RF'),
        'RB': robot.get_encoder('RB'),
        'LF': robot.get_encoder('LF'),
        'LB': robot.get_encoder('LB')
    }
    
    # Print changes
    print("\nEncoder changes:")
    for motor in ['RF', 'RB', 'LF', 'LB']:
        change = end_values[motor] - start_values[motor]
        print(f"{motor}: {change}")
        
def test_line_following(robot, oled_objects):
    print("\nTesting line following for 30 seconds...")
    print("Place robot on the line and press Enter to start")
    input()
    
    disp, image, draw, font = oled_objects
    start_time = time.time()
    base_speed = 30
    
    try:
        while time.time() - start_time < 30:
            sensors = robot.read_line_sensors()
            sensor_bits = format(sensors, '05b')
            print(f"Sensors: {sensor_bits}", end='\r')
            
            if all([disp, image, draw, font]):
                draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
                draw.text((0, 0), "Line Following", font=font, fill=255)
                draw.text((0, 20), f"Sensors: {sensor_bits}", font=font, fill=255)
                time_left = 30 - (time.time() - start_time)
                draw.text((0, 40), f"Time: {time_left:.1f}s", font=font, fill=255)
                disp.image(image)
                disp.show()
            
            if sensors & 0b00100:  # Center sensor
                robot.move(speed=base_speed, turn=0)
            elif sensors & 0b00010:  # Left of center
                robot.move(speed=base_speed-10, turn=-15)
            elif sensors & 0b01000:  # Right of center
                robot.move(speed=base_speed-10, turn=15)
            elif sensors & 0b00001:  # Far left
                robot.move(speed=base_speed-15, turn=-25)
            elif sensors & 0b10000:  # Far right
                robot.move(speed=base_speed-15, turn=25)
            else:
                robot.stop()
            
            time.sleep(0.01)
            
    finally:
        robot.stop()
        if all([disp, image, draw, font]):
            disp.fill(0)
            disp.show()
        print("\nLine following test completed")

def test_battery(robot, oled_objects):
    print("\nTesting battery voltage...")
    try:
        disp, image, draw, font = oled_objects
        
        for i in range(5):  # Read 5 times
            voltage = robot.get_battery()
            print(f"Battery Voltage: {voltage:.1f}V")
            
            # Update OLED display
            if all([disp, image, draw, font]):
                draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
                draw.text((0, 0), "Battery Status:", font=font, fill=255)
                draw.text((0, 20), f"Voltage: {voltage:.1f}V", font=font, fill=255)
                
                # Add battery level indicator (9V-13V range)
                level = min(100, max(0, (voltage - 9.0) * 100 / (13.0 - 9.0)))  # Map 9V-13V to 0-100%
                draw.text((0, 40), f"Level: {level:.0f}%", font=font, fill=255)
                
                # Draw battery bar
                bar_width = int(disp.width * level / 100)
                draw.rectangle((0, 55, bar_width, 63), outline=255, fill=255)
                
                # Add low battery warning
                if voltage < 9.5:
                    draw.text((0, 30), "LOW BATTERY!", font=font, fill=255)
                
                disp.image(image)
                disp.show()
            
            time.sleep(1)
            
    except Exception as e:
        print(f"Error reading voltage: {e}")
    finally:
        if all([disp, image, draw, font]):
            disp.fill(0)
            disp.show()
            
def test_servos(robot, oled_objects):
    print("\nTesting servos...")
    disp, image, draw, font = oled_objects
    
    positions = [(45, 135), (135, 45), (0, 180), (180, 0), (90, 90)]
    
    for pos1, pos2 in positions:
        print(f"Moving to positions: Servo1={pos1}°, Servo2={pos2}°")
        
        if all([disp, image, draw, font]):
            draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
            draw.text((0, 0), "Servo Test", font=font, fill=255)
            draw.text((0, 20), f"Servo 1: {pos1}°", font=font, fill=255)
            draw.text((0, 40), f"Servo 2: {pos2}°", font=font, fill=255)
            disp.image(image)
            disp.show()
        
        robot.set_servo(1, pos1)
        robot.set_servo(2, pos2)
        time.sleep(1)
    
    robot.set_servo(1, 90)
    robot.set_servo(2, 90)

def test_buzzer(robot, oled_objects):
    print("\nPlaying Mario theme...")
    try:
        disp, image, draw, font = oled_objects
        if all([disp, image, draw, font]):
            draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
            draw.text((0, 20), "Playing", font=font, fill=255)
            draw.text((0, 30), "Mario Theme", font=font, fill=255)
            disp.image(image)
            disp.show()
        
        for note, duration in MARIO_MELODY:
            if note == 0:
                time.sleep(duration)
            else:
                robot.play_tone(note, duration)
                
        print("Melody completed!")
        
    except Exception as e:
        print(f"Error playing melody: {e}")
    finally:
        if all([disp, image, draw, font]):
            disp.fill(0)
            disp.show()

def main():
    robot = RobotController(wheel_diameter=98)
    oled_objects = initialize_oled()
    
    robot.set_servo(1, 90)
    robot.set_servo(2, 90)
    
    try:
        while True:
            test_menu()
            choice = input("\nSelect test (0-10): ")
            
            if choice == '0':
                break
            elif choice == '1':
                test_basic_movements(robot)
            elif choice == '2':
                test_distance_movement(robot, oled_objects)
            elif choice == '3':
                test_square(robot)
            elif choice == '4':
                test_circle(robot)
            elif choice == '5':
                test_speeds(robot)
            elif choice == '6':
                test_encoders(robot)
            elif choice == '7':
                test_line_following(robot, oled_objects)
            elif choice == '8':
                test_battery(robot, oled_objects)
            elif choice == '9':
                test_servos(robot, oled_objects)
            elif choice == '10':
                test_buzzer(robot, oled_objects)
            elif choice == '11':
                shift_pos = input('Enter Shift Position (L, R)')
                speed = int(input("Enter speed (1-100): "))
                test_horizontal_movement(robot, shift_pos, speed)
            else:
                print("Invalid choice!")
                
            input("\nPress Enter to continue...")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        robot.set_servo(1, 90)
        robot.set_servo(2, 90)
        time.sleep(0.5)
        
        if all(oled_objects):
            oled_objects[0].fill(0)
            oled_objects[0].show()
            
        robot.cleanup()
        print("\nTest completed")

if __name__ == "__main__":
    main()