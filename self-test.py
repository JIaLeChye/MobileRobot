from RPi_Robot_Hat_Lib  import RobotController
# the oled library 
import adafruit_ssd1306, board
from PIL import Image, ImageDraw, ImageFont 

import time

robot = RobotController()
robot.__version__()

# Mario main theme notes (frequency in Hz, duration in seconds)
mario_theme = [
	(660, 0.1), (660, 0.1), (0, 0.1), (660, 0.1), (0, 0.1), (510, 0.1), (660, 0.1), (0, 0.1), (770, 0.1),
	(0, 0.3), (380, 0.1), (0, 0.3),
	(510, 0.1), (0, 0.2), (380, 0.1), (0, 0.2), (320, 0.1), (0, 0.2), (440, 0.1), (0, 0.1), (480, 0.08), (0, 0.08), (450, 0.08), (0, 0.08), (430, 0.08), (0, 0.1), (380, 0.1), (660, 0.1), (0, 0.1), (760, 0.08), (0, 0.08), (860, 0.08), (0, 0.1), (700, 0.08), (784, 0.08), (0, 0.08), (660, 0.1), (0, 0.1), (520, 0.1), (580, 0.08), (480, 0.08)
]

## OLED Test Function
def oled_test():
	# Initialize I2C interface for OLED
	i2c = board.I2C()
	oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

	# Clear the display
	oled.fill(0)
	oled.show()

	# Create blank image for drawing
	image = Image.new("1", (oled.width, oled.height))
	draw = ImageDraw.Draw(image)

	# Use default PIL font
	try:
		font = ImageFont.load_default()
	except:
		font = None

	# Display "Self-Test" message using PIL
	draw.text((0, 0), "Self-Test", font=font, fill=255)
	draw.text((0, 10), "All Systems", font=font, fill=255)
	draw.text((0, 20), "Operational", font=font, fill=255)

	# Display the image
	oled.image(image)
	oled.show()

	time.sleep(5)

	# Clear the display after showing the message
	oled.fill(0)
	oled.show()

def play_mario_theme(robot):
	for freq, dur in mario_theme:
		if freq == 0:
			time.sleep(dur)
		else:
			robot.play_tone(freq, dur)
			time.sleep(0.05)

## Move Forward Function
def forward_movement():
	robot.Forward( 50)  # Set both motors to move forward at speed 50
	time.sleep(2)  # Move forward for 2 seconds
	robot.stop()  # Stop the motors


try:
	# Play Mario theme
	play_mario_theme(robot)
	oled_test()
	forward_movement()

except Exception as e:
	print("An error occurred:", e)
except KeyboardInterrupt: 
	print("Program stopped by User")
	robot.cleanup()
finally:
	robot.cleanup()
	print("Self-test completed")
