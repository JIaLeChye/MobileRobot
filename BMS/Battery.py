from RPi_Robot_Hat_Lib import RobotController
import time 
import os
import sys
import logging, logging.handlers
import busio 
import board
import signal 
import adafruit_ssd1306 
from PIL import Image, ImageDraw, ImageFont

# Logger Setup
logger = logging.getLogger('battery_logger')
logger.setLevel(logging.DEBUG)

# Create a log format with timestamp, level name, function name, and message
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')


# Create a stderr handler for error logs (critical and above)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)
stderr_handler.setFormatter(formatter)

# Create a stdout handler for debug and info logs
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

# Add handlers to the logger
# logger.addHandler(log_handler)
logger.addHandler(stderr_handler)
logger.addHandler(stdout_handler)


def clear_log_files():
    """Truncate log files used by battery.service at startup to match systemd paths.
    Uses the current user's home directory to align with the service's User setting.
    """
    try:
        # Match service log locations on Desktop for the current user
        home_dir = os.path.expanduser("~")
        log_dir = os.path.join(home_dir, "Desktop", "Battery_Log")
        stdout_log = os.path.join(log_dir, "battery_log.txt")
        stderr_log = os.path.join(log_dir, "battery_error_log.txt")

        # Ensure directory exists
        os.makedirs(log_dir, exist_ok=True)
        cleared = 0
        for fpath in (stdout_log, stderr_log):
            try:
                # Truncate the file to zero length (create if missing)
                open(fpath, 'w').close()
                cleared += 1
            except Exception as e:
                logger.warning(f"Could not truncate log file {fpath}: {e}")
        if cleared:
            logger.info(f"Cleared {cleared} log file(s) in {log_dir}")
    except Exception as e:
        logger.warning(f"Log cleanup exception: {e}")


robot = RobotController()
LOW_BATTERY_TRESH = 11
USB_VOLTAGE = 5
CHECK_INTERVAL = 30

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


# Graceful shutdown handler
# systemd sends SIGTERM when you run: `systemctl stop battery.service`.
# This handler exits the program immediately so that the `finally:` block below
# can run and clean up hardware (clear OLED, stop buzzer, log shutdown, etc.).
#
# signum: the signal number (SIGTERM)
# frame:  current stack frame (unused here)
def handle_sigterm(signum, frame):
    sys.exit(0)

# Register the handler so the script can exit cleanly when stopped by systemd
signal.signal(signal.SIGTERM, handle_sigterm) 

def battery_checker(battery_stat):
        if USB_VOLTAGE < battery_stat <= LOW_BATTERY_TRESH:
            logger.warning(f"Battery Low Voltage detected: {battery_stat}")
            disp.fill(0)
            disp.show()
            # Clear the image buffer to avoid overlapping text
            draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
            draw.text((0, 10), "LOW BATTERY!", font=font, fill=255)
            draw.text((0, 20), "ROBOT WILL SHUTDOWN", font=font, fill=255)
            draw.text((0, 30), "AT 10.5V", font=font, fill=255)
            disp.image(image)
            disp.show()
            time.sleep(5)
            for i in range(5):
                robot.play_tone(2000, 1)
                disp.fill(0)
                disp.show()
                time.sleep(0.2)
                # Clear the image buffer before drawing the next frame
                # Invert visuals for attention
                draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=255)
                draw.text((30, 30), "LOW BATTERY!", font=font, fill=0)
                disp.image(image)
                disp.show()
                # time.sleep(1)
            robot.cleanup_buzzer()
            # time.sleep(CHECK_INTERVAL)
            if USB_VOLTAGE < battery_stat <= 10.5: 
                for i in range(5): 
                    logger.warning(f"Shutting down due to low battery: {battery_stat}")
                    disp.fill(0)
                    disp.show()
                    # Clear the image buffer before drawing the next frame
                    # Invert visuals for attention
                    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=255)
                    # Split into two lines to avoid any missing-space rendering issues
                    draw.text((10, 20), "PLEASE", font=font, fill=0)
                    draw.text((10, 35), "RECHARGE!", font=font, fill=0)
                    draw.text((10, 50), f"VOLTAGE: {battery_stat}V", font=font, fill=0)
                    disp.image(image)
                    disp.show()
                    time.sleep(10)
                # Use passwordless sudo with absolute path for reliability under systemd
                os.system("sudo -n /usr/sbin/shutdown -h now")
        elif battery_stat <= USB_VOLTAGE:
            logger.warning(f"USB Voltage detected: {battery_stat}")
            # Clear the image buffer before drawing USB warning
            draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
            draw.text((0, 10), "USB Voltage detected", font=font, fill=255)
            draw.text((0, 20), f"VOLTAGE: {battery_stat}", font=font, fill=255)
            draw.text((0, 30), "CAUTION!", font=font, fill=255)
            draw.text((0, 40), "DO NOT START ", font=font, fill=255)
            draw.text((0, 50), "MOTOR!", font=font, fill=255)
            disp.image(image)
            disp.show()
        else:
            Display_battery(battery_stat)
            # time.sleep(1)


def main():
    global font
    # Clear existing log files at startup
    clear_log_files()
    logger.debug("\n\n")
    logger.debug("/--------------------------/")
    logger.debug("-------Script Started-------")
    logger.debug("/--------------------------/")

    robot.play_tone(1000, 0.5)
    time.sleep(0.2)
    robot.play_tone(1000, 0.5)
    robot.cleanup_buzzer()
    while True: 
        try:
            battery_stat = robot.get_battery()  
            battery_checker(battery_stat)
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Failed to read battery or update display: {e}")
        
        time.sleep(CHECK_INTERVAL)
            

try:
    if __name__ == '__main__':
        main() 

except KeyboardInterrupt:
    robot.cleanup()  
    disp.fill(0)
    disp.show() 
    logger.warning("Program Exit: User Interupt")
except Exception as e:
    logger.error(f"An error occurred: {e}") 

finally:
    disp.fill(0)
    disp.show() 
    logger.info("Script Ended")
    exit()
