#!/usr/bin/env python3
"""
Comprehensive Robot Self-Check System
Tests ALL functions from the MobileRobot library suite.
"""

import time
import sys

try:
    from RPi_Robot_Hat_Lib import RobotController
except ImportError:
    from Libraries.RPi_Robot_Hat_Lib.RPi_Robot_Hat_Lib import RobotController

from Libraries.Ultrasonic_Sensor.Ultrasonic_sens import Ultrasonic
from Libraries.IR_Sensor.IRSens import IRsens

# OLED Display support
try:
    import board
    import busio
    import adafruit_ssd1306
    from PIL import Image, ImageDraw, ImageFont
    OLED_AVAILABLE = True
except ImportError:
    OLED_AVAILABLE = False

# Camera support
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

def comprehensive_self_check():
    """Comprehensive test of ALL robot functions"""
    print("🤖 Starting comprehensive robot self-check...")
    print("=" * 50)
    
    robot = RobotController(debug=True)
    ultrasonic = Ultrasonic(debug=True)
    ir_sensor = IRsens(debug=True)
    results = {}
    oled_lines = []
    
    # Initialize OLED if available
    oled_display = None
    if OLED_AVAILABLE:
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            oled_display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
            print("✓ OLED display initialized")
        except Exception as e:
            print(f"⚠ OLED initialization failed: {e}")
            OLED_AVAILABLE = False
    
    try:
        # 1. I2C Communication Test
        print("\n📡 Testing I2C Communication...")
        try:
            version = robot.__version__()
            print(f"✓ I2C communication: OK (Version: {version})")
            results['i2c'] = True
            oled_lines.append("I2C: PASS")
        except Exception as e:
            print(f"✗ I2C communication: FAIL ({e})")
            results['i2c'] = False
            oled_lines.append("I2C: FAIL")

        # 2. System Reset Test
        print("\n🔄 Testing System Reset...")
        try:
            robot.reset_system()
            robot.reset_encoders()
            print("✓ System reset: OK")
            results['reset'] = True
        except Exception as e:
            print(f"✗ System reset: FAIL ({e})")
            results['reset'] = False

        # 3. Motor Control Tests
        print("\n🚗 Testing Motor Control Functions...")
        try:
            # Test basic movements
            print("  Testing Forward/Backward...")
            robot.Forward(30)
            time.sleep(0.5)
            robot.Backward(30)
            time.sleep(0.5)
            
            # Test turning
            print("  Testing Left/Right turns...")
            robot.turn_left(30)
            time.sleep(0.5)
            robot.turn_right(30)
            time.sleep(0.5)
            
            # Test horizontal movement (mecanum wheels)
            print("  Testing Horizontal movement...")
            robot.Horizontal_Left(30)
            time.sleep(0.5)
            robot.Horizontal_Right(30)
            time.sleep(0.5)
            
            # Test individual motor control
            print("  Testing Individual motors...")
            robot.set_motor('RF', 30)
            time.sleep(0.3)
            robot.set_motor('RB', 30)
            time.sleep(0.3)
            robot.set_motor('LF', 30)
            time.sleep(0.3)
            robot.set_motor('LB', 30)
            time.sleep(0.3)
            
            # Test all motors together
            print("  Testing All motors simultaneously...")
            robot.set_motors(30, 30, 30, 30)
            time.sleep(0.5)
            
            # Test move function (speed + turn)
            print("  Testing move function...")
            robot.move(speed=30, turn=0)
            time.sleep(0.5)
            robot.move(speed=0, turn=30)
            time.sleep(0.5)
            
            robot.Brake()
            print("✓ Motor control: OK")
            results['motors'] = True
            oled_lines.append("Motors: PASS")
        except Exception as e:
            print(f"✗ Motor control: FAIL ({e})")
            results['motors'] = False
            oled_lines.append("Motors: FAIL")

        # 4. Encoder Tests
        print("\n📊 Testing Encoder Functions...")
        try:
            # Reset encoders first
            robot.reset_encoders()
            time.sleep(0.1)
            
            # Test individual encoder reading
            print("  Testing individual encoders...")
            enc_before = {}
            for motor in ['RF', 'RB', 'LF', 'LB']:
                enc_before[motor] = robot.get_encoder(motor)
                print(f"    {motor} encoder: {enc_before[motor]}")
            
            # Test all encoders at once
            all_enc_before = robot.get_all_encoders()
            print(f"  All encoders: {all_enc_before}")
            
            # Move robot and check encoder changes
            robot.Forward(30)
            time.sleep(1)
            robot.Brake()
            
            # Check encoder changes
            changes_detected = False
            for motor in ['RF', 'RB', 'LF', 'LB']:
                enc_after = robot.get_encoder(motor)
                if abs(enc_after - enc_before[motor]) > 5:
                    changes_detected = True
                    print(f"    {motor}: {enc_before[motor]} → {enc_after} ✓")
            
            if changes_detected:
                print("✓ Encoders: OK (movement detected)")
                results['encoders'] = True
                oled_lines.append("Encoders: PASS")
            else:
                print("✗ Encoders: FAIL (no movement detected)")
                results['encoders'] = False
                oled_lines.append("Encoders: FAIL")
        except Exception as e:
            print(f"✗ Encoders: FAIL ({e})")
            results['encoders'] = False
            oled_lines.append("Encoders: FAIL")

        # 5. RPM and Distance Tests (including calibration)
        print("\n⚡ Testing RPM and Distance Functions...")
        try:
            robot.Forward(50)
            time.sleep(1)
            
            # Test RPM measurement
            rpm_lf = robot.get_rpm('LF')
            rpm_rf = robot.get_rpm('RF')
            print(f"  RPM - LF: {rpm_lf:.1f}, RF: {rpm_rf:.1f}")
            
            # Test distance measurement
            distance_lf = robot.get_distance('LF')
            distance_rf = robot.get_distance('RF')
            print(f"  Distance - LF: {distance_lf:.3f}m, RF: {distance_rf:.3f}m")
            
            # Test calibration (note: this is for advanced users)
            try:
                print("  Testing calibration readiness...")
                # Just verify the function exists, don't run full calibration
                calibration_func = getattr(robot, 'calibrate_distance', None)
                if calibration_func:
                    print("    ✓ Calibration function available")
                else:
                    print("    ⚠ Calibration function not found")
            except Exception as cal_e:
                print(f"    ⚠ Calibration test: {cal_e}")
            
            robot.Brake()
            print("✓ RPM and Distance: OK")
            results['rpm_distance'] = True
        except Exception as e:
            print(f"✗ RPM and Distance: FAIL ({e})")
            results['rpm_distance'] = False

        # 6. Line Sensor Tests
        print("\n📏 Testing Line Sensors...")
        try:
            digital = robot.read_line_sensors()
            analog = robot.read_line_analog()
            print(f"  Digital sensors: {bin(digital)} ({digital})")
            print(f"  Analog sensors: {analog}")
            print("✓ Line sensors: OK")
            results['line_sensors'] = True
            oled_lines.append("Line: PASS")
        except Exception as e:
            print(f"✗ Line sensors: FAIL ({e})")
            results['line_sensors'] = False
            oled_lines.append("Line: FAIL")

        # 7. Servo Tests
        print("\n🔧 Testing Servo Functions...")
        try:
            print("  Testing servo movements...")
            for servo in [1, 2, 3, 4]:
                robot.set_servo(servo, 90)
                time.sleep(0.3)
                robot.set_servo(servo, 0)
                time.sleep(0.3)
                robot.set_servo(servo, 180)
                time.sleep(0.3)
                robot.set_servo(servo, 90)  # Center position
                time.sleep(0.3)
            print("✓ Servos: OK")
            results['servos'] = True
        except Exception as e:
            print(f"✗ Servos: FAIL ({e})")
            results['servos'] = False

        # 8. Battery Monitoring
        print("\n🔋 Testing Battery Monitoring...")
        try:
            voltage = robot.get_battery()
            print(f"  Battery voltage: {voltage:.2f}V")
            if voltage > 6.0:  # Reasonable minimum for robot operation
                print("✓ Battery: OK")
                results['battery'] = True
                oled_lines.append("Batt: PASS")
            else:
                print(f"⚠ Battery: LOW ({voltage:.2f}V)")
                results['battery'] = False
                oled_lines.append("Batt: LOW")
        except Exception as e:
            print(f"✗ Battery: FAIL ({e})")
            results['battery'] = False
            oled_lines.append("Batt: FAIL")

        # 9. Buzzer/Sound Tests
        print("\n🔊 Testing Sound Functions...")
        try:
            print("  Playing test tones...")
            robot.play_tone(1000, 0.2)  # 1kHz for 0.2 seconds
            time.sleep(0.3)
            robot.play_tone(2000, 0.2)  # 2kHz for 0.2 seconds
            time.sleep(0.3)
            robot.play_tone(500, 0.2)   # 500Hz for 0.2 seconds
            print("✓ Buzzer: OK")
            results['buzzer'] = True
        except Exception as e:
            print(f"✗ Buzzer: FAIL ({e})")
            results['buzzer'] = False

        # 10. OLED Display Tests
        print("\n📺 Testing OLED Display...")
        try:
            if OLED_AVAILABLE and oled_display is not None:
                # Test basic OLED functionality
                oled_display.fill(0)
                oled_display.text("Self-Check", 0, 0, 1)
                oled_display.text("Running...", 0, 10, 1)
                for i, line in enumerate(oled_lines[:4]):  # Show first 4 results
                    oled_display.text(line, 0, 20 + i*10, 1)
                oled_display.show()
                time.sleep(2)
                
                # Test display with PIL (if available)
                try:
                    image = Image.new("1", (oled_display.width, oled_display.height))
                    draw = ImageDraw.Draw(image)
                    font = ImageFont.load_default()
                    draw.text((0, 0), "Advanced Test", font=font, fill=255)
                    draw.text((0, 15), f"Motors: {len([k for k,v in results.items() if 'motor' in k and v])}/1", font=font, fill=255)
                    draw.text((0, 30), f"Sensors: {len([k for k,v in results.items() if 'sensor' in k and v])}", font=font, fill=255)
                    oled_display.image(image)
                    oled_display.show()
                    time.sleep(2)
                    print("✓ OLED Display: OK (Full functionality)")
                except Exception as pil_error:
                    print(f"✓ OLED Display: OK (Basic functionality, PIL error: {pil_error})")
                
                # Clear display
                oled_display.fill(0)
                oled_display.show()
                
                results['oled'] = True
            else:
                print("⚠ OLED Display: Library not available")
                results['oled'] = False
        except Exception as e:
            print(f"✗ OLED Display: FAIL ({e})")
            results['oled'] = False

        # 11. Ultrasonic Sensor Tests (ALL functions)
        print("\n📡 Testing Ultrasonic Sensors...")
        try:
            # Test basic distance readings
            left, front, right = ultrasonic.distances()
            print(f"  Basic distances - Left: {left:.1f}cm, Front: {front:.1f}cm, Right: {right:.1f}cm")
            
            # Test individual sensor functions
            print("  Testing individual sensors...")
            left_single = ultrasonic.get_distance(ultrasonic.Left_sensor)
            front_single = ultrasonic.get_distance(ultrasonic.Front_sensor)
            right_single = ultrasonic.get_distance(ultrasonic.Right_sensor)
            print(f"    Individual - Left: {left_single:.1f}cm, Front: {front_single:.1f}cm, Right: {right_single:.1f}cm")
            
            # Test averaged readings
            print("  Testing averaged readings...")
            left_avg = ultrasonic.get_distance_average(ultrasonic.Left_sensor, samples=3)
            front_avg = ultrasonic.get_distance_average(ultrasonic.Front_sensor, samples=3)
            right_avg = ultrasonic.get_distance_average(ultrasonic.Right_sensor, samples=3)
            print(f"    Averaged - Left: {left_avg:.1f}cm, Front: {front_avg:.1f}cm, Right: {right_avg:.1f}cm")
            
            # Test obstacle detection functions
            closest_distance, closest_sensor = ultrasonic.get_closest_obstacle()
            print(f"  Closest obstacle: {closest_distance:.1f}cm on {closest_sensor} sensor")
            
            # Test path clearance
            path_clear = ultrasonic.is_path_clear(min_distance=20)
            print(f"  Path clear (>20cm): {path_clear}")
            
            if all(d > 0 for d in [left, front, right]):
                print("✓ Ultrasonic: OK (all functions tested)")
                results['ultrasonic'] = True
                oled_lines.append("Ultra: PASS")
            else:
                print("✗ Ultrasonic: FAIL (invalid readings)")
                results['ultrasonic'] = False
                oled_lines.append("Ultra: FAIL")
        except Exception as e:
            print(f"✗ Ultrasonic: FAIL ({e})")
            results['ultrasonic'] = False
            oled_lines.append("Ultra: FAIL")

        # 12. IR Sensor Tests
        print("\n👁 Testing IR Sensor...")
        try:
            ir_status = ir_sensor.status()
            print(f"  IR Sensor status: {ir_status}")
            print("✓ IR Sensor: OK")
            results['ir'] = True
            oled_lines.append("IR: PASS")
        except Exception as e:
            print(f"✗ IR Sensor: FAIL ({e})")
            results['ir'] = False
            oled_lines.append("IR: FAIL")

        # 13. Camera Tests
        print("\n📷 Testing Camera...")
        if CAMERA_AVAILABLE:
            try:
                if CAMERA_TYPE == "picamera2":
                    # Use picamera2 for Raspberry Pi 5
                    picam2 = Picamera2()
                    camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
                    picam2.configure(camera_config)
                    picam2.start()
                    time.sleep(2)  # Allow camera to warm up
                    array = picam2.capture_array()
                    picam2.stop()
                    if array is not None and array.size > 0:
                        print(f"✓ Camera: OK (captured {array.shape} frame with picamera2)")
                        results['camera'] = True
                    else:
                        print("✗ Camera: FAIL (no frame captured)")
                        results['camera'] = False
                elif CAMERA_TYPE == "opencv":
                    # Fallback to OpenCV
                    cap = cv2.VideoCapture(0)
                    if not cap.isOpened():
                        raise Exception("Camera not accessible")
                    ret, frame = cap.read()
                    cap.release()
                    if ret and frame is not None:
                        print(f"✓ Camera: OK (captured {frame.shape} frame with OpenCV)")
                        results['camera'] = True
                    else:
                        print("✗ Camera: FAIL (no frame captured)")
                        results['camera'] = False
            except Exception as e:
                print(f"✗ Camera: FAIL ({e})")
                results['camera'] = False
        else:
            print("⚠ Camera: No camera library available")
            results['camera'] = False

        # 14. Distance Movement Tests (ALL functions)
        print("\n📐 Testing Precise Distance Movement...")
        try:
            print("  Testing move_distance function...")
            initial_pos = robot.get_distance('LF')
            robot.move_distance(0.1, speed=30)  # Move 0.1 meters
            final_pos = robot.get_distance('LF')
            actual_distance = abs(final_pos - initial_pos)
            print(f"    move_distance: Requested: 0.1m, Actual: {actual_distance:.3f}m")
            
            print("  Testing move_distance_simple function...")
            initial_pos_simple = robot.get_distance('RF')
            robot.move_distance_simple(10, speed=30)  # Move 10 cm
            final_pos_simple = robot.get_distance('RF')
            actual_distance_simple = abs(final_pos_simple - initial_pos_simple)
            print(f"    move_distance_simple: Requested: 10cm, Actual: {actual_distance_simple*100:.1f}cm")
            
            # Test ticks to distance conversion
            test_ticks = 100
            converted_distance = robot.ticks_to_distance(test_ticks)
            print(f"    ticks_to_distance: {test_ticks} ticks = {converted_distance:.3f}m")
            
            # Check accuracy for main function
            if 0.08 <= actual_distance <= 0.12:  # ±2cm tolerance
                print("✓ Distance Movement: OK")
                results['distance_movement'] = True
            else:
                print("⚠ Distance Movement: INACCURATE")
                results['distance_movement'] = False
        except Exception as e:
            print(f"✗ Distance Movement: FAIL ({e})")
            results['distance_movement'] = False

    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        robot.Brake()
        robot.stop()
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
        
        # Final Results Summary
        print("\n" + "=" * 50)
        print("🏁 COMPREHENSIVE SELF-CHECK RESULTS:")
        print("=" * 50)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{test_name.replace('_', ' ').title():<20}: {status}")
        
        print("-" * 50)
        print(f"Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL SYSTEMS OPERATIONAL!")
        elif passed >= total * 0.8:
            print("⚠ MOSTLY OPERATIONAL - Check failed components")
        else:
            print("❌ MULTIPLE FAILURES - Service required")
        
        # Final OLED summary
        try:
            if OLED_AVAILABLE and oled_display is not None:
                oled_display.fill(0)
                oled_display.text("Self-Check Done", 0, 0, 1)
                oled_display.text(f"{passed}/{total} Tests Pass", 0, 15, 1)
                if passed == total:
                    oled_display.text("ALL SYSTEMS OK!", 0, 30, 1)
                else:
                    oled_display.text("Check Failed", 0, 30, 1)
                    oled_display.text("Components", 0, 40, 1)
                oled_display.show()
        except Exception:
            pass

def self_check():
    """Wrapper function for backward compatibility"""
    comprehensive_self_check()

if __name__ == "__main__":
    comprehensive_self_check()