#!/bin/bash

# Productivity Tracker Nuitka Build Script

# Ensure virtual environment exists (skip if running in Docker where we pre-install deps)
if [ ! -d "venv" ] && [ -z "$DOCKER_BUILD" ]; then
    echo "Virtual environment 'venv' not found. Please create it first or run via docker_build.sh."
    exit 1
fi

PYTHON_EXE="./venv/bin/python3"
if [ ! -f "$PYTHON_EXE" ]; then
    PYTHON_EXE="python3"
fi

# Clean previous output to avoid stale artifacts
echo "Cleaning output directory..."
rm -rf output/

# Run Nuitka compilation
$PYTHON_EXE -m nuitka \
    --standalone \
    --enable-plugin=pyside6 \
    --include-package=controller \
    --include-package=model \
    --include-package=view \
    --include-package=mediapipe \
    --include-package-data=mediapipe \
    --follow-imports \
    --output-dir=output \
    --output-filename=productivity_tracker \
    --linux-icon=assets/images/icon.svg \
    main.py

# Copy assets to output directory if compilation succeeded
if [ $? -eq 0 ]; then
    echo "Compilation successful. Copying assets..."
    # The output directory is output/main.dist/
    mkdir -p output/main.dist/assets
    cp -r assets/* output/main.dist/assets/
    echo "Build complete! You can find the app in output/main.dist/"
    echo "To run: ./output/main.dist/productivity_tracker"
else
    echo "Compilation failed."
fi
