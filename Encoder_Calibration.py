##-------Encoder Calibration Section-------##
import os
import time
import RPi_Robot_Hat_Lib
import json


robot = RPi_Robot_Hat_Lib.RobotController()

def load_calibration_data():
    """
    Load calibration data from ~/.config/mobile_robot/calibration.json.
    Returns a dictionary with calibration data if found, empty dict otherwise.
    """
    config_dir = os.path.expanduser("~/.config/mobile_robot")
    calibration_data = {}
    
    # Load overall system calibration
    overall_calib_path = os.path.join(config_dir, "calibration.json")
    if os.path.exists(overall_calib_path):
        try:
            with open(overall_calib_path, "r") as f:
                calibration_data = json.load(f)
                print(f"Loaded calibration from {overall_calib_path}")
        except Exception as e:
            print(f"[ERROR] Failed to load calibration: {e}")
    
    return calibration_data

def display_calibration_status():
    """Display current calibration status."""
    print("\n=== Calibration Status ===")
    calib_data = load_calibration_data()
    
    if calib_data:
        print(f"Calibration Factor: {calib_data.get('calibration_factor', 'N/A')}")
        print(f"Actual Distance: {calib_data.get('actual_distance_m', 'N/A')}m")
        print(f"Measured Distance: {calib_data.get('measured_distance_m', 'N/A')}m")
        print(f"Last Calibrated: {calib_data.get('timestamp', 'N/A')}")
    else:
        print("No calibration data found.")
        print("Run calibration to create calibration data.")
    
    print("=========================\n")

def calibrate_distance(actual_distance_m=1.0):
    """
    Run on-ground calibration procedure for the entire robot.
    Uses the move_distance function to move precisely and get accurate measurements.
    Saves calibration factor to ~/.config/mobile_robot/calibration.json (always overwrites).
    Args:
        actual_distance_m: The measured distance in meters. Defaults to 0.10 (10cm).
    """
    
    print("\nDistance Calibration Tool")
    print("On-ground calibration for entire robot")
    print(f"The robot will attempt to move {actual_distance_m}m ({actual_distance_m*100:.0f}cm).")
    print("Please measure the ACTUAL distance traveled after movement.")
    
    print("\nStarting calibrated movement...")
    try:
        # Use the library's move_distance function which handles everything
        measured_distance_m = robot.move_distance(actual_distance_m, speed=100)
        
        print(f"\nMovement completed!")
        print(f"Library reported distance: {measured_distance_m:.4f}m ({measured_distance_m*100:.1f}cm)")
        print(f"Expected distance: {actual_distance_m:.4f}m ({actual_distance_m*100:.1f}cm)")
        actual_distance = float(input("Press Enter after measuring the actual distance traveled...\nActual distance (m): "))
        
    except Exception as e:
        print(f"[ERROR] Robot movement failed: {e}")
        return
    
    if measured_distance_m == 0:
        print("[ERROR] No movement detected! Check:")
        print("1. Robot wheels touching ground")
        print("2. Motors working properly") 
        print("3. Encoders connected")
        print("4. Sufficient battery power")
        return
    
    # Calculate calibration correction factor
    correction_factor = actual_distance / measured_distance_m
    print(f"\nCorrection factor needed: {correction_factor:.5f}")
    print(f"(Actual: {actual_distance:.4f}m ÷ Measured: {measured_distance_m:.4f}m)")
    
    # Load existing calibration factor
    existing_calib_data = load_calibration_data()
    existing_factor = existing_calib_data.get('calibration_factor', 1.0)
    print(f"Existing calibration factor: {existing_factor:.5f}")
    
    # Apply correction to existing calibration factor
    new_calibration_factor = existing_factor * correction_factor
    print(f"New calibration factor: {new_calibration_factor:.5f}")
    print(f"({existing_factor:.5f} × {correction_factor:.5f})")
    
    # Save calibration data
    config_dir = os.path.expanduser("~/.config/mobile_robot")
    try:
        os.makedirs(config_dir, exist_ok=True)
        calib_path = os.path.join(config_dir, "calibration.json")
        data = {
            "calibration_factor": new_calibration_factor,
            "previous_factor": existing_factor,
            "correction_factor": correction_factor,
            "actual_distance_m": actual_distance_m,
            "measured_distance_m": measured_distance_m,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(calib_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Calibration data saved to {calib_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save calibration data: {e}")
        print(f"New calibration factor: {new_calibration_factor:.5f} (not saved)")

if __name__ == "__main__":
    try: 
        print("Encoder Calibration Tool")
        print("1. Display calibration status")
        print("2. Run calibration (10cm)")
        print("3. Custom calibration distance")
        
        choice = input("Enter choice (1-3): ")
        
        if choice == '1':
            display_calibration_status()
        elif choice == '2':
            calibrate_distance()
        elif choice == '3':
            distance_input = input("Actual distance in meters [0.10]: ").strip()
            actual_distance = float(distance_input) if distance_input else 0.10
            calibrate_distance(actual_distance_m=actual_distance)
        else:
            print("Invalid choice")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        robot.cleanup()
