"""
MobileRobot Version Information
This file is automatically updated by GitHub Actions.
"""

__version__ = "2.0.4"
__author__ = "JiaLeChye"
__description__ = "Mobile Robot Control System for Raspberry Pi"
__url__ = "https://github.com/JIaLeChye/MobileRobot"

def get_version():
    """Return the current version string."""
    return __version__

def print_version():
    """Print version information."""
    print(f"MobileRobot v{__version__}")
    print(f"Author: {__author__}")
    print(f"Repository: {__url__}")

if __name__ == "__main__":
    print_version()
