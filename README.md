# MobileRobot 🤖

[![Version](https://img.shields.io/badge/version-2.0.2-blue.svg)](./version.py)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204%2F5-red.svg)](https://raspberrypi.org)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)

> **Documentation Languages**: [English](README.md) | [中文](使用说明.md)

A comprehensive mobile robot control system designed for Raspberry Pi 4/5 with advanced computer vision, autonomous navigation, and remote control capabilities.

## 🚀 Features

### Core Functionality
- **Motor Control**: Precise 4-wheel mecanum drive control with encoder feedback
- **Computer Vision**: Object tracking, recognition, and QR/AprilTag detection
- **Autonomous Navigation**: Line following and obstacle avoidance
- **Remote Control**: Mobile app integration via Blynk platform
- **Sensor Integration**: Ultrasonic, IR, line sensors, and camera
- **Real-time Monitoring**: OLED display and battery management

### Advanced Capabilities
- **Hand Gesture Control**: OpenCV-based gesture recognition
- **TensorFlow Integration**: Object detection and classification
- **Multiple Navigation Modes**: Sensor-based and vision-based navigation
- **Hardware Abstraction**: Clean API for all robot functions

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Hardware Requirements](#hardware-requirements)
- [User Applications](#user-applications)
- [Libraries](#libraries)
- [Contributing](#contributing)
- [Version Control](#version-control)
- [Documentation](#documentation)

## ⚡ Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/JIaLeChye/MobileRobot.git
   cd MobileRobot
   ```

2. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Test your robot**:
   ```bash
   source venv/bin/activate
   python robot_self_check.py
   ```

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

## 🔌 Hardware Requirements

### Required Components
- **Raspberry Pi 4 or 5** (4GB+ RAM recommended)
- **Raspberry Pi Camera Module** (v2 or v3)
- **4x Geared Motors** with encoders
- **Motor Driver Board** (PCA9685-based)
- **Ultrasonic Sensors** (3x HC-SR04)
- **IR Obstacle Sensor**
- **Line Following Sensors** (5-array)
- **OLED Display** (128x64 SSD1306)
- **Battery Pack** (7.4V Li-Po recommended)

### Optional Components
- **Servo Motors** (2x for camera pan/tilt)
- **Buzzer** for audio feedback
- **IMU Sensor** for orientation tracking

### Wiring Diagram
```
[Include wiring diagram or link to detailed hardware setup]
```

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

## 📖 Version Control

This project follows [Semantic Versioning](https://semver.org/):
- **Major.Minor.Patch** (e.g., 1.2.3)
- See [CHANGELOG.md](./CHANGELOG.md) for release history
- See [RELEASE.md](./RELEASE.md) for release process

### Current Version: 1.0.0
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

---

**Made with ❤️ for the robotics community**
