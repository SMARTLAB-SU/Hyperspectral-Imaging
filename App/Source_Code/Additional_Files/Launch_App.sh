#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "Starting Hyperspectral Imaging Application..."

if [ -f "../../exe/HyperspectralImaging.exe" ]; then
    ../../exe/HyperspectralImaging.exe
elif [ -f "../Py/desktop_app/main.py" ]; then
    python3 "../Py/desktop_app/main.py"
else
    echo "Executable or main script not found."
fi
