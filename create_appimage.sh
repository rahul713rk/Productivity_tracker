#!/bin/bash

# Script to create a true AppImage from Nuitka standalone build

APP_NAME="ProductivityTracker"
LOWER_NAME="productivity_tracker"
BUILD_DIR="build/main.dist"
APPDIR="build/AppDir"

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
cp "$LOWER_NAME.desktop" "$APPDIR/$LOWER_NAME.desktop"
cp "assets/images/icon.svg" "$APPDIR/usr/share/icons/hicolor/scalable/apps/$LOWER_NAME.svg"
cp "assets/images/icon.svg" "$APPDIR/icon.svg" # Matches Icon=icon in desktop file

# 4. Create AppRun symlink
cat <<EOF > "$APPDIR/AppRun"
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"
export PATH="\$HERE/usr/bin:\$PATH"
cd "\$HERE/usr/bin"
exec ./$LOWER_NAME "\$@"
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
if [ ! -f "appimagetool" ]; then
    echo "appimagetool found empty or missing."
    exit 1
fi
export ARCH=x86_64
# Use --appimage-extract-and-run to avoid libfuse2 issues
./appimagetool --appimage-extract-and-run "$APPDIR" "${APP_NAME}-x86_64.AppImage"

echo "Done! Final AppImage created: ${APP_NAME}-x86_64.AppImage"
