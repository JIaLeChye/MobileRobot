#!/bin/bash

# MCupdater Service Installation Script
# Run this script to install the Mobile Robot Code Updater as a systemd service

set -e

SERVICE_NAME="MCupdater"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/${SERVICE_NAME}.service"

echo "🚀 Installing Mobile Robot Code Updater Service..."

# Check if running as root/sudo
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

# Verify files exist
if [[ ! -f "$SERVICE_FILE" ]]; then
    echo "❌ Service file not found: $SERVICE_FILE"
    exit 1
fi

# Install packaging dependency if not present
echo "📦 Checking Python dependencies..."
python3 -c "import packaging" 2>/dev/null || {
    echo "Installing packaging library..."
    pip3 install packaging
}

# Copy service file to systemd directory
echo "📋 Installing service file..."
cp "$SERVICE_FILE" /etc/systemd/system/

# Set proper permissions
chmod 644 /etc/systemd/system/${SERVICE_NAME}.service

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

# Enable the service (will run at boot)
echo "⚡ Enabling ${SERVICE_NAME} service..."
systemctl enable ${SERVICE_NAME}.service

# Show status
echo "📊 Service status:"
systemctl status ${SERVICE_NAME}.service --no-pager -l

echo ""
echo "✅ MCupdater service installed successfully!"
echo ""
echo "📋 Useful commands:"
echo "  • Check service status:   systemctl status ${SERVICE_NAME}.service"
echo "  • Check service logs:     journalctl -u ${SERVICE_NAME}.service -f"
echo "  • Check updater logs:     tail -f /tmp/mcupdater.log"
echo "  • Run updater manually:   systemctl start ${SERVICE_NAME}.service"
echo "  • Disable service:        systemctl disable ${SERVICE_NAME}.service"
echo "  • Remove service:         systemctl disable ${SERVICE_NAME}.service && rm /etc/systemd/system/${SERVICE_NAME}.service"
echo ""
echo "🔍 The updater will:"
echo "  • Run once at boot after network is available"
echo "  • Check for repository updates automatically"
echo "  • Pull changes and run setup.sh when updates are found"
echo "  • Log all activity to /tmp/mcupdater.log"