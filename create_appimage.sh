#!/bin/bash

# Script to create a true AppImage from Nuitka standalone build

APP_NAME="ProductivityTracker"
LOWER_NAME="productivity-tracker"
BINARY_NAME="productivity_tracker"
BUILD_DIR="output/main.dist"
APPDIR="output/AppDir"

# 1. Ensure the Nuitka build exists
if [ ! -d "$BUILD_DIR" ]; then
    echo "Nuitka build not found at $BUILD_DIR. Please run nuitka_build.sh first."
    exit 1
fi

echo "Setting up AppDir structure..."
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/icons/hicolor/scalable/apps"

# 2. Copy the standalone build contents
cp -r "$BUILD_DIR/"* "$APPDIR/usr/bin/"

# 3. Add Desktop file and Icons
# Ensure the desktop file name matches the icon and executable if needed
cp "productivity_tracker.desktop" "$APPDIR/$LOWER_NAME.desktop"
cp "assets/images/icon.svg" "$APPDIR/usr/share/icons/hicolor/scalable/apps/$LOWER_NAME.svg"
cp "assets/images/icon.svg" "$APPDIR/$LOWER_NAME.svg"
ln -s "$LOWER_NAME.svg" "$APPDIR/.DirIcon"

# 4. Create AppRun script
cat <<EOF > "$APPDIR/AppRun"
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"
export PATH="\$HERE/usr/bin:\$PATH"
# Run the binary from its directory so it can find its assets
cd "\$HERE/usr/bin"
exec ./${BINARY_NAME} "\$@"
EOF
chmod +x "$APPDIR/AppRun"

# 5. Download appimagetool if not present
if [ ! -f "appimagetool" ]; then
    echo "Downloading appimagetool..."
    wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
    if [ $? -ne 0 ]; then
        echo "Failed to download appimagetool. Please check your internet connection."
        exit 1
    fi
    chmod +x appimagetool
fi

# 6. Build the AppImage
echo "Building AppImage..."
export ARCH=x86_64

# In Docker or some environments, FUSE might not be available.
# We try to use --appimage-extract-and-run, and if that fails, we try extracting manually.
if [ -n "$DOCKER_BUILD" ] || ! ./appimagetool --version >/dev/null 2>&1; then
    echo "FUSE not available or in Docker, extracting appimagetool..."
    ./appimagetool --appimage-extract >/dev/null
    ./squashfs-root/AppRun "$APPDIR" "${APP_NAME}-x86_64.AppImage"
    rm -rf squashfs-root
else
    ./appimagetool "$APPDIR" "${APP_NAME}-x86_64.AppImage"
fi

if [ $? -ne 0 ]; then
    echo "AppImage creation failed."
    exit 1
fi

echo "Done! Final AppImage created: ${APP_NAME}-x86_64.AppImage"
