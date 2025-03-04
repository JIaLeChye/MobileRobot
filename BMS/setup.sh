#!/bin/bash 
USER_HOME="/home/raspberry"
SERVICE_NAME="battery.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"

# Find the absolute path of Battery.py in the user's Desktop
BATTERY_SCRIPT=$(find "$USER_HOME/Desktop" -name "Battery.py" -print -quit)

if [ -z "$BATTERY_SCRIPT" ]; then
    echo "Error: Battery.py not found on the Desktop."
    exit 1
fi

echo "Battery script found at: $BATTERY_SCRIPT"
echo "Updating service file at $SERVICE_PATH..."
ls -l "$SERVICE_PATH"

# Update ExecStart and WorkingDirectory in the service file
sudo sed -i "s|ExecStart=.*|ExecStart=/usr/bin/python3 $BATTERY_SCRIPT|" "$SERVICE_PATH"
sudo sed -i "s|WorkingDirectory=.*|WorkingDirectory=$(dirname "$BATTERY_SCRIPT")|" "$SERVICE_PATH"

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Restarting ${SERVICE_NAME}..."
sudo systemctl restart ${SERVICE_NAME}

echo "Service status:"
sudo systemctl status ${SERVICE_NAME}
