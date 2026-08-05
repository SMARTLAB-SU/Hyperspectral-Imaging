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

# Check if dependencies are missing (system and python libs)
MISSING_DEPS=0
if ! command -v libcamerify &> /dev/null; then
    MISSING_DEPS=1
fi
if ! python3 -c "import PyQt6, cv2, numpy, pandas, matplotlib, sklearn" &> /dev/null; then
    MISSING_DEPS=1
fi

# If anything is missing, open a terminal and run the apt install command automatically
if [ $MISSING_DEPS -eq 1 ]; then
    echo "Missing dependencies detected. Launching terminal to install them..."
    
    # Identify available terminal emulator
    TERMINAL=""
    for t in lxterminal xterm gnome-terminal konsole kitty; do
        if command -v "$t" &> /dev/null; then
            TERMINAL="$t"
            break
        fi
    done
    
    INSTALL_CMD="echo '======================================================='; \
                 echo ' Installing dependencies for Hyperspectral System '; \
                 echo '======================================================='; \
                 echo 'Please enter your sudo password to authorize installation:'; \
                 echo ''; \
                 sudo apt update && sudo apt install -y python3-pyqt6 python3-opencv python3-numpy python3-pandas python3-matplotlib python3-sklearn libcamera-tools; \
                 sudo apt install -y python3-picamera2 || true; \
                 echo ''; \
                 echo '-------------------------------------------------------'; \
                 echo 'Dependency installation completed!'; \
                 echo 'Starting the application now...'; \
                 sleep 2"

    if [ -n "$TERMINAL" ]; then
        if [ "$TERMINAL" = "lxterminal" ]; then
            lxterminal --title="Hyperspectral System Installer" -e bash -c "$INSTALL_CMD"
        elif [ "$TERMINAL" = "xterm" ]; then
            xterm -title "Hyperspectral System Installer" -e bash -c "$INSTALL_CMD"
        else
            "$TERMINAL" -e bash -c "$INSTALL_CMD"
        fi
        # Wait for the terminal to finish the installation process
        sleep 5
    else
        # Fallback inline if no terminal emulator is found
        sudo apt update && sudo apt install -y python3-pyqt6 python3-opencv python3-numpy python3-pandas python3-matplotlib python3-sklearn libcamera-tools
    fi
fi

# Now run the application (avoid libcamerify if native picamera2 is available to prevent device locks)
if python3 -c "from picamera2 import Picamera2" &> /dev/null; then
    echo "Using native Picamera2 driver. Running application..."
    python3 desktop_app/main.py
elif command -v libcamerify &> /dev/null; then
    echo "Using libcamerify compatibility layer. Running application..."
    libcamerify python3 desktop_app/main.py
else
    # Show warning if neither is available, then fallback to standard execution
    python3 -c "
import sys
try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    app = QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle('Camera Driver Warning')
    msg.setText('Both native picamera2 and libcamerify compatibility wrapper are missing. The app will launch in simulation mode.')
    msg.exec()
except Exception:
    pass
"
    python3 desktop_app/main.py
fi
