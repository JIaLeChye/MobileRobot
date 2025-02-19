from RPi_Robot_Hat_Lib import RobotController
import time 
import os
import sys
import logging, logging.handlers
import busio 
import board
import adafruit_ssd1306 
from PIL import Image, ImageDraw, ImageFont

# Logger Setup
logger = logging.getLogger('battery_logger')
logger.setLevel(logging.DEBUG)

# Create a log format with timestamp, level name, function name, and message
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

# Create a rotating file handler to manage log size and keep old logs
# Check is the log file exist, if not create new log file 

log_file = "/home/raspberry/battery/battery_log.txt"
if not os.path.exists(log_file):
           # Create the directory if it doesn't exist
           os.makedirs(os.path.dirname(log_file), exist_ok=True)
           
           # Create empty log file
           with open(log_file, 'w') as f:
               pass  # Creates empty file
           print(f"Created new log file at: {log_file}")
        
log_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)  # 5MB per file, 5 backups
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(formatter)

# Create a stderr handler for error logs (critical and above)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)
stderr_handler.setFormatter(formatter)

# Create a stdout handler for debug and info logs
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(log_handler)
logger.addHandler(stderr_handler)
logger.addHandler(stdout_handler)

robot = RobotController()
LOW_BATTERY_TRESH = 11
USB_VOLTAGE = 5
CHECK_INTERVAL = 60

i2c = busio.I2C(board.SCL, board.SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
disp.fill(0)
disp.show()
image = Image.new("1", (disp.width, disp.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

def Display_battery(battery_stat):
    voltage = battery_stat
    CurrentTime = time.time() 
    CurrentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(CurrentTime))
    logger.info(f"{CurrentTime} --> Battery Voltage: {voltage:.1f}V")
    
    # Update OLED display
    if all([disp, image, draw, font]):
        draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
        draw.text((0, 0), "Battery Status:", font=font, fill=255)
        draw.text((0, 20), f"Voltage: {voltage:.1f}V", font=font, fill=255)
        
        # Add battery level indicator (9V-13V range)
        level = min(100, max(0, (voltage - 11) * 100 / (13.0 - 11)))  # Map 9V-13V to 0-100%
        draw.text((0, 40), f"Level: {level:.0f}%", font=font, fill=255)
        
        # Draw battery bar
        bar_width = int(disp.width * level / 100)
        draw.rectangle((0, 55, bar_width, 63), outline=255, fill=255)
        disp.image(image)
        disp.show()
    else:
        logger.error("OLED display not initialized.")   
    time.sleep(1)

def main():
    global font
    logger.debug("Script Started")
    robot.play_tone(1000, 0.5)
    time.sleep(0.2)
    robot.play_tone(1000, 0.5)
    robot.cleanup_buzzer()
    
    while True: 
        try:
            battery_stat = robot.get_battery()
            if USB_VOLTAGE < battery_stat <= LOW_BATTERY_TRESH:
                logger.warning(f"Battery Low Voltage detected: {battery_stat}")
                draw.text((0, 30), "LOW BATTERY!", font=font, fill=255)
                draw.text((0, 40), "ROBOT WILL SHUTDOWN", font=font, fill=255)
                draw.text((0, 50), "AT 10.5V", font=font, fill=255)
                disp.image(image)
                disp.show()
                time.sleep(1)
                for i in range(5):
                    robot.play_tone(2000, 1)
                    disp.fill(0)
                    disp.show()
                    time.sleep(0.2)
                    draw.text((0, 30), "LOW BATTERY!", font=font, fill=255)
                    disp.image(image)
                    disp.show()
                    # time.sleep(1)
                robot.cleanup_buzzer()
                time.sleep(CHECK_INTERVAL)
                if USB_VOLTAGE < battery_stat <= 10.5: 
                    for i in range(5): 
                        logger.warning(f"Shutting down due to low battery: {battery_stat}")
                        disp.fill(0)
                        disp.show()
                        draw.text((0, 30), "PLS RECHAGRE!", font=font, fill=255)
                        draw.text((0,40), f"VOLTAGE: {battery_stat}", font=font, fill=255)
                        disp.image(image)
                        disp.show()
                        time.sleep(10)
                    os.system("sudo shutdown -h now")
            elif battery_stat <= USB_VOLTAGE:
                logger.warning(f"USB Voltage detected: {battery_stat}")
                draw.text((0, 10), "USB Voltage detected", font=font, fill=255)
                draw.text((0, 20), f"VOLTAGE: {battery_stat}", font=font, fill=255)
                draw.text((0, 30), "CAUTION!", font=font, fill=255)
                draw.text((0, 40), "DO NOT START ", font=font, fill=255)
                draw.text((0, 50), "MOTOR!", font=font, fill=255)
                disp.image(image)
                disp.show()
            else:
                Display_battery(battery_stat)
        except Exception as e:
            logger.error(f"Failed to read battery or update display: {e}")
        
        time.sleep(CHECK_INTERVAL)

try:
    if __name__ == '__main__':
        main() 

except KeyboardInterrupt:
    robot.cleanup()  
    logger.warning("Program Exit: User Interupt")
except Exception as e:
    logger.error(f"An error occurred: {e}") 

finally:
    disp.fill(0)
    disp.show() 
    logger.info("Script Ended")
    exit()
