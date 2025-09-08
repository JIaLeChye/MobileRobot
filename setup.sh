#!/bin/bash

# Enhanced Setup Script for Mobile Robot on Raspberry Pi 5
# This script installs all required dependencies and libraries

set -e  # Exit on any error

echo "================================================================"
echo "Mobile Robot Setup Script for Raspberry Pi 5"
echo "================================================================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This script is designed for Raspberry Pi systems"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Function to check if command was successful
check_status() {
    if [ $? -eq 0 ]; then
        echo "✓ $1 completed successfully"
    else
        echo "✗ $1 failed"
        exit 1
    fi
}

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y
check_status "System update"

# Install essential system dependencies
echo "Installing essential system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    i2c-tools \
    git \
    cmake \
    build-essential \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7 \
    libtiff5 \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test
check_status "System dependencies installation"

# Install Raspberry Pi 5 specific camera library
echo "Installing Raspberry Pi 5 camera libraries..."
sudo apt install -y python3-picamera2 python3-libcamera
check_status "Camera libraries installation"

# Enable I2C interface
echo "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0
check_status "I2C interface enable"

# Enable Camera interface
echo "Enabling Camera interface..."
sudo raspi-config nonint do_camera 0
check_status "Camera interface enable"

# Create virtual environment (recommended for Pi 5)
echo "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    check_status "Virtual environment creation"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
check_status "Virtual environment activation"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
check_status "Pip upgrade"

# Remove old GPIO libraries that conflict with Pi 5
echo "Removing conflicting GPIO libraries..."
pip uninstall -y RPi.GPIO rpi-gpio rpi-lgpio 2>/dev/null || true
sudo apt remove -y python3-rpi.gpio 2>/dev/null || true
check_status "Old GPIO libraries removal"

# Install modern GPIO library for Pi 5
echo "Installing modern GPIO library (rpi-lgpio)..."
pip install rpi-lgpio==0.6
check_status "rpi-lgpio installation"

# Install Python dependencies from requirements.txt
echo "Installing Python requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    check_status "Requirements installation"
else
    echo "Warning: requirements.txt not found, installing essential packages manually"
    pip install \
        adafruit-circuitpython-ssd1306 \
        adafruit-circuitpython-pca9685 \
        opencv-python \
        numpy \
        pillow \
        smbus2 \
        matplotlib \
        scipy
    check_status "Manual packages installation"
fi

# Install MobileRobot custom libraries as Python packages
echo "Installing MobileRobot custom libraries..."

# Install main Robot Hat Library
if [ -d "RPi_Robot_Hat_Lib" ]; then
    echo "Installing RPi Robot Hat Library..."
    cd RPi_Robot_Hat_Lib
    pip install -e .
    cd ..
    check_status "RPi Robot Hat Library installation"
else
    echo "Warning: RPi_Robot_Hat_Lib directory not found"
fi

# Install Ultrasonic Sensor Library
if [ -d "Libraries/Ultrasonic_Sensor" ]; then
    echo "Installing Ultrasonic Sensor Library..."
    cd Libraries/Ultrasonic_Sensor
    # Create setup.py if it doesn't exist
    if [ ! -f "setup.py" ]; then
        cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="ultrasonic-sensor",
    version="1.0.0",
    description="Ultrasonic Sensor Library for MobileRobot",
    py_modules=["Ultrasonic_sens"],
    install_requires=[
        "rpi-lgpio",
    ],
    python_requires=">=3.8",
)
EOF
    fi
    pip install -e .
    cd ../..
    check_status "Ultrasonic Sensor Library installation"
fi

# Install IR Sensor Library  
if [ -d "Libraries/IR_Sensor" ]; then
    echo "Installing IR Sensor Library..."
    cd Libraries/IR_Sensor
    # Create setup.py if it doesn't exist
    if [ ! -f "setup.py" ]; then
        cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="ir-sensor",
    version="1.0.0", 
    description="IR Sensor Library for MobileRobot",
    py_modules=["IRSens"],
    install_requires=[
        "rpi-lgpio",
    ],
    python_requires=">=3.8",
)
EOF
    fi
    pip install -e .
    cd ../..
    check_status "IR Sensor Library installation"
fi

# Install additional sensor libraries
echo "Installing additional sensor libraries..."
pip install \
    gpiozero \
    pigpio \
    pyserial \
    blynklib
check_status "Additional libraries installation"

# Set up permissions for GPIO and I2C
echo "Setting up GPIO and I2C permissions..."
sudo usermod -a -G gpio,i2c,spi $USER
check_status "Permissions setup"

# Create systemd service for pigpio daemon (useful for precise timing)
echo "Setting up pigpio daemon service..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
check_status "Pigpio daemon setup"

# Test I2C connectivity
echo "Testing I2C connectivity..."
if command -v i2cdetect &> /dev/null; then
    echo "I2C devices detected:"
    sudo i2cdetect -y 1 || echo "No I2C devices found or permission issue"
fi

# Check installed packages
echo "Checking installed Python packages..."
pip list | grep -E "(rpi|gpio|ssd1306|pca9685|opencv|numpy|pillow|smbus|ultrasonic|ir-sensor)"

# Test MobileRobot library imports
echo "Testing MobileRobot library imports..."
python3 -c "
try:
    from RPi_Robot_Hat_Lib import RobotController
    print('✓ RPi_Robot_Hat_Lib imported successfully')
except ImportError as e:
    print('✗ RPi_Robot_Hat_Lib import failed:', e)

try:
    from Ultrasonic_sens import Ultrasonic
    print('✓ Ultrasonic sensor library imported successfully')
except ImportError as e:
    print('✗ Ultrasonic sensor library import failed:', e)

try:
    from IRSens import IRsens
    print('✓ IR sensor library imported successfully')
except ImportError as e:
    print('✗ IR sensor library import failed:', e)
"

echo "================================================================"
echo "Setup completed successfully!"
echo "================================================================"
echo
echo "IMPORTANT NOTES:"
echo "1. Please reboot your Raspberry Pi to ensure all changes take effect"
echo "2. Activate the virtual environment before running scripts:"
echo "   source venv/bin/activate"
echo "3. Your user has been added to gpio, i2c, and spi groups"
echo "4. Camera and I2C interfaces have been enabled"
echo "5. Run 'sudo reboot' to complete the setup"
echo
echo "Test your setup with: python robot_self_check.py"
echo "================================================================"

# Offer to reboot
read -p "Would you like to reboot now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo reboot
fi 
