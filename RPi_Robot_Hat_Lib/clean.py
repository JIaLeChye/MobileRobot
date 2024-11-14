import RPi.GPIO as GPIO 
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

def play_tone(frequency, duration):
        """
        Play a tone on the buzzer
        frequency: in Hz
        duration: in seconds
        """
        try:
            # Initialize buzzer if not already done
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(12, GPIO.OUT)  # Using GPIO 12 for buzzer
            buzzer_pwm = GPIO.PWM(12, 440)  # Start with 440Hz
            buzzer_pwm.start(0)
            
            if frequency > 0:
                buzzer_pwm.ChangeFrequency(frequency)
                buzzer_pwm.ChangeDutyCycle(50)
                time.sleep(duration)
                buzzer_pwm.ChangeDutyCycle(0)
                time.sleep(0.1)
                # GPIO.cleanup(12)  # Cleanup buzzer GPIO
            else:
                time.sleep(duration)
                
        except Exception as e:
            print(f"Error playing tone: {e}")


play_tone(1000,2)
