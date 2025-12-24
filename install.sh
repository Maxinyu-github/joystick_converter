#!/bin/bash
# Joystick Converter Installation Script for Raspberry Pi

set -e

echo "========================================="
echo "Joystick Converter Installation Script"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get the actual user (not root when using sudo)
ACTUAL_USER="${SUDO_USER:-pi}"
ACTUAL_HOME=$(eval echo "~$ACTUAL_USER")
INSTALL_DIR="$ACTUAL_HOME/joystick_converter"

echo "Installing to: $INSTALL_DIR"
echo "User: $ACTUAL_USER"
echo ""

# Update system
echo "Step 1: Updating system packages..."
apt update
apt upgrade -y

# Install dependencies
echo ""
echo "Step 2: Installing dependencies..."
apt install -y python3 python3-pip python3-dev git

# Install Python packages
echo ""
echo "Step 3: Installing Python packages..."
pip3 install flask evdev --break-system-packages

# Copy files if not already in home directory
if [ "$PWD" != "$INSTALL_DIR" ]; then
    echo ""
    echo "Step 4: Copying files to $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
    cp -r . "$INSTALL_DIR/"
    chown -R "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR"
fi

# Create config directory
echo ""
echo "Step 5: Creating configuration directory..."
mkdir -p "$INSTALL_DIR/config/examples"
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR/config"

# Enable USB Gadget mode
echo ""
echo "Step 6: Configuring USB Gadget mode..."

# Add to /boot/config.txt
if ! grep -q "dtoverlay=dwc2" /boot/config.txt; then
    echo "dtoverlay=dwc2" >> /boot/config.txt
    echo "Added dtoverlay=dwc2 to /boot/config.txt"
else
    echo "dtoverlay=dwc2 already in /boot/config.txt"
fi

# Add to /boot/cmdline.txt
if ! grep -q "modules-load=dwc2,libcomposite" /boot/cmdline.txt; then
    sed -i 's/rootwait/rootwait modules-load=dwc2,libcomposite/' /boot/cmdline.txt
    echo "Added modules to /boot/cmdline.txt"
else
    echo "Modules already in /boot/cmdline.txt"
fi

# Load modules now
echo ""
echo "Step 7: Loading kernel modules..."
modprobe dwc2 || true
modprobe libcomposite || true

# Install systemd services
echo ""
echo "Step 8: Installing systemd services..."

# Update service file paths
sed -i "s|/home/pi/joystick_converter|$INSTALL_DIR|g" "$INSTALL_DIR/systemd/joystick-converter.service"
sed -i "s|/home/pi/joystick_converter|$INSTALL_DIR|g" "$INSTALL_DIR/systemd/joystick-web.service"

# Update user in web service
sed -i "s|User=pi|User=$ACTUAL_USER|g" "$INSTALL_DIR/systemd/joystick-web.service"

# Copy service files
cp "$INSTALL_DIR/systemd/joystick-converter.service" /etc/systemd/system/
cp "$INSTALL_DIR/systemd/joystick-web.service" /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Reboot your Raspberry Pi: sudo reboot"
echo "2. After reboot, start the services:"
echo "   sudo systemctl start joystick-converter"
echo "   sudo systemctl start joystick-web"
echo ""
echo "3. Enable auto-start on boot:"
echo "   sudo systemctl enable joystick-converter"
echo "   sudo systemctl enable joystick-web"
echo ""
echo "4. Access the web interface:"
echo "   http://$(hostname -I | awk '{print $1}'):8080"
echo ""
echo "5. Check service status:"
echo "   sudo systemctl status joystick-converter"
echo "   sudo systemctl status joystick-web"
echo ""
echo "Configuration file: $INSTALL_DIR/config/mappings.json"
echo "========================================="
