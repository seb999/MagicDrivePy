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


# Define the path to your .NET Core application executable
app_path2="/home/sebastien/Git/MagicDrive/bin/Release/net6.0/MagicDrive.dll"

# Check if the application executable exists
if [ ! -f "$app_path2" ]; then
  echo "Error: Application MagicDrive executable not found!"
  exit 1
fi

# Start the .NET Core application
echo "Starting MagicDrive .NET Core application..."
#$HOME/.dotnet/dotnet "$app_path2"
/home/sebastien/.dotnet/dotnet "$app_path2"


# Define the path to your Python application script
app_path3="/home/sebastien/Git/MagicDrivePyService/_magicDriveStreaming.py"

# Check if the application script exists
if [ ! -f "$app_path3" ]; then
  echo "Error: Streaming service script not found!"
  exit 1
fi

# Start the Python application
echo "Starting Streaming/Tensorflow camera service..."
/usr/bin/python3 "$app_path3"

