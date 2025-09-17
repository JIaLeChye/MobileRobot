import RPi.GPIO as GPIO 
import time 

__version__ = "2.0.0"



class IRsens:
    __init_check = False 

    def __init__(self, IrPin = 24, debug=False): 
        self.Irsensor = IrPin
        self.debug = debug 
        if not IRsens.__init_check: 
            GPIO.setmode(GPIO.BCM)
            IRsens.__init_check = True
        if debug == True:
            print("IR Sensor Initialized")  
            

    def status(self): 
        GPIO.setup(self.Irsensor, GPIO.IN )
        stat = None
        if GPIO.input(self.Irsensor) == 1: 
            stat = 0 
        elif GPIO.input(self.Irsensor) == 0: 
            stat = 1 
        if stat == None:
            if self.debug == True:
                print("IR Sensor: Error reading sensor")
            raise ValueError("Error reading IR sensor")    
        if self.debug == True:
            print(f"IR Sensor: {stat}")
        return stat
    

    def cleanup(self):
        if self.debug == True:
            print("IR Sensor Cleanup")
        try:
            GPIO.cleanup(self.Irsensor)
        except Exception as e:
            print(f"GPIO cleanup error: {e}")
        IRsens.__init_check = False
            

if __name__ == "__main__":
    IR = IRsens(debug = True)
    try:
        while True: 
            print(IR.status())
            time.sleep(0.5)
    except KeyboardInterrupt:
        IR.cleanup()
        print("Program stopped by User")
    except Exception as e:
        print(f"An error occurred: {e}")
        IR.cleanup()
            
           
