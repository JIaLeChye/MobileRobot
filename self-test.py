from RPi_Robot_Hat_Lib import RobotController
from Ultrasonic_sens import Ultrasonic
from IRSens import IRsens
import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
from picamera2 import Picamera2  


# Mario tune notes (frequency in Hz)
MARIO_MELODY = [ 
    (660, 0.12), (660, 0.12), (0, 0.12), (660, 0.12), (0, 0.12), (523, 0.12), (660, 0.12),
    (0, 0.12), (784, 0.12), (0, 0.12), (392, 0.12), (0, 0.12), (523, 0.12), (0, 0.12),
    (392, 0.12), (0, 0.12), (330, 0.12), (0, 0.12), (440, 0.12), (0, 0.12), (494, 0.12),
    (466, 0.12), (440, 0.12), (0, 0.12), (392, 0.12), (0, 0.12), (660, 0.12), (784, 0.12),
    (880, 0.12), (0, 0.12), (698, 0.12), (784, 0.12), (0, 0.12), (660, 0.12), (0, 0.12),
    (523, 0.12), (587, 0.12), (494, 0.12)
]

def initialize_oled():
    global disp, image, draw, font
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
    print("11. Ultrasonic sensor test")
    print("12. IR sensor test")
    print("13. Camera test")
    print("14. OLED test")
    print("15. I2C test")
    print("0. Exit")

def test_i2C():
    print("\nTesting I2C bus...")
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        while not i2c.try_lock():
            pass
        addresses = i2c.scan()
        i2c.unlock()
        if addresses:
            print("I2C devices found at addresses:")
            for addr in addresses:
                if hex(addr) == hex(0x3c):  # Common address for SSD1306 OLED
                    print(f"  - {hex(addr)} (OLED Display)")
                elif hex(addr) == hex(0x9):  # RPi Robot Hat
                    print(f"  - {hex(addr)} (Raspberry Pi Robot Hat)")
                elif hex(addr) == hex(0x8):  # Grove Pi Hat
                    print(f"  - {hex(addr)} (Grove Pi Hat)")
                else:
                    print(f"  - {hex(addr)} (Unknown Device)")
        else:
            print("No I2C devices found.")
    except Exception as e:
        print(f"I2C test error: {e}")


    print("I2C test completed.\n")
def test_camera():
    print("\nTesting Camera...")
    picam2 = None
    try:
        picam2 = Picamera2()
        picam2.start()
        time.sleep(2)  # Allow camera to warm up
        frame = picam2.capture_array()
        if frame is not None:
            print("Camera test successful: Frame captured.")
        else:
            print("Camera test failed: No frame captured.")
    except ImportError:
        print("Picamera2 is not installed.")
    except Exception as e:
        print(f"Camera test error: {e}")
    finally:
        if picam2 is not None:
            try:
                print("Stopping camera...")
                picam2.stop()
                picam2.close()  # Properly close the camera to free resources
            except Exception as e:
                print(f"Error closing camera: {e}")
        print("Camera test completed.\n")

def test_OLED():
    global disp, image, draw, font
    print("\nTesting OLED display...")
    try:
        disp, image, draw, font = initialize_oled()
        if all([disp, image, draw, font]):
            draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
            draw.text((0, 0), "OLED Test", font=font, fill=255)
            disp.image(image)
            disp.show()
            time.sleep(3)
            disp.fill(1)
            disp.show()
            time.sleep(3)
            disp.fill(0)
            disp.show()
            print("OLED test successful.")
        else:
            print("OLED test failed: Display not initialized.")
    except Exception as e:
        print(f"OLED test error: {e}")
    finally:
        if all([disp, image, draw, font]) and disp is not None:
            disp.fill(0)
            disp.show()
        print("OLED test completed.\n")


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

    print("\nTesting encoders (with reset)...")
    print("Resetting encoders to zero...")
    robot.reset_encoders()
    time.sleep(0.2)
    start_values = {
        'RF': robot.get_encoder('RF'),
        'RB': robot.get_encoder('RB'),
        'LF': robot.get_encoder('LF'),
        'LB': robot.get_encoder('LB')
    }
    print("Initial encoder values:")
    for k, v in start_values.items():
        print(f"  {k}: {v}")

    print("Moving forward...")
    robot.Forward(50)
    time.sleep(2)
    robot.stop()
    time.sleep(0.2)

    end_values = {
        'RF': robot.get_encoder('RF'),
        'RB': robot.get_encoder('RB'),
        'LF': robot.get_encoder('LF'),
        'LB': robot.get_encoder('LB')
    }
    print("Final encoder values:")
    for k, v in end_values.items():
        print(f"  {k}: {v}")

    print("\nEncoder changes:")
    for motor in ['RF', 'RB', 'LF', 'LB']:
        change = end_values[motor] - start_values[motor]
        print(f"{motor}: {change}")
    print("Encoder test complete.\n")
        
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

            if sensors == 0:
                print("\nNo line detected. Stopping test.")
                robot.stop()
                break
            elif sensors & 0b00100:  # Center sensor
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
    global disp, image, draw, font
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
    global disp, image, draw, font
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

def test_ultrasonic():
    print("\nTesting Ultrasonic Sensors...")
    ultrasonic = Ultrasonic(debug=True)
    print("\nRaw distance readings (cm):")
    for i in range(3):
        left, front, right = ultrasonic.distances()
        print(f"  Reading {i+1}: Left: {left if left else 'N/A'} | Front: {front if front else 'N/A'} | Right: {right if right else 'N/A'}")
        time.sleep(1)
    print("\nAveraged readings (cm):")
    left, front, right = ultrasonic.distances(use_average=True, samples=5)
    print(f"  Left: {left if left else 'N/A'} | Front: {front if front else 'N/A'} | Right: {right if right else 'N/A'}")
    distance, direction = ultrasonic.get_closest_obstacle()
    if distance:
        print(f"Closest obstacle: {distance:.1f}cm to the {direction}")
    else:
        print("No obstacles detected")
    print("\nPath clear test (30cm threshold):")
    if ultrasonic.is_path_clear(30):
        print("Path is clear for 30cm+")
    else:
        print("Path is blocked within 30cm")
    ultrasonic.cleanup()
    print("Ultrasonic sensor test complete.\n")

def test_ir_sensor():
    print("\nTesting IR Sensor...")
    ir = IRsens(debug=True)
    print("Reading IR sensor status for 5 seconds...")
    start = time.time()
    try:
        while time.time() - start < 5:
            status = ir.status()
            print(f"IR Sensor Status: {'Obstacle' if status else 'Clear'}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nIR sensor test interrupted.")
    finally:
        ir.cleanup()
        print("IR sensor test complete.\n")

def main():
    robot = RobotController(wheel_diameter=98)
    oled_objects = initialize_oled()
    
    robot.set_servo(1, 90)
    robot.set_servo(2, 90)
    
    try:
        while True:
            test_menu()
            choice = input("\nSelect test (0-15): ")
            
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
                test_ultrasonic()
            elif choice == '12':
                test_ir_sensor()
            elif choice == '13':
                test_camera()
            elif choice == '14':
                test_OLED()
            elif choice == '15':
                test_i2C()
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
        
        if all(oled_objects) and oled_objects[0] is not None:
            oled_objects[0].fill(0)
            oled_objects[0].show()
            
        robot.cleanup()
        print("\nTest completed")

if __name__ == "__main__":
    main()
