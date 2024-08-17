# Library Version Number: V1.2

import RPi.GPIO as GPIO 
import adafruit_ssd1306
import board 
import time

class Encoder:
    """
    Class to handle encoder inputs and display RPM values on an OLED display.
    """
    isinit = False

    def __init__(self, debug=False, ENCODER_RES=13, gear_ratio=30, LEFT_HALLSEN=20, RIGHT_HALLSEN=10, ODISPLAY=False, OLED_addr=0x3c):
        """
        Initialize the Encoder object with specified parameters.
        """
        if not Encoder.isinit:
            self.debug = debug 
            self.ODISPLAY = ODISPLAY 
            self.ENCODER_RES = ENCODER_RES 
            self.LEFT_HALLSEN = LEFT_HALLSEN
            self.RIGHT_HALLSEN = RIGHT_HALLSEN
            self.gear_ratio = gear_ratio
            self.OLED_addr = OLED_addr 
            
            self.left_enc_val = 0
            self.right_enc_val = 0


            if self.debug:
                print("Encoder Resolution =", self.ENCODER_RES)
                print("Gear Ratio =", self.gear_ratio)
                print("Left Hall Sensor Pin =", self.LEFT_HALLSEN)
                print("Right Hall Sensor Pin =", self.RIGHT_HALLSEN)
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
                GPIO.setup(self.LEFT_HALLSEN, GPIO.IN)
                GPIO.setup(self.RIGHT_HALLSEN, GPIO.IN) 
                if self.debug:
                    current_Mode = GPIO.getmode()
                    print("Current GPIO Mode:", current_Mode)
                    print(f"Setting up edge detection for pins: LEFT={self.LEFT_HALLSEN}, RIGHT={self.RIGHT_HALLSEN}")
                GPIO.add_event_detect(self.LEFT_HALLSEN, GPIO.RISING, callback=self.left_update)
                GPIO.add_event_detect(self.RIGHT_HALLSEN, GPIO.RISING, callback=self.right_update)
                if self.debug:
                    print("GPIO edge detection added successfully.")
                break
            except RuntimeError as e:
                retry_count -= 1
                print(f"Error adding edge detection: {e}. Retries left: {retry_count}")
                time.sleep(1)
                GPIO.remove_event_detect(self.LEFT_HALLSEN)
                GPIO.remove_event_detect(self.RIGHT_HALLSEN)
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



        start_time = time.time()
        left_start_enc_val = self.left_enc_val
        right_start_enc_val = self.right_enc_val

        time.sleep(readback_duration) 
        
        left_end_enc_val = self.left_enc_val 
        right_end_enc_val = self.right_enc_val 
        
        end_time = time.time()
        
        left_pulse_count = left_end_enc_val - left_start_enc_val
        right_pulse_count = right_end_enc_val - right_start_enc_val
        
        time_interval = end_time - start_time
        
        left_rpm = (left_pulse_count * 60) / (time_interval * self.ENCODER_RES) / self.gear_ratio
        right_rpm = (right_pulse_count * 60) / (time_interval * self.ENCODER_RES) / self.gear_ratio

        if self.ODISPLAY:
            self.oled.fill(0)
            self.oled.text("Left Motor:", 1, 10, 1)
            self.oled.text("{:.2f} rpm".format(left_rpm), 1, 25, 1)
            self.oled.text("Right Motor:", 1, 40, 1)
            self.oled.text("{:.2f} rpm".format(right_rpm), 1, 55, 1)
            self.oled.show()
        
        return left_rpm, right_rpm
        
    def left_update(self, channel): 
        """
        Callback function for left encoder interrupt.
        """
        self.left_enc_val += 1
    
    def right_update(self, channel): 
        """
        Callback function for right encoder interrupt.
        """
        self.right_enc_val += 1 

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
    enc = Encoder(ODISPLAY=False, debug=True)
    try: 
        while True:
            left_rpm, right_rpm = enc.encoder()
            print("Left Motor: {:.2f}".format(left_rpm))  
            print("Right Motor: {:.2f}".format(right_rpm))
            time.sleep(1)
    except KeyboardInterrupt:
        enc.stop()
        exit() 
