#!/bin/bash

# Productivity Tracker Nuitka Build Script

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment 'venv' not found. Please create it first."
    exit 1
fi

# Run Nuitka compilation using the venv
./venv/bin/python3 -m nuitka \
    --standalone \
    --enable-plugin=pyside6 \
    --include-package=controller \
    --include-package=model \
    --include-package=view \
    --follow-imports \
    --output-dir=build \
    --output-filename=productivity_tracker \
    --linux-icon=assets/images/icon.svg \
    main.py

# Copy assets to build directory if compilation succeeded
if [ $? -eq 0 ]; then
    echo "Compilation successful. Copying assets..."
    # The build directory is usually build/main.dist/
    # We want to place assets inside that directory
    mkdir -p build/main.dist/assets
    cp -r assets/* build/main.dist/assets/
    echo "Build complete! You can find the app in build/main.dist/"
    echo "To run: ./build/main.dist/productivity_tracker"
else
    echo "Compilation failed."
fi
