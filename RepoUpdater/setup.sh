#!/bin/bash

# Variables

# Resolve the actual user even when run with sudo
if [ -n "$SUDO_USER" ]; then
    SERVICE_USER="$SUDO_USER"
else
    SERVICE_USER="$USER"
fi
# Resolve that user's home directory
USER_HOME=$(getent passwd "$SERVICE_USER" | cut -d: -f6 2>/dev/null || echo "$HOME")
SERVICE_NAME="MCupdater.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Search for updater.py in current script directory first
UPDATER_SCRIPT=$(find "$SCRIPT_DIR" -maxdepth 2 -name "updater.py" -print -quit)
# If not found, do a full system search (slow)
if [ -z "$UPDATER_SCRIPT" ]; then
    UPDATER_SCRIPT=$(find / -name "updater.py" 2>/dev/null | head -n 1)
fi

# Log paths in Debug_log in home directory to match updater.py logging
STANDARD_OUTPUT="updater_log.txt"
STANDARD_ERROR_OUTPUT="updater_log.txt"
LOG_FILE_PATH="$USER_HOME/Debug_log"

echo "User Directory is $USER_HOME"

# Check if updater.py exists
if [ -z "$UPDATER_SCRIPT" ]; then
    echo "Error: updater.py not found."
    exit 1
fi

echo "Updater script found at: $UPDATER_SCRIPT"

# Check if MCupdater.service file exists in the current directory
if [ ! -f "MCupdater.service" ]; then
    echo "Error: MCupdater.service file not found in the current directory."
    exit 1
fi

if [ -f "$SERVICE_PATH" ]; then 
    echo "Old MCupdater.service file found" 
    echo "Deleting old MCupdater.service file"
    sudo rm $SERVICE_PATH || {
        echo "Error: Old service file found but unable to remove $SERVICE_PATH" 
        exit 1
    }
fi 

# Copy the service file to /etc/systemd/system/
echo "Copying MCupdater.service to $SERVICE_PATH..."
sudo cp MCupdater.service "$SERVICE_PATH" || {
    echo "Error: Failed to copy MCupdater.service to $SERVICE_PATH."
    exit 1
}

echo "Ensuring required keys exist in service file (within [Service])..."
# Insert missing keys immediately after the [Service] header to avoid placing them under [Install]
if ! sudo grep -q '^User=' "$SERVICE_PATH"; then
    sudo sed -i "/^\[Service\]/a User=$SERVICE_USER" "$SERVICE_PATH"
fi
if ! sudo grep -q '^WorkingDirectory=' "$SERVICE_PATH"; then
    sudo sed -i "/^\[Service\]/a WorkingDirectory=$(dirname "$UPDATER_SCRIPT")" "$SERVICE_PATH"
fi
if ! sudo grep -q '^ExecStart=' "$SERVICE_PATH"; then
    sudo sed -i "/^\[Service\]/a ExecStart=/usr/bin/python3 $UPDATER_SCRIPT" "$SERVICE_PATH"
fi
if ! sudo grep -q '^StandardOutput=' "$SERVICE_PATH"; then
    sudo sed -i "/^\[Service\]/a StandardOutput=file:$LOG_FILE_PATH/$STANDARD_OUTPUT" "$SERVICE_PATH"
fi
if ! sudo grep -q '^StandardError=' "$SERVICE_PATH"; then
    sudo sed -i "/^\[Service\]/a StandardError=file:$LOG_FILE_PATH/$STANDARD_ERROR_OUTPUT" "$SERVICE_PATH"
fi
if ! sudo grep -q '^Environment=MCUPDATER_LOG_DIR=' "$SERVICE_PATH"; then
    sudo sed -i "/^\[Service\]/a Environment=MCUPDATER_LOG_DIR=$LOG_FILE_PATH" "$SERVICE_PATH"
fi

# Update User name
echo "Updating Service User: $SERVICE_USER"
sudo sed -i "s|^User=.*|User=$SERVICE_USER|" "$SERVICE_PATH" || {
    echo "Error: Failed to modify Username in $SERVICE_PATH"
    exit 1
}

echo "Updating service file at $SERVICE_PATH..."
# Update only within the [Service] section using sed range between [Service] and next section header
sudo sed -i "/^\\[Service\\]/,/^\\[/ s|^ExecStart=.*|ExecStart=/usr/bin/python3 $UPDATER_SCRIPT|" "$SERVICE_PATH" || {
    echo "Error: Failed to update ExecStart in $SERVICE_PATH."
    exit 1
}
sudo sed -i "/^\\[Service\\]/,/^\\[/ s|^WorkingDirectory=.*|WorkingDirectory=$(dirname "$UPDATER_SCRIPT")|" "$SERVICE_PATH" || {
    echo "Error: Failed to update WorkingDirectory in $SERVICE_PATH."
    exit 1
}
sudo sed -i "s|^Environment=MCUPDATER_LOG_DIR=.*|Environment=MCUPDATER_LOG_DIR=$LOG_FILE_PATH|" "$SERVICE_PATH" || {
    echo "Error: Failed to update MCUPDATER_LOG_DIR in $SERVICE_PATH."
    exit 1
}

# Update log file paths
echo "Updating log file paths..."

if [ ! -d "$LOG_FILE_PATH" ]; then
    echo "Creating log directory: $LOG_FILE_PATH"
    sudo -u "$SERVICE_USER" mkdir -p "$LOG_FILE_PATH" || {
        echo "Error: Failed to create log directory."
        exit 1
    }
else
    echo "Log folder exists: $LOG_FILE_PATH"
fi

# Ensure ownership so the service user can write logs
sudo chown -R "$SERVICE_USER":"$SERVICE_USER" "$LOG_FILE_PATH" || true

# Ensure log files exist and have correct ownership
sudo -u "$SERVICE_USER" touch "$LOG_FILE_PATH/$STANDARD_OUTPUT" "$LOG_FILE_PATH/$STANDARD_ERROR_OUTPUT" || true
sudo chown "$SERVICE_USER":"$SERVICE_USER" "$LOG_FILE_PATH/$STANDARD_OUTPUT" "$LOG_FILE_PATH/$STANDARD_ERROR_OUTPUT" || true

sudo sed -i "s|^StandardOutput=.*|StandardOutput=file:$LOG_FILE_PATH/$STANDARD_OUTPUT|" "$SERVICE_PATH" || {
    echo "Error: Failed to update StandardOutput in $SERVICE_PATH."
    exit 1
}

sudo sed -i "s|^StandardError=.*|StandardError=file:$LOG_FILE_PATH/$STANDARD_ERROR_OUTPUT|" "$SERVICE_PATH" || {
    echo "Error: Failed to update StandardError in $SERVICE_PATH."
    exit 1
}

# Verify the service file
echo "Service file updated (showing contents):"
sudo sed -n '1,120p' "$SERVICE_PATH"

# Reload systemd daemon before enabling in case the unit was just updated
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload || {
    echo "Error: Failed to reload systemd daemon."
    exit 1
}

echo "Unmasking service if masked..."
sudo systemctl unmask "$SERVICE_NAME" || true

sudo systemctl enable "$SERVICE_NAME" || {
    echo "Error: Failed to enable $SERVICE_NAME."
    exit 1
}
echo "$SERVICE_NAME enabled" 

# Note: MCupdater is a oneshot service, so we don't restart it like battery.service
# Instead, we can run it once to test
echo "Testing ${SERVICE_NAME}..."
sudo systemctl start "$SERVICE_NAME" || {
    echo "Warning: Failed to start $SERVICE_NAME. Check logs for details."
}

# Check service status
echo "Service status:"
sudo systemctl status "$SERVICE_NAME"


# --- Desktop autostart for GUI (LXDE/desktop login) ---
AUTOSTART_DIR="$USER_HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/mobilerobot-updater.desktop"
PYTHON_EXEC=$(command -v python3)

echo "Setting up desktop autostart for GUI updater..."
mkdir -p "$AUTOSTART_DIR"
cat > "$AUTOSTART_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=MobileRobot Updater
Exec=$PYTHON_EXEC $UPDATER_SCRIPT
X-GNOME-Autostart-enabled=true
EOF
chown "$SERVICE_USER":"$SERVICE_USER" "$AUTOSTART_FILE"
echo "Desktop autostart entry created at $AUTOSTART_FILE"

echo "Setup complete! The MCupdater service will run automatically when needed."
echo "To manually trigger an update, run: sudo systemctl start $SERVICE_NAME"
echo "To check logs, see: $LOG_FILE_PATH/$STANDARD_OUTPUT"
echo "The GUI updater will also run on desktop login for user $SERVICE_USER."