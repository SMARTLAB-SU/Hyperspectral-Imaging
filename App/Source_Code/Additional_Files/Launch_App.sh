#!/bin/bash
# Get absolute path of this script and directory
SCRIPT_PATH="$(realpath "$0" 2>/dev/null || readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

# Navigate to the directory of this script
cd "$SCRIPT_DIR"

# Automatically create a desktop shortcut icon if it does not exist
DESKTOP_DIR="$HOME/Desktop"
if [ -d "$DESKTOP_DIR" ]; then
    DESKTOP_FILE="$DESKTOP_DIR/hyperspectral.desktop"
    if [ ! -f "$DESKTOP_FILE" ]; then
        echo "Creating desktop shortcut..."
        cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name=Hyperspectral Imaging
Comment=Launch Hyperspectral Imaging System
Exec=/bin/bash "$SCRIPT_PATH"
Icon=$SCRIPT_DIR/sanjivani.png
Terminal=false
Type=Application
Categories=Utility;
EOF
        chmod +x "$DESKTOP_FILE"
    fi
fi

# Run the application using Python 3 with libcamerify for Pi Camera Module 3 support
libcamerify python3 desktop_app/main.py
