#!/bin/bash
# Launch_App.sh - Opens Google Drive download link for Launch_App script
URL="https://drive.google.com/file/d/1r98-Xi5oIY5FQlEpG-3-fmzJGQVb_Eqc/view?usp=drive_link"

echo "Opening Launch_App.sh download link..."

if command -v xdg-open > /dev/null; then
    xdg-open "$URL"
elif command -v open > /dev/null; then
    open "$URL"
elif command -v start > /dev/null; then
    start "$URL"
else
    python3 -m webbrowser "$URL" 2>/dev/null || python -m webbrowser "$URL" 2>/dev/null
fi
