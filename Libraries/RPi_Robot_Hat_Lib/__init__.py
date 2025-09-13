"""
RPi Robot Hat Library
====================

A comprehensive library for controlling Raspberry Pi robot hat with:
- Motor control with encoder feedback
- Sensor integration (ultrasonic, IR, line sensors)
- Servo control
- Battery monitoring
- Buzzer/sound functions
- Autonomous navigation capabilities

Example usage:
    >>> from RPi_Robot_Hat_Lib import RobotController
    >>> robot = RobotController()
    >>> robot.Forward(50)  # Move forward at 50% speed
    >>> robot.stop()       # Stop all motors
"""

from .RPi_Robot_Hat_Lib import RobotController
from .Encoder import *  # If Encoder module exists

Author: JIaLeChye
GitHub: https://github.com/JIaLeChye/MobileRobot
"""

__version__ = "1.2.13"
__author__ = "JIaLeChye"
__email__ = "jialecjl2016@outlook.com"
__license__ = "MIT"

__all__ = ["RobotController"]
