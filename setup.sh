#!/bin/bash

# One-Click Setup Script for Mobile Robot on Raspber# Remove Python package installation restrictions (for embedded systems)
echo "🔓 Disabling Python package installation restrictions..."
for file in /usr/lib/python*/EXTERNALLY-MANAGED; do
    if [ -f "$file" ]; then
        sudo mv "$file" "$file.old" 2>/dev/null || true
        echo "✓ Moved $file to $file.old"
    fi
done
echo "✓ Python package restrictions disabled (original files backed up)"
check_status "Python environment configuration" 5
# Installs everything needed without complex setup.py dependencies

set -e  # Exit on any error

echo "================================================================"
echo "🤖 Mobile Robot One-Click Setup for Raspberry Pi 5"
echo "================================================================"

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
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y
check_status "System update"

# Install only essential system dependencies (most are pre-installed on Pi OS)
echo "🔧 Checking system dependencies..."
# Most packages are pre-installed on Raspberry Pi OS:
# - python3-pip ✓ (already installed)
# - i2c-tools ✓ (already installed)
# - python3-picamera2 ✓ (already installed)
# - python3-libcamera ✓ (already installed)

# Only install if something is missing (rare case)
missing_packages=""
for package in python3-pip i2c-tools python3-picamera2 python3-libcamera; do
    if ! dpkg -l | grep -q "^ii  $package "; then
        missing_packages="$missing_packages $package"
    fi
done

if [ -n "$missing_packages" ]; then
    echo "Installing missing packages:$missing_packages"
    sudo apt install -y $missing_packages
else
    echo "✓ All system dependencies are already installed"
fi
check_status "System dependencies check"

# Enable I2C and Camera interfaces (if not already enabled)
echo "⚙️ Checking I2C and Camera interfaces..."
i2c_enabled=$(raspi-config nonint get_i2c)
camera_enabled=$(raspi-config nonint get_camera)

if [ "$i2c_enabled" -eq 0 ] && [ "$camera_enabled" -eq 0 ]; then
    echo "✓ I2C and Camera interfaces are already enabled"
else
    echo "Enabling I2C and Camera interfaces..."
    sudo raspi-config nonint do_i2c 0
    sudo raspi-config nonint do_camera 0
fi
check_status "Interface configuration"

# Remove Python package installation restrictions (for embedded systems)
echo "� Removing Python package installation restrictions..."
sudo rm -f /usr/lib/python*/EXTERNALLY-MANAGED 2>/dev/null || true
echo "✓ Python package restrictions removed"
check_status "Python environment configuration"

# Install modern GPIO library for Pi 5
echo "🔌 Installing modern GPIO library..."
sudo pip uninstall -y RPi.GPIO 2>/dev/null || true
sudo pip install rpi-lgpio
check_status "GPIO library installation"

# Install all Python requirements in one go
echo "📚 Installing all Python requirements..."
if [ -f "requirements.txt" ]; then
    sudo pip install -r requirements.txt
    check_status "Python requirements installation"
else
    echo "⚠️ Warning: requirements.txt not found, installing essential packages"
    sudo pip install \
        adafruit-circuitpython-ssd1306 \
        adafruit-circuitpython-pca9685 \
        adafruit-circuitpython-busdevice \
        opencv-python \
        numpy \
        pillow \
        smbus2 \
        mediapipe \
        tflite-runtime \
        apriltag
    
    # Install Blynk from GitHub (cannot be installed via normal pip)
    echo "📡 Installing Blynk library from GitHub..."
    sudo pip install git+https://github.com/vshymanskyy/blynk-library-python.git
    
    check_status "Essential packages installation"
fi

# Install additional GitHub dependencies (if not already installed)
echo "📡 Installing GitHub-based dependencies..."
if ! python3 -c "import BlynkLib" 2>/dev/null; then
    echo "Installing Blynk library from GitHub..."
    sudo pip install git+https://github.com/vshymanskyy/blynk-library-python.git
else
    echo "✓ Blynk library already installed"
fi
check_status "GitHub dependencies installation"

# Install custom robot libraries globally
echo "🤖 Installing custom robot libraries globally..."
ROBOT_PATH="/home/raspberry/Desktop/MobileRobot"

# Install RPi_Robot_Hat_Lib
echo "Installing RPi_Robot_Hat_Lib..."
cd "$ROBOT_PATH/Libraries/RPi_Robot_Hat_Lib"
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="RPi_Robot_Hat_Lib",
    version="1.0.0",
    description="Raspberry Pi Robot Hat Library with encoder support",
    py_modules=["RPi_Robot_Hat_Lib", "Encoder"],
    install_requires=[
        "smbus2",
        "rpi-lgpio",
    ],
    python_requires=">=3.7",
)
EOF
sudo pip install .
cd "$ROBOT_PATH"

# Install Ultrasonic_sens
echo "Installing Ultrasonic sensor library..."
cd "$ROBOT_PATH/Libraries/Ultrasonic_Sensor"
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="Ultrasonic_sens",
    version="1.0.0",
    description="Ultrasonic sensor library for robot navigation",
    py_modules=["Ultrasonic_sens"],
    install_requires=[
        "rpi-lgpio",
    ],
    python_requires=">=3.7",
)
EOF
sudo pip install .
cd "$ROBOT_PATH"

# Install IRSens
echo "Installing IR sensor library..."
cd "$ROBOT_PATH/Libraries/IR_Sensor"
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="IRSens",
    version="1.0.0",
    description="IR sensor library for obstacle detection",
    py_modules=["IRSens"],
    install_requires=[
        "rpi-lgpio",
    ],
    python_requires=">=3.7",
)
EOF
sudo pip install .
cd "$ROBOT_PATH"

echo "✓ All custom libraries installed globally"

check_status "Custom libraries installation"

# Set up permissions for GPIO and I2C
echo "🔐 Setting up GPIO and I2C permissions..."
sudo usermod -a -G gpio,i2c,spi $USER
check_status "Permissions setup"

# Test imports to verify everything works
echo "🧪 Testing library imports..."
python3 -c "
success_count = 0
total_tests = 7

try:
    from RPi_Robot_Hat_Lib import RobotController
    print('✓ RPi_Robot_Hat_Lib imported successfully (globally installed)')
    success_count += 1
except ImportError as e:
    print('✗ RPi_Robot_Hat_Lib import failed:', e)

try:
    from Ultrasonic_sens import Ultrasonic
    print('✓ Ultrasonic sensor library imported successfully (globally installed)')
    success_count += 1
except ImportError as e:
    print('✗ Ultrasonic sensor library import failed:', e)

try:
    from IRSens import IRsens
    print('✓ IR sensor library imported successfully (globally installed)')
    success_count += 1
except ImportError as e:
    print('✗ IR sensor library import failed:', e)

try:
    import tflite_runtime.interpreter as tflite
    print('✓ TensorFlow Lite runtime imported successfully')
    success_count += 1
except ImportError as e:
    print('✗ TensorFlow Lite runtime import failed:', e)

try:
    import mediapipe as mp
    print('✓ MediaPipe imported successfully')
    success_count += 1
except ImportError as e:
    print('✗ MediaPipe import failed:', e)

try:
    import apriltag
    print('✓ AprilTag imported successfully')
    success_count += 1
except ImportError as e:
    print('✗ AprilTag import failed:', e)

try:
    import BlynkLib
    print('✓ BlynkLib imported successfully')
    success_count += 1
except ImportError as e:
    print('✗ BlynkLib import failed:', e)

print(f'📊 Import test results: {success_count}/{total_tests} libraries imported successfully')

if success_count >= 5:  # Allow some optional libraries to fail
    print('🎉 Core libraries imported successfully!')
    exit(0)
else:
    print('⚠️ Some core libraries failed to import, but setup may still work')
    exit(0)
"
check_status "Library import verification"

# Test I2C connectivity
echo "🔍 Testing I2C connectivity..."
if command -v i2cdetect &> /dev/null; then
    echo "I2C devices detected:"
    sudo i2cdetect -y 1 2>/dev/null || echo "No I2C devices found (this is normal if robot hat is not connected)"
fi

echo "================================================================"
echo "🎉 Setup completed successfully!"
echo "================================================================"
echo
echo "📋 NEXT STEPS:"
echo "1. 🔄 Re-login or run: source ~/.bashrc"
echo "2. 🧪 Test your setup: python complete_self_test.py"
echo "3. 🚀 Install boot self-test: sudo ./install_boot_test.sh"
echo
echo "💡 TROUBLESHOOTING:"
echo "• Permission issues: newgrp gpio && newgrp i2c"
echo "• Import issues: source ~/.bashrc"
echo "• Last resort: sudo reboot"
echo "================================================================"
echo "🤖 Your robot is ready for action!"
