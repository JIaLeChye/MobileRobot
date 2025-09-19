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

# Helper to get an installed package (distribution) version using importlib.metadata
# Usage: get_dist_version <dist-name>
get_dist_version() {
    local dist="$1"
    python3 - <<PY
import sys
dist = ${dist@Q}
try:
    from importlib.metadata import version
except Exception:
    from importlib_metadata import version  # fallback if needed
try:
    print(version(dist))
except Exception:
    print("unknown")
PY
}

# Helper to parse local package version from setup.py in a directory
# Usage: get_local_setup_version <dir-with-setup.py>
get_local_setup_version() {
    local dir="$1"
    python3 - "$dir" <<'PY'
import sys, re
from pathlib import Path
root = Path(sys.argv[1])
sp = root / 'setup.py'
try:
    text = sp.read_text(encoding='utf-8', errors='ignore')
    m = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", text)
    print(m.group(1) if m else "")
except Exception:
    print("")
PY
}

# Install a local library only if version differs from installed dist
# Usage: install_local_if_needed <dir> <dist-name>
install_local_if_needed() {
    local dir="$1"
    local dist="$2"
    if [ ! -d "$dir" ]; then return 0; fi
    local local_ver
    local installed_ver
    local_ver=$(get_local_setup_version "$dir")
    installed_ver=$(get_dist_version "$dist")
    if [ -n "$local_ver" ] && [ -n "$installed_ver" ] && [ "$local_ver" = "$installed_ver" ]; then
        echo "  -> $dist==$installed_ver already installed; skipping"
        return 0
    fi
    echo "  -> Installing $dist (local version: ${local_ver:-unknown}, installed: ${installed_ver:-none})"
    ( cd "$dir" && sudo pip3 install . ) || return 1
}

echo "=============================================================="
echo "Mobile Robot One-Click Setup for Raspberry Pi 5"
echo "=============================================================="

echo "=============================================================="
echo "Step 0): Configure Python environment policy"
echo "=============================================================="
echo "Adjusting Python package policy (EXTERNALLY-MANAGED)..."
for file in /usr/lib/python*/EXTERNALLY-MANAGED; do
    if [ -f "$file" ]; then
        sudo mv "$file" "$file.old" 2>/dev/null || true
        echo "  moved $file -> $file.old"
    fi
done
check_status "Python environment configuration"

echo "=============================================================="
echo "Step 1): Update system packages"
echo "=============================================================="
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y
check_status "System update"

echo "=============================================================="
echo "Step 2): Install system dependencies"
echo "=============================================================="
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

echo "=============================================================="
echo "Step 3): Enable I2C and Camera interfaces"
echo "=============================================================="
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

echo "=============================================================="
echo "Step 4): Install Python requirements"
echo "=============================================================="
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
        # If VCS requirement (git+...), try to skip if same commit already installed
        if echo "$clean_pkg" | grep -Eq '^git\+'; then
            # Extract egg/dist name and commit ref (text after @, before #)
            egg_name=$(echo "$clean_pkg" | sed -n 's/.*[#&]egg=\([^&]*\).*/\1/p')
            commit_ref=$(echo "$clean_pkg" | sed -n 's/.*@\([^#]*\).*/\1/p')
            if [ -n "$egg_name" ] && [ -n "$commit_ref" ]; then
                installed_commit=$(python3 - "$egg_name" <<'PY'
import sys, json, os
name = sys.argv[1]
try:
    from importlib.metadata import distribution
except Exception:
    from importlib_metadata import distribution
try:
    d = distribution(name)
    commit = ""
    for f in (d.files or []):
        if str(f).endswith('direct_url.json'):
            p = d.locate_file(f)
            try:
                with open(p, 'r') as fh:
                    du = json.load(fh)
                vcs = du.get('vcs_info') or {}
                commit = vcs.get('commit_id', '')
            except Exception:
                pass
            break
    print(commit)
except Exception:
    print("")
PY
                )
                if [ -n "$installed_commit" ] && [ "$installed_commit" = "$commit_ref" ]; then
                    echo "     (VCS $egg_name at commit $commit_ref already installed) - skipping"
                    continue
                fi
            fi
            # Fall through to pip install for VCS if we can't confirm commit match
        fi
        # Derive base package name (strip version specifiers and extras)
        pkg_base="${clean_pkg%%[<>=!~ ]*}"
        pkg_base="${pkg_base%%[*}"
        if python3 -m pip show "$pkg_base" >/dev/null 2>&1; then
            echo "     (already installed: $pkg_base) - skipping"
            continue
        fi
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
echo "=============================================================="
echo "Step 5): Install local libraries"
echo "=============================================================="
ROBOT_PATH=$(pwd)
echo "Installing local libraries (skip if same version already installed)..."
install_local_if_needed "$ROBOT_PATH/Libraries/RPi_Robot_Hat_Lib" "rpi-robot-hat-lib" || true
install_local_if_needed "$ROBOT_PATH/Libraries/Ultrasonic_Sensor" "ultrasonic-sensor-lib" || true
install_local_if_needed "$ROBOT_PATH/Libraries/IR_Sensor" "ir-sensor-lib" || true
check_status "Local libraries installation"

# Consolidated RPi_Robot_Hat_Lib installation to avoid redundancy
if [ -d "$ROBOT_PATH/Libraries/RPi_Robot_Hat_Lib" ]; then
    echo "Ensuring RPi_Robot_Hat_Lib is installed..."
    install_local_if_needed "$ROBOT_PATH/Libraries/RPi_Robot_Hat_Lib" "rpi-robot-hat-lib" || {
        echo "[FAIL] RPi_Robot_Hat_Lib installation failed";
        exit 1;
    }
fi

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

echo "=============================================================="
echo "Step 6): Permissions and group membership"
echo "=============================================================="
echo "Adding user to gpio,i2c,spi groups..."
sudo usermod -a -G gpio,i2c,spi "$USER" || true
check_status "Permissions setup"

echo "=============================================================="
echo "Step 7): I2C quick probe (optional)"
echo "=============================================================="
echo "I2C quick probe (optional)..."
if command -v i2cdetect >/dev/null 2>&1; then
    sudo i2cdetect -y 1 2>/dev/null || echo "No I2C devices detected (ok if hardware not connected)"
fi

# 8) Install BMS battery service (systemd)
echo "=============================================================="
echo "Step 8): Install BMS battery service"
echo "=============================================================="
BMS_DIR="$(pwd)/BMS"
BMS_SETUP_RESULT="skipped"
BMS_ENABLED=""
BMS_ACTIVE=""
if [ -d "$BMS_DIR" ]; then
    if [ -f "$BMS_DIR/setup.sh" ]; then
        echo "Running BMS/setup.sh to install battery service..."
        ( cd "$BMS_DIR" && bash ./setup.sh )
        if [ $? -eq 0 ]; then BMS_SETUP_RESULT="ok"; else BMS_SETUP_RESULT="failed"; fi
    elif [ -f "$BMS_DIR/setup.py" ]; then
        echo "Running BMS/setup.py to install battery service..."
        ( cd "$BMS_DIR" && python3 ./setup.py )
        if [ $? -eq 0 ]; then BMS_SETUP_RESULT="ok"; else BMS_SETUP_RESULT="failed"; fi
    else
        echo "No setup.sh or setup.py found in BMS; skipping"
        BMS_SETUP_RESULT="missing"
    fi
    # Probe service status if systemctl is available
    if command -v systemctl >/dev/null 2>&1; then
        BMS_SERVICE_NAME="battery.service"
        if systemctl list-unit-files | grep -q "^${BMS_SERVICE_NAME}"; then
            BMS_ENABLED=$(systemctl is-enabled "$BMS_SERVICE_NAME" 2>/dev/null || echo "unknown")
            BMS_ACTIVE=$(systemctl is-active "$BMS_SERVICE_NAME" 2>/dev/null || echo "unknown")
            echo "BMS service status: enabled=$BMS_ENABLED, active=$BMS_ACTIVE"
        else
            echo "BMS service unit ($BMS_SERVICE_NAME) not registered yet."
        fi
    fi
else
    echo "BMS directory not found; skipping"
    BMS_SETUP_RESULT="missing"
fi

# 9) FINAL GPIO library setup for Pi 5 - Done last to prevent conflicts
echo "=============================================================="
echo "FINAL: GPIO Library Setup for Raspberry Pi 5"
echo "=============================================================="

# Step 1: Remove ALL old RPi.GPIO installations that may have been installed by dependencies
echo "Final cleanup: Removing any RPi.GPIO installations that conflict with rpi-lgpio..."
sudo pip3 uninstall -y RPi.GPIO 2>/dev/null || true
sudo pip3 uninstall -y RPi.GPIO --break-system-packages 2>/dev/null || true
pip3 uninstall -y RPi.GPIO 2>/dev/null || true  # Remove user-installed version
sudo apt remove -y python3-rpi.gpio 2>/dev/null || true

# Step 2: Clean up any remaining RPi.GPIO files that might cause conflicts
echo "Cleaning up old RPi.GPIO files (preserving RPi_Robot_Hat_Lib)..."
sudo rm -rf /usr/local/lib/python3.11/dist-packages/RPi.GPIO* 2>/dev/null || true
sudo rm -rf /usr/local/lib/python3.11/dist-packages/rpi_lgpio* 2>/dev/null || true
# Also clean user-installed packages - be specific to avoid removing RPi_Robot_Hat_Lib
rm -rf ~/.local/lib/python3.11/site-packages/RPi.GPIO* 2>/dev/null || true

# Step 3: Install rpi-lgpio via apt (provides RPi.GPIO compatibility for Pi 5)
echo "Installing rpi-lgpio via apt..."
sudo apt install --reinstall -y python3-rpi-lgpio

# Step 4: Verify the installation works
echo "Verifying GPIO library installation..."
if python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(12, GPIO.OUT); print('RPi.GPIO compatibility layer working')" 2>/dev/null; then
    echo "✓ RPi.GPIO compatibility layer working properly"
else
    echo "✗ RPi.GPIO compatibility layer failed - this may cause issues"
fi

# Show which module path is being used to detect shadowed pip wheels
python3 - <<'PY'
try:
    import RPi.GPIO as GPIO
    import os
    p = getattr(GPIO, '__file__', 'unknown')
    print(f"RPi.GPIO module path: {p}")
    if 'dist-packages' in p and ('rpi' in p.lower() or 'RPi' in p):
        print('[OK] rpi-lgpio shim likely active')
    elif 'site-packages' in p:
        print('[WARN] pip RPi.GPIO wheel may be shadowing the shim')
except Exception as e:
    print('Could not inspect RPi.GPIO path:', e)
PY

echo "GPIO setup completed - Pi 5 compatible libraries installed."
check_status "Final GPIO library installation"

echo "=============================================================="
echo "Setup completed"
echo "=============================================================="
if [ ${#fail_pkgs[@]} -gt 0 ]; then
    echo -e "\nPIP INSTALL SUMMARY:\n  success: ${#success_pkgs[@]}\n  failed: ${#fail_pkgs[@]}\n  failed list:";
    for p in "${fail_pkgs[@]}"; do echo "    - $p"; done
else
    echo -e "\nPIP INSTALL SUMMARY:\n  success: ${#success_pkgs[@]}\n  failed: 0"
fi

# Final summary and user instructions
echo ""
echo "What was added/updated in this run:"
echo "- System: apt update/upgrade applied"
if [ -n "${missing_packages}" ]; then
    echo "- Dependencies installed via apt:${missing_packages}"
else
    echo "- Dependencies installed via apt: none (already present)"
fi
echo "- Python packages from requirements.txt: success ${#success_pkgs[@]}, failed ${#fail_pkgs[@]}"
if [ ${#success_pkgs[@]} -gt 0 ]; then
    echo "  Successful installs:"
    for p in "${success_pkgs[@]}"; do echo "    - $p"; done
fi
if [ ${#fail_pkgs[@]} -gt 0 ]; then
    echo "  Failed installs:"
    for p in "${fail_pkgs[@]}"; do echo "    - $p"; done
fi
echo "- Local libraries installed and verified:"
echo "    - RPi_Robot_Hat_Lib ($(get_dist_version rpi-robot-hat-lib))"
echo "    - Ultrasonic_Sensor ($(get_dist_version ultrasonic-sensor-lib))"
echo "    - IR_Sensor ($(get_dist_version ir-sensor-lib))"
echo "- Interfaces enabled if needed: I2C, Camera"
echo "- Permissions updated: added $USER to gpio,i2c,spi groups"
echo "- GPIO stack: removed conflicting RPi.GPIO; installed python3-rpi-lgpio (Pi 5 compatible)"
echo "- I2C quick probe executed (if i2cdetect present)"
if [ -n "${BMS_SETUP_RESULT}" ]; then
    echo "- BMS battery service: install ${BMS_SETUP_RESULT}; status: enabled=${BMS_ENABLED:-n/a}, active=${BMS_ACTIVE:-n/a}"
fi

cat <<EOF
==============================================================
Setup completed successfully!
Next steps:
    1) Reboot the Raspberry Pi: sudo reboot
    2) After reboot, run your robot scripts from the MobileRobot directory
==============================================================
EOF
