#!/bin/bash

# Activate virtual environment
if [ -d "jellyenv" ]; then
    source jellyenv/bin/activate
else
    echo "Virtual environment not found. Creating one..."
    python3 -m venv jellyenv
    source jellyenv/bin/activate
    pip install -r requirements.txt
fi

# Check if config.py exists
if [ ! -f "config.py" ]; then
    echo "config.py not found. Creating from template..."
    if [ -f "config.template.py" ]; then
        cp config.template.py config.py
        echo "Please edit config.py with your Jellyfin API key and server information."
        exit 1
    else
        echo "config.template.py not found. Cannot create config.py."
        exit 1
    fi
fi

# Start the application
python3 JellySearchV3.py