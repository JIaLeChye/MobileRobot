# MobileRobot 🤖

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](./version.py)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204%2F5-red.svg)](https://raspberrypi.org)


A comprehensive mobile robot control system designed for Raspberry Pi 4/5 with advanced computer vision, autonomous navigation, and remote control capabilities.

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

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Repository Structure](#repository-structure)
- [Hardware Requirements](#hardware-requirements)
- [User Applications](#user-applications)
- [Libraries](#libraries)
- [Contributing](#contributing)
- [Documentation](#documentation)

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

### 📚 Understanding the Code

- **Libraries/**: Core robot functionality - start here to understand the basics
- **Examples/**: Each folder contains working examples with specific features
- **Documentation**: Each folder has its own README with detailed explanations

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
├── 📋 requirements.txt             # Python dependencies
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
│   └── KCF_Tracker/                # Advanced tracking algorithms
├── 🤖 Object-Recognition(TF)/      # TensorFlow object recognition
├── 📱 Mobile_Controller/           # Remote control via mobile app
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

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](./CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and test thoroughly
4. Submit a pull request

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

#### Current Library Versions
- **RPi_Robot_Hat_Lib**: 1.2.14
- **Ultrasonic_sens**: 1.0.4
- **IRSens**: 1.0.4

#### Example Workflow
```bash
# Regular development (automatic versioning)
git add Libraries/RPi_Robot_Hat_Lib/RPi_Robot_Hat_Lib.py
git commit -m "Fix encoder filtering bug"
# ✅ Version automatically bumped: 1.2.2 → 1.2.3

# Major feature release (manual versioning)
./bump_version.sh major RPi_Robot_Hat_Lib
git add .
git commit -m "Major update: Add new movement algorithms"
# ✅ Version manually bumped: 1.2.3 → 2.0.0
```

#### Files Managed
- `Libraries/RPi_Robot_Hat_Lib/RPi_Robot_Hat_Lib.py` - Main library with version string
- `Libraries/RPi_Robot_Hat_Lib/setup.py` - Package setup with version
- `Libraries/Ultrasonic_Sensor/setup.py` - Sensor library setup
- `Libraries/IR_Sensor/setup.py` - IR sensor library setup
- `.git/hooks/pre-commit` - Automatic version detection hook
- `bump_version.sh` - Manual version management script

#### Benefits
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

### Getting Started
- [Hardware Setup Guide](./docs/hardware-setup.md)
- [Software Installation](./docs/installation.md)
- [First Run Tutorial](./docs/first-run.md)

### API Reference
- [RPi_Robot_Hat_Lib API](./docs/api-reference.md)
- [Sensor Libraries](./docs/sensors.md)
- [Examples and Tutorials](./docs/examples.md)

### Troubleshooting
- [Common Issues](./docs/troubleshooting.md)
- [Hardware Debugging](./docs/hardware-debug.md)
- [Performance Optimization](./docs/optimization.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- Raspberry Pi Foundation for the amazing platform
- OpenCV community for computer vision tools
- Adafruit for excellent hardware libraries
- TensorFlow team for machine learning capabilities

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JIaLeChye/MobileRobot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/JIaLeChye/MobileRobot/discussions)
- **Wiki**: [Project Wiki](https://github.com/JIaLeChye/MobileRobot/wiki)