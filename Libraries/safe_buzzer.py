#!/usr/bin/env python3
"""
Improved Buzzer Control for Robot
=================================

This module provides safe buzzer control with proper PWM cleanup.
"""

import RPi.GPIO as GPIO
import time
import atexit

class SafeBuzzer:
    """Safe buzzer control with proper cleanup"""
    
    def __init__(self, pin=12):
        self.pin = pin
        self.pwm = None
        self._is_setup = False
        
        # Register cleanup function
        atexit.register(self.cleanup)
    
    def setup(self):
        """Setup GPIO and PWM"""
        if not self._is_setup:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.pin, GPIO.OUT)
                self.pwm = GPIO.PWM(self.pin, 440)
                self.pwm.start(0)
                self._is_setup = True
            except Exception as e:
                print(f"Buzzer setup error: {e}")
    
    def play_tone(self, frequency, duration):
        """Play a tone safely"""
        try:
            if not self._is_setup:
                self.setup()
            
            if self.pwm and frequency > 0:
                self.pwm.ChangeFrequency(frequency)
                self.pwm.ChangeDutyCycle(50)
                time.sleep(duration)
                self.pwm.ChangeDutyCycle(0)
            else:
                time.sleep(duration)
                
        except Exception as e:
            print(f"Error playing tone: {e}")
    
    def cleanup(self):
        """Safe cleanup"""
        try:
            if self.pwm and self._is_setup:
                self.pwm.ChangeDutyCycle(0)
                self.pwm.stop()
                self.pwm = None
            if self._is_setup:
                GPIO.cleanup(self.pin)
                self._is_setup = False
        except Exception as e:
            # Ignore cleanup errors
            pass

# Global buzzer instance
_buzzer = None

def get_buzzer():
    """Get or create buzzer instance"""
    global _buzzer
    if _buzzer is None:
        _buzzer = SafeBuzzer()
    return _buzzer

def play_safe_tone(frequency, duration):
    """Play a tone safely"""
    buzzer = get_buzzer()
    buzzer.play_tone(frequency, duration)

if __name__ == "__main__":
    # Test the safe buzzer
    print("Testing safe buzzer...")
    play_safe_tone(440, 0.5)
    play_safe_tone(880, 0.5)
    print("Test complete!")
