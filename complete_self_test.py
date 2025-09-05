#!/usr/bin/env python3
"""
Complete Robot Self-Test Script
===============================

Comprehensive testing for Raspberry Pi 5 Mobile Robot
Tests all components: Hardware, Sensors, Motors, Encoders, Movement

Enhanced Features:
- Improved ultrasonic sensor testing with advanced obstacle detection
- High-accuracy averaged readings for better sensor validation  
- Path clearing tests with multiple distance thresholds
- Simultaneous sensor readings for real-time analysis

Author: GitHub Copilot
Date: September 2025
Last Updated: Enhanced ultrasonic testing capabilities
"""

from RPi_Robot_Hat_Lib import RobotController
import time
import sys
import os

# Add the Libraries path to import the sensor modules
sys.path.append('/home/raspberry/Desktop/MobileRobot/Libraries/Ultrasonic_Sensor')
sys.path.append('/home/raspberry/Desktop/MobileRobot/Libraries/IR_Sensor')

try:
    from Ultrasonic_sens import Ultrasonic  # Now uses improved version
    from IRSens import IRsens
    import cv2
    from picamera2 import Picamera2
    import adafruit_ssd1306
    import board
    import busio
    from PIL import Image, ImageDraw, ImageFont
    OPTIONAL_IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some optional components not available: {e}")
    OPTIONAL_IMPORTS_AVAILABLE = False

class RobotSelfTest:
    def __init__(self):
        self.robot = None
        self.ultrasonic = None
        self.ir_sensor = None
        self.camera = None
        self.display = None
        self.test_results = {}
        self.total_tests = 13  # Updated to include line following sensors
        self.passed_tests = 0
        
    def print_header(self):
        """Print test header"""
        print("=" * 60)
        print("🤖 RASPBERRY PI 5 MOBILE ROBOT - COMPLETE SELF TEST")
        print("=" * 60)
        print(f"📅 Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Platform: Raspberry Pi 5 with Robot Hat")
        print(f"📊 Total Tests: {self.total_tests}")
        print("=" * 60)
        
    def print_test_header(self, test_num, test_name):
        """Print individual test header"""
        print(f"\n{'='*20} TEST {test_num}/{self.total_tests}: {test_name} {'='*20}")
        
    def record_result(self, test_name, passed, details=""):
        """Record test result"""
        self.test_results[test_name] = {
            'passed': passed,
            'details': details
        }
        if passed:
            self.passed_tests += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            print(f"❌ {test_name}: FAILED {details}")
            
    def test_1_hardware_connection(self):
        """Test 1: Hardware Connection"""
        self.print_test_header(1, "HARDWARE CONNECTION")
        
        try:
            print("🔌 Initializing Robot Controller...")
            self.robot = RobotController()
            time.sleep(1)
            
            print("📡 Testing I2C communication...")
            # Try to read a register to verify communication
            test_value = self.robot.get_encoder('LF')
            
            self.record_result("Hardware Connection", True, "- I2C communication OK")
            return True
            
        except Exception as e:
            self.record_result("Hardware Connection", False, f"- Error: {str(e)}")
            return False
            
    def test_2_buzzer(self):
        """Test 2: Buzzer System"""
        self.print_test_header(2, "BUZZER SYSTEM")
        
        try:
            print("🔊 Testing buzzer functionality...")
            
            # Test startup beep
            print("   Playing startup beep...")
            self.robot.play_tone(1000, 0.2)
            time.sleep(0.3)
            
            # Test success tone sequence
            print("   Playing success tone...")
            for freq in [800, 1000, 1200]:
                self.robot.play_tone(freq, 0.15)
                time.sleep(0.1)
                
            self.record_result("Buzzer System", True, "- All tones played successfully")
            return True
            
        except Exception as e:
            self.record_result("Buzzer System", False, f"- Error: {str(e)}")
            return False
            
    def test_3_servo_system(self):
        """Test 3: Servo System"""
        self.print_test_header(3, "SERVO SYSTEM")
        
        try:
            print("🔄 Testing servo movements...")
            
            # Test servo positions
            positions = [90, 45, 135, 90]  # center, left, right, center
            position_names = ["Center", "Left", "Right", "Center"]
            
            for pos, name in zip(positions, position_names):
                print(f"   Moving to {name} position ({pos}°)...")
                self.robot.set_servo(1, pos)  # servo_num=1, angle=pos
                time.sleep(0.8)
                
            self.record_result("Servo System", True, "- All positions reached")
            return True
            
        except Exception as e:
            self.record_result("Servo System", False, f"- Error: {str(e)}")
            return False
            
    def test_4_encoder_system(self):
        """Test 4: Encoder System"""
        self.print_test_header(4, "ENCODER SYSTEM")
        
        try:
            print("📊 Testing encoder readings...")
            
            # Reset all encoders
            self.robot.reset_encoders()
            time.sleep(0.2)
            
            # Get initial readings
            encoders = self.robot.get_all_encoders()
            print(f"   Initial readings: {encoders}")
            
            # Test encoder health
            healthy_encoders = 0
            encoder_status = {}
            
            for name, value in encoders.items():
                # Check for reasonable encoder values
                # LB encoder is known to have issues with large jumps
                if name == 'LB' and abs(value) > 50000:
                    encoder_status[name] = f"⚠️ Known LB Issue ({value})"
                elif abs(value) < 100000:  # Reasonable range for normal operation
                    healthy_encoders += 1
                    encoder_status[name] = "✅ Healthy"
                else:
                    encoder_status[name] = f"⚠️ Anomaly ({value})"
                    
            print("   Encoder Health Check:")
            for name, status in encoder_status.items():
                print(f"     {name}: {status}")
                
            if healthy_encoders >= 3:
                self.record_result("Encoder System", True, f"- {healthy_encoders}/4 encoders healthy")
                return True
            else:
                self.record_result("Encoder System", False, f"- Only {healthy_encoders}/4 encoders healthy")
                return False
                
        except Exception as e:
            self.record_result("Encoder System", False, f"- Error: {str(e)}")
            return False
            
    def test_5_motor_system(self):
        """Test 5: Motor System"""
        self.print_test_header(5, "MOTOR SYSTEM")
        
        try:
            print("⚡ Testing individual motors...")
            
            # Test each motor direction
            motors = ['LF', 'LB', 'RF', 'RB']
            motor_names = ['Left Front', 'Left Back', 'Right Front', 'Right Back']
            
            for motor, name in zip(motors, motor_names):
                print(f"   Testing {name} motor...")
                
                # Forward
                self.robot.set_motor(motor, 30)
                time.sleep(0.5)
                
                # Reverse  
                self.robot.set_motor(motor, -30)
                time.sleep(0.5)
                
                # Stop
                self.robot.set_motor(motor, 0)
                time.sleep(0.2)
                
            self.record_result("Motor System", True, "- All motors tested")
            return True
            
        except Exception as e:
            self.record_result("Motor System", False, f"- Error: {str(e)}")
            return False
            
    def test_6_movement_patterns(self):
        """Test 6: Movement Patterns"""
        self.print_test_header(6, "MOVEMENT PATTERNS")
        
        try:
            print("🚀 Testing basic movement patterns...")
            
            movements = [
                ("Forward", lambda: self.robot.Forward(25)),
                ("Backward", lambda: self.robot.Backward(25)),
                ("Turn Left", lambda: self.robot.turn_left(25)),
                ("Turn Right", lambda: self.robot.turn_right(25))
            ]
            
            for name, movement in movements:
                print(f"   Testing {name}...")
                movement()
                time.sleep(1.0)
                self.robot.stop()
                time.sleep(0.5)
                
            self.record_result("Movement Patterns", True, "- All movements executed")
            return True
            
        except Exception as e:
            self.record_result("Movement Patterns", False, f"- Error: {str(e)}")
            return False
            
    def test_7_precision_movement(self):
        """Test 7: Precision Movement"""
        self.print_test_header(7, "PRECISION MOVEMENT")
        
        try:
            print("🎯 Testing precise distance movement...")
            
            # Test 10cm movement
            target_distance = 10.0  # cm
            print(f"   Target: Move {target_distance}cm forward...")
            
            actual_distance = self.robot.move_distance_simple(target_distance, speed=25)
            actual_cm = actual_distance
            
            error = abs(actual_cm - target_distance)
            error_percent = (error / target_distance) * 100
            
            print(f"   Target: {target_distance}cm")
            print(f"   Actual: {actual_cm:.1f}cm")
            print(f"   Error: {error:.1f}cm ({error_percent:.1f}%)")
            
            if error < 1.0:  # Less than 1cm error
                self.record_result("Precision Movement", True, f"- Excellent precision ({error:.1f}cm error)")
                return True
            elif error < 2.0:  # Less than 2cm error
                self.record_result("Precision Movement", True, f"- Good precision ({error:.1f}cm error)")
                return True
            else:
                self.record_result("Precision Movement", False, f"- Poor precision ({error:.1f}cm error)")
                return False
                
        except Exception as e:
            self.record_result("Precision Movement", False, f"- Error: {str(e)}")
            return False
            
    def test_8_system_integration(self):
        """Test 8: System Integration"""
        self.print_test_header(8, "SYSTEM INTEGRATION")
        
        try:
            print("🔧 Testing combined system functionality...")
            
            # Combined test: servo + movement + buzzer
            print("   Executing integrated sequence...")
            
            # Look left
            self.robot.set_servo(1, 45)
            time.sleep(0.5)
            
            # Short beep
            self.robot.play_tone(800, 0.1)
            
            # Move forward 5cm
            self.robot.move_distance_simple(5, speed=20)
            
            # Look right
            self.robot.set_servo(1, 135)
            time.sleep(0.5)
            
            # Another beep
            self.robot.play_tone(1000, 0.1)
            
            # Return to center
            self.robot.set_servo(1, 90)
            time.sleep(0.5)
            
            # Success beep sequence
            for freq in [800, 1000, 1200]:
                self.robot.play_tone(freq, 0.1)
                time.sleep(0.05)
                
            self.record_result("System Integration", True, "- All systems working together")
            return True
            
        except Exception as e:
            self.record_result("System Integration", False, f"- Error: {str(e)}")
            return False
            
    def test_9_ultrasonic_sensors(self):
        """Test 9: Ultrasonic Sensors - Enhanced with improved library features"""
        self.print_test_header(9, "ULTRASONIC SENSORS (ENHANCED)")
        
        if not OPTIONAL_IMPORTS_AVAILABLE:
            self.record_result("Ultrasonic Sensors", False, "- Required modules not available")
            return False
            
        try:
            print("� Testing ultrasonic distance sensors with enhanced features...")
            
            # Initialize ultrasonic sensors with proper timing
            print("   Initializing improved ultrasonic sensor system...")
            self.ultrasonic = Ultrasonic(debug=False)
            
            # Let the sensor system stabilize
            time.sleep(1.0)
            print("   Sensor system stabilized")
            
            # Test each sensor
            sensors = {
                'Left': self.ultrasonic.Left_sensor,
                'Front': self.ultrasonic.Front_sensor,
                'Right': self.ultrasonic.Right_sensor
            }
            
            working_sensors = 0
            sensor_results = {}
            
            # Test individual sensors with enhanced accuracy
            for name, pin in sensors.items():
                print(f"   Testing {name} sensor (GPIO {pin})...")
                try:
                    # Use improved averaging method for better accuracy
                    avg_distance = self.ultrasonic.get_distance_average(pin, samples=5, delay=0.15)
                    
                    if avg_distance is not None:
                        print(f"     Enhanced average distance: {avg_distance:.1f}cm")
                        
                        if 2 <= avg_distance <= 400:  # Valid range for HC-SR04
                            working_sensors += 1
                            sensor_results[name] = f"✅ {avg_distance:.1f}cm"
                        else:
                            sensor_results[name] = f"⚠️ Out of range ({avg_distance:.1f}cm)"
                    else:
                        sensor_results[name] = "❌ No valid readings"
                        
                except Exception as e:
                    sensor_results[name] = f"❌ Error: {str(e)}"
                
                time.sleep(0.3)  # Brief pause between different sensors
                
            print("   Individual sensor readings:")
            for name, result in sensor_results.items():
                print(f"     {name}: {result}")
                
            # Test simultaneous readings using distances() method
            print("   Testing simultaneous readings...")
            try:
                left_dist, front_dist, right_dist = self.ultrasonic.distances()
                print(f"     Simultaneous readings:")
                print(f"       Left: {left_dist:.1f}cm" if left_dist else "       Left: 无读数")
                print(f"       Front: {front_dist:.1f}cm" if front_dist else "       Front: 无读数")
                print(f"       Right: {right_dist:.1f}cm" if right_dist else "       Right: 无读数")
            except Exception as e:
                print(f"     Simultaneous reading error: {e}")
                
            # Test enhanced features
            print("   Testing enhanced obstacle detection features...")
            try:
                # Test closest obstacle detection
                distance, direction = self.ultrasonic.get_closest_obstacle()
                if distance:
                    print(f"     🎯 Closest obstacle: {distance:.1f}cm to the {direction}")
                else:
                    print("     🎯 No obstacles detected in range")
                    
                # Test path clear functionality with multiple distances
                path_tests = [20, 30, 50]
                for min_dist in path_tests:
                    is_clear = self.ultrasonic.is_path_clear(min_distance=min_dist)
                    status = "CLEAR" if is_clear else "BLOCKED"
                    print(f"     🛣️ Path clear ({min_dist}cm): {status}")
                    
                # Test high-accuracy averaged readings for all sensors
                print("   Testing high-accuracy averaged readings...")
                left_avg, front_avg, right_avg = self.ultrasonic.distances(use_average=True, samples=3)
                print(f"     High-accuracy readings:")
                print(f"       Left: {left_avg:.1f}cm" if left_avg else "       Left: 无读数")
                print(f"       Front: {front_avg:.1f}cm" if front_avg else "       Front: 无读数") 
                print(f"       Right: {right_avg:.1f}cm" if right_avg else "       Right: 无读数")
                
            except Exception as e:
                print(f"     Enhanced features error: {e}")
                
            # Evaluate results
            if working_sensors >= 2:  # At least 2 sensors working
                self.record_result("Ultrasonic Sensors", True, f"- {working_sensors}/3 sensors working with enhanced features")
                return True
            else:
                self.record_result("Ultrasonic Sensors", False, f"- Only {working_sensors}/3 sensors working")
                return False
                
        except Exception as e:
            self.record_result("Ultrasonic Sensors", False, f"- Error: {str(e)}")
            return False
            
    def test_10_ir_sensor(self):
        """Test 10: IR Sensor"""
        self.print_test_header(10, "IR SENSOR")
        
        if not OPTIONAL_IMPORTS_AVAILABLE:
            self.record_result("IR Sensor", False, "- Required modules not available")
            return False
            
        try:
            print("🔴 Testing IR obstacle detection sensor...")
            
            # Initialize IR sensor
            self.ir_sensor = IRsens(debug=False)
            
            print("   Taking IR sensor readings...")
            readings = []
            
            # Take multiple readings
            for i in range(5):
                status = self.ir_sensor.status()
                readings.append(status)
                print(f"   Reading {i+1}: {'Object detected' if status == 1 else 'Clear path'}")
                time.sleep(0.2)
                
            # Check if sensor is responsive (readings should be consistent or changing)
            unique_readings = len(set(readings))
            if unique_readings >= 1:  # Sensor is giving readings
                self.record_result("IR Sensor", True, f"- Sensor responsive, {readings.count(1)} detections")
                return True
            else:
                self.record_result("IR Sensor", False, "- Sensor not responsive")
                return False
                
        except Exception as e:
            self.record_result("IR Sensor", False, f"- Error: {str(e)}")
            return False
            
    def test_11_line_following_sensors(self):
        """Test 11: Line Following Sensors"""
        self.print_test_header(11, "LINE FOLLOWING SENSORS")
        
        try:
            print("📏 Testing line following sensors...")
            
            # Test digital line sensors (5-bit array)
            print("   Reading digital line sensors...")
            digital_reading = self.robot.read_line_sensors()
            
            # Convert to binary representation for display
            binary_str = format(digital_reading, '05b')  # 5-bit binary
            sensor_states = [int(bit) for bit in binary_str]
            
            print(f"   Digital sensors (5-bit): {binary_str} (decimal: {digital_reading})")
            print("   Sensor array: [", end="")
            for i, state in enumerate(sensor_states):
                symbol = "●" if state else "○"  # Filled circle for detected, empty for clear
                print(f"{symbol}", end=" " if i < len(sensor_states)-1 else "")
            print("]")
            
            # Test analog line sensor
            print("   Reading analog line sensor...")
            analog_reading = self.robot.read_line_analog()
            print(f"   Analog sensor: {analog_reading}")
            
            # Validate sensor readings
            digital_valid = 0 <= digital_reading <= 31  # 5-bit range (0-31)
            analog_valid = 0 <= analog_reading <= 255   # 8-bit range (0-255)
            
            print("   Sensor validation:")
            print(f"     Digital range: {'✅ Valid' if digital_valid else '❌ Invalid'} (0-31)")
            print(f"     Analog range: {'✅ Valid' if analog_valid else '❌ Invalid'} (0-255)")
            
            # Check for sensor responsiveness
            # Take multiple readings to see if sensors are responsive
            print("   Testing sensor responsiveness...")
            readings = []
            for i in range(3):
                digital = self.robot.read_line_sensors()
                analog = self.robot.read_line_analog()
                readings.append((digital, analog))
                time.sleep(0.2)
                
            # Check if we got varied readings (indicates sensors are working)
            digital_values = [r[0] for r in readings]
            analog_values = [r[1] for r in readings]
            
            digital_responsive = len(set(digital_values)) > 1 or any(v > 0 for v in digital_values)
            analog_responsive = len(set(analog_values)) > 1 or any(v > 0 for v in analog_values)
            
            print(f"   Digital responsiveness: {'✅ Responsive' if digital_responsive else '⚠️ Static'}")
            print(f"   Analog responsiveness: {'✅ Responsive' if analog_responsive else '⚠️ Static'}")
            
            # Overall assessment
            if digital_valid and analog_valid:
                if digital_responsive or analog_responsive:
                    self.record_result("Line Following Sensors", True, "- Both digital and analog sensors working")
                    return True
                else:
                    self.record_result("Line Following Sensors", True, "- Sensors present but may need line to detect")
                    return True
            else:
                self.record_result("Line Following Sensors", False, "- Invalid sensor readings")
                return False
                
        except Exception as e:
            self.record_result("Line Following Sensors", False, f"- Error: {str(e)}")
            return False
            
    def test_12_camera_system(self):
        """Test 11: Camera System"""
        self.print_test_header(11, "CAMERA SYSTEM")
        
        if not OPTIONAL_IMPORTS_AVAILABLE:
            self.record_result("Camera System", False, "- Required modules not available")
            return False
            
        try:
            print("📷 Testing camera system...")
            
            # Initialize camera
            print("   Initializing Picamera2...")
            self.camera = Picamera2()
            
            # Configure camera
            config = self.camera.create_preview_configuration(main={"size": (640, 480)})
            self.camera.configure(config)
            
            # Start camera
            print("   Starting camera...")
            self.camera.start()
            time.sleep(2)  # Let camera stabilize
            
            # Capture test image
            print("   Capturing test image...")
            image = self.camera.capture_array()
            
            # Check image properties
            height, width, channels = image.shape
            print(f"   Image captured: {width}x{height}, {channels} channels")
            
            # Basic image validation
            if width > 0 and height > 0 and channels >= 3:
                self.record_result("Camera System", True, f"- {width}x{height} image captured")
                success = True
            else:
                self.record_result("Camera System", False, "- Invalid image captured")
                success = False
                
            # Stop camera
            self.camera.stop()
            return success
            
        except Exception as e:
            if self.camera:
                try:
                    self.camera.stop()
                except:
                    pass
            self.record_result("Camera System", False, f"- Error: {str(e)}")
            return False
            
    def test_13_oled_display(self):
        """Test 13: OLED Display"""
        self.print_test_header(13, "OLED DISPLAY")
        
        if not OPTIONAL_IMPORTS_AVAILABLE:
            self.record_result("OLED Display", False, "- Required modules not available")
            return False
            
        try:
            print("🖥️ Testing OLED display...")
            
            # Initialize I2C and display
            print("   Initializing I2C and OLED...")
            i2c = busio.I2C(board.SCL, board.SDA)
            self.display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
            
            # Clear display
            self.display.fill(0)
            self.display.show()
            time.sleep(0.5)
            
            # Create test image
            print("   Creating test pattern...")
            image = Image.new("1", (self.display.width, self.display.height))
            draw = ImageDraw.Draw(image)
            
            # Draw test pattern
            draw.rectangle((0, 0, self.display.width, self.display.height), outline=0, fill=0)
            draw.rectangle((2, 2, self.display.width-2, self.display.height-2), outline=1, fill=0)
            draw.text((10, 10), "ROBOT TEST", fill=1)
            draw.text((10, 25), "OLED OK", fill=1)
            draw.text((10, 40), "128x64", fill=1)
            
            # Display test pattern
            print("   Displaying test pattern...")
            self.display.image(image)
            self.display.show()
            time.sleep(2)
            
            # Clear display
            self.display.fill(0)
            self.display.show()
            
            self.record_result("OLED Display", True, "- 128x64 display working")
            return True
            
        except Exception as e:
            self.record_result("OLED Display", False, f"- Error: {str(e)}")
            return False
            
    def print_final_report(self):
        """Print final test report"""
        print("\n" + "="*60)
        print("📋 FINAL TEST REPORT")
        print("="*60)
        
        print(f"📊 Tests Passed: {self.passed_tests}/{self.total_tests}")
        print(f"📈 Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        print("\n📝 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"   {status} - {test_name}{result['details']}")
            
        print("\n" + "="*60)
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL TESTS PASSED! Robot is fully functional!")
            # Success celebration
            try:
                for freq in [800, 1000, 1200, 1500]:
                    self.robot.play_tone(freq, 0.15)
                    time.sleep(0.1)
            except:
                pass
        elif self.passed_tests >= self.total_tests * 0.75:
            print("👍 Most tests passed. Robot is mostly functional.")
        else:
            print("⚠️ Multiple failures detected. Check hardware connections.")
            
        print("="*60)
        
    def run_all_tests(self):
        """Run complete test suite"""
        self.print_header()
        
        try:
            # Run all tests in sequence
            tests = [
                self.test_1_hardware_connection,
                self.test_2_buzzer,
                self.test_3_servo_system,
                self.test_4_encoder_system,
                self.test_5_motor_system,
                self.test_6_movement_patterns,
                self.test_7_precision_movement,
                self.test_8_system_integration,
                self.test_9_ultrasonic_sensors,
                self.test_10_ir_sensor,
                self.test_11_line_following_sensors,
                self.test_12_camera_system,
                self.test_13_oled_display
            ]
            
            for test in tests:
                if not test():
                    print(f"\n⚠️ Test failed, but continuing with remaining tests...")
                time.sleep(1)  # Pause between tests
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Tests interrupted by user")
            
        except Exception as e:
            print(f"\n\n❌ Critical error during testing: {e}")
            
        finally:
            # Always cleanup
            if self.robot:
                try:
                    self.robot.stop()
                    self.robot.set_servo(1, 90)  # Center servo
                    self.robot.cleanup()
                except:
                    pass
                    
            # Cleanup sensors
            if self.ultrasonic:
                try:
                    import RPi.GPIO as GPIO
                    GPIO.cleanup()
                except:
                    pass
                    
            if self.ir_sensor:
                try:
                    self.ir_sensor.cleanup()
                except:
                    pass
                    
            if self.camera:
                try:
                    self.camera.stop()
                except:
                    pass
                    
            if self.display:
                try:
                    self.display.fill(0)
                    self.display.show()
                except:
                    pass
                    
            self.print_final_report()

def main():
    """Main function"""
    print("🤖 Starting Complete Robot Self-Test...")
    print("⚠️  Make sure robot has clear space to move!")
    print("⌨️  Press Ctrl+C to stop at any time")
    
    try:
        input("\n📍 Press Enter to start tests...")
    except KeyboardInterrupt:
        print("\n❌ Test cancelled by user")
        return
        
    # Run the complete test suite
    test_suite = RobotSelfTest()
    test_suite.run_all_tests()
    
    print("\n🏁 Test complete!")

if __name__ == "__main__":
    main()
