#!/bin/bash

# Variables
USER_HOME="$HOME"
SERVICE_NAME="battery.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"
BATTERY_SCRIPT=$(find "$USER_HOME/Desktop" -name "Battery.py" -print -quit)

echo "User Directory is $USER_HOME"

# Check if Battery.py exists
if [ -z "$BATTERY_SCRIPT" ]; then
    echo "Error: Battery.py not found on the Desktop."
    exit 1
fi

echo "Battery script found at: $BATTERY_SCRIPT"

# Check if battery.service file exists in the current directory
if [ ! -f "battery.service" ]; then
    echo "Error: battery.service file not found in the current directory."
    exit 1
fi

# Copy the service file to /etc/systemd/system/
echo "Copying battery.service to $SERVICE_PATH..."
sudo cp battery.service "$SERVICE_PATH" || {
    echo "Error: Failed to copy battery.service to $SERVICE_PATH."
    exit 1
}

# Update ExecStart and WorkingDirectory in the service file
echo "Updating service file at $SERVICE_PATH..."
sudo sed -i "s|ExecStart=.*|ExecStart=/usr/bin/python3 $BATTERY_SCRIPT|" "$SERVICE_PATH" || {
    echo "Error: Failed to update ExecStart in $SERVICE_PATH."
    exit 1
}

sudo sed -i "s|WorkingDirectory=.*|WorkingDirectory=$(dirname "$BATTERY_SCRIPT")|" "$SERVICE_PATH" || {
    echo "Error: Failed to update WorkingDirectory in $SERVICE_PATH."
    exit 1
}

# Verify the service file
echo "Service file updated:"
ls -l "$SERVICE_PATH"cd

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload || {
    echo "Error: Failed to reload systemd daemon."
    exit 1
}

# Restart the service
echo "Restarting ${SERVICE_NAME}..."
sudo systemctl restart "$SERVICE_NAME" || {
    echo "Error: Failed to restart $SERVICE_NAME."
    exit 1
}

# Check service status
echo "Service status:"
sudo systemctl status "$SERVICE_NAME"