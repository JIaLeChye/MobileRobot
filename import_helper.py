"""
Import helper for MobileRobot applications.

This module provides easy access to the MobileRobot libraries
which are now installed as proper Python packages.

Usage:
    from import_helper import RobotController, Ultrasonic, IRsens
    
    # Or import directly (after setup.sh installation):
    from RPi_Robot_Hat_Lib import RobotController
    from Ultrasonic_sens import Ultrasonic
    from IRSens import IRsens
"""

# Import main classes for easy access
try:
    from RPi_Robot_Hat_Lib import RobotController
except ImportError:
    print("Warning: RPi_Robot_Hat_Lib not installed. Run setup.sh first.")
    RobotController = None

try:
    from Ultrasonic_sens import Ultrasonic
except ImportError:
    print("Warning: Ultrasonic sensor library not installed. Run setup.sh first.")
    Ultrasonic = None

try:
    from IRSens import IRsens
except ImportError:
    print("Warning: IR sensor library not installed. Run setup.sh first.")
    IRsens = None

# Make everything available for wildcard imports
__all__ = ['RobotController', 'Ultrasonic', 'IRsens']
