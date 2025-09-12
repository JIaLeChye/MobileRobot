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
# Include build tools required for packages like apriltag
for package in python3-pip i2c-tools python3-picamera2 python3-libcamera cmake build-essential python3-dev pkg-config; do
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

    # Generic import and version checks script placeholder
    cat << 'EOF' > /tmp/test_libs.py

    # Install RPi_Robot_Hat_Lib
    echo "Installing RPi_Robot_Hat_Lib..."
    cd "$ROBOT_PATH/Libraries/RPi_Robot_Hat_Lib"
    sudo pip install .
    cd "$ROBOT_PATH"

    # Install Ultrasonic_sens
    echo "Installing Ultrasonic sensor library..."
    cd "$ROBOT_PATH/Libraries/Ultrasonic_Sensor"
    sudo pip install .
    cd "$ROBOT_PATH"

    # Install IRSens
    echo "Installing IR sensor library..."
    cd "$ROBOT_PATH/Libraries/IR_Sensor"
    sudo pip install .
    cd "$ROBOT_PATH"

# Install modern GPIO library for Pi 5
echo "🔌 Installing modern GPIO library..."
sudo pip uninstall -y RPi.GPIO 2>/dev/null || true
sudo pip install rpi-lgpio
check_status "GPIO library installation"


# Do not abort on individual pip install failures; record successes and failures
echo "📚 Installing all Python requirements..."
success_pkgs=()
fail_pkgs=()
if [ -f "requirements.txt" ]; then
    while read -r pkg || [ -n "$pkg" ]; do
    # Skip empty lines and comments
        [[ "$pkg" =~ ^#.*$ || -z "$pkg" ]] && continue
        echo "Installing $pkg ..."
        if sudo pip install $pkg; then
            success_pkgs+=("$pkg")
        else
            fail_pkgs+=("$pkg")
        fi
    done < requirements.txt
else
    echo "❌ requirements.txt not found, no packages will be installed."
fi

echo "\n========= PIP INSTALL SUMMARY ========="
echo "✅ Successfully installed:"
for pkg in "${success_pkgs[@]}"; do
    echo "  - $pkg"
done
if [ ${#fail_pkgs[@]} -gt 0 ]; then
    echo "❌ Failed to install:"
    for pkg in "${fail_pkgs[@]}"; do
        echo "  - $pkg"
    done
else
    echo "All packages installed successfully."
fi
echo "======================================="

# Install additional GitHub dependencies (if not already installed)
echo "📡 Installing GitHub-based dependencies..."
if ! python3 -c "import BlynkLib" 2>/dev/null; then
    echo "Installing Blynk library from GitHub..."
echo -e "\n========= PIP INSTALL SUMMARY ========="
echo "✅ Successfully installed:"
for pkg in "${success_pkgs[@]}"; do
    echo "  - $pkg"
done
if [ ${#fail_pkgs[@]} -gt 0 ]; then
    echo "❌ Failed to install:"
    for pkg in "${fail_pkgs[@]}"; do
        echo "  - $pkg"
    done
else
    echo "All packages installed successfully."
fi
echo "======================================="
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
echo "1. 🔄 Reboot your Raspberry Pi: sudo reboot"
echo "2. 🚀 After reboot, run your robot scripts from the Desktop/MobileRobot directory"

echo "================================================================"
echo "🤖 Your robot is ready for action!"
