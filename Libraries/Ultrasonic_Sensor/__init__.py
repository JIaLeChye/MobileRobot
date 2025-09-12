"""
Ultrasonic Sensor Library
========================

A library for controlling ultrasonic sensors on Raspberry Pi robots.

Features:
- Distance measurement
- Obstacle detection
- Multiple sensor support
- Averaged readings for accuracy

Example usage:
    >>> from Ultrasonic_sens import Ultrasonic
    >>> sensor = Ultrasonic()
    >>> left, front, right = sensor.distances()
    >>> print(f"Front distance: {front}cm")
"""

from .Ultrasonic_sens import Ultrasonic

__version__ = "1.0.3"
__author__ = "JIaLeChye"
__email__ = "jialecjl2016@outlook.com"
__license__ = "MIT"

__all__ = ["Ultrasonic"]
