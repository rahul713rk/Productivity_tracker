#!/bin/bash

# Unified Build Script for Productivity Tracker

echo "Starting build process..."

# 1. Run Nuitka Build
echo "--- Running Nuitka Build ---"
bash nuitka_build.sh
if [ $? -ne 0 ]; then
    echo "Nuitka build failed. Exiting."
    exit 1
fi

# 2. Build AppImage
echo "--- Building AppImage ---"
bash create_appimage.sh
if [ $? -ne 0 ]; then
    echo "AppImage build failed."
else
    echo "AppImage build successful."
fi

# 3. Build Debian Package
echo "--- Building Debian Package ---"
bash create_deb.sh
if [ $? -ne 0 ]; then
    echo "Debian package build failed."
else
    echo "Debian package build successful."
fi

# 4. Build Snap Package (if snapcraft is installed)
if command -v snapcraft >/dev/null 2>&1; then
    echo "--- Building Snap Package ---"
    snapcraft
    if [ $? -ne 0 ]; then
        echo "Snap build failed."
    else
        echo "Snap build successful."
    fi
else
    echo "Snapcraft not found. Skipping Snap build."
    echo "To build Snap, install snapcraft: sudo snap install snapcraft --classic"
fi

echo "--- All build tasks completed ---"
echo "Build artifacts can be found in the 'output' directory."
# List packages safely without failing the script if some types are missing
ls -lh *.AppImage *.deb *.snap 2>/dev/null || true
ls -R output/main.dist 2>/dev/null | head -n 20 || true
