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
    sudo sed -i "/^\[Service\]/a ExecStart=/usr/bin/python3 $UPDATER_SCRIPT --service" "$SERVICE_PATH"
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
sudo sed -i "/^\\[Service\\]/,/^\\[/ s|^ExecStart=.*|ExecStart=/usr/bin/python3 $UPDATER_SCRIPT --service|" "$SERVICE_PATH" || {
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

# Inject CLI auto updater block into .bashrc (idempotent)
BASHRC_FILE="$USER_HOME/.bashrc"
AUTO_BLOCK_START="# >>> MOBILE ROBOT AUTO UPDATE START >>>"
AUTO_BLOCK_END="# <<< MOBILE ROBOT AUTO UPDATE END <<<"
# Use the main updater script in headless mode for SSH sessions
CLI_UPDATER_PATH="$UPDATER_SCRIPT"

if [ ! -f "$CLI_UPDATER_PATH" ]; then
    echo "Warning: updater.py not found at $CLI_UPDATER_PATH (auto SSH update will be skipped)."
else
    # Backup and clean .bashrc 
    if [ -f "$BASHRC_FILE" ]; then
        echo "Backing up existing .bashrc to $BASHRC_FILE.mobilebot.bak"
        cp "$BASHRC_FILE" "$BASHRC_FILE.mobilebot.bak" || true
        # Remove problematic lines that could hang the setup
        sed -i '/sudo systemctl.*MCupdater/d' "$BASHRC_FILE" || true
        sed -i '/checking Repository Update/d' "$BASHRC_FILE" || true
    fi
    # Remove existing block if present
    if grep -q "$AUTO_BLOCK_START" "$BASHRC_FILE"; then
        echo "Updating existing auto-update block in .bashrc"
        # Use awk to strip existing block
        awk -v start="$AUTO_BLOCK_START" -v end="$AUTO_BLOCK_END" '
            $0 ~ start {flag=1; next} 
            $0 ~ end {flag=0; next} 
            !flag {print}
        ' "$BASHRC_FILE" > "$BASHRC_FILE.tmp" && mv "$BASHRC_FILE.tmp" "$BASHRC_FILE"
    else
        echo "Adding auto-update block to .bashrc"
    fi
    echo "Adding auto-update block to .bashrc..."
    {
        echo "$AUTO_BLOCK_START"
        echo "# Run repository CLI updater on interactive SSH login"  
        echo "if [ -z \"\${SKIP_REPO_AUTOUPDATE}\" ] \\"
        echo "   && [ -n \"\$SSH_CONNECTION\" ] \\"
        echo "   && [ -t 0 ] && [ -t 1 ]; then"
        echo "    # Avoid recursion if user sources .bashrc inside updater"
        echo "    if [ -z \"\${INSIDE_REPO_AUTOUPDATE}\" ]; then"
        echo "        INSIDE_REPO_AUTOUPDATE=1 python3 \"$CLI_UPDATER_PATH\" --headless || true"
        echo "    fi"
        echo "fi"
        echo "# Show brief updater log summary"
        echo "LOGFILE_DISPLAY_PATH=\"$LOG_FILE_PATH/$STANDARD_OUTPUT\""
        echo "if [ -f \"\$LOGFILE_DISPLAY_PATH\" ]; then"
        echo "    echo \"--- MCupdater current session log: ---\""
        echo "    awk '/^\/----------.*---------\/\$/ {session=\$0; delete lines; n=0; next} {if(session) lines[++n]=\$0} END {if(session) {print \"   \" session; for(i=1;i<=n;i++) print \"   \" lines[i]}}' \"\$LOGFILE_DISPLAY_PATH\" | tail -n 15"
        echo "    echo \"--- End of MCupdater log ---\""
        echo "    # Status summary"
        echo "    CURRENT_SESSION=\$(awk '/^\/----------.*---------\/\$/ {session=\$0; delete lines; n=0; next} {if(session) lines[++n]=\$0} END {if(session) for(i=1;i<=n;i++) print lines[i]}' \"\$LOGFILE_DISPLAY_PATH\")"
        echo "    if echo \"\$CURRENT_SESSION\" | grep -q \"Repository updated successfully\\|Repo updated successfully\"; then"
        echo "        echo \"✅ MCupdater: Repository updated\""
        echo "    elif echo \"\$CURRENT_SESSION\" | grep -q \"Repository up to date\\|already up to date\"; then"
        echo "        echo \"✅ MCupdater: Already up to date\""
        echo "    elif echo \"\$CURRENT_SESSION\" | grep -qi \"network error\\|Network lost\\|Update skipped - no network\\|offline\\|timeout\\|could not resolve\"; then"
        echo "        echo \"❌ MCupdater: Network issue\""
        echo "    elif echo \"\$CURRENT_SESSION\" | grep -qi \"conflict\\|overwrite\\|Local changes conflict\"; then"
        echo "        echo \"⚠️ MCupdater: File conflicts need attention\""
        echo "    else"
        echo "        echo \"ℹ️ MCupdater: Check log above for details\""
        echo "    fi"
        echo "else"
        echo "    echo \"No MCupdater log found at \$LOGFILE_DISPLAY_PATH\""
        echo "fi"
        echo "$AUTO_BLOCK_END"
    } >> "$BASHRC_FILE"
    chown "$SERVICE_USER":"$SERVICE_USER" "$BASHRC_FILE" || true
fi

echo "Setup complete!"
echo "- MCupdater systemd service installed: $SERVICE_NAME"
echo "- CLI auto updater will run on SSH login (set SKIP_REPO_AUTOUPDATE=1 to skip)"
echo "- GUI updater autostarts on desktop login"
echo "To manually force update: python3 $UPDATER_SCRIPT --headless"
echo "Logs: $LOG_FILE_PATH/$STANDARD_OUTPUT"