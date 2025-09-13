#!/bin/bash
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

# 4) GPIO library for Pi 5 - Complete fix with verification
echo "=============================================================="
echo "GPIO Library Setup for Raspberry Pi 5"
echo "=============================================================="

# Step 1: Remove ALL old RPi.GPIO installations (pip and system)
echo "Removing old RPi.GPIO library completely..."
sudo pip3 uninstall -y RPi.GPIO 2>/dev/null || true
sudo pip3 uninstall -y RPi.GPIO --break-system-packages 2>/dev/null || true
sudo apt remove -y python3-rpi.gpio 2>/dev/null || true

# Step 2: Clean up any remaining RPi.GPIO files that might cause conflicts
echo "Cleaning up old RPi.GPIO files..."
sudo rm -rf /usr/local/lib/python3.11/dist-packages/RPi* 2>/dev/null || true
sudo rm -rf /usr/local/lib/python3.11/dist-packages/rpi_lgpio* 2>/dev/null || true

# Step 3: Install rpi-lgpio via apt (provides RPi.GPIO compatibility for Pi 5)
echo "Installing rpi-lgpio via apt..."
sudo apt install --reinstall -y python3-rpi-lgpio

# Step 4: Verify the installation works
echo "Verifying GPIO library installation..."
if python3 -c "import RPi.GPIO as GPIO; print('RPi.GPIO compatibility layer working')" 2>/dev/null; then
    echo "✓ RPi.GPIO compatibility layer working properly"
else
    echo "✗ RPi.GPIO compatibility layer failed - this may cause issues"
fi

echo "GPIO setup completed - Pi 5 compatible libraries installed."
check_status "GPIO library installation"

# 5) Python dependencies from requirements.txt (best-effort)
echo "Installing Python requirements (best-effort)..."
success_pkgs=()
fail_pkgs=()
if [ -f "requirements.txt" ]; then
    while IFS= read -r pkg || [ -n "$pkg" ]; do
        # Skip empty lines and full-line comments
        if [ -z "$pkg" ] || echo "$pkg" | grep -Eq '^\s*#'; then
            continue
        fi
        # Remove inline comments and trim whitespace/CRLF
        clean_pkg=$(echo "$pkg" | cut -d'#' -f1 | tr -d '\r' | xargs)
        if [ -z "$clean_pkg" ]; then
            continue
        fi
        echo "  -> $clean_pkg"
        if sudo pip3 install "$clean_pkg"; then
            success_pkgs+=("$clean_pkg")
        else
            fail_pkgs+=("$clean_pkg")
        fi
    done < requirements.txt
else
    echo "requirements.txt not found; skipping"
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

# Consolidated RPi_Robot_Hat_Lib installation to avoid redundancy
if [ -d "$ROBOT_PATH/Libraries/RPi_Robot_Hat_Lib" ]; then
    echo "Installing RPi_Robot_Hat_Lib..."
    ( cd "$ROBOT_PATH/Libraries/RPi_Robot_Hat_Lib" && sudo pip3 install . ) || {
        echo "[FAIL] RPi_Robot_Hat_Lib installation failed";
        exit 1;
    }
fi

# Remove RPi.GPIO if installed by Adafruit libraries
echo "Checking for and removing RPi.GPIO to prevent conflicts..."
sudo pip3 uninstall -y RPi.GPIO 2>/dev/null || true
check_status "RPi.GPIO removal after Adafruit library installation"

# Verify custom library installations
custom_libraries=("RPi_Robot_Hat_Lib" "Ultrasonic_Sensor" "IR_Sensor")
for lib in "${custom_libraries[@]}"; do
    echo "Verifying $lib installation..."
    if python3 -c "import $lib" 2>/dev/null; then
        echo "✓ $lib installed and working"
    # Corrected verification for Ultrasonic_Sensor library
    elif [ "$lib" == "Ultrasonic_Sensor" ]; then
        if python3 -c "import Ultrasonic_sens" 2>/dev/null; then
            echo "✓ Ultrasonic_Sensor installed and working"
        else
            echo "✗ Ultrasonic_Sensor installation failed or not working"
            exit 1
        fi
    # Corrected verification for IR_Sensor library
    elif [ "$lib" == "IR_Sensor" ]; then
        if python3 -c "import IRSens" 2>/dev/null; then
            echo "✓ IR_Sensor installed and working"
        else
            echo "✗ IR_Sensor installation failed or not working"
            exit 1
        fi
    else
        echo "✗ $lib installation failed or not working"
        exit 1
    fi
done

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
if [ ${#fail_pkgs[@]} -gt 0 ]; then
    echo -e "\nPIP INSTALL SUMMARY:\n  success: ${#success_pkgs[@]}\n  failed: ${#fail_pkgs[@]}\n  failed list:";
    for p in "${fail_pkgs[@]}"; do echo "    - $p"; done
else
    echo -e "\nPIP INSTALL SUMMARY:\n  success: ${#success_pkgs[@]}\n  failed: 0"
fi

# Final user instructions
cat <<EOF
==============================================================
Setup completed successfully!
Next steps:
  1) Reboot the Raspberry Pi: sudo reboot
  2) After reboot, run your robot scripts from the MobileRobot directory
==============================================================
EOF
