#!/bin/bash
"""
Install Boot Self-Test System
=============================

This script installs the boot self-test as a system service
to run automatically when the robot starts up.

Usage:
  sudo ./install_boot_test.sh [options]

Options:
  --enable     Install and enable the service (default)
  --disable    Disable the service
  --remove     Remove the service completely
  --status     Show service status
  
Author: GitHub Copilot
Date: September 2025
"""

SERVICE_NAME="robot-boot-test"
SERVICE_FILE="robot-boot-test.service"
INSTALL_PATH="/etc/systemd/system/$SERVICE_NAME.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_files() {
    if [ ! -f "$SCRIPT_DIR/$SERVICE_FILE" ]; then
        print_error "Service file not found: $SERVICE_FILE"
        exit 1
    fi
    
    if [ ! -f "$SCRIPT_DIR/boot_self_test.py" ]; then
        print_error "Boot test script not found: boot_self_test.py"
        exit 1
    fi
    
    if [ ! -f "$SCRIPT_DIR/complete_self_test.py" ]; then
        print_error "Complete test script not found: complete_self_test.py"
        exit 1
    fi
}

install_service() {
    print_status "Installing robot boot self-test service..."
    
    # Copy service file
    cp "$SCRIPT_DIR/$SERVICE_FILE" "$INSTALL_PATH"
    print_success "Service file copied to $INSTALL_PATH"
    
    # Make boot test script executable
    chmod +x "$SCRIPT_DIR/boot_self_test.py"
    print_success "Boot test script made executable"
    
    # Reload systemd
    systemctl daemon-reload
    print_success "Systemd configuration reloaded"
    
    # Enable service
    systemctl enable "$SERVICE_NAME"
    print_success "Service enabled for startup"
    
    print_success "Boot self-test service installed successfully!"
    print_status "The robot will now run self-tests on every boot"
    print_status "Use 'sudo systemctl status $SERVICE_NAME' to check status"
}

disable_service() {
    print_status "Disabling robot boot self-test service..."
    
    systemctl disable "$SERVICE_NAME"
    systemctl stop "$SERVICE_NAME" 2>/dev/null
    
    print_success "Service disabled"
}

remove_service() {
    print_status "Removing robot boot self-test service..."
    
    # Stop and disable service
    systemctl stop "$SERVICE_NAME" 2>/dev/null
    systemctl disable "$SERVICE_NAME" 2>/dev/null
    
    # Remove service file
    if [ -f "$INSTALL_PATH" ]; then
        rm "$INSTALL_PATH"
        print_success "Service file removed"
    fi
    
    # Reload systemd
    systemctl daemon-reload
    
    print_success "Service removed completely"
}

show_status() {
    print_status "Robot Boot Self-Test Service Status:"
    echo
    
    if [ -f "$INSTALL_PATH" ]; then
        print_success "Service file exists: $INSTALL_PATH"
        
        if systemctl is-enabled "$SERVICE_NAME" >/dev/null 2>&1; then
            print_success "Service is enabled"
        else
            print_warning "Service is disabled"
        fi
        
        if systemctl is-active "$SERVICE_NAME" >/dev/null 2>&1; then
            print_success "Service is running"
        else
            print_status "Service is not currently running (normal for oneshot service)"
        fi
        
        echo
        print_status "Recent service logs:"
        journalctl -u "$SERVICE_NAME" --no-pager -n 10
        
    else
        print_warning "Service is not installed"
    fi
}

# Main script logic
case "${1:-enable}" in
    "enable"|"install")
        check_root
        check_files
        install_service
        ;;
    "disable")
        check_root
        disable_service
        ;;
    "remove"|"uninstall")
        check_root
        remove_service
        ;;
    "status")
        show_status
        ;;
    *)
        echo "Usage: $0 [enable|disable|remove|status]"
        echo
        echo "Commands:"
        echo "  enable   - Install and enable boot self-test (default)"
        echo "  disable  - Disable boot self-test"
        echo "  remove   - Remove boot self-test completely"
        echo "  status   - Show current status"
        exit 1
        ;;
esac
