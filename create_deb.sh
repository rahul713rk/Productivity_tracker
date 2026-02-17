#!/bin/bash

# Script to create a .deb package from Nuitka standalone build

APP_NAME="productivity-tracker"
VERSION="1.0"
ARCH="amd64"
BUILD_DIR="build/main.dist"
DEB_ROOT="build/deb_package"
INSTALL_LOCATION="/opt/$APP_NAME"

# 1. Ensure the Nuitka build exists
if [ ! -d "$BUILD_DIR" ]; then
    echo "Nuitka build not found at $BUILD_DIR. Please run nuitka_build.sh first."
    exit 1
fi

echo "Setting up DEB package structure..."
# Clean previous build attempt
if [ -d "$DEB_ROOT" ]; then
    rm -rf "$DEB_ROOT"
fi

# Create directory structure
mkdir -p "$DEB_ROOT/DEBIAN"
mkdir -p "$DEB_ROOT$INSTALL_LOCATION"
mkdir -p "$DEB_ROOT/usr/bin"
mkdir -p "$DEB_ROOT/usr/share/applications"
mkdir -p "$DEB_ROOT/usr/share/icons/hicolor/scalable/apps"

# 2. Copy the standalone build contents to /opt/productivity-tracker
echo "Copying application files..."
cp -r "$BUILD_DIR/"* "$DEB_ROOT$INSTALL_LOCATION/"

# 3. Create a wrapper script in /usr/bin to launch the app
echo "Creating launcher script..."
cat <<EOF > "$DEB_ROOT/usr/bin/$APP_NAME"
#!/bin/bash
exec "$INSTALL_LOCATION/productivity_tracker" "\$@"
EOF
chmod 755 "$DEB_ROOT/usr/bin/$APP_NAME"

# 4. Copy Icon and Desktop File
echo "Setting up desktop integration..."
cp "assets/images/icon.svg" "$DEB_ROOT/usr/share/icons/hicolor/scalable/apps/$APP_NAME.svg"

# Create the .desktop file
cat <<EOF > "$DEB_ROOT/usr/share/applications/$APP_NAME.desktop"
[Desktop Entry]
Name=Productivity Tracker
Exec=$APP_NAME
Icon=$APP_NAME
Type=Application
Categories=Utility;
Comment=Track your productivity with face detection and global input tracking.
Terminal=false
EOF
chmod 644 "$DEB_ROOT/usr/share/applications/$APP_NAME.desktop"

# 5. Create Control File
echo "Generating control file..."
# Calculate generic installed size in KB
SIZE=$(du -sk "$DEB_ROOT" | cut -f1)

cat <<EOF > "$DEB_ROOT/DEBIAN/control"
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Maintainer: Rahul <rahul@example.com>
Depends: libgl1-mesa-glx, libxcb-cursor0
Installed-Size: $SIZE
Description: Productivity Tracker
 A productivity tracker that monitors camera feed for face detection 
 and tracks global input events to provide insights into your work habits.
 .
 Built with Python, PySide6, and MediaPipe.
EOF

# 6. Build the .deb package
echo "Building .deb package..."
dpkg-deb --build "$DEB_ROOT" "${APP_NAME}_${VERSION}_${ARCH}.deb"

echo "Done! Final DEB package created: ${APP_NAME}_${VERSION}_${ARCH}.deb"
