# MobileRobot

[![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)](./version.py)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204%2F5-red.svg)](https://raspberrypi.org)


## Features

### Core Functionality
- Motor control with encoder feedback
- Computer vision: object tracking, recognition, QR and AprilTag detection
- Autonomous navigation: line following and obstacle avoidance
- Remote control via Blynk mobile app
- Sensor integration: ultrasonic, IR, line sensors, and camera
- OLED display and battery management

### Additional Capabilities
- Hand gesture control (OpenCV-based)
- TensorFlow and TensorFlow Lite object detection
- Multiple navigation modes (sensor and vision based)

## Table of Contents
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Repository Structure](#repository-structure)
- [User Applications](#user-applications)
- [Libraries](#libraries)
- [Documentation](#documentation)
- [Maintenance & Diagnostics](#maintenance--diagnostics)
- [Release Notes](#release-notes)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/JIaLeChye/MobileRobot.git
   cd MobileRobot
   ```
2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. Example usage:
   ```bash
   cd Motor_and_Encoder
   python3 Motor_and_Encoder.py
   ```

## Repository Structure

```
MobileRobot/
├── README.md                     # Project documentation
├── setup.sh                      # Installation script
├── reset.sh                      # Reset / cleanup script
├── requirements.txt              # Python dependencies
├── version.py                    # Project version info
├── self-test.py                  # Hardware/self test script
├── Encoder_Calibration.py        # Encoder calibration utility
├── Motor_and_Encoder/            # Motor control and encoder examples
├── Line_Following/               # Line following (OpenCV / sensors)
│   ├── With_OpenCV/
│   └── With_Sensors/
├── Obstacle_Avoidance/           # Obstacle avoidance examples
│   ├── with_camera/
│   └── without_camera/
├── Object_Tracking/              # Object tracking (color, KCF)
│   ├── Color_Based/
│   └── KCF_Tracler/              # (typo in folder name; intended: KCF_Tracker)
├── Object-Recofnition(TF)/       # TensorFlow object recognition (folder name typo)
├── Object-Recognition(TFLite)/   # TensorFlow Lite object recognition
├── Object_Tracking_with_Avoidance/ # Tracking combined with avoidance
├── Mobile_Controller/            # Remote control via mobile app
├── Hand-Gesture/                 # Gesture control
├── April_Tag_Recognition/        # AprilTag detection
├── QR_Code_Recognition/          # QR code detection
├── HSV_Color_Picker/             # Color calibration tool
├── BMS/                          # Battery management system
├── Libraries/                    # Core libraries
│   ├── RPi_Robot_Hat_Lib/
│   ├── Ultrasonic_Sensor/
│   └── IR_Sensor/
└── RepoUpdater/                  # (utility / maintenance, optional to document)
```

Note: Folder names with typos (e.g. `Object-Recofnition(TF)`, `KCF_Tracler`) are shown exactly as they exist. Rename them for clarity if you update scripts that reference them.


## Installation

### Automated Setup (Recommended)
Run the provided setup script to install all dependencies and configure your Raspberry Pi:
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Installation
1. Update system:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
2. Install dependencies:
   ```bash
   sudo apt install -y python3-pip python3-venv i2c-tools git cmake build-essential
   ```
3. Enable hardware interfaces:
   ```bash
   sudo raspi-config nonint do_i2c 0
   sudo raspi-config nonint do_camera 0
   ```
4. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Install robot library:
   ```bash
   cd Libraries/RPi_Robot_Hat_Lib
   pip install .
   ```

## User Applications

### Navigation & Control
| Application           | Description                                 | Hardware Required         |
|----------------------|---------------------------------------------|--------------------------|
| Line_Following       | Line following (OpenCV/sensor-based)        | Camera, Line sensors     |
| Obstacle_Avoidance   | Obstacle detection and avoidance            | Ultrasonic sensors       |
| Mobile_Controller    | Remote control via smartphone app           | Blynk platform           |
| Hand_Gesture         | Gesture-based robot control                 | Camera                   |

### Computer Vision
| Application           | Description                                 | Hardware Required         |
|----------------------|---------------------------------------------|--------------------------|
| Object_Tracking      | Real-time object tracking                   | Camera                   |
| Object_Recognition   | Object detection (TensorFlow/TFLite)        | Camera                   |
| QR_Code_Recognition  | QR code detection and processing            | Camera                   |
| April_Tag_Recognition| AprilTag detection for navigation           | Camera                   |

### Utilities
| Application           | Description                                 | Hardware Required         |
|----------------------|---------------------------------------------|--------------------------|
| Motor_and_Encoder    | Motor control and encoder testing           | Motors, Encoders         |
| HSV_Color_Picker     | Color calibration tool                      | Camera                   |
| BMS                  | Battery monitoring system                   | Battery sensor           |
| RepoUpdater          | Automated repository update utility         | None                     |

## Libraries

### Core Libraries
- RPi_Robot_Hat_Lib: Main robot control library
- Ultrasonic_Sensor: Distance measurement and obstacle detection
- IR_Sensor: Infrared obstacle detection

### Maintenance / Services
- BMS: Battery management system (monitoring, logging, optional service)
- RepoUpdater: Automated repository update helper (script + optional systemd service)

### Main Dependencies
- OpenCV: Computer vision and image processing
- TensorFlow/TensorFlow Lite: Machine learning and object recognition
- Blynk: Mobile app connectivity
- Adafruit libraries: Hardware interfacing

## Version Control

This project uses [Semantic Versioning](https://semver.org/): Major.Minor.Patch (e.g., 1.2.3)

### Library Versions

Current library versions (auto-managed by the workflow `library-version-updater.yml`). Do not manually edit the version numbers on the lines below—automation searches for the pattern `**Name**: x.y.z` and patches them when source files change.

**RPi_Robot_Hat_Lib**: 1.2.16  
**Ultrasonic_Sensor**: 1.0.4  
**IR_Sensor**: 1.0.4  

Legacy module filenames referenced in code:
- `Ultrasonic_sens.py` (main implementation file inside `Ultrasonic_Sensor`)
- `IRSens.py` (main implementation file inside `IR_Sensor`)

If you bump MINOR or MAJOR versions manually, ensure consistency across:
1. The library's `setup.py` `version=` field
2. Any `self.lib_ver` or `__version__` attributes inside the main Python module
3. These README lines (only if automation is not triggered)

Patch bumps (third digit) are automatic when meaningful library `.py` files change.

## Documentation
Primary reference materials are provided as Jupyter notebooks within the repository. Open them in JupyterLab, VS Code, or `jupyter notebook`.

### Core Systems
- Motor & Encoder: `Motor_and_Encoder/Motor_and_Encoder.ipynb`
- Battery Management: `BMS/Battery.ipynb`
- Battery Service Setup: `BMS/battery.service.ipynb`

### Navigation
- Line Following (OpenCV): `Line_Following/With_OpenCV/Line_Following.ipynb`
- Line Following (Sensors): `Line_Following/With_Sensors/Line_Following.ipynb`
- Obstacle Avoidance (Camera): `Obstacle_Avoidance/with_camera/Obstacle_Avoidance.ipynb`
- Obstacle Avoidance (Sensors): `Obstacle_Avoidance/without_camera/Obstacle_Avoidance.ipynb`

### Vision & Recognition
- Object Recognition (TensorFlow): `Object-Recofnition(TF)/Object_Recognition(tensor_Flow).ipynb`
- Object Recognition (TensorFlow Lite): `Object-Recognition(TFLite)/Object_Recognition_with_TFLite.ipynb`
- Object Tracking (Color-Based): `Object_Tracking/Color_Based/Object_tracking.ipynb`
- Object Tracking (KCF): `Object_Tracking/KCF_Tracler/Object_tracking.ipynb`
- Object Tracking with Avoidance: `Object_Tracking_with_Avoidance/Object_Tracking_with Avoidance.ipynb`
- AprilTag Recognition: `April_Tag_Recognition/April-Tag_Recognition.ipynb`
- QR Code Recognition: `QR_Code_Recognition/QR_Recognition.ipynb`

### Interaction & Control
- Mobile Controller: `Mobile_Controller/Mobile_Controller/Mobile_Controller_V2.ipynb`
- Mobile Controller (Obstacle Alert): `Mobile_Controller/With_Obstacle_Alert/Mobile_Controller_With_Obstacle_Alert.ipynb`
- Hand Gesture Control: `Hand-Gesture/Hand_gesture.ipynb`

### Tools
- HSV Color Picker: `HSV_Color_Picker/HSV_Color_Picker.ipynb`

### Libraries & APIs
- Robot Hat Library Overview: `Libraries/RPi_Robot_Hat_Lib/RPi_Robot_Hat_Lib.ipynb`
- Robot Hat Library API Reference: `Libraries/RPi_Robot_Hat_Lib/RPi_Robot_Hat_Lib_API.ipynb`
- Ultrasonic Sensor Library: `Libraries/Ultrasonic_Sensor/Ultrasonic_sens.ipynb`
- IR Sensor Library: `Libraries/IR_Sensor/IRSens.ipynb`
  
### Update Utility
- RepoUpdater (script/service): `RepoUpdater/updater.py` (automated pull/update if integrated as a systemd service `MCupdater.service`)

Each notebook contains runnable examples and explanations of parameters, expected inputs, and outputs.

## Maintenance & Diagnostics

Utilities supporting verification, calibration, version tracking, and automated updates.

### Self-Test (`self-test.py`)
Runs a basic hardware validation (I2C bus, expected device presence, optional camera open test).
Run:
```bash
python3 self-test.py
```

### Version (`version.py` and library version)
`version.py` holds the project version. The control library exposes its version via `RobotController().__version__()`:
```bash
python3 -c "from Libraries.RPi_Robot_Hat_Lib.RPi_Robot_Hat_Lib import RobotController; RobotController().__version__()"
```

### Encoder Calibration (`Encoder_Calibration.py`)
Generates a calibration factor stored at `~/.config/mobile_robot/calibration.json` to improve distance accuracy.
Procedure:
```bash
python3 Encoder_Calibration.py
```
Follow the prompts, measure actual travel, and re-run after mechanical changes.

### RepoUpdater (`RepoUpdater/updater.py`)
Optional pull/update helper. Manual run:
```bash
python3 RepoUpdater/updater.py
```
Optional service setup:
```bash
sudo cp RepoUpdater/MCupdater.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable MCupdater.service
sudo systemctl start MCupdater.service
```
Check / disable:
```bash
systemctl status MCupdater.service
sudo systemctl disable --now MCupdater.service
```

### Battery Management System (BMS)
Monitors voltage and related metrics. See notebooks in `BMS/` for logic and (if present) service workflow.

## Release Notes

### 2.2.0 (Current)
- Added Maintenance & Diagnostics section (self-test, calibration, updater, BMS)
- Added structured documentation section linking all notebooks
- Refined README to a professional format (removed excessive styling/emojis)
- Updated repository structure section to reflect actual filesystem
- Clarified feature scope and removed non-existent claims

### 2.0.0
- Introduced Raspberry Pi 5 compatibility adjustments
- Improved setup automation script (`setup.sh`)
- Added self-test script for hardware validation
- Added encoder calibration utility (`Encoder_Calibration.py`)

### 1.9.x
- Added TensorFlow Lite object recognition examples
- Expanded AprilTag and QR code recognition modules
- Improved motor distance handling and encoder stability

### 1.8.x
- Added gesture control module (OpenCV-based)
- Added color-based and KCF tracking examples
- Introduced HSV color picker calibration tool

### 1.7.x
- Added battery management system (logging + monitoring)
- Added mobile controller with obstacle alert variation
- OLED display integration improvements

### 1.6.x
- Initial integration of TensorFlow object recognition
- Line following (sensor vs OpenCV) separated into distinct modules

### 1.5.x and earlier
- Core motor control and encoder feedback
- Base ultrasonic and IR sensor libraries
- Initial project scaffolding and example scripts

---
If a change is missing or inaccurate, update this section alongside functional commits to keep users informed.

