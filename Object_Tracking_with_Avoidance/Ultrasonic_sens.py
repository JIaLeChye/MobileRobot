import RPi.GPIO as GPIO
import time

class Ultrasonic:
    """
    Class to represent an ultrasonic sensor.
    """
    __init_check = False 
    SOUND_SPEED = 34300  # Speed of sound in cm/s

    def __init__(self, Left_sensor=5, Front_sensor=16, Right_sensor = 18, debug=False):
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

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(Left_sensor, GPIO.OUT)
            GPIO.setup(Front_sensor, GPIO.OUT)
            GPIO.setup(Right_sensor, GPIO.OUT)
            if self.debug:
                print("Ultrasonic sensor initialized.")
            Ultrasonic.__init_check = True
        else:
            if self.debug: 
                print("Ultrasonic sensor already initialized.")
            pass

    def send_trigger_pulse(self, pin):
        """
        Sends a 10 microsecond high pulse on the specified pin to trigger the sensor.
        """
        GPIO.output(pin, True)
        time.sleep(0.001) 
        GPIO.output(pin, False)
        if self.debug:
            print(f"Trigger Sent{pin}")

    def wait_for_echo(self, pin):
        """
        Waits for rising and falling edges on the echo pin (specified pin) to calculate pulse duration.
        """
        GPIO.setup(pin, GPIO.IN)
        pulse_start = time.time()
        Initial_Time = pulse_start  
        timeout = 0.01  # Timeout set to 10 milliseconds
        while GPIO.input(pin) == 0 and time.time() - Initial_Time < timeout:
            pulse_start = time.time()
            if self.debug:
                print("Waiting for echo...")

        if GPIO.input(pin) == 0:
            print("Time Out: No echo received.")
            return None

        pulse_end = time.time()
        while GPIO.input(pin) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        return pulse_duration


    def get_distance(self, pin):
        """
        Measures distance using the ultrasonic sensor connected to the specified pin and returns the calculated value.
        """
        GPIO.setup(pin, GPIO.OUT)
        self.send_trigger_pulse(pin)

        pulse_duration = self.wait_for_echo(pin)

        if pulse_duration is None:
            GPIO.setup(pin, GPIO.OUT)
            self.send_trigger_pulse(pin)
            print("Error: No echo received. Retrying...")
            time.sleep(0.1)
            self.send_trigger_pulse(pin)  # Retry sending trigger pulse
            pulse_duration = self.wait_for_echo(pin)  # Wait for echo again
            return None 
                

        distance = pulse_duration * self.SOUND_SPEED / 2
        if self.debug:
            print(f"Distance: {distance} cm for pin {pin}")
        return distance

           
    
    def distances(self):
        """
        Get the distance measurement form the left, front and right sensor 
        """
        Left = self.get_distance(self.Left_sensor)
        Front = self.get_distance(self.Front_sensor)
        Right = self.get_distance(self.Right_sensor)
        if self.debug:
            print(f"Left: {Left}, Front: {Front}, Right:{Right}")
        return Left, Front, Right

    def cleanup(self):
        """
        Cleans up GPIO pins
        """
        if self.debug:
            print("Cleaning up GPIO pins...")
        GPIO.cleanup()

if __name__ == "__main__":
    try:
        ultrasonic = Ultrasonic(debug=True)
        while True: 
            Left, Front, Right = ultrasonic.distances()
            if (Left and Front and Right) is not None: 
                print("Left: {:.2f} cm".format(Left))
                print("Front: {:.2f} cm".format(Front))
                print("Right: {:.2f} cm".format(Right))
                time.sleep(1)
                print(" ")
    except KeyboardInterrupt:
        ultrasonic.cleanup()
        print("Exiting...")
