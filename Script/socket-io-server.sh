#!/bin/bash

# Define the path to your Python application script
app_path="/home/sebastien/Git/MagicDrivePyService/_magicDriveSocketIoServer.py"

# Check if the application script exists
if [ ! -f "$app_path" ]; then
  echo "Error: socket-io server script not found!"
  exit 1
fi

# Start the Python application
echo "Starting Socket-io server..."
/usr/bin/python3 "$app_path"
