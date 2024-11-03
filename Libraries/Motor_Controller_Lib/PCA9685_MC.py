from PCA9685 import PCA9685 # Library From Servo HAT (using PCA9685 I2C PWM)
import time # Import the time Library 

# Use print(Function.__doc__) to view the codumentation of the function. 
# print(Motor_Controller.__doc__)

class Motor_Controller:
    # Declare all the Variables 
    """
    This Library uses the PCA9685 I2C PWM Module to simulate the PWM Frequency. 
    Dependency: PCA9685
              : Time 
    
    All the Motor Driver is assigned:
    F_M1A = 4 (I2C Channel)
    F_M1B = 5 (I2C Channel)
    F_M2A = 6 (I2C Channel)
    F_M2B = 7 (I2C Channel)
    B_M1A = 8 (I2C Channel)
    B_M1B = 9 (I2C Channel)
    B_M2A = 10 (I2C Channel)
    B_M2B = 11 (I2C Channel)

    **All the Channel Pins is according to the Servo HAT Pinout 

    /-----Fornt Motor Driver----/
    F_M1A:  (Left Motor @ Forward Motion)
    F_M1B:  (Left Motor @ Backward Motion)

    F_M2A:  (Right Motor @ Forward Motion)
    F_M2B:  (Right Motor @ Backward Motion)

    /-----Back Motor-----/ 
    B_M1A: (Left Motor @ Forward Motion)
    B_M1B: (Left Motor @ Backward Motion)

    B_M2A: (Right Motor @ Forward Motion)
    B_M2B: (Right Motor @ Backward Motion)

    ** The calculation of the Freq is 
    FREQ = (Freq/100 * 19999)
    

    """
    __init__check = False 

    def __init__(self, addr=0x40, PWMFreq=50, debug=False):
        """
        All the Motor Driver is assigned:
        :F_M1A = 4 (I2C Channel)
        :F_M1B = 5 (I2C Channel)
        :F_M2A = 6 (I2C Channel)
        :F_M2B = 7 (I2C Channel)
        :B_M1A = 8 (I2C Channel)
        :B_M1B = 9 (I2C Channel)
        :B_M2A = 10 (I2C Channel)
        :B_M2B = 11 (I2C Channel)

        In default:
        :param I2C address = 0x40 
        :param PWM Frequency  = 50Hz
        :param Debug = False 
        ++++++++++++++++++++++++
        use Motor_Controller(addr=[I2C address], PWMFreq=[PWM Frequency], debug=[True/False])

        """
        if not Motor_Controller.__init__check:
        
            self.debug = debug 
            self.addr =  addr 
            self.PWMFreq = PWMFreq 
            self.PWM = PCA9685(addr)
            self.PWM.setPWMFreq(PWMFreq)

            self.F_M1A = 4
            self.F_M1B = 5
            self.F_M2A = 6
            self.F_M2B = 7
            self.B_M1A = 8
            self.B_M1B = 9
            self.B_M2A = 10
            self.B_M2B = 11
            if self.debug :
                print("Servo HAT initialise")
                print("All Motor Driver is configured")
            
            Motor_Controller.__init__check = True 
        else:
            if self.debug:
                print("Servo HAT is already initialise")


    
    
    def Forward(self, Freq):
        """
        This function Makes the Motor to Move Forward 
        Use Motor_Controller(debug=True) to print the value of FREQ 
        """
        FREQ = (Freq/100 * 19999)
        # Front Motor Driver 
        self.PWM.setServoPulse(self.F_M1A , FREQ)
        self.PWM.setServoPulse(self.F_M1B , 0)
        self.PWM.setServoPulse(self.F_M2A , FREQ)
        self.PWM.setServoPulse(self.F_M2B , 0)
        
        #Back Motor Driver
        self.PWM.setServoPulse(self.B_M1A, FREQ)
        self.PWM.setServoPulse(self.B_M1B, 0)
        self.PWM.setServoPulse(self.B_M2A, FREQ)
        self.PWM.setServoPulse(self.B_M2B, 0)
        if self.debug:
            print(f"Forward Moving: {FREQ}")



    def Backward(self, Freq):
        """
        This function Makes the Motor to Move Backward 
        Use Motor_Controller(debug=True) to print the value of FREQ 
        
        """
        
        FREQ = (Freq/100 * 19999)
        #Front Motor Driver
        self.PWM.setServoPulse(self.F_M1A , 0)
        self.PWM.setServoPulse(self.F_M1B , FREQ)
        self.PWM.setServoPulse(self.F_M2A , 0)
        self.PWM.setServoPulse(self.F_M2B , FREQ)
        
        #Back Motor Driver
        self.PWM.setServoPulse(self.B_M1A, 0)
        self.PWM.setServoPulse(self.B_M1B, FREQ)
        self.PWM.setServoPulse(self.B_M2A, 0)
        self.PWM.setServoPulse(self.B_M2B, FREQ)
        if self.debug:
            print(f"Backward Moving: {FREQ}")

    def Brake(self):
        """
        This function Makes the Motor to Stop

        Use Motor_Controller(debug=True) to print the status of the Motor 


        """
        
        #Front Motor Driver
        self.PWM.setServoPulse(self.F_M1A , 0)
        self.PWM.setServoPulse(self.F_M1B , 0)
        self.PWM.setServoPulse(self.F_M2A , 0)
        self.PWM.setServoPulse(self.F_M2B , 0)
        
        #Back Motor Driver
        self.PWM.setServoPulse(self.B_M1A, 0)
        self.PWM.setServoPulse(self.B_M1B, 0)
        self.PWM.setServoPulse(self.B_M2A, 0)
        self.PWM.setServoPulse(self.B_M2B, 0)
        if self.debug:
            print("Brake")
            print("All Channel are assigned to PWM = 0")
        
    def Horizontal_Right(self, Freq):
        """
        This function Makes the Motor to Move Horizontal Right 
        **!!This Function Requires the Omniwheels to work!!**
        Use Motor_Controller(debug=True) to print the value of FREQ 
        
        """
        
        FREQ = (Freq/100 * 19999)
        # Move Backward
        self.PWM.setServoPulse(self.F_M1A , 0)
        self.PWM.setServoPulse(self.F_M1B , FREQ)
        #Move Forward
        self.PWM.setServoPulse(self.F_M2A , FREQ)
        self.PWM.setServoPulse(self.F_M2B , 0)
        

        
        #Back Motor Driver
        #Move Forward
        self.PWM.setServoPulse(self.B_M1A, FREQ)
        self.PWM.setServoPulse(self.B_M1B, 0)
        #Move Backward
        self.PWM.setServoPulse(self.B_M2A, 0)
        self.PWM.setServoPulse(self.B_M2B, FREQ)
        if self.debug:
            print(f"Horizontal Right Moving: {FREQ}")

    def Horizontal_Left(self, Freq):
        
        """
        This function Makes the Motor to Move Horizontal Left 
        **!! This Function Requires Omniwheels to work**!! 
        Use Motor_Controller(debug=True) to print the value of FREQ 
        
        """
        
        
        FREQ = (Freq/100 * 19999)
        # Move Forward
        self.PWM.setServoPulse(self.F_M1A , FREQ)
        self.PWM.setServoPulse(self.F_M1B , 0)

        self.PWM.setServoPulse(self.F_M2A , 0)
        self.PWM.setServoPulse(self.F_M2B , FREQ)
        
        #Back Motor Driver
        self.PWM.setServoPulse(self.B_M1A, 0)
        self.PWM.setServoPulse(self.B_M1B, FREQ)
        
        self.PWM.setServoPulse(self.B_M2A, FREQ)
        self.PWM.setServoPulse(self.B_M2B, 0)
        if self.debug:
            print(f"Horizontal Left Moving: {FREQ}")


    def AntiClock_Rotate(self, Freq):
        """
        This function Makes the Car to Rotate Anti-clockwise
        Use Motor_Controller(debug=True) to print the value of FREQ 
        
        """
        
        FREQ = (Freq/100 * 19999)
        self.PWM.setServoPulse(self.F_M1A , FREQ)
        self.PWM.setServoPulse(self.F_M1B , 0)
        self.PWM.setServoPulse(self.F_M2A , 0)
        self.PWM.setServoPulse(self.F_M2B , FREQ)
        
        #Back Motor Driver
        self.PWM.setServoPulse(self.B_M1A, FREQ)
        self.PWM.setServoPulse(self.B_M1B, 0)
        self.PWM.setServoPulse(self.B_M2A, 0)
        self.PWM.setServoPulse(self.B_M2B, FREQ)
        if self.debug:
            print(f"Anti-Clockwise Rotation Moving: {FREQ}")


    def Clock_Rotate(self, Freq):
        
        """
        This function Makes the Motor to Rotate Clockwise
        Use Motor_Controller(debug=True) to print the value of FREQ 
        
        """
        FREQ = (Freq/100 * 19999)
        self.PWM.setServoPulse(self.F_M1A , 0)
        self.PWM.setServoPulse(self.F_M1B , FREQ)
        self.PWM.setServoPulse(self.F_M2A , FREQ)
        self.PWM.setServoPulse(self.F_M2B , 0)
        
        #Back Motor Driver
        self.PWM.setServoPulse(self.B_M1A, 0)
        self.PWM.setServoPulse(self.B_M1B, FREQ)
        self.PWM.setServoPulse(self.B_M2A, FREQ)
        self.PWM.setServoPulse(self.B_M2B, 0)
        if self.debug:
            print(f"Clockwise Rotation Moving: {FREQ}")
    
    def servoPulse(self, channel, Freq):

        """
        This function sets the servo position
        Use Motor_Controller(debug=True) to print the value of FREQ and the Channel. 
        
        """

        self.PWM.setServoPulse(channel, Freq)

        if self.debug:
            print(f"Servo Pulse at {Freq}")
            print(f"The Servo Channel is {channel}")


    def cleanup(self):
        """
        This function cleans up the GPIO
        """
        for i in range(16):
            self.PWM.setServoPulse(i, 0)

    
if __name__ == '__main__':
    """
    This is the Demo Code of this Library 
    The Horizontal Movement Requires Omniwheels 
    Run this library directly to try on it ! 
    Adjust the Freq for faster @ Slower Speed. 
    """
    try:
        Motor = Motor_Controller()
        Freq = 20
        while True:
            Motor.AntiClock_Rotate(Freq)
     

    except KeyboardInterrupt:
        Motor.cleanup()
    except Exception as e:
        print("Error Accour:", e)
        Motor.cleanup()