import time
import sys

try:
    from RPi_Robot_Hat_Lib import RobotController
except ImportError:
    from Libraries.RPi_Robot_Hat_Lib.RPi_Robot_Hat_Lib import RobotController

from Libraries.Ultrasonic_Sensor.Ultrasonic_sens import Ultrasonic
from Libraries.IR_Sensor.IRSens import IRsens

try:
    from picamera2 import Picamera2
    CAMERA_AVAILABLE = True
    CAMERA_TYPE = "picamera2"
except ImportError:
    try:
        import cv2
        CAMERA_AVAILABLE = True
        CAMERA_TYPE = "opencv"
    except ImportError:
        CAMERA_AVAILABLE = False
        CAMERA_TYPE = None

def self_check():
    print("Starting robot self-check...")
    robot = RobotController(debug=True)
    ultrasonic = Ultrasonic(debug=True)
    ir_sensor = IRsens(debug=True)
    results = {}
    oled_lines = []
    
    try:
        # I2C Communication Test
        try:
            robot.__version__()
            print("I2C communication: OK")
            results['i2c'] = True
            oled_lines.append("I2C: PASS")
        except Exception as e:
            print(f"I2C communication: FAIL ({e})")
            results['i2c'] = False
            oled_lines.append("I2C: FAIL")

        # Motor Test
        print("Testing motors...")
        try:
            robot.Forward(30)
            time.sleep(1)
            robot.Backward(30)
            time.sleep(1)
            robot.Brake()
            print("Motors: OK")
            results['motors'] = True
            oled_lines.append("Motors: PASS")
        except Exception as e:
            print(f"Motors: FAIL ({e})")
            results['motors'] = False
            oled_lines.append("Motors: FAIL")

        # Encoder Test
        print("Testing encoders...")
        try:
            enc_before = robot.get_encoder('LF')
            robot.Forward(30)
            time.sleep(1)
            robot.Brake()
            enc_after = robot.get_encoder('LF')
            if enc_after != enc_before:
                print(f"Encoders: OK (LF: {enc_before} -> {enc_after})")
                results['encoders'] = True
                oled_lines.append("Encoders: PASS")
            else:
                print("Encoders: FAIL (no change detected)")
                results['encoders'] = False
                oled_lines.append("Encoders: FAIL")
        except Exception as e:
            print(f"Encoders: FAIL ({e})")
            results['encoders'] = False
            oled_lines.append("Encoders: FAIL")

        # Line Sensor Test
        print("Testing line sensors...")
        try:
            digital = robot.read_line_sensors()
            analog = robot.read_line_analog()
            print(f"Line sensors: OK (Digital: {bin(digital)}, Analog: {analog})")
            results['line_sensors'] = True
            oled_lines.append("Line: PASS")
        except Exception as e:
            print(f"Line sensors: FAIL ({e})")
            results['line_sensors'] = False
            oled_lines.append("Line: FAIL")

        # Ultrasonic Sensor Test
        print("Testing ultrasonic sensors...")
        try:
            left, front, right = ultrasonic.distances()
            print(f"Ultrasonic: L={left:.1f}cm F={front:.1f}cm R={right:.1f}cm")
            results['ultrasonic'] = True
            oled_lines.append("Ultra: PASS")
        except Exception as e:
            print(f"Ultrasonic: FAIL ({e})")
            results['ultrasonic'] = False
            oled_lines.append("Ultra: FAIL")

        # IR Sensor Test
        print("Testing IR sensor...")
        try:
            ir_status = ir_sensor.status()
            print(f"IR Sensor: {ir_status}")
            results['ir'] = True
            oled_lines.append("IR: PASS")
        except Exception as e:
            print(f"IR Sensor: FAIL ({e})")
            results['ir'] = False
            oled_lines.append("IR: FAIL")

        # Battery Test
        print("Testing battery voltage...")
        try:
            voltage = robot.get_battery()
            print(f"Battery voltage: {voltage:.2f}V")
            results['battery'] = True
            oled_lines.append("Batt: PASS")
        except Exception as e:
            print(f"Battery voltage: FAIL ({e})")
            results['battery'] = False
            oled_lines.append("Batt: FAIL")

        # OLED Test
        print("Testing OLED display...")
        try:
            robot.disp.fill(0)
            robot.disp.text("Self-Check", 0, 0, 1)
            for i, line in enumerate(oled_lines[:6]):  # Limit to 6 lines to fit screen
                robot.disp.text(line, 0, 10 + i*10, 1)
            robot.disp.show()
            print("OLED: OK")
            results['oled'] = True
        except Exception as e:
            print(f"OLED: FAIL ({e})")
            results['oled'] = False

        # Servo Test (if available)
        try:
            print("Testing servos...")
            robot.set_servo(1, 90)
            time.sleep(0.5)
            robot.set_servo(1, 0)
            time.sleep(0.5)
            robot.set_servo(1, 90)
            print("Servos: OK")
            results['servo'] = True
        except Exception as e:
            print(f"Servos: FAIL ({e})")
            results['servo'] = False

        # Buzzer Test (if available)
        try:
            print("Testing buzzer...")
            robot.play_tone(1000, 0.2)
            print("Buzzer: OK")
            results['buzzer'] = True
        except Exception as e:
            print(f"Buzzer: FAIL ({e})")
            results['buzzer'] = False

        # Camera Test
        print("Testing camera...")
        if CAMERA_AVAILABLE:
            try:
                if CAMERA_TYPE == "picamera2":
                    # Use picamera2 for Raspberry Pi 5
                    picam2 = Picamera2()
                    camera_config = picam2.create_preview_configuration()
                    picam2.configure(camera_config)
                    picam2.start()
                    time.sleep(2)  # Allow camera to warm up
                    array = picam2.capture_array()
                    picam2.stop()
                    if array is not None and array.size > 0:
                        print("Camera: OK (frame captured with picamera2)")
                        results['camera'] = True
                    else:
                        print("Camera: FAIL (no frame with picamera2)")
                        results['camera'] = False
                elif CAMERA_TYPE == "opencv":
                    # Fallback to OpenCV for older systems
                    cap = cv2.VideoCapture(0)
                    if not cap.isOpened():
                        raise Exception("Camera not detected")
                    ret, frame = cap.read()
                    cap.release()
                    if ret:
                        print("Camera: OK (frame captured with OpenCV)")
                        results['camera'] = True
                    else:
                        print("Camera: FAIL (no frame with OpenCV)")
                        results['camera'] = False
            except Exception as e:
                print(f"Camera: FAIL ({e})")
                results['camera'] = False
        else:
            print("Camera: No camera library available (install picamera2 or opencv)")
            results['camera'] = False

    finally:
        robot.Brake()
        try:
            robot.cleanup()
        except Exception:
            pass
        try:
            ultrasonic.cleanup()
        except Exception:
            pass
        try:
            ir_sensor.cleanup()
        except Exception:
            pass
        
        print("\nSelf-check complete. Results:")
        for k, v in results.items():
            print(f"{k}: {'PASS' if v else 'FAIL'}")

if __name__ == "__main__":
    self_check()
