import smbus
import time
import math
import RPi.GPIO as GPIO
import os, json

class RobotController:
    def load_motor_calibration(self, motor):
        """
        Load per-motor calibration data if available. Returns (ticks_per_rev, calibration_factor) or (None, None) if not found.
        """
        
        config_dir = os.path.expanduser("~/.config/mobile_robot")
        calib_path = os.path.join(config_dir, f"calibration_{motor}.json")
        if os.path.exists(calib_path):
            try:
                with open(calib_path, "r") as f:
                    data = json.load(f)
                return data.get("ticks_per_rev"), data.get("calibration_factor")
            except Exception as e:
                print(f"Error loading calibration for {motor}: {e}")
        return None, None

    def __init__(self, wheel_diameter=100, debug=False):  # diameter in mm
        # Setup I2C communication
        self.address = 0x09
        self.bus = smbus.SMBus(1)

        self.debug = debug 
        self.rpm_init = False 
        
        # Robot physical parameters
        self.WHEEL_DIAMETER = wheel_diameter / 1000.0  # Convert to meters
        self.WHEEL_CIRCUMFERENCE = math.pi * self.WHEEL_DIAMETER
        self.GEAR_RATIO = 30
        self.ENCODER_PPR = 13
        self.TICKS_PER_REV = self.ENCODER_PPR * self.GEAR_RATIO * 4 # 4x quadrature encoding
        self.calibration_factor = 2 # Calibration factor
        
        # Register addresses
        self.REG_MOTOR_RF = 1
        self.REG_MOTOR_RB = 2
        self.REG_MOTOR_LF = 3
        self.REG_MOTOR_LB = 4
        self.REG_ENCODER_RF_LOW = 5
        self.REG_ENCODER_RF_HIGH = 6
        self.REG_ENCODER_RB_LOW = 7
        self.REG_ENCODER_RB_HIGH = 8
        self.REG_ENCODER_LF_LOW = 9
        self.REG_ENCODER_LF_HIGH = 10
        self.REG_ENCODER_LB_LOW = 11
        self.REG_ENCODER_LB_HIGH = 12
        self.REG_SERVO_1 = 13
        self.REG_SERVO_2 = 14
        self.REG_LINE_SENSOR = 15
        self.REG_LINE_ANALOG = 16
        self.REG_VOLTAGE = 17
        self.REG_ENCODER_RESET = 18
        self.REG_SYSTEM_RESET = 19
        self.lib_ver= "1.2.14"

        # Internal helper dicts for DRY code (do not remove explicit assignments above)
        self.MOTOR_REGS = {
            'RF': self.REG_MOTOR_RF,
            'RB': self.REG_MOTOR_RB,
            'LF': self.REG_MOTOR_LF,
            'LB': self.REG_MOTOR_LB
        }
        self.ENCODER_REGS = {
            'RF': (self.REG_ENCODER_RF_LOW, self.REG_ENCODER_RF_HIGH),
            'RB': (self.REG_ENCODER_RB_LOW, self.REG_ENCODER_RB_HIGH),
            'LF': (self.REG_ENCODER_LF_LOW, self.REG_ENCODER_LF_HIGH),
            'LB': (self.REG_ENCODER_LB_LOW, self.REG_ENCODER_LB_HIGH)
        }

        self.previous_counts = {'RF': 0, 'RB': 0, 'LF': 0, 'LB': 0}
        self.first_read = {'RF': True, 'RB': True, 'LF': True, 'LB': True}


    def __version__(self):
        """Return the library version"""
        print(f"RPi_Robot_Hat_Lib Version: {self.lib_ver}")
        return self.lib_ver


    ##---------Communication section--------##
    def _read_byte(self, reg):
        """Read a byte from an I2C register"""
        try:
            value = self.bus.read_byte_data(self.address, reg)
            return value
        except Exception as e:
            print(f"Error reading from register {reg}: {e}")
            return 0

    def _write_byte(self, reg, value):
        """Write a byte to an I2C register"""
        try:
            self.bus.write_byte_data(self.address, reg, value)
        except Exception as e:
            print(f"Error writing to register {reg}: {e}")

    def reset_encoders(self, debug=False):
        """Reset all encoder counts to zero"""
        try:
            self._write_byte(self.REG_ENCODER_RESET, 0xA5)
            time.sleep(0.1)  # Give the coprocessor time to process the reset
            if debug or self.debug:
                print("Encoders reset successfully.")
                print("Left Front Encoder:", self.get_encoder('LF'))
                print("Left Back Encoder:", self.get_encoder('LB'))
                print("Right Front Encoder:", self.get_encoder('RF'))
                print("Right Back Encoder:", self.get_encoder('RB'))
            return True
        except Exception as e:
            print(f"Error resetting encoders: {e}")
            return False
        
    def reset_system(self):
        """
        Perform a complete reset of the RP2040 coprocessor.
        This will restart all systems and reset all registers to default values.
        """
        try:
            print("Initiating system reset...")
            self._write_byte(self.REG_SYSTEM_RESET, 0xA5)
            time.sleep(1)  # Give time for the reset to complete
            print("System reset complete. Re-initializing connection...")
            # Re-initialize I2C bus after reset
            self.bus = smbus.SMBus(1)
            return True
        except Exception as e:
            print(f"Error during system reset: {e}")
            return False
    ##########################################


    ##---------Movement Section-----------##
    def Forward(self, speed):
        """Move forward with specified speed (0-100)"""
        self.move(speed)  # Positive speed for forward

    def Backward(self, speed):
        """Move backward with specified speed (0-100)"""
        self.move(-speed)  # Negative speed for backward

    def move(self, speed=0, turn=0):
        """
        Basic movement control
        speed: -100 to 100 (negative for backward, positive for forward)
        turn: -100 to 100 (negative for right, positive for left)
        """
        left_speed = speed + turn
        right_speed = speed - turn
        
        left_speed = max(-100, min(100, left_speed))
        right_speed = max(-100, min(100, right_speed))
        
        # Convert to byte values (0-127 for forward, 128-255 for backward)
        self.set_motor('LF', left_speed)
        self.set_motor('LB', left_speed)
        self.set_motor('RF', right_speed)
        self.set_motor('RB', right_speed)

    def Brake(self):
        """Stop all motors"""
        self.stop()
    
    def turn_left(self, speed):
        """Turn left with specified speed (0-100)"""
        self.move(0, speed)  # Use existing move function with turn parameter
    
    def turn_right(self, speed):
        """Turn right with specified speed (0-100)"""
        self.move(0, -speed)  # Use existing move function with negative turn

    def Horizontal_Left(self, speed):
        """Move Horizontal Left with specified spedd (0 - 100)"""
        self.set_motor('LF', -abs(speed))
        self.set_motor('RF', abs(speed))
        self.set_motor('LB', abs(speed))
        self.set_motor('RB', -abs(speed))
    
    def Horizontal_Right(self, speed):
        """Move Horizontal Right with specified spedd (0 - 100)"""
        self.set_motor('LF', abs(speed))
        self.set_motor('RF', -abs(speed))
        self.set_motor('LB', -abs(speed))
        self.set_motor('RB', abs(speed))
    
    def set_motor(self, motor, speed):
       """Set motor speed (-100 to 100)"""
       motor_registers = {
           'RF': self.REG_MOTOR_RF,
           'RB': self.REG_MOTOR_RB,
           'LF': self.REG_MOTOR_LF,
           'LB': self.REG_MOTOR_LB
       }
       
       speed = max(-100, min(100, speed))
       if speed >= 0:
           byte_value = int(speed * 127 / 100)
       else:
           byte_value = 256 + int(speed * 127 / 100)
           
       try:
           self._write_byte(motor_registers[motor], byte_value)
       except Exception as e:
           print(f"Error setting motor speed: {e}")
           self.stop() # Stop all Motor
    ##########################################


    ##-----------Encoder Section------------##
    def get_encoder(self, motor, debug=False):
        """Get encoder count for a specific motor
        Parms:
            motor: 'RF', 'RB', 'LF', 'LB'
            debug: If True, print debug information
        Returns:
            Encoder count as signed integer
        """


        if motor not in ['RF', 'RB', 'LF', 'LB']:
            print("Invalid motor. Choose from 'RF', 'RB', 'LF', 'LB'.")
            return 0
        

        encoder_registers = {
            'RF': (self.REG_ENCODER_RF_LOW, self.REG_ENCODER_RF_HIGH),
            'RB': (self.REG_ENCODER_RB_LOW, self.REG_ENCODER_RB_HIGH),
            'LF': (self.REG_ENCODER_LF_LOW, self.REG_ENCODER_LF_HIGH),
            'LB': (self.REG_ENCODER_LB_LOW, self.REG_ENCODER_LB_HIGH)
        }
        
        try:
            reg_low, reg_high = encoder_registers[motor]
            low = self._read_byte(reg_low)
            high = self._read_byte(reg_high)
            value = (high << 8) | low
            if debug == True or self.debug ==True:
                print("##################\n DEBUG STATEMENT FOR get_encoder() \n##################")
                print(f"Encoder value for {motor}: {value}")
                print(f"Encoder low: {low}")
                print (f"Encoder high: {high}")
                print(f"Encoder reg_low: {reg_low}")
                print(f"Encoder reg_high: {reg_high}")
                print("##################\n DEBUG STATEMENT FOR get_encoder() \n##################")
            return value # if value < 32768 else value - 65536
        except Exception as e:
            print(f"Error reading encoder: {e}")
            return 0
        
    def get_encoder_delta(self, motor, debug=False):
         """
        Get the encoder delta (change) since the last read,
        with wraparound handling and direction correction for left motors.
        
        Args:
            motor (str): One of 'RF', 'RB', 'LF', 'LB'
            debug (bool): Enable debug output

        Returns:
            int: Signed delta (positive for forward)
        """
         if motor not in ['RF', 'RB', 'LF', 'LB']:
            print("Invalid motor. Choose from 'RF', 'RB', 'LF', 'LB'.")
            return 0
         current = self.get_encoder(motor)
         if self.first_read[motor]:
             self.previous_counts[motor] = current
             self.first_read[motor] = False
             return 0  # No delta on first read
 
         prev = self.previous_counts[motor]
 
         # Wraparound-safe delta
         delta = (current - prev) & 0xFFFF
         if delta > 32767:
             delta -= 65536  # Convert to signed delta
 
         # Flip sign for left motors
         if motor in ['LF', 'LB']:
             delta *= -1
 
         self.previous_counts[motor] = current
 
         if debug or getattr(self, 'debug', False):
             print(f"\n=== DEBUG: get_encoder_delta('{motor}') ===")
             print(f"Previous: {prev}")
             print(f"Current : {current}")
             print(f"Delta   : {delta}")
             print("==========================================\n")
         return delta
    
    def get_rpm(self, motor, debug=False):
     """
     Calculate RPM for a specific motor with wraparound-safe encoder delta.
 
     Args:
         motor (str): One of 'RF', 'RB', 'LF', 'LB'
         debug (bool): If True, print debug info
 
     Returns:
         float: RPM (positive for forward, negative for reverse)
     """
     if not self.rpm_init:
         # Initialize all motors
         self._previous_data = {
             m: {'ticks': self.get_encoder(m), 'time': time.time()}
             for m in ['RF', 'RB', 'LF', 'LB']
         }
         self.rpm_init = True
         return 0
 
     try:
         current_ticks = self.get_encoder(motor)
         current_time = time.time()
 
         prev_data = self._previous_data[motor]
         prev_ticks = prev_data['ticks']
         prev_time = prev_data['time']
 
         delta_time = current_time - prev_time
         delta_ticks = (current_ticks - prev_ticks) & 0xFFFF  # Wraparound-safe

         if delta_ticks > 32767:
             delta_ticks -= 65536  # Signed conversion
         if motor in ['LF', 'LB']:
            delta_ticks *= -1  # Invert for left motors
        
 
         if delta_time == 0:
             if debug or getattr(self, 'debug', False):
                 print(f"[{motor}] Warning: Δt is 0")
             return 0
 
         if delta_ticks == 0:
             if debug or getattr(self, 'debug', False):
                 print(f"[{motor}] No movement detected")
             return 0
 
         # Calculate RPM
         rev_per_sec = delta_ticks / (self.TICKS_PER_REV * delta_time)
         rpm = rev_per_sec * 60
 
 
         # Update previous data
         self._previous_data[motor] = {
             'ticks': current_ticks,
             'time': current_time
         }
 
         if debug or getattr(self, 'debug', False):
             print(f"\n=== DEBUG: get_rpm('{motor}') ===")
             print(f"Previous Ticks: {prev_ticks}")
             print(f"Current Ticks : {current_ticks}")
             print(f"Delta Ticks   : {delta_ticks}")
             print(f"Delta Time    : {delta_time:.6f} s")
             print(f"Ticks/Rev     : {self.TICKS_PER_REV}")
             print(f"RPM           : {rpm:.2f}")
             print("===================================\n")
 
         return rpm
 
     except Exception as e:
         print(f"[Error] Failed to calculate RPM for {motor}: {e}")
         return 0

    def get_distance(self, motor, debug=False):
        """
        Calculate calibrated distance traveled by a specific motor in meters.
        Uses per-motor calibration if available, otherwise falls back to global values.
        Args:
            motor (str): One of 'RF', 'RB', 'LF', 'LB'
            debug (bool): If True, print debug information
        Returns:
            float: Distance in meters (always positive)
        """
        if motor not in ['RF', 'RB', 'LF', 'LB']:
            print("Invalid motor. Choose from 'RF', 'RB', 'LF', 'LB'.")
            return 0
        
        if not hasattr(self, 'total_ticks'):
            self.total_ticks = {'RF': 0, 'RB': 0, 'LF': 0, 'LB': 0}

        try:
            delta_ticks = self.get_encoder_delta(motor)
            self.total_ticks[motor] += delta_ticks

            # Load calibration if available
            # ticks_per_rev, cal_factor = self.load_motor_calibration(motor)
            # if ticks_per_rev is None:
            #     ticks_per_rev = self.TICKS_PER_REV
            # if cal_factor is None:
            #     cal_factor = self.calibration_factor
            ticks_per_rev = self.TICKS_PER_REV
            cal_factor = self.calibration_factor

            # Wheel distance per revolution
            wheel_circumference = self.WHEEL_CIRCUMFERENCE  # in meters

            revolutions = self.total_ticks[motor] / ticks_per_rev
            distance_m = revolutions * wheel_circumference * cal_factor

            if debug or getattr(self, 'debug', False):
                print(f"\n=== DEBUG: get_distance('{motor}') ===")
                print(f"Delta ticks : {delta_ticks}")
                print(f"Total ticks : {self.total_ticks[motor]}")
                print(f"Revolutions : {revolutions}")
                print(f"Distance    : {distance_m:.4f} meters")
                print("========================================\n")

            return abs(distance_m)

        except Exception as e:
            print(f"Error calculating distance for {motor}: {e}")
            return 0
    
    def get_all_encoders(self):
        """Get all encoder values at once"""
        return {
            'RF': self.get_encoder('RF'),
            'RB': self.get_encoder('RB'), 
            'LF': self.get_encoder('LF'),
            'LB': self.get_encoder('LB')
        }
 
    def move_distance(self, distance, speed=40, debug=False):
        """Move the robot a specific distance in meters with wraparound-safe tracking"""
        print(f"\nMoving {distance:.2f} meters at speed {speed}")
        debug = self.debug 
        direction = 1 if distance >= 0 else -1
        speed = abs(speed) * direction
        target_distance = abs(distance)

        # ✅ Reset encoder deltas + accumulated distance
        self.reset_encoders() 
        time.sleep(0.2)

        if direction > 0:
            self.Forward(abs(speed))
        else:
            self.Backward(abs(speed))

        last_avg_distance = 0
        stall_counter = 0
        max_stall_count = 10

        stopping_distance = max(0.01, abs(speed) * 0.0005)
        effective_target = target_distance - stopping_distance
        valid_motors = []
        while True:
            try:
                distances = {}
                

                for motor in ['LF', 'RF', 'RB', 'LB']:
                    dist = self.get_distance(motor)  # ✅ Uses encoder delta + calibration
                    distances[motor] = dist

                    if debug:
                        print(f"DEBUG: {motor} distance: {dist * 100:.1f}cm")

                    if dist < 5.0:  # Sanity check
                        valid_motors.append(motor)
                    elif debug:
                        print(f"DEBUG: {motor} excluded - too far: {dist * 100:.1f}cm")

                if len(valid_motors) >= 2:
                    avg_distance = sum(distances[motor] for motor in valid_motors) / len(valid_motors)
                else:
                    print("Warning: Not enough valid encoder readings!")
                    break

                if abs(avg_distance - last_avg_distance) < 0.001:
                    stall_counter += 1
                    if stall_counter >= max_stall_count:
                        print("Warning: Robot appears to be stalled. Stopping.")
                        break
                else:
                    stall_counter = 0
                    last_avg_distance = avg_distance

                print(f"Progress: {avg_distance * 100:.1f}cm / {target_distance * 100:.1f}cm")
                print(f"  Valid encoders: {valid_motors}")
                for motor in valid_motors:
                    print(f"    {motor}: {distances[motor] * 100:.1f}cm")

                if avg_distance >= effective_target:
                    print(f"Approaching target! Stopping early to account for momentum...")
                    break

                time.sleep(0.1)

            except Exception as e:
                print(f"Error during movement: {e}")
                break

        self.stop()
        time.sleep(0.2)

        # Final distance report
        final_distances = {m: self.get_distance(m) for m in valid_motors}
        final_avg = sum(final_distances[m] for m in valid_motors) / len(valid_motors)
        
        print("Movement completed.")
        print(f"Final distance: {final_avg * 100:.1f}cm")
        return final_avg
    
    ##########################################


    ##--------Servo Movement section--------## 
    def set_servo(self, servo_num, angle):
        """
        Set servo position (0-180 degrees)
        servo_num: 1 or 2
        angle: 0-180
        """
        if servo_num not in [1, 2]:
            print("Servo number must be 1 or 2")
            return
            
        # Clamp angle to valid range
        angle = max(0, min(180, angle))
        
        # Select the correct register
        reg = self.REG_SERVO_1 if servo_num == 1 else self.REG_SERVO_2
        
        try:
            self._write_byte(reg, angle)
        except Exception as e:
            print(f"Error setting servo angle: {e}")

    ##########################################



    ##----Line Following sensor section-----##
    def read_line_sensors(self):
        """Read the digital line sensors (5 bits)"""
        try:
            return self._read_byte(self.REG_LINE_SENSOR)
        except Exception as e:
            print(f"Error reading line sensors: {e}")
            return 0

    def read_line_analog(self):
        """Read the analog line sensor value"""
        try:
            return self._read_byte(self.REG_LINE_ANALOG)
        except Exception as e:
            print(f"Error reading analog line sensor: {e}")
            return 0
    
    ##########################################



    ##------------Battery Section-----------## 
    def get_battery(self):
        """Read battery voltage"""
        try:
            value = self._read_byte(self.REG_VOLTAGE)
            return value / 10.0  # Convert to actual voltage
        except Exception as e:
            print(f"Error reading voltage: {e}")
            return 0
    
    ##########################################


    ##-------Buzzer and Sound Section-------##        
    def play_tone(self, frequency, duration):
        """
        Play a tone on the buzzer
        frequency: in Hz
        duration: in seconds
        """
        try:
            if not hasattr(self, 'buzzer_pwm'):
                # Initialize buzzer if not already done
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(12, GPIO.OUT)  # Using GPIO 12 for buzzer
                self.buzzer_pwm = GPIO.PWM(12, 440)  # Start with 440Hz
                self.buzzer_pwm.start(0)
            
            if frequency > 0:
                self.buzzer_pwm.ChangeFrequency(frequency)
                self.buzzer_pwm.ChangeDutyCycle(50)
                time.sleep(duration)
                self.buzzer_pwm.ChangeDutyCycle(0)
                time.sleep(0.1)
                # Don't cleanup here, let cleanup() handle it
            else:
                time.sleep(duration)
                
        except Exception as e:
            print(f"Error playing tone: {e}")

    ##########################################


    ##--------Clean Up anb Stop Section--------##
    def stop(self):
        """Stop all motors"""
        for motor in ['RF', 'RB', 'LF', 'LB']:
            self.set_motor(motor, 0)

    def cleanup_buzzer(self):
        """Safely stop the buzzer PWM and release its GPIO pin."""
        try:
            if hasattr(self, 'buzzer_pwm'):
                try:
                    self.buzzer_pwm.stop()
                except Exception as e:
                    print(f"Warning: Buzzer PWM stop error: {e}")
                try:
                    delattr(self, 'buzzer_pwm')
                except Exception as e:
                    print(f"Warning: Buzzer attribute cleanup error: {e}")
            # Attempt to cleanup the buzzer pin (GPIO 12)
            try:
                GPIO.cleanup(12)
            except Exception:
                # Ignore if not set up or already cleaned
                pass
        except Exception as e:
            print(f"Warning: Buzzer cleanup exception: {e}")

    def cleanup(self):
        """Clean up resources"""
        self.stop()
        # Center servos
        self.set_servo(1, 90)
        self.set_servo(2, 90)
        # Cleanup buzzer safely
        self.cleanup_buzzer()
    
    ##############################################

# Example usage
if __name__ == "__main__":
    robot = RobotController(debug=False)
    robot.__version__()
    try:
        distance = 1.0  # meters
        speed = 60  # speed percentage
        robot.play_tone(440, 1)  # Play A4 for 1 second
        # robot.move_distance(1.0, speed=40)  # Move forward 1 meter at speed 40
        robot.reset_encoders(debug=False)
        robot.move_distance(distance, speed, debug=True)
        
        # while True:
        #     # motor = 'LF'
        #     # robot.set_motor(motor, 50)
        #     # enc_value = robot.get_encoder('LF')
        #     delta_rf = 
        #     # delta_lf = robot.get_encoder_delta('LF', debug=True)
        #     # print(f"Left Front Encoder: {enc_value}")
        #     time.sleep(0.3)
        # # robot.calibrate_distance(mode='freewheel', actual_distance_cm=10, motor='LF')
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        robot.cleanup()
        print("Cleanup done")