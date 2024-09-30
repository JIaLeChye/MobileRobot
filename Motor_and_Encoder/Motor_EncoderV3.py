import RPi.GPIO as GPIO
import adafruit_ssd1306
import board
import time

class Encoder:
    """
    Class to handle encoder inputs, display RPM values on an OLED display, 
    and control motors to move a specific distance.
    """
    isinit = False

    def __init__(self, debug=False, ENCODER_RES=13, gear_ratio=30, LEFT_HALLSEN_A=20, LEFT_HALLSENS_B=21,  RIGHT_HALLSEN_A=10, RIGHT_HALLSENS_B=9, ODISPLAY=False, OLED_addr=0x3c, wheel_diameter = 100):
        """
        Initialize the Encoder object with specified parameters.
        """
        if not Encoder.isinit:
            self.debug = debug
            self.ODISPLAY = ODISPLAY
            self.ENCODER_RES = ENCODER_RES
            self.LEFT_HALLSEN_A = LEFT_HALLSEN_A
            self.RIGHT_HALLSEN_A = RIGHT_HALLSEN_A
            self.LEFT_HALLSEN_B = LEFT_HALLSENS_B
            self.RIGHT_HALLSEN_B = RIGHT_HALLSENS_B
            self.gear_ratio = gear_ratio
            self.OLED_addr = OLED_addr
            self.wheel_diameter = wheel_diameter/100  # Convert to meters
            self.Left_state = 0 # The value of the Left encoder in Binary 
            self.Right_state = 0 # The value of the Left encoder in Binary 
            
            self.left_enc_val = 0
            self.right_enc_val = 0

            if self.debug:
                print("Encoder Resolution =", self.ENCODER_RES)
                print("Gear Ratio =", self.gear_ratio)
                print("Left Hall Sensor Pin =", self.LEFT_HALLSEN_A, "," , self.LEFT_HALLSEN_B)
                print("Right Hall Sensor Pin =", self.RIGHT_HALLSEN_A, "," ,self.RIGHT_HALLSEN_B)
                print("Wheel Diameter =", self.wheel_diameter)
                print("OLED Display Enabled =", self.ODISPLAY)
                print("OLED address =", self.OLED_addr)
                print("Debug Mode Enabled =", self.debug)
                print("I2C Initialization Complete -- Motor_Encoder")
                print("All values initialized -- Motor_Encoder")
                
            if self.ODISPLAY:
                self.i2c = board.I2C()
                self.oled = adafruit_ssd1306.SSD1306_I2C(128, 64, self.i2c, addr=OLED_addr)
                print("OLED Display Enabled")
                self.oled.fill(1)
                self.oled.show()
                self.oled.fill(0)
                self.oled.text("OLED ENABLED", 25, 30, 1)
                self.oled.show()
                time.sleep(1)
            Encoder.isinit = True
    
    def setup(self):
        """
        Set up GPIO pins and initialize encoder.
        """
        retry_count = 3
        while retry_count >= 0:
            try:
                GPIO.cleanup() # Clean up GPIO
                GPIO.setmode(GPIO.BCM) # Set GPIO Mode to BCM
                GPIO.setwarnings(False)
                GPIO.setup(self.LEFT_HALLSEN_A, GPIO.IN)
                GPIO.setup(self.RIGHT_HALLSEN_A, GPIO.IN)
                GPIO.setup(self.LEFT_HALLSEN_B, GPIO.IN)
                GPIO.setup(self.RIGHT_HALLSEN_B, GPIO.IN)
                self.left_last_state = GPIO.input(self.LEFT_HALLSEN_A, )
                self.right_last_state = GPIO.input(self.RIGHT_HALLSEN_A) 
                if self.debug:
                    current_Mode = GPIO.getmode()
                    print("Current GPIO Mode:", current_Mode)
                    print(f"Setting up edge detection for pins: LEFT={self.LEFT_HALLSEN_A, self.RIGHT_HALLSEN_B}, RIGHT={self.RIGHT_HALLSEN_A, self.RIGHT_HALLSEN_B}")
                GPIO.add_event_detect(self.LEFT_HALLSEN_A, GPIO.BOTH, callback=self.left_update)
                # GPIO.add_event_detect(self.LEFT_HALLSEN_B,GPIO.BOTH, callback=self.left_update)
                GPIO.add_event_detect(self.RIGHT_HALLSEN_A, GPIO.BOTH, callback=self.right_update)
                # GPIO.add_event_detect(self.RIGHT_HALLSEN_B, GPIO.BOTH, callback=self.right_update)
                if self.debug:
                    print("GPIO edge detection added successfully.")
                break
            except RuntimeError as e:
                retry_count -= 1
                print(f"Error adding edge detection: {e}. Retries left: {retry_count}")
                time.sleep(1)
                GPIO.remove_event_detect(self.LEFT_HALLSEN_A)
                GPIO.remove_event_detect(self.RIGHT_HALLSEN_A)
                GPIO.cleanup()  # Ensure GPIO cleanup before retrying

        if retry_count == 0:
            print("Failed to add edge detection after multiple attempts.")
            raise RuntimeError("Failed to add edge detection after multiple attempts.")

        if self.debug:
            print("GPIO Initialization Complete -- Motor_Encoder")
            
        self.left_enc_val = 0
        self.right_enc_val = 0
        
        if self.ODISPLAY:
            self.oled.fill(0)
            self.oled.show()
            self.oled.text("MOTOR ENCODER", 23, 20, 1)
            self.oled.text("Setup Complete", 20, 35, 1)
            self.oled.show()
            time.sleep(1)
    
    def encoder(self, readback_duration=0.1):
        """
        Read encoder values and calculate RPM.
        """
        if not hasattr(self, 'setup_done'):
            self.setup()
            self.setup_done = True  # Flag to avoid repeated setup

        # start_time = time.time()
        
        # left_start_enc_val = self.left_enc_val
        # right_start_enc_val = self.right_enc_val

        # time.sleep(readback_duration)
        
        # left_end_enc_val = self.left_enc_val
        # right_end_enc_val = self.right_enc_val
        
        # end_time = time.time()
        
        left_pulse_count = self.left_enc_val # left_end_enc_val - left_start_enc_val
        right_pulse_count = self.right_enc_val # right_end_enc_val - right_start_enc_val
        
        # time_interval = end_time - start_time
        
        left_rpm = (left_pulse_count/self.ENCODER_RES) / self.gear_ratio #* (60/ time_interval) 
        right_rpm = (right_pulse_count/self.ENCODER_RES) / self.gear_ratio  #* (60/ time_interval) 

        if self.ODISPLAY:
            self.oled.fill(0)
            self.oled.text("Left Motor:", 1, 10, 1)
            self.oled.text("{:.2f} rpm".format(left_rpm), 1, 25, 1)
            self.oled.text("Right Motor:", 1, 40, 1)
            self.oled.text("{:.2f} rpm".format(right_rpm), 1, 55, 1)
            self.oled.show()
        if self.debug: 
            print("Left RPM: {:.2f}".format(left_rpm))
            print("Right RPM: {:.2f}".format(right_rpm))
            print("Pulse detected at Left: {:.2f},  ".format(left_pulse_count))
            print("Pulse detected at Right: {:.2f}".format(right_pulse_count))
        return left_rpm, right_rpm
        
    def left_update(self, channel):
        """
        Callback function for left encoder interrupt.
        """
        Left_state  = self.Left_state & 3 
        if GPIO.input(self.LEFT_HALLSEN_A):  
            Left_state |= 4 

        if GPIO.input(self.LEFT_HALLSEN_B):
            Left_state |= 8
        self.Left_state = Left_state >> 2

        if Left_state == 1 or Left_state == 7 or Left_state == 8 or Left_state == 14:
            self.left_enc_val += 1  # Forward  

        
        elif Left_state == 2 or Left_state == 4 or Left_state == 11 or Left_state == 13:
            self.left_enc_val -= 1  # Reverse
        
        elif Left_state == 3 or Left_state == 12:
            print("Error ! Detection skiped Occured")
            pass

        elif Left_state == 6 or Left_state == 9:
            print("Error ! Detection skiped Occured")
            pass

        if self.debug:
            print("Left Encoder Value:", self.left_enc_val)
            print("Left State:{:04b}".format(Left_state))


    def right_update(self, channel):
        """
        Callback function for right encoder interrupt.
        """
        Right_state  = self.Right_state & 3 
        if GPIO.input(self.RIGHT_HALLSEN_A):  
            Right_state |= 4 

        if GPIO.input(self.RIGHT_HALLSEN_B):
            Right_state |= 8
        self.Right_state = Right_state >> 2

        if Right_state == 1 or Right_state == 7 or Right_state == 8 or Right_state == 14:
            self.right_enc_val += 1  # Forward  

        
        elif Right_state == 2 or Right_state == 4 or Right_state == 11 or Right_state == 13:
            self.right_enc_val -= 1  # Reverse
        
        elif Right_state == 3 or Right_state == 12:
            print("Error ! Detection skiped Occured")
            pass

        elif Right_state == 6 or Right_state == 9:
            print("Error ! Detection skiped Occured")
            pass

        if self.debug:
            print("Left Encoder Value:", self.right_enc_val)
            print("Left State:{:04b}".format(Right_state))
            
        self.right_enc_val += 1  # Forward
        if self.debug: 
            print("Right Encoder Value:", self.right_enc_val)

   

    def distance(self):
        """
        Calculate the distance moved by the motor based on encoder pulses.
        """
        Left_pulse_count = self.left_enc_val
        Right_pulse_count = self.right_enc_val
        Left_revs = Left_pulse_count / self.ENCODER_RES  # Motor shaft revolutions
        wheel_revs = Left_revs / self.gear_ratio  # Wheel revolutions
        Left_distance = wheel_revs * (self.wheel_diameter * 3.1416)  # Distance in meters (Get the Circumference)

        Right_revs = Right_pulse_count / self.ENCODER_RES  # Motor shaft revolutions
        wheel_revs = Right_revs / self.gear_ratio  # Wheel revolutions
        Right_distance = wheel_revs * (self.wheel_diameter * 3.1416)  # Distance in meters (Get the Circumference)
        if self.debug:
            print("Left Distance: {:.4f} meters".format(Left_distance))
            print("Right Distance: {:.4f} meters".format(Right_distance))
        if self.ODISPLAY:
            self.oled.fill(0)
            self.oled.text("Left Distance:", 1, 10, 1)
            self.oled.text("{:.4f} m".format(Left_distance), 1, 25, 1)
            self.oled.text("Right Distance:", 1, 40, 1)
            self.oled.text("{:.4f} m".format(Right_distance), 1, 55, 1)
            self.oled.show()    
        return Left_distance , Right_distance 


    def stop(self):
        """
        Clean up GPIO resources and OLED display.
        """
        GPIO.cleanup()
        if self.ODISPLAY:
            self.oled.fill(0)
            self.oled.show()
            self.i2c.deinit()

if __name__ == '__main__':
    enc = Encoder(ODISPLAY=False, debug=False)
    try:
        while True:
            left_rpm, right_rpm = enc.encoder()
            print("Left Motor: {:.2f}".format(left_rpm))
            print("Right Motor: {:.2f}".format(right_rpm))
            time.sleep(1)
            Left_distance, Right_distence  = enc.distance()
            print("Left Distance: {:.2f}m".format(Left_distance))
            print("Right Distance: {:.2f}m".format(Right_distence))
    except KeyboardInterrupt:
        enc.stop()
        exit()
