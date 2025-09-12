#!/bin/bash

# One-Click Setup Script for Mobile Robot on Raspberry Pi 5
# ASCII-only output; safe to run multiple times (idempotent where possible)

set -e

# Helper to print status
check_status() {
    if [ $? -eq 0 ]; then
        echo "[OK] $1"
    else
        echo "[FAIL] $1"
        exit 1
    fi
}

echo "=============================================================="
echo "Mobile Robot One-Click Setup for Raspberry Pi 5"
echo "=============================================================="

# 0) Soften Python EXTERNALLY-MANAGED policy (embedded friendly)
echo "Adjusting Python package policy (EXTERNALLY-MANAGED)..."
for file in /usr/lib/python*/EXTERNALLY-MANAGED; do
    if [ -f "$file" ]; then
        sudo mv "$file" "$file.old" 2>/dev/null || true
        echo "  moved $file -> $file.old"
    fi
done
check_status "Python environment configuration"

# 1) System update
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y
check_status "System update"

# 2) System dependencies (incl. build tools for native wheels like apriltag)
echo "Checking system dependencies..."
missing_packages=""
for package in python3-pip i2c-tools python3-picamera2 python3-libcamera cmake build-essential python3-dev pkg-config; do
    if ! dpkg -l | grep -q "^ii  $package "; then
        missing_packages="$missing_packages $package"
    fi
done
if [ -n "$missing_packages" ]; then
    echo "Installing:$missing_packages"
    sudo apt install -y $missing_packages
else
    echo "All system dependencies already installed"
fi
check_status "System dependencies check"

# 3) Enable I2C and Camera (if disabled)
echo "Checking I2C and Camera interfaces..."
if command -v raspi-config >/dev/null 2>&1; then
    i2c_enabled=$(raspi-config nonint get_i2c || echo 1)
    camera_enabled=$(raspi-config nonint get_camera || echo 1)
    if [ "$i2c_enabled" -ne 0 ]; then
        echo "Enabling I2C..."
        sudo raspi-config nonint do_i2c 0 || true
    fi
    if [ "$camera_enabled" -ne 0 ]; then
        echo "Enabling Camera..."
        sudo raspi-config nonint do_camera 0 || true
    fi
else
    echo "raspi-config not found; skipping interface toggles"
fi
check_status "I2C/Camera check"

# 4) GPIO library for Pi 5
echo "Installing modern GPIO library (rpi-lgpio)..."
sudo pip3 uninstall -y RPi.GPIO 2>/dev/null || true
sudo pip3 install --upgrade pip
sudo pip3 install rpi-lgpio
check_status "GPIO library installation"

# 5) Python dependencies from requirements.txt (best-effort)
echo "Installing Python requirements (best-effort)..."
success_pkgs=()
fail_pkgs=()
if [ -f "requirements.txt" ]; then
    while IFS= read -r pkg || [ -n "$pkg" ]; do
        # Skip empty lines and comments
        if [ -z "$pkg" ] || echo "$pkg" | grep -Eq '^\s*#'; then
            continue
        fi
        echo "  -> $pkg"
        if sudo pip3 install $pkg; then
            success_pkgs+=("$pkg")
        else
            fail_pkgs+=("$pkg")
        fi
    done < requirements.txt
else
    echo "requirements.txt not found; skipping"
fi
echo "PIP INSTALL SUMMARY"
echo "  success: ${#success_pkgs[@]}"
echo "  failed:  ${#fail_pkgs[@]}"
if [ ${#fail_pkgs[@]} -gt 0 ]; then
    echo "  failed list:"; for p in "${fail_pkgs[@]}"; do echo "    - $p"; done
fi

# 6) Install local libraries via pip (editable copies not required)
ROBOT_PATH=$(pwd)
echo "Installing local libraries..."
if [ -d "$ROBOT_PATH/Libraries/RPi_Robot_Hat_Lib" ]; then
    ( cd "$ROBOT_PATH/Libraries/RPi_Robot_Hat_Lib" && sudo pip3 install . ) || true
fi
if [ -d "$ROBOT_PATH/Libraries/Ultrasonic_Sensor" ]; then
    ( cd "$ROBOT_PATH/Libraries/Ultrasonic_Sensor" && sudo pip3 install . ) || true
fi
if [ -d "$ROBOT_PATH/Libraries/IR_Sensor" ]; then
    ( cd "$ROBOT_PATH/Libraries/IR_Sensor" && sudo pip3 install . ) || true
fi
check_status "Local libraries installation"

# 7) Permissions for GPIO/I2C
echo "Adding user to gpio,i2c,spi groups..."
sudo usermod -a -G gpio,i2c,spi "$USER" || true
check_status "Permissions setup"

# 8) I2C quick probe (optional)
echo "I2C quick probe (optional)..."
if command -v i2cdetect >/dev/null 2>&1; then
    sudo i2cdetect -y 1 2>/dev/null || echo "No I2C devices detected (ok if hardware not connected)"
fi

echo "=============================================================="
echo "Setup completed"
echo "=============================================================="
echo "Next steps:"
echo "  1) Reboot the Raspberry Pi: sudo reboot"
echo "  2) After reboot, run your robot scripts from the MobileRobot directory"
echo "=============================================================="
