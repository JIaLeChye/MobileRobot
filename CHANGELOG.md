# Changelog

All notable changes to the MobileRobot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2025-09-08

### Added
- Raspberry Pi 5 compatibility with rpi-lgpio library
- picamera2 support for Pi 5 camera functionality
- Comprehensive `robot_self_check.py` for hardware diagnostics
- `import_helper.py` for centralized library imports
- Enhanced setup.sh script with Pi 5 detection and configuration
- **Proper Python package installation** - Libraries now install as system-wide packages
- **Automated versioning** - GitHub Actions automatically manage releases
- Automatic setup.py creation for sensor libraries
- Import testing in setup script
- OLED display integration for test results
- Battery monitoring in self-check system
- Git version control with proper .gitignore configuration

### Changed
- **BREAKING**: Migrated from RPi.GPIO to rpi-lgpio (Pi 5 requirement)
- **BREAKING**: Updated from picamera to picamera2 (Pi 5 requirement)
- Centralized library structure - removed duplicate files
- Updated dependencies to Python 3.8+ minimum
- Improved error handling in hardware initialization

### Removed
- 18 duplicate and obsolete files including:
  - Multiple copies of RPi_Robot_Hat_Lib.py across application folders
  - Old test files: boot_self_test.py, complete_self_test.py
  - Obsolete service files and installation scripts
  - Individual component test scripts

### Fixed
- GPIO compatibility issues with Raspberry Pi 5
- Camera initialization problems on newer Pi models
- Dependency conflicts in setup process
- Import path issues across application folders

## [1.x] - Legacy Versions
### Added
- Enhanced setup.sh script for Raspberry Pi 5 compatibility
- Comprehensive robot self-check script (robot_self_check.py)
- Support for picamera2 library for Raspberry Pi 5
- Virtual environment support in setup script
- GPIO permission configuration
- I2C and camera interface auto-enablement

### Changed
- Updated GPIO library from RPi.GPIO to rpi-lgpio for Pi 5 compatibility
- Improved error handling in setup script
- Enhanced documentation and setup instructions

### Fixed
- GPIO compatibility issues with Raspberry Pi 5
- Camera interface support for modern Pi systems
- I2C permission and access issues

## [1.0.0] - 2025-09-08

### Added
- Initial release of MobileRobot project
- Core robot control library (RPi_Robot_Hat_Lib)
- Motor control and encoder reading functionality
- Line following capabilities (OpenCV and sensor-based)
- Object tracking and recognition features
- Obstacle avoidance algorithms
- Mobile controller integration with Blynk
- Hand gesture control
- QR code and April tag recognition
- Battery management system
- Ultrasonic sensor library
- IR sensor library
- OLED display support
- Multiple example applications and demos

### Libraries Included
- RPi_Robot_Hat_Lib - Core robot control
- Ultrasonic_Sensor - Distance measurement
- IR_Sensor - Infrared obstacle detection
- Motor_Encoder - Precise movement control

### Applications
- April_Tag_Recognition - Computer vision tag detection
- Hand-Gesture - Gesture-based robot control
- Line_Following - Autonomous line following
- Mobile_Controller - Remote control via mobile app
- Object_Tracking - Visual object tracking
- Object-Recognition - TensorFlow-based object detection
- Obstacle_Avoidance - Autonomous navigation
- QR_Code_Recognition - QR code detection and processing
- HSV_Color_Picker - Color calibration tool
