@echo off
:: Navigate to the directory of this script
cd /d "%~dp0"

echo Starting Hyperspectral Imaging Application...

if exist "..\exe\HyperspectralImaging.exe" (
    start "" "..\exe\HyperspectralImaging.exe"
) else if exist "..\Source_Code\Py\desktop_app\main.py" (
    python "..\Source_Code\Py\desktop_app\main.py"
) else (
    echo Executable or main script not found.
    pause
)
