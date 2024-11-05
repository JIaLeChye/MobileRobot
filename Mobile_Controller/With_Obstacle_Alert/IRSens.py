import RPi.GPIO as GPIO 
import time 



class IRsens:
    __init_check = False 

    def __init__(self, IrPin = 24, debug=False): 

        if not IRsens.__init_check: 
            self.Irsensor = IrPin
            GPIO.setmode(GPIO.BCM)
            IRsens.__init_check = True
        self.debug = debug 
        if debug == True:
            print("IR Sensor Initialized")  
            

    def status(self): 
        GPIO.setup(self.Irsensor, GPIO.IN )
        if GPIO.input(self.Irsensor) == 1: 
            stat = 0 
        elif GPIO.input(self.Irsensor) == 0: 
            stat = 1 
        if self.debug == True:
            print(f"IR Sensor: {stat}")
        return stat
    

    def cleanup(self):
        GPIO.cleanup()
            

if __name__ == "__main__":
    try:
        IR = IRsens()
        while True: 
            print(IR.status())
            time.sleep(0.5)
    except KeyboardInterrupt:
        IR.cleanup()
            
           