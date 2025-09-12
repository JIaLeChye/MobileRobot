#!/bin/bash

# Variables

USER_NAME=$(whoami)
USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6 2>/dev/null || echo "$HOME")
SERVICE_NAME="battery.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# 先在当前脚本目录查找 Battery.py
BATTERY_SCRIPT=$(find "$SCRIPT_DIR" -maxdepth 2 -name "Battery.py" -print -quit)
# 如果没找到，再全局搜索
if [ -z "$BATTERY_SCRIPT" ]; then
    BATTERY_SCRIPT=$(find / -name "Battery.py" 2>/dev/null | head -n 1)
fi
STANDARD_OUTPUT="Battery_log.txt" 
STANDARD_ERROR_OUTPUT="Battery_error_log.txt" 
LOG_FILE_PATH="$USER_HOME/Desktop/Battery_Log" 

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

if [ -f "$SERVICE_PATH" ]; then 
    echo "Old Battery.service file found" 
    echo "deleting old battery.service file"
    sudo rm $SERVICE_PATH || {
        echo "Error old service file found but unable to remove $SERVICE_PATH" 
        exit 1
    }
fi 
# Copy the service file to /etc/systemd/system/
echo "Copying battery.service to $SERVICE_PATH..."
sudo cp battery.service "$SERVICE_PATH" || {
    echo "Error: Failed to copy battery.service to $SERVICE_PATH."
    exit 1
}

# Update User name 
echo "Updating User Name: $USER_NAME" 
sudo sed -i "s|^User=.*|User=$USER_NAME|" "$SERVICE_PATH" || {
    echo "Error: Fail to modify Username in $SERVICE_PATH"
    exit 1
}

# Update ExecStart and WorkingDirectory in the service file
echo "Updating service file at $SERVICE_PATH..."
sudo sed -i "s|^ExecStart=.*|ExecStart=/usr/bin/python3 $BATTERY_SCRIPT|" "$SERVICE_PATH" || {
    echo "Error: Failed to update ExecStart in $SERVICE_PATH."
    exit 1
}

sudo sed -i "s|^WorkingDirectory=.*|WorkingDirectory=$(dirname "$BATTERY_SCRIPT")|" "$SERVICE_PATH" || {
    echo "Error: Failed to update WorkingDirectory in $SERVICE_PATH."
    exit 1
}

# Update log file paths


echo "Updating log file paths..."


if [ ! -d "$LOG_FILE_PATH" ]; then
    echo "Creating log directory: $LOG_FILE_PATH"
    mkdir -p "$LOG_FILE_PATH" || {
        echo "Error: Failed to create log directory."
        exit 1
    }
else
    echo "Log folder exists: $LOG_FILE_PATH"
fi

sudo sed -i "s|^StandardOutput=.*|StandardOutput=file:$LOG_FILE_PATH/$STANDARD_OUTPUT|" "$SERVICE_PATH" || {
    echo "Error: Failed to update StandardOutput in $SERVICE_PATH."
    exit 1
}

sudo sed -i "s|^StandardError=.*|StandardError=file:$LOG_FILE_PATH/$STANDARD_ERROR_OUTPUT|" "$SERVICE_PATH" || {
    echo "Error: Failed to update StandardError in $SERVICE_PATH."
    exit 1
}

# Verify the service file
echo "Service file updated:"
ls -l "$SERVICE_PATH"

sudo systemctl enable "$SERVICE_NAME" || {
    echo "Error: Failed to enable $SERVICE_NAME."
    exit 1
}
echo "$SERVICE_NAME enabled" 

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
