#!/bin/bash

# List available audio devices
echo "Listing available audio devices:"
aplay -l

# Set HDMI as the default device (replace card and device numbers with your system's values)
HDMI_CARD=0  # Replace with your HDMI card number
HDMI_DEVICE=3  # Replace with your HDMI device number

# Backup the existing ALSA configuration
echo "Backing up existing ALSA configuration..."
sudo cp /etc/asound.conf /etc/asound.conf.bak

# Set HDMI as the default in the ALSA configuration
echo "Setting HDMI as default output device in /etc/asound.conf..."
echo -e "pcm.!default {\n    type hw\n    card $HDMI_CARD\n    device $HDMI_DEVICE\n}" | sudo tee /etc/asound.conf > /dev/null

# Reload ALSA to apply changes
echo "Reloading ALSA..."
sudo alsa force-reload

echo "HDMI audio set as default. Please restart your system if necessary."
