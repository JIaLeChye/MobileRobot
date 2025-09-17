##-------Encoder Calibration Section-------##
import os
import time
import RPi_Robot_Hat_Lib
import json

robot = RPi_Robot_Hat_Lib.RobotController()
def calibrate_distance(mode='freewheel', actual_distance_cm= 10, motor='ALL', rotations=10):
    """
    Run calibration procedure with option for on-ground or freewheel calibration.
    Can calibrate a single motor (by counting rotations) or all motors (average distance).
    Uses default values for all arguments, so no Optional typing is needed.
    Saves calibration factor to ~/.config/mobile_robot/calibration.json (always overwrites).
    Args:
        mode: 'on-ground' or 'freewheel'. Defaults to 'freewheel'.
        actual_distance_cm: The measured distance in cm. Defaults to 10.
        motor: 'ALL' for all motors, or a specific motor ('LF', 'RF', 'LB', 'RB'). Defaults to 'ALL'.
        rotations: Number of wheel rotations for single motor calibration. Defaults to 10.
    """
    
    print("\nDistance Calibration Tool")
    mode = mode.lower() if isinstance(mode, str) else 'freewheel'
    if mode not in ['on-ground', 'freewheel']:
        print("Invalid mode argument, defaulting to 'freewheel'.")
        mode = 'freewheel'
    if isinstance(motor, str) and motor.upper() in ['LF', 'RF', 'LB', 'RB']:
        # Single motor calibration (robot moves the motor, user counts cycles)
        motor = motor.upper()
        robot.reset_encoders()
        print(f"\nSingle Motor Calibration Selected for {motor}.")
        print(robot.get_encoder(motor))
        print("The robot will move the specified motor at a constant speed.")
        print("Please count the number of full wheel cycles (rotations) and enter the actual number after the motor stops.")
        print("Ensure the robot is elevated so the wheel can spin freely without touching the ground.")
        print("You may want to mark the wheel with tape to help count rotations.")
        # Load and display previous calibration if available
        prev_ticks_per_rev, prev_cal_factor = robot.load_motor_calibration(motor)
        if prev_ticks_per_rev is not None and prev_cal_factor is not None:
            print(f"Previous calibration for {motor}:\n  Ticks per rev: {prev_ticks_per_rev:.2f}\n  Calibration factor: {prev_cal_factor:.5f}")
        else:
            print(f"No previous calibration found for {motor}.")
        print("Resetting encoder...")
        max_reset_attempts = 3
        for reset_attempt in range(max_reset_attempts):
            robot.reset_encoders()
            # Wait and confirm encoder is zero
            reset_val = None
            for attempt in range(20):
                time.sleep(0.05)
                reset_val = robot.get_encoder(motor)
                if reset_val == 0:
                    break
            if reset_val == 0:
                break
            print(f"[WARNING] Encoder for {motor} did not reset to zero after reset attempt {reset_attempt+1} (value: {reset_val}). Retrying...")
        else:
            print(f"[ERROR] Encoder for {motor} failed to reset after {max_reset_attempts} attempts. Calibration aborted.")
            return
        print(f"The robot will now move the {motor} motor at a constant speed.")
        print(f"Please count the number of full wheel cycles (rotations) and enter the actual number after the motor stops.")
        speed = 40  # Set a reasonable calibration speed
        cycles_to_run = rotations
        # Calculate ticks needed for the requested number of cycles
        # Use last saved ticks_per_rev if available, else default
        ticks_per_rev_est = prev_ticks_per_rev if prev_ticks_per_rev is not None else robot.TICKS_PER_REV
        target_ticks = int(cycles_to_run * ticks_per_rev_est)
        print(f"Target: {cycles_to_run} cycles (about {target_ticks} encoder ticks, using ticks_per_rev={ticks_per_rev_est:.2f})")
        # Start motor
        time.sleep(2)  # Give user time to prepare
        robot.set_motor(motor, speed)
        start_ticks = robot.get_encoder(motor)
        start_time = time.time()
        timeout = 20  # seconds
        print(f"[DEBUG] Starting encoder: {start_ticks}")
        while True:
            current_ticks = robot.get_encoder(motor)
            tick_diff = abs(current_ticks - start_ticks)
            print(f"[DEBUG] Encoder: {current_ticks}, Tick diff: {tick_diff}")
            if tick_diff >= target_ticks:
                break
            if time.time() - start_time > timeout:
                print("[ERROR] Calibration timeout: Encoder not responding as expected.")
                break
            time.sleep(0.05)
        robot.set_motor(motor, 0)
        print(f"Motor stopped after reaching {cycles_to_run} cycles (estimated) or timeout.")
        # User enters actual number of cycles observed
        try:
            user_cycles = float(input("Enter the ACTUAL number of cycles you observed: "))
        except Exception:
            print("No valid input for cycles. Aborting calibration.")
            return
        ticks = abs(robot.get_encoder(motor)) - start_ticks
        print(f"Encoder ticks counted: {ticks}")
        if user_cycles == 0:
            print("Cycles cannot be zero. Aborting calibration.")
            return
        # Estimate cycles from encoder ticks and estimated ticks per rev
        est_cycles = ticks / ticks_per_rev_est
        print(f"Estimated cycles (from encoder): {est_cycles:.2f}")
        # Calculate percentage difference
        percent_diff = 100.0 * abs(est_cycles - user_cycles) / user_cycles
        print(f"Percentage difference: {percent_diff:.2f}%")
        ticks_per_rev = ticks / user_cycles
        print(f"Ticks per revolution for {motor}: {ticks_per_rev:.2f}")
        # Calculate calibration factor
        actual = actual_distance_cm / 100.0
        measured = user_cycles * robot.WHEEL_CIRCUMFERENCE
        cal_factor = actual / measured
        print(f"\nNew calibration factor for {motor}: {cal_factor:.5f}")
        # Save calibration data
        config_dir = os.path.expanduser("~/.config/mobile_robot")
        os.makedirs(config_dir, exist_ok=True)
        calib_path = os.path.join(config_dir, f"calibration_{motor}.json")
        data = {"ticks_per_rev": ticks_per_rev, "calibration_factor": cal_factor, "date": time.strftime("%Y-%m-%d %H:%M:%S")}
        with open(calib_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Calibration data saved to {calib_path}")
        return
    # All-motor calibration (average)
    if motor == 'ALL':
        if mode == 'freewheel':
            print("\nFreewheel Calibration Selected.")
            print("Resetting encoders...")
            robot.reset_encoders()
            print("Place robot on a flat surface. Roll the robot forward in a straight line.")
            print("(No user input required. Proceeding...)")
            distances = {m: robot.get_distance(m) for m in ['LF','RF','LB','RB']}
            avg_dist = sum(distances.values()) / 4
            print("\nReported distances:")
            for m, d in distances.items():
                print(f"  {m}: {d*100:.1f}cm")
            print(f"Average: {avg_dist*100:.1f}cm")
        else:
            print("\nOn-ground Calibration Selected.")
            print("The robot will move forward for 5 seconds. Please measure the actual distance traveled.")
            print("(No user input required. Proceeding...)")
            print("Resetting encoders...")
            robot.reset_encoders()
            print("Encoders reset. Starting movement...")
            print("\nMoving forward...")
            robot.Forward(50)
            time.sleep(5)
            robot.stop()
            distances = {m: robot.get_distance(m) for m in ['LF','RF','LB','RB']}
            avg_dist = sum(distances.values()) / 4
            print("\nReported distances:")
            for m, d in distances.items():
                print(f"  {m}: {d*100:.1f}cm")
            print(f"Average: {avg_dist*100:.1f}cm")
        actual = actual_distance_cm / 100.0
        if avg_dist != 0:
            robot.calibration_factor = actual / avg_dist
            print(f"\nNew calibration factor: {robot.calibration_factor:.5f}")
            config_dir = os.path.expanduser("~/.config/mobile_robot")
            os.makedirs(config_dir, exist_ok=True)
            calib_path = os.path.join(config_dir, "calibration.json")
            data = {"calibration_factor": robot.calibration_factor, "date": time.strftime("%Y-%m-%d %H:%M:%S")}
            with open(calib_path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Calibration data saved to {calib_path}")
        else:
            print("Error: Average reported distance is zero. Calibration aborted.")
##########################################

try: 
    calibrate_distance(mode='freewheel', actual_distance_cm=10, motor='ALL', rotations=10)
    # robot.reset_encoders(debug = True)
    # time.sleep(1)
    # print(robot.get_encoder('LF'))
except Exception as e:
    print(f"Calibration failed: {e}")

except KeyboardInterrupt:
    print("\nCalibration interrupted by user.")