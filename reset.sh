#!/bin/bash
# Factory reset for the MobileRobot project (non-destructive to OS basics)
# - Removes project services and Python libs
# - Restores Python policy files we moved
# - Cleans project logs/caches
# - Keeps SSH and networking intact

set -e

echo "=============================================================="
echo "MobileRobot Project Reset (safe: keeps SSH/network)"
echo "=============================================================="

# Helpers
okfail() {
        if [ $1 -eq 0 ]; then echo "[OK] $2"; else echo "[FAIL] $2"; fi
}

# 1) Stop/disable and remove BMS battery.service
echo "-- Removing BMS systemd service (battery.service) --"
if command -v systemctl >/dev/null 2>&1; then
        sudo systemctl stop battery.service 2>/dev/null || true
        sudo systemctl disable battery.service 2>/dev/null || true
        if [ -f "/etc/systemd/system/battery.service" ]; then
                sudo rm -f /etc/systemd/system/battery.service
                echo "  Removed /etc/systemd/system/battery.service"
        fi
        sudo systemctl daemon-reload || true
        sudo systemctl reset-failed 2>/dev/null || true
        echo "  BMS service removed (if present)"
else
        echo "  systemctl not available; skipping service removal"
fi

# 2) Uninstall custom Python libraries
echo "-- Uninstalling custom Python libraries --"
packages=(
    rpi-robot-hat-lib
    ir-sensor-lib
    ultrasonic-sensor-lib
)
for pkg in "${packages[@]}"; do
    echo "  Uninstalling $pkg..."
    if sudo pip3 uninstall -y "$pkg" >/dev/null 2>&1; then
            echo "    removed $pkg"
    else
            echo "    (not found or already removed): $pkg"
    fi
done

# 2b) Uninstall Python packages from requirements.txt (best-effort)
if [ -f "requirements.txt" ]; then
  echo "-- Uninstalling Python packages from requirements.txt (best-effort) --"
  while IFS= read -r pkg || [ -n "$pkg" ]; do
      # Skip empty and comment lines
      if [ -z "$pkg" ] || echo "$pkg" | grep -Eq '^\s*#'; then
          continue
      fi
      clean_pkg=$(echo "$pkg" | cut -d'#' -f1 | tr -d '\r' | xargs)
      [ -n "$clean_pkg" ] || continue
      # Try to resolve dist name
      dist_name=""
      if echo "$clean_pkg" | grep -Eq '^git\+'; then
          dist_name=$(echo "$clean_pkg" | sed -n 's/.*[#&]egg=\([^&]*\).*/\1/p')
      fi
      if [ -z "$dist_name" ]; then
          dist_name="${clean_pkg%%[<>=!~ ]*}"
          dist_name="${dist_name%%[*}"
      fi
      if [ -n "$dist_name" ]; then
          echo "  Uninstalling $dist_name..."
          sudo pip3 uninstall -y "$dist_name" >/dev/null 2>&1 || true
      fi
  done < requirements.txt
fi

# 3) Restore Python EXTERNALLY-MANAGED policy files if previously moved
echo "-- Restoring Python EXTERNALLY-MANAGED policy (if previously moved) --"
for file in /usr/lib/python*/EXTERNALLY-MANAGED; do
    [ -e "$file" ] || continue
    # if the .old exists alongside, skip (we didn't move it here)
    :
done
for old in /usr/lib/python*/EXTERNALLY-MANAGED.old; do
    if [ -f "$old" ]; then
        orig=${old%.old}
        if [ ! -f "$orig" ]; then
            echo "  Restoring $(basename "$orig")"
            sudo mv "$old" "$orig" || true
        else
            # original exists; drop the old backup
            sudo rm -f "$old" || true
        fi
    fi
done

# 4) Clean project logs and caches
echo "-- Cleaning project logs and caches --"
LOG_DIR="$HOME/Desktop/Battery_Log"
if [ -d "$LOG_DIR" ]; then
    rm -rf "$LOG_DIR" && echo "  Removed $LOG_DIR" || echo "  Could not remove $LOG_DIR"
fi
# Remove __pycache__ and *.egg-info within project tree
find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -prune -exec rm -rf {} + 2>/dev/null || true

# 5) Keep SSH and networking
echo "-- Ensuring SSH is enabled (network left untouched) --"
if command -v systemctl >/dev/null 2>&1; then
    if sudo systemctl enable ssh >/dev/null 2>&1; then echo "  ssh enabled"; fi
    if sudo systemctl start ssh >/dev/null 2>&1; then echo "  ssh started"; fi
fi

echo "=============================================================="
echo "Reset complete:"
echo "  - BMS service removed (if present)"
echo "  - Custom Python libs uninstalled (if present)"
echo "  - Policy files restored when applicable"
echo "  - Project logs and caches cleaned"
echo "  - SSH kept enabled; networking untouched"
echo "=============================================================="
