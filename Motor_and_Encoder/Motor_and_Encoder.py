from PCA9685_MC import Motor_Controller
from Motor_EncoderV2 import Encoder 
import time
import threading 

def init():
    global enc, Motor , shutdown_event
    Motor = Motor_Controller() 
    enc = Encoder() 
    shutdown_event = threading.Event()
    

def Movement():
    global Motor, shutdown_event
    while not shutdown_event.is_set(): 
        
        Motor.Forward(20)
        time.sleep(5)
        Motor.Brake()
        time.sleep(1)
        Motor.Backward(20)
        time.sleep(5)
        Motor.Brake()
        time.sleep(1)
    

def encoder():
    global enc , shutdown_event
    while not shutdown_event.is_set():
        
        Left_enc, Right_enc = enc.encoder()
        Left_dist, Right_dist = enc.distance()
        print("Left Motor: {:.2f}".format(Left_enc))
        print("Right Motor: {:.2f}".format(Right_enc))
        print("Left Distance: {:.2f}m".format(Left_dist))
        print("Right Distance: {:.2f}m".format(Right_dist))
        time.sleep(0.2)
    


def cleanup():
    global Motor, enc, shutdown_event

    # Set shutdown event
    while shutdown_event.set(): 
        # Wait for threads to finish
        Movement_thred.join()
        encoder_thred.join()

        # Stop motor and encoder
        Motor.cleanup()
        enc.stop()

if __name__ == '__main__':
    try: 
        init()
        Movement_thred = threading.Thread(target=Movement)
        encoder_thred = threading.Thread(target=encoder)
        Movement_thred.start()
        encoder_thred.start()
        
    except KeyboardInterrupt:
        print("Shutting down")
        cleanup() 
    
