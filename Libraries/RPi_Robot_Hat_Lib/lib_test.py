from RPi_Robot_Hat_Lib import RobotController
import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

Motor = RobotController()
OLED_addr = 0x3c
i2c = busio.I2C(board.SCL, board.SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=OLED_addr)

# Create an image object for the OLED display
image = Image.new("1", (disp.width, disp.height))  # Create a new image every time
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()


Update_interval = 1

def display_two_motors_data(motor1, motor2):
    """Display data for two motors on top and bottom of the OLED."""
    # Clear the display before updating it
    disp.fill(0)
    disp.show()

    # Get encoder, distance, and RPM for both motors
    encoder1 = Motor.get_encoder(motor1)
    distance1 = abs(Motor.get_distance(motor1))
    rpm1 = abs(Motor.get_rpm(motor1))

    encoder2 = Motor.get_encoder(motor2)
    distance2 = abs(Motor.get_distance(motor2))
    rpm2 = abs(Motor.get_rpm(motor2))

    # Create a new image object for each motor display
    image = Image.new("1", (disp.width, disp.height))
    draw = ImageDraw.Draw(image)

    # Display motor 1 data at the top of the screen
    draw.text((0, 0), f"Motor: {motor1}", font=font, fill=255)
    draw.text((0, 10), f"Dist: {distance1:.2f} cm", font=font, fill=255)
    draw.text((0, 20), f"RPM: {rpm1:.2f} RPM", font=font, fill=255)

    # draw a line in betwen them 
    draw.line((0, 33, 128, 33),width=2, fill=255)
    # Display motor 2 data at the bottom of the screen
    draw.text((0, 35), f"Motor: {motor2}", font=font, fill=255)
    draw.text((0, 45), f"Dist: {distance2:.2f} cm", font=font, fill=255)
    draw.text((0, 55), f"RPM: {rpm2:.2f} RPM ", font=font, fill=255)

    # Update the display
    disp.image(image)
    disp.show()


    print(f"Motor: {motor1}")
    print(f"Encoder: {encoder1}")
    print(f"Distance: {distance1:.2f} cm")
    print(f"RPM: {rpm1:.2f} RPM")
    print
    print(f"Motor: {motor2}")
    print(f"Encoder: {encoder2}")
    print(f"Distance: {distance2:.2f} cm")
    print(f"RPM: {rpm2:.2f} RPM")
    print("\n")


def main():
    print("Program Start")
    Motor.reset_encoders()
    while True:
        Motor.move(30,0)
        # Display two motors' data top and bottom
        display_two_motors_data('RF', 'RB')  # Display data for RF and RB motors
        time.sleep(Update_interval)  # Wait for 1 second

        display_two_motors_data('LF', 'LB')  # Display data for LF and LB motors
        time.sleep(Update_interval)  # Wait for 1 second

try:
    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    Motor.cleanup()
finally:
    Motor.cleanup()
    disp.fill(0)
    disp.show()
