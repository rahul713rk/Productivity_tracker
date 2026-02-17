#!/bin/bash

# Productivity Tracker Nuitka Build Script

# Ensure Nuitka is installed
if ! command -v nuitka &> /dev/null
then
    echo "Nuitka could not be found. Please install it with 'pip install nuitka'."
    exit
fi

# Run Nuitka compilation
python3 -m nuitka \
    --standalone \
    --enable-plugin=pyside6 \
    --nofollow-imports \
    --include-package=controller \
    --include-package=model \
    --include-package=view \
    --follow-imports \
    --output-dir=build \
    --output-filename=productivity_tracker \
    main.py

# Copy assets to build directory if compilation succeeded
if [ $? -eq 0 ]; then
    echo "Compilation successful. Copying assets..."
    mkdir -p build/main.dist/assets
    cp -r assets/* build/main.dist/assets/
    echo "Build complete! You can find the app in build/main.dist/"
else
    echo "Compilation failed."
fi
