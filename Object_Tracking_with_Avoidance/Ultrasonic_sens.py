import RPi.GPIO as GPIO
import time

class Ultrasonic:
    SOUND_SPEED = 34300  # Speed of sound in cm/s

    def __init__(self, Left_sensor=5, Front_sensor=16, Right_sensor=18, debug=False):
        """
        Initializes GPIO pins for the ultrasonic sensors.
        """
        self.Left_sensor = Left_sensor
        self.Front_sensor = Front_sensor
        self.Right_sensor = Right_sensor
        self.debug = debug

        # Initialize GPIO only once
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Left_sensor, GPIO.OUT)
        GPIO.setup(Front_sensor, GPIO.OUT)
        GPIO.setup(Right_sensor, GPIO.OUT)

        if self.debug:
            print("Ultrasonic sensors initialized.")

    def send_trigger_pulse(self, pin):
        """
        Sends a 10 microsecond high pulse on the specified pin to trigger the sensor.
        """
        # Set the pin to output before using it
        GPIO.setup(pin, GPIO.OUT)  # Ensure pin is set to output mode before using it
        
        GPIO.output(pin, True)
        time.sleep(0.001)  # 10 microseconds pulse duration
        GPIO.output(pin, False)
        
        if self.debug:
            print(f"Trigger Sent to pin {pin}")

    def wait_for_echo(self, pin):
        """
        Waits for echo signal, returns duration of pulse.
        """
        GPIO.setup(pin, GPIO.IN)
        pulse_start = time.time()

        # Wait for pulse start
        while GPIO.input(pin) == 0:
            pulse_start = time.time()

        # Wait for pulse end
        pulse_end = time.time()
        while GPIO.input(pin) == 1:
            pulse_end = time.time()

        # Calculate pulse duration
        pulse_duration = pulse_end - pulse_start
        return pulse_duration

    def get_distance(self, pin):
        """
        Measure distance from a specific sensor.
        """
        self.send_trigger_pulse(pin)
        pulse_duration = self.wait_for_echo(pin)

        if pulse_duration is None:
            return None

        distance = pulse_duration * self.SOUND_SPEED / 2
        return distance

    def distances(self):
        """
        Returns distances from Left, Front, and Right sensors.
        """
        Left = self.get_distance(self.Left_sensor)
        Front = self.get_distance(self.Front_sensor)
        Right = self.get_distance(self.Right_sensor)

        if self.debug:
            print(f"Left: {Left}, Front: {Front}, Right: {Right}")

        return Left, Front, Right

    def cleanup(self):
        """
        Cleans up GPIO settings when finished.
        """
        GPIO.cleanup()
        if self.debug:
            print("Cleaned up GPIO.")

if __name__ == "__main__":
    ultrasonic = Ultrasonic(debug=True)

    try:
        while True:
            Left, Front, Right = ultrasonic.distances()
            if Left is not None and Front is not None and Right is not None:
                print(f"Left: {Left} cm, Front: {Front} cm, Right: {Right} cm")
            time.sleep(1)

    except KeyboardInterrupt:
        ultrasonic.cleanup()
        print("Exiting program.")
