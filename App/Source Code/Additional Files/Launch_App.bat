@echo off
:: Navigate to the directory of this script
cd /d "%~dp0"

echo Starting Hyperspectral Imaging application...
python desktop_app/main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%
    echo Please make sure you have installed all dependencies using:
    echo pip install -r requirements.txt
    echo.
    pause
)
