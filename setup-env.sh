#!/bin/bash

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
  echo "Error: Python3 is not installed."
fi

# Check if .venv folder exists, create if missing
if [ ! -d ".venv" ]; then
  echo ".venv folder not found. Creating a new virtual environment..."
  python3 -m venv .venv

  if [ $? -ne 0 ]; then
    echo "Failed to create a virtual environment."
  fi

  echo ".venv created successfully."
fi

# Activate the virtual environment (cross-platform support)
echo "Activating the virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

# Check if activation was successful
if [ "$VIRTUAL_ENV" != "" ]; then
  echo "Virtual environment activated: $VIRTUAL_ENV"
else
  echo "Failed to activate the virtual environment."
fi

# Check if requirements.txt exists and install dependencies
if [ ! -f "requirements.txt" ]; then
  echo "Error: requirements.txt file not found in the current directory."
  deactivate # Clean up before exiting.
fi

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt > pip_install.log 2>&1

if [ $? -eq 0 ]; then
  echo "Dependencies installed successfully."
else
  echo "Error occurred while installing dependencies. Check pip_install.log for details."
fi

# Deactivate the virtual environment (optional)
# deactivate
# echo "Virtual environment deactivated."

