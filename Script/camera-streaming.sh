#!/bin/bash

# Define the path to your Python application script
app_path="/home/sebastien/Git/MagicDrivePyService/_magicDriveStreaming.py"

# Check if the application script exists
if [ ! -f "$app_path" ]; then
  echo "Error: Streaming service script not found!"
  exit 1
fi

# Start the Python application
echo "Starting Streaming/Tensorflow camera service..."
/usr/bin/python3 "$app_path"
