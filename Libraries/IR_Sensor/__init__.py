"""
IR Sensor Library
================

A library for controlling infrared sensors on Raspberry Pi robots.

Features:
- Obstacle detection
- Proximity sensing
- Digital signal processing
- Simple API

Example usage:
    >>> from IRSens import IRsens
    >>> sensor = IRsens()
    >>> status = sensor.status()
    >>> print(f"IR sensor status: {status}")
"""

from .IRSens import IRsens

__version__ = "1.0.2"
__author__ = "JIaLeChye"
__email__ = "jialecjl2016@outlook.com"
__license__ = "MIT"

__all__ = ["IRsens"]
