import RPi.GPIO as GPIO
import time

__version__ = "1.0.3"

class Ultrasonic:
    """
    Improved class for ultrasonic distance sensors (HC-SR04 compatible).
    Each sensor uses a single pin for both trigger and echo.
    """
    __init_check = False 
    SOUND_SPEED = 34300  # Speed of sound in cm/s at 20C

    def __init__(self, Left_sensor=5, Front_sensor=16, Right_sensor=18, debug=False):
        """
        Initializes GPIO pins for the ultrasonic sensors.
        :param Left_sensor: Left sensor GPIO pin (default 5)
        :param Front_sensor: Front sensor GPIO pin (default 16) 
        :param Right_sensor: Right sensor GPIO pin (default 18)
        :param debug: Enable debug mode (default False)
        """
        if not Ultrasonic.__init_check:
            self.Left_sensor = Left_sensor
            self.Front_sensor = Front_sensor  
            self.Right_sensor = Right_sensor
            self.debug = debug

            # Initialize GPIO mode only once
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)  # Disable warnings for cleaner output
            
            if self.debug:
                print("Ultrasonic sensor system initialized.")
                print(f"Sensors: Left={Left_sensor}, Front={Front_sensor}, Right={Right_sensor}")
            
            Ultrasonic.__init_check = True
        else:
            if self.debug: 
                print("Ultrasonic sensor already initialized.")

    def send_trigger_pulse(self, pin):
        """
        Sends a proper 10 microsecond trigger pulse on the specified pin.
        """
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, False)
        time.sleep(0.000002)  # 2 microseconds low
        GPIO.output(pin, True)
        time.sleep(0.00001)   # 10 microseconds high (trigger pulse)
        GPIO.output(pin, False)
        
        if self.debug:
            print(f"Trigger pulse sent to pin {pin}")

    def wait_for_echo(self, pin):
        """
        Waits for the echo response and measures the pulse duration.
        Returns pulse duration in seconds, or None if timeout.
        """
        GPIO.setup(pin, GPIO.IN)
        
        # Timeout values
        timeout_start = 0.02    # 20ms timeout for echo start
        timeout_duration = 0.03 # 30ms timeout for echo duration (max ~5m range)
        
        start_time = time.time()
        
        # Wait for echo to start (rising edge)
        while GPIO.input(pin) == 0:
            if time.time() - start_time > timeout_start:
                if self.debug:
                    print(f"Timeout waiting for echo start on pin {pin}")
                return None

        # Record when echo started
        pulse_start = time.time()
        pulse_end = pulse_start

        # Wait for echo to end (falling edge)
        while GPIO.input(pin) == 1:
            pulse_end = time.time()
            if pulse_end - pulse_start > timeout_duration:
                if self.debug:
                    print(f"Timeout during echo on pin {pin}")
                return None
        
        # Calculate pulse duration
        pulse_duration = pulse_end - pulse_start
        
        if self.debug:
            print(f"Echo duration: {pulse_duration*1000000:.1f} microseconds")
            
        return pulse_duration

    def get_distance(self, pin):
        """
        Measures distance using the ultrasonic sensor on the specified pin.
        Returns distance in centimeters, or None if measurement failed.
        """
        try:
            # Send trigger pulse
            self.send_trigger_pulse(pin)
            
            # Small delay to ensure trigger is processed
            time.sleep(0.00001)
            
            # Wait for and measure echo
            pulse_duration = self.wait_for_echo(pin)
            
            if pulse_duration is None:
                if self.debug:
                    print(f"No valid echo received from pin {pin}")
                return None
            
            # Calculate distance: distance = (time * speed) / 2
            # Divide by 2 because sound travels to object and back
            distance = (pulse_duration * self.SOUND_SPEED) / 2
            
            # Validate distance (HC-SR04 range: 2cm to 400cm)
            if distance < 2 or distance > 400:
                if self.debug:
                    print(f"Distance out of valid range: {distance:.1f}cm")
                return None
                
            if self.debug:
                print(f"Pin {pin}: {distance:.1f}cm")
                
            return distance
            
        except Exception as e:
            if self.debug:
                print(f"Error measuring distance on pin {pin}: {e}")
            return None

    def get_distance_average(self, pin, samples=3, delay=0.1):
        """
        Gets multiple distance readings and returns the average for better accuracy.
        :param pin: GPIO pin number
        :param samples: Number of samples to take (default 3)
        :param delay: Delay between samples in seconds (default 0.1)
        :return: Average distance in cm, or None if all samples failed
        """
        readings = []
        
        for i in range(samples):
            distance = self.get_distance(pin)
            if distance is not None:
                readings.append(distance)
            
            if i < samples - 1:  # Don't delay after last sample
                time.sleep(delay)
        
        if not readings:
            if self.debug:
                print(f"No valid readings from pin {pin}")
            return None
            
        average = sum(readings) / len(readings)
        
        if self.debug:
            print(f"Pin {pin} average from {len(readings)} samples: {average:.1f}cm")
            
        return average

    def distances(self, use_average=False, samples=3):
        """
        Get distance measurements from all three sensors.
        :param use_average: If True, uses averaged readings for better accuracy
        :param samples: Number of samples for averaging (if use_average=True)
        :return: Tuple of (Left, Front, Right) distances in cm
        """
        if use_average:
            Left = self.get_distance_average(self.Left_sensor, samples)
            Front = self.get_distance_average(self.Front_sensor, samples)
            Right = self.get_distance_average(self.Right_sensor, samples)
        else:
            Left = self.get_distance(self.Left_sensor)
            time.sleep(0.1)  # Small delay between sensors
            Front = self.get_distance(self.Front_sensor)
            time.sleep(0.1)
            Right = self.get_distance(self.Right_sensor)
            
        if self.debug:
            print(f"All sensors - Left: {Left}, Front: {Front}, Right: {Right}")
            
        return Left, Front, Right

    def get_closest_obstacle(self):
        """
        Returns the distance to the closest obstacle and its direction.
        :return: Tuple of (distance, direction) or (None, None) if no obstacles detected
        """
        left, front, right = self.distances()
        
        # Filter out None values
        valid_readings = {}
        if left is not None:
            valid_readings['Left'] = left
        if front is not None:
            valid_readings['Front'] = front  
        if right is not None:
            valid_readings['Right'] = right
            
        if not valid_readings:
            return None, None
            
        # Find closest obstacle (type-checker friendly)
        closest_direction, closest_distance = min(
            valid_readings.items(), key=lambda kv: kv[1]
        )
        
        if self.debug:
            print(f"Closest obstacle: {closest_distance:.1f}cm to the {closest_direction}")
            
        return closest_distance, closest_direction

    def is_path_clear(self, min_distance=20):
        """
        Checks if the path ahead is clear.
        :param min_distance: Minimum safe distance in cm (default 20cm)
        :return: Boolean indicating if path is clear
        """
        front_distance = self.get_distance(self.Front_sensor)
        
        if front_distance is None:
            if self.debug:
                print("Cannot determine if path is clear - sensor error")
            return False
            
        is_clear = front_distance > min_distance
        
        if self.debug:
            status = "CLEAR" if is_clear else "BLOCKED"
            print(f"Path status: {status} (front distance: {front_distance:.1f}cm)")
            
        return is_clear

    def cleanup(self):
        """
        Cleans up GPIO pins and resets initialization flag.
        """
        try:
            GPIO.cleanup()
            Ultrasonic.__init_check = False
            if self.debug:
                print("GPIO cleanup completed")
        except Exception as e:
            if self.debug:
                print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    ultrasonic = None
    try:
        print("Testing Improved Ultrasonic Sensor Library")
        print("=" * 50)

        ultrasonic = Ultrasonic(debug=True)

        print("\nBasic distance test...")
        for i in range(3):
            left, front, right = ultrasonic.distances()
            print(f"Reading {i+1}:")
            print(f"  Left: {left:.1f}cm" if left else "  Left: No reading")
            print(f"  Front: {front:.1f}cm" if front else "  Front: No reading")
            print(f"  Right: {right:.1f}cm" if right else "  Right: No reading")
            time.sleep(1)

        print("\nAveraged readings test...")
        left, front, right = ultrasonic.distances(use_average=True, samples=5)
        print("Averaged readings:")
        print(f"  Left: {left:.1f}cm" if left else "  Left: No reading")
        print(f"  Front: {front:.1f}cm" if front else "  Front: No reading")
        print(f"  Right: {right:.1f}cm" if right else "  Right: No reading")

        print("\nObstacle detection test...")
        distance, direction = ultrasonic.get_closest_obstacle()
        if distance:
            print(f"Closest obstacle: {distance:.1f}cm to the {direction}")
        else:
            print("No obstacles detected")

        print("\nPath clear test...")
        if ultrasonic.is_path_clear(30):
            print("Path is clear for 30cm+")
        else:
            print("Path is blocked within 30cm")

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during test: {e}")
    finally:
        try:
            if ultrasonic is not None:
                ultrasonic.cleanup()
        except Exception:
            pass
        print("Test complete")
