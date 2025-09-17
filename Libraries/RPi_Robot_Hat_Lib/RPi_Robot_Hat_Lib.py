import smbus
import time
import math
import RPi.GPIO as GPIO

class RobotController:
    def load_motor_calibration(self, motor):
        """
        Load per-motor calibration data if available. Returns (ticks_per_rev, calibration_factor) or (None, None) if not found.
        """
        import os, json
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

    def __init__(self, wheel_diameter=97, debug=False):  # diameter in mm
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
        self.TICKS_PER_REV = self.ENCODER_PPR * self.GEAR_RATIO
        self.calibration_factor = 0.0157  # Calibration factor
        
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
        self.lib_ver= "1.2.13"

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

    def __version__(self):
        """Return the library version"""
        print(f"RPi_Robot_Hat_Lib Version: {self.lib_ver}")
        return self.lib_ver


    ##-- Communication section----##
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
        
    ###################################
    ##---------Movement Section-------##
    ###################################
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
    ############################################


    ##-----Motor Encoder Section------##
    
    def get_encoder(self, motor, debug=False):
        """Get encoder count for a specific motor"""
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
            return value if value < 32768 else value - 65536
        except Exception as e:
            print(f"Error reading encoder: {e}")
            return 0
    
    def get_rpm(self, motor, debug=False):
        """Calculate RPM for a specific motor"""
        
        if self.rpm_init is False:
            self._previous_data = {
                'RF': {'ticks': self.get_encoder('RF'), 'time': time.time()},
                'RB': {'ticks': self.get_encoder('RB'), 'time': time.time()},
                'LF': {'ticks': self.get_encoder('LF'), 'time': time.time()},
                'LB': {'ticks': self.get_encoder('LB'), 'time': time.time()}
            }
            self.rpm_init = True
            return 0  # Return 0 for first call

        try: 
            current_ticks = self.get_encoder(motor) 
            current_time = time.time() 

            prev_ticks = self._previous_data[motor]['ticks']
            prev_time = self._previous_data[motor]['time'] 

            delta_time = current_time - prev_time 
            delta_ticks = current_ticks - prev_ticks

            if debug == True or self.debug == True:
                print("##############################")
                print("DEBUG STATEMENT FOR get_rpm()")
                print("##############################")
                print(f"Motor: {motor}")
                print(f"Current ticks: {current_ticks}")
                print(f"Previous ticks: {prev_ticks}")
                print(f"Delta ticks: {delta_ticks}") 
                print(f"Delta time: {delta_time:.6f}")
                print("##############################")
                
            # Update previous data for this motor only
            self._previous_data[motor] = {'ticks': current_ticks, 'time': current_time}

            if delta_time == 0: 
                if debug == True or self.debug == True:
                    print(f"Warning: Delta time is zero for {motor}")
                return 0 
                
            if delta_ticks == 0:
                if debug == True or self.debug == True: 
                    print(f"Warning: Delta ticks is zero for {motor}")
                return 0
            
            # Calculate RPM
            revolutions_per_second = delta_ticks / self.TICKS_PER_REV / delta_time
            rpm = revolutions_per_second * 60
            
            # Apply direction correction for left motors (they rotate opposite)
            if motor in ['LF', 'LB']:
                rpm = -rpm 
                
            return rpm
            
        except Exception as e:
            print(f"Error calculating RPM for {motor}: {e}")
            return 0
        
       
        
    def get_distance(self, motor, debug=False):
        """
        Calculate calibrated distance traveled by a specific motor in meters.
        Uses per-motor calibration if available, otherwise falls back to global values.
        """
        try:
            ticks = self.get_encoder(motor)
            # Check for unreasonable encoder values
            if abs(ticks) > 50000:
                if debug or self.debug:
                    print(f"Warning: Unusual encoder value for {motor}: {ticks}")
            # Try to load per-motor calibration
            ticks_per_rev, cal_factor = self.load_motor_calibration(motor)
            if ticks_per_rev is None:
                ticks_per_rev = self.TICKS_PER_REV
            if cal_factor is None:
                cal_factor = self.calibration_factor
            revolutions = ticks / ticks_per_rev
            distance = revolutions * self.WHEEL_CIRCUMFERENCE * cal_factor
            return abs(distance)
        except Exception as e:
            print(f"Error calculating distance for {motor}: {e}")
            return 0
    
    def ticks_to_distance(self, ticks):
        """Convert encoder ticks to distance in millimeters"""
        try:
            revolutions = ticks / self.TICKS_PER_REV
            distance_m = revolutions * self.WHEEL_CIRCUMFERENCE * self.calibration_factor
            return abs(distance_m * 1000)  # Convert to millimeters
        except Exception as e:
            print(f"Error converting ticks to distance: {e}")
            return 0
    
    def get_all_encoders(self):
        """Get all encoder values at once"""
        return {
            'RF': self.get_encoder('RF'),
            'RB': self.get_encoder('RB'), 
            'LF': self.get_encoder('LF'),
            'LB': self.get_encoder('LB')
        }
    
    def set_motors(self, rf_speed, rb_speed, lf_speed, lb_speed):
        """Set all motor speeds individually"""
        self.set_motor('RF', rf_speed)
        self.set_motor('RB', rb_speed)
        self.set_motor('LF', lf_speed)
        self.set_motor('LB', lb_speed)
        
    def move_distance(self, distance, speed=40):
        """Move the robot a specific distance in meters with improved error checking"""
        print(f"\nMoving {distance:.2f} meters at speed {speed}")
        
        # Determine direction
        direction = 1 if distance >= 0 else -1
        speed = abs(speed) * direction  # Ensure speed direction matches distance direction
        target_distance = abs(distance)
        valid_motors = []
        
        # Reset encoders for accurate measurement
        self.reset_encoders()
        time.sleep(0.2)  # Wait for reset to complete
        
        # Get initial encoder readings
        initial_encoders = self.get_all_encoders()
        
        # Start moving
        if direction > 0:
            self.Forward(abs(speed))
        else:
            self.Backward(abs(speed))
        
        # Variables for movement monitoring
        last_avg_distance = 0
        stall_counter = 0
        max_stall_count = 10
        
        # Calculate stopping distance based on speed (momentum compensation)
        stopping_distance = max(0.01, abs(speed) * 0.0005)  # Estimate based on speed
        effective_target = target_distance - stopping_distance
        
        while True:
            try:
                # Get current encoder readings
                current_encoders = self.get_all_encoders()
                
                # Calculate distances for each wheel
                distances = {}
                valid_motors = []
                
                for motor in ['LF', 'RF', 'RB', 'LB']:  # Include all motors
                    delta_ticks = abs(current_encoders[motor] - initial_encoders[motor])
                    distances[motor] = self.ticks_to_distance(delta_ticks) / 1000.0  # Convert to meters
                    
                    # Debug: Print individual distances
                    if self.debug:
                        print(f"DEBUG: {motor} distance: {distances[motor]*1000:.1f}mm")
                    
                    # Only include motors with reasonable readings
                    if distances[motor] < 5.0:  # Less than 5 meters (relaxed sanity check)
                        valid_motors.append(motor)
                    elif self.debug:
                        print(f"DEBUG: {motor} excluded - distance too large: {distances[motor]*1000:.1f}mm")
                
                # Calculate average distance using only valid encoders
                if len(valid_motors) >= 2:
                    avg_distance = sum(distances[motor] for motor in valid_motors) / len(valid_motors)
                else:
                    print("Warning: Not enough valid encoder readings!")
                    break
                
                # Check for stalling
                if abs(avg_distance - last_avg_distance) < 0.001:  # Less than 1mm progress
                    stall_counter += 1
                    if stall_counter >= max_stall_count:
                        print("Warning: Robot appears to be stalled. Stopping.")
                        break
                else:
                    stall_counter = 0
                    last_avg_distance = avg_distance
                
                # Print progress with better formatting
                print(f"Progress: {avg_distance*100:.1f}cm / {target_distance*100:.1f}cm")
                print(f"  Valid encoders: {valid_motors}")
                for motor in valid_motors:
                    print(f"    {motor}: {distances[motor]*100:.1f}cm")
                
                # Check if we've reached the effective target (with stopping compensation)
                if avg_distance >= effective_target:
                    print(f"Approaching target! Stopping early to account for momentum...")
                    break
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error during movement: {e}")
                break
        
        # Stop the robot
        self.stop()
        time.sleep(0.2)  # Allow time to fully stop
        
        # Get final measurement
        final_encoders = self.get_all_encoders()
        final_distances = {}
        for motor in valid_motors:
            delta_ticks = abs(final_encoders[motor] - initial_encoders[motor])
            final_distances[motor] = self.ticks_to_distance(delta_ticks) / 1000.0
        
        final_avg_distance = sum(final_distances[motor] for motor in valid_motors) / len(valid_motors)
        
        print("Movement completed.")
        print(f"Final distance: {final_avg_distance*100:.1f}cm")
        
        # Return final distance achieved
        return final_avg_distance
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
    
    #############################################



    # ##-------Encoder Calibration Section-------## 
    # def calibrate_distance(self, mode='freewheel', actual_distance_cm=10, motor='ALL', rotations=10):
    #     """
    #     Run calibration procedure with option for on-ground or freewheel calibration.
    #     Can calibrate a single motor (by counting rotations) or all motors (average distance).
    #     Uses default values for all arguments, so no Optional typing is needed.
    #     Saves calibration factor to ~/.config/mobile_robot/calibration.json (always overwrites).

    #     Args:
    #         mode: 'on-ground' or 'freewheel'. Defaults to 'freewheel'.
    #         actual_distance_cm: The measured distance in cm. Defaults to 10.
    #         motor: 'ALL' for all motors, or a specific motor ('LF', 'RF', 'LB', 'RB'). Defaults to 'ALL'.
    #         rotations: Number of wheel rotations for single motor calibration. Defaults to 10.
    #     """
    #     import os, json
    #     print("\nDistance Calibration Tool")
    #     mode = mode.lower() if isinstance(mode, str) else 'freewheel'
    #     if mode not in ['on-ground', 'freewheel']:
    #         print("Invalid mode argument, defaulting to 'freewheel'.")
    #         mode = 'freewheel'

    #     if isinstance(motor, str) and motor.upper() in ['LF', 'RF', 'LB', 'RB']:
    #         # Single motor calibration (robot moves the motor, user counts cycles)
    #         motor = motor.upper()
    #         print(f"\nSingle Motor Calibration Selected for {motor}.")
    #         # Load and display previous calibration if available
    #         prev_ticks_per_rev, prev_cal_factor = self.load_motor_calibration(motor)
    #         if prev_ticks_per_rev is not None and prev_cal_factor is not None:
    #             print(f"Previous calibration for {motor}:\n  Ticks per rev: {prev_ticks_per_rev:.2f}\n  Calibration factor: {prev_cal_factor:.5f}")
    #         else:
    #             print(f"No previous calibration found for {motor}.")
    #         print("Resetting encoder...")
    #         max_reset_attempts = 3
    #         for reset_attempt in range(max_reset_attempts):
    #             self.reset_encoders()
    #             # Wait and confirm encoder is zero
    #             reset_val = None
    #             for attempt in range(20):
    #                 time.sleep(0.05)
    #                 reset_val = self.get_encoder(motor)
    #                 if reset_val == 0:
    #                     break
    #             if reset_val == 0:
    #                 break
    #             print(f"[WARNING] Encoder for {motor} did not reset to zero after reset attempt {reset_attempt+1} (value: {reset_val}). Retrying...")
    #         else:
    #             print(f"[ERROR] Encoder for {motor} failed to reset after {max_reset_attempts} attempts. Calibration aborted.")
    #             return
    #         print(f"The robot will now move the {motor} motor at a constant speed.")
    #         print(f"Please count the number of full wheel cycles (rotations) and enter the actual number after the motor stops.")
    #         speed = 40  # Set a reasonable calibration speed
    #         cycles_to_run = rotations
    #         # Calculate ticks needed for the requested number of cycles
    #         # Use last saved ticks_per_rev if available, else default
    #         ticks_per_rev_est = prev_ticks_per_rev if prev_ticks_per_rev is not None else self.TICKS_PER_REV
    #         target_ticks = int(cycles_to_run * ticks_per_rev_est)
    #         print(f"Target: {cycles_to_run} cycles (about {target_ticks} encoder ticks, using ticks_per_rev={ticks_per_rev_est:.2f})")
    #         # Start motor
    #         time.sleep(2)  # Give user time to prepare
    #         self.set_motor(motor, speed)
    #         start_ticks = self.get_encoder(motor)
    #         start_time = time.time()
    #         timeout = 20  # seconds
    #         print(f"[DEBUG] Starting encoder: {start_ticks}")
    #         while True:
    #             current_ticks = self.get_encoder(motor)
    #             tick_diff = abs(current_ticks - start_ticks)
    #             print(f"[DEBUG] Encoder: {current_ticks}, Tick diff: {tick_diff}")
    #             if tick_diff >= target_ticks:
    #                 break
    #             if time.time() - start_time > timeout:
    #                 print("[ERROR] Calibration timeout: Encoder not responding as expected.")
    #                 break
    #             time.sleep(0.05)
    #         self.set_motor(motor, 0)
    #         print(f"Motor stopped after reaching {cycles_to_run} cycles (estimated) or timeout.")
    #         # User enters actual number of cycles observed
    #         try:
    #             user_cycles = float(input("Enter the ACTUAL number of cycles you observed: "))
    #         except Exception:
    #             print("No valid input for cycles. Aborting calibration.")
    #             return
    #         ticks = abs(self.get_encoder(motor)) - start_ticks
    #         print(f"Encoder ticks counted: {ticks}")
    #         if user_cycles == 0:
    #             print("Cycles cannot be zero. Aborting calibration.")
    #             return
    #         # Estimate cycles from encoder ticks and estimated ticks per rev
    #         est_cycles = ticks / ticks_per_rev_est
    #         print(f"Estimated cycles (from encoder): {est_cycles:.2f}")
    #         # Calculate percentage difference
    #         percent_diff = 100.0 * abs(est_cycles - user_cycles) / user_cycles
    #         print(f"Percentage difference: {percent_diff:.2f}%")
    #         ticks_per_rev = ticks / user_cycles
    #         print(f"Ticks per revolution for {motor}: {ticks_per_rev:.2f}")
    #         # Calculate calibration factor
    #         actual = actual_distance_cm / 100.0
    #         measured = user_cycles * self.WHEEL_CIRCUMFERENCE
    #         cal_factor = actual / measured
    #         print(f"\nNew calibration factor for {motor}: {cal_factor:.5f}")
    #         # Save calibration data
    #         config_dir = os.path.expanduser("~/.config/mobile_robot")
    #         os.makedirs(config_dir, exist_ok=True)
    #         calib_path = os.path.join(config_dir, f"calibration_{motor}.json")
    #         data = {"ticks_per_rev": ticks_per_rev, "calibration_factor": cal_factor, "date": time.strftime("%Y-%m-%d %H:%M:%S")}
    #         with open(calib_path, "w") as f:
    #             json.dump(data, f, indent=2)
    #         print(f"Calibration data saved to {calib_path}")
    #         return

    #     # All-motor calibration (average)
    #     if motor == 'ALL':
    #         if mode == 'freewheel':
    #             print("\nFreewheel Calibration Selected.")
    #             print("Resetting encoders...")
    #             self.reset_encoders()
    #             print("Place robot on a flat surface. Roll the robot forward in a straight line.")
    #             print("(No user input required. Proceeding...)")
    #             distances = {m: self.get_distance(m) for m in ['LF','RF','LB','RB']}
    #             avg_dist = sum(distances.values()) / 4
    #             print("\nReported distances:")
    #             for m, d in distances.items():
    #                 print(f"  {m}: {d*100:.1f}cm")
    #             print(f"Average: {avg_dist*100:.1f}cm")

    #         else:
    #             print("\nOn-ground Calibration Selected.")
    #             print("The robot will move forward for 5 seconds. Please measure the actual distance traveled.")
    #             print("(No user input required. Proceeding...)")
    #             print("Resetting encoders...")
    #             self.reset_encoders()
    #             print("Encoders reset. Starting movement...")
    #             print("\nMoving forward...")
    #             self.Forward(50)
    #             time.sleep(5)
    #             self.stop()
    #             distances = {m: self.get_distance(m) for m in ['LF','RF','LB','RB']}
    #             avg_dist = sum(distances.values()) / 4
    #             print("\nReported distances:")
    #             for m, d in distances.items():
    #                 print(f"  {m}: {d*100:.1f}cm")
    #             print(f"Average: {avg_dist*100:.1f}cm")

    #         actual = actual_distance_cm / 100.0
    #         if avg_dist != 0:
    #             self.calibration_factor = actual / avg_dist
    #             print(f"\nNew calibration factor: {self.calibration_factor:.5f}")
    #             config_dir = os.path.expanduser("~/.config/mobile_robot")
    #             os.makedirs(config_dir, exist_ok=True)
    #             calib_path = os.path.join(config_dir, "calibration.json")
    #             data = {"calibration_factor": self.calibration_factor, "date": time.strftime("%Y-%m-%d %H:%M:%S")}
    #             with open(calib_path, "w") as f:
    #                 json.dump(data, f, indent=2)
    #             print(f"Calibration data saved to {calib_path}")
    #         else:
    #             print("Error: Average reported distance is zero. Calibration aborted.")
    # ##########################################



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

    #############################################


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

if __name__ == "__main__":
    robot = RobotController(debug=True)
    robot.__version__()
    try:
        robot.play_tone(440, 1)  # Play A4 for 1 second
        robot.move_distance(1.0, speed=40)  # Move forward 1 meter at speed 40
        # robot.calibrate_distance(mode='freewheel', actual_distance_cm=10, motor='LF')
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        robot.cleanup()
        print("Cleanup done")