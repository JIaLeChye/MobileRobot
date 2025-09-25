# MobileRobot 🤖

[![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)](./version.py)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204%2F5-red.svg)](https://raspberrypi.org)


A comprehensive mobile robot control system designed for Raspberry Pi 4/5 with advanced computer vision, autonomous navigation, and remote control capabilities.
## 📋 Table of Contents
- [🚀 Features](#-features)
- [⚡ Quick Start](#-quick-start)
- [📁 Repository Structure](#-repository-structure)
- [🔧 Installation](#-installation)
- [📱 User Applications](#-user-applications)
- [📚 Libraries](#-libraries)
- [📖 Version Control & Changelog](#-version-control--changelog)
- [📖 Documentation](#-documentation)
- [📞 Support](#-support)

## 🚀 Features

### Core Functionality
- **Motor Control**: Precise 4-wheel mecanum drive control with enhanced encoder feedback and calibration
- **Computer Vision**: Object tracking, recognition, and QR/AprilTag detection with automatic model downloads
- **Autonomous Navigation**: Line following and obstacle avoidance
- **Remote Control**: Mobile app integration via Blynk platform
- **Sensor Integration**: Ultrasonic, IR, line sensors, and camera
- **Real-time Monitoring**: OLED display and advanced battery management system

### Advanced Capabilities
- **Hand Gesture Control**: OpenCV-based gesture recognition
- **TensorFlow Integration**: Object detection and classification with automatic setup
- **Multiple Navigation Modes**: Sensor-based and vision-based navigation
- **Hardware Abstraction**: Clean API for all robot functions
- **Automatic Setup**: Self-downloading models and configuration files
- **Per-Motor Calibration**: Individual motor tuning for improved accuracy


## ⚡ Quick Start

### 📥 Download & Setup

1. **Download the repository**:
   ```bash
   git clone https://github.com/JIaLeChye/MobileRobot.git
   cd MobileRobot
   ```

2. **Run the automatic setup**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   
   This script will:
   - ✅ Install all required Python packages
   - ✅ Set up the robot control libraries
   - ✅ Configure hardware interfaces
   - ✅ Test the installation

### 🎮 Explore the Examples

After setup, you can run any example directly:

```bash
# Motor control basics
cd Motor_and_Encoder
python3 Motor_and_Encoder.py

# Line following with camera
cd Line_Following/With_OpenCV
python3 Line_Following.py

# Object tracking
cd Object_Tracking/Color_Based
python3 Color_Based_Tracking.py

# Remote control via mobile app
cd Mobile_Controller/Mobile_Controller
python3 Mobile_Controller.py
```

### 🔧 Customization
All examples are designed to be easily modified:
1. Open any Python file in your favorite editor
2. Modify parameters, thresholds, or behavior
3. Run the modified code to see changes

### 🆘 Need Help?

1. Check the jupyter notebook in each folder
2. Look at the code comments for explanations
3. Start with simple examples before complex ones
4. Use the Libraries/ folder to understand core functions

## 📁 Repository Structure

The repository is organized by functionality to make it easy to explore:

```
MobileRobot/
├── 📖 README.md                    # This file - start here!
├── ⚡ setup.sh                     # One-click installation script
├── � reset.sh                     # System reset and cleanup script
├── 🧪 self-test.py                 # Hardware validation and testing
├── ⚙️ Encoder_Calibration.py       # Motor encoder calibration utility
├── �📋 requirements.txt             # Python dependencies
├── 📊 version.py                   # Version management and information
│
├── 🚗 Motor_and_Encoder/           # Basic motor control with encoders
├── 🎯 Line_Following/              # Line following algorithms
│   ├── With_OpenCV/                # Vision-based line following
│   └── With_Sensors/               # Sensor-based line following
├── 🚧 Obstacle_Avoidance/          # Obstacle detection and avoidance
│   ├── with_camera/                # Vision-based avoidance
│   └── without_camera/             # Sensor-based avoidance
├── 👁️ Object_Tracking/             # Object detection and tracking
│   ├── Color_Based/                # Color-based tracking
│   └── KCF_Tracler/                # Advanced KCF tracking algorithms
├── 🎯 Object_Tracking_with_Avoidance/ # Combined tracking and navigation
├── 🤖 Object-Recofnition(TF)/      # TensorFlow object recognition
├── 🤖 Object-Recognition(TFLite)/  # TensorFlow Lite object recognition
├── 📱 Mobile_Controller/           # Remote control via mobile app
│   ├── Mobile_Controller/          # Basic mobile control
│   └── With_Obstacle_Alert/        # Enhanced control with obstacle detection
├── 👋 Hand-Gesture/                # Gesture-based control
├── 🏷️ April_Tag_Recognition/       # AprilTag detection and tracking
├── 📷 QR_Code_Recognition/         # QR code detection
├── 🎨 HSV_Color_Picker/            # Color calibration tool
├── 🔋 BMS/                         # Battery management system
│
└── 📚 Libraries/                   # Core robot libraries
    ├── RPi_Robot_Hat_Lib/          # Main robot control library
    ├── Ultrasonic_Sensor/          # Distance sensor library
    └── IR_Sensor/                  # Infrared sensor library
```

### 🎯 How to Use This Repository

1. **🚀 Start with setup.sh** - Installs everything automatically
2. **📚 Check Libraries/** - Core functionality for all applications  
3. **🎮 Explore Applications** - Each folder contains working examples
4. **📖 Read Documentation** - Each folder has its own README
5. **🔧 Customize** - Modify examples for your specific needs


## 🔧 Installation

### Automated Setup (Recommended)
The `setup.sh` script automatically installs all dependencies and configures your Raspberry Pi:

```bash
# Download and run setup
wget https://raw.githubusercontent.com/JIaLeChye/MobileRobot/master/setup.sh
chmod +x setup.sh
./setup.sh
```

### Manual Installation
<details>
<summary>Click to expand manual installation steps</summary>

1. **Update system**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install system dependencies**:
   ```bash
   sudo apt install -y python3-pip python3-venv i2c-tools git cmake build-essential
   ```

3. **Enable hardware interfaces**:
   ```bash
   sudo raspi-config nonint do_i2c 0
   sudo raspi-config nonint do_camera 0
   ```

4. **Install Python packages**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Install robot library**:
   ```bash
   cd RPi_Robot_Hat_Lib
   pip install .
   ```
</details>

## 📱 User Applications

### Navigation & Control
| Application | Description | Hardware Required |
|-------------|-------------|-------------------|
| **Line_Following** | Autonomous line following with OpenCV and sensors | Camera, Line sensors |
| **Obstacle_Avoidance** | Autonomous navigation with obstacle detection | Ultrasonic sensors |
| **Mobile_Controller** | Remote control via smartphone app | Blynk platform |
| **Hand_Gesture** | Gesture-based robot control | Camera |

### Computer Vision
| Application | Description | Hardware Required |
|-------------|-------------|-------------------|
| **Object_Tracking** | Real-time object tracking and following | Camera |
| **Object_Recognition** | TensorFlow-based object detection | Camera |
| **QR_Code_Recognition** | QR code detection and processing | Camera |
| **April_Tag_Recognition** | AprilTag detection for navigation | Camera |

### Utilities
| Application | Description | Hardware Required |
|-------------|-------------|-------------------|
| **Motor_and_Encoder** | Motor control and encoder testing | Motors, Encoders |
| **HSV_Color_Picker** | Color calibration tool for vision | Camera |
| **BMS** | Battery monitoring system | Battery sensor |

## 📚 Libraries

### Core Libraries
- **RPi_Robot_Hat_Lib**: Main robot control library
- **Ultrasonic_Sensor**: Distance measurement and obstacle detection
- **IR_Sensor**: Infrared obstacle detection
- **Motor_Encoder**: Precise motor control with encoder feedback

### Dependencies
- **OpenCV**: Computer vision and image processing
- **TensorFlow**: Machine learning and object recognition
- **Blynk**: Mobile app connectivity
- **Adafruit Libraries**: Hardware interfacing (OLED, PCA9685)

### Coding Standards
- Follow PEP 8 for Python code
- Include docstrings for all functions
- Test on hardware before submitting
- Update documentation as needed

## 📖 Version Control & Changelog

This project follows [Semantic Versioning](https://semver.org/) with **automatic version management**:
- **Major.Minor.Patch** (e.g., 1.2.3)

### 🆕 Recent Updates (Version 2.1.0)

#### New Features & Improvements
- **🤖 Enhanced Object Recognition**: Added automatic model and label file download functionality
  - **TensorFlow Lite**: `download_if_missing()` and `ensure_dir_exists()` functions for automatic model setup
  - **TensorFlow (Full)**: `ensure_model_present()` and `ensure_label_map_present()` functions
  - **Auto-Download**: Missing model files are automatically downloaded from GitHub repositories
  - **Robust Error Handling**: Better error messages and fallback mechanisms for network issues

- **⚙️ Enhanced Motor Control**: Improved motor calibration and distance tracking
  - **Per-Motor Calibration**: Individual motor calibration data storage in `~/.config/mobile_robot/`
  - **Encoder Calibration Tool**: New `Encoder_Calibration.py` for precise distance measurements
  - **Improved Accuracy**: Better encoder handling and distance calculations

- **🔋 Battery Management System**: Enhanced monitoring and logging capabilities
  - **Advanced Logging**: Structured logging system with timestamps and function names
  - **System Service**: Battery monitoring can run as a systemd service
  - **OLED Display**: Real-time battery status display integration

- **🛠️ Development Improvements**: Better testing and validation
  - **Enhanced Self-Test**: Improved camera and I2C device testing
  - **OpenCV Integration**: Better camera testing with OpenCV functionality
  - **Error Detection**: More comprehensive hardware validation

### Current Library Versions
- **RPi_Robot_Hat_Lib**: 1.2.16
- **Ultrasonic_sens**: 1.0.4
- **IRSens**: 1.0.4


### Files Managed
- `Libraries/RPi_Robot_Hat_Lib/RPi_Robot_Hat_Lib.py` - Main library with version string
- `Libraries/RPi_Robot_Hat_Lib/setup.py` - Package setup with version
- `Libraries/Ultrasonic_Sensor/setup.py` - Sensor library setup
- `Libraries/IR_Sensor/setup.py` - IR sensor library setup
-

### Benefits
- **No manual version tracking** - Automatic patch increments
- **Consistent versioning** - All related files stay in sync  
- **Git integration** - Works seamlessly with your workflow
- **Flexible control** - Manual override for major/minor versions
- **Clear history** - Version changes are tracked in Git commits

### Current Version: 2.1.0
- ✅ **Automatic Model Downloads**: Object recognition systems now automatically download required files
- ✅ **Enhanced Motor Calibration**: Per-motor calibration with improved accuracy
- ✅ **Advanced Battery Monitoring**: Comprehensive logging and system service integration
- ✅ **Improved Testing**: Enhanced self-test capabilities with camera and I2C validation
- ✅ Raspberry Pi 5 compatibility
- ✅ Enhanced setup automation
- ✅ Comprehensive self-check system
- ✅ Modern camera library support

## 📖 Documentation

### 📚 Interactive Jupyter Notebooks
Each application includes comprehensive documentation with code explanations, usage examples, and step-by-step tutorials:

#### Core Applications
- **🚗 [Motor & Encoder Control](./Motor_and_Encoder/Motor_and_Encoder.ipynb)** - Basic motor control and encoder usage
- **🔋 [Battery Management System](./BMS/Battery.ipynb)** - Power monitoring and management
- **🔋 [Battery Service Setup](./BMS/battery.service.ipynb)** - System service configuration

#### Navigation & Autonomous Control
- **🎯 [Line Following (OpenCV)](./Line_Following/With_OpenCV/Line_Following.ipynb)** - Vision-based line following
- **🎯 [Line Following (Sensors)](./Line_Following/With_Sensors/Line_Following.ipynb)** - Sensor-based line following
- **🚧 [Obstacle Avoidance (Camera)](./Obstacle_Avoidance/with_camera/Obstacle_Avoidance.ipynb)** - Vision-based navigation
- **🚧 [Obstacle Avoidance (Sensors)](./Obstacle_Avoidance/without_camera/Obstacle_Avoidance.ipynb)** - Sensor-based navigation

#### Computer Vision & Recognition
- **🤖 [Object Recognition (TensorFlow)](./Object-Recofnition(TF)/Object_Recognition(tensor_Flow).ipynb)** - Full TensorFlow object detection
- **🤖 [Object Recognition (TensorFlow Lite)](./Object-Recognition(TFLite)/Object_Recognition_with_TFLite.ipynb)** - Lightweight object detection
- **👁️ [Object Tracking (Color-Based)](./Object_Tracking/Color_Based/Object_tracking.ipynb)** - Color-based object tracking
- **👁️ [Object Tracking (KCF)](./Object_Tracking/KCF_Tracler/Object_tracking.ipynb)** - Advanced KCF tracking algorithm
- **📷 [QR Code Recognition](./QR_Code_Recognition/QR_Recognition.ipynb)** - QR code detection and processing
- **🏷️ [AprilTag Recognition](./April_Tag_Recognition/April-Tag_Recognition.ipynb)** - AprilTag detection for navigation
- **👋 [Hand Gesture Control](./Hand-Gesture/Hand_gesture.ipynb)** - Gesture-based robot control
- **🎨 [HSV Color Picker](./HSV_Color_Picker/HSV_Color_Picker.ipynb)** - Color calibration tool

#### Remote Control & Mobile Integration
- **📱 [Mobile Controller](./Mobile_Controller/Mobile_Controller/Mobile_Controller_V2.ipynb)** - Smartphone remote control
- **📱 [Mobile Controller with Obstacle Alert](./Mobile_Controller/With_Obstacle_Alert/Mobile_Controller_With_Obstacle_Alert.ipynb)** - Enhanced mobile control

#### Advanced Applications
- **🎯 [Object Tracking with Avoidance](./Object_Tracking_with_Avoidance/Object_Tracking_with%20Avoidance.ipynb)** - Combined tracking and navigation

#### Library Documentation
- **📚 [RPi Robot Hat Library](./Libraries/RPi_Robot_Hat_Lib/RPi_Robot_Hat_Lib.ipynb)** - Main robot control library
- **📚 [RPi Robot Hat API Reference](./Libraries/RPi_Robot_Hat_Lib/RPi_Robot_Hat_Lib_API.ipynb)** - Complete API documentation
- **📏 [Ultrasonic Sensor Library](./Libraries/Ultrasonic_Sensor/Ultrasonic_sens.ipynb)** - Distance measurement library
- **🔍 [IR Sensor Library](./Libraries/IR_Sensor/IRSens.ipynb)** - Infrared detection library

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JIaLeChye/MobileRobot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/JIaLeChye/MobileRobot/discussions)
- **Wiki**: [Project Wiki](https://github.com/JIaLeChye/MobileRobot/wiki)