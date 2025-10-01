#!/bin/bash
# speakup GUI Startup Script

# Activate virtual environment
source venv/bin/activate

# Check if pystray is installed for system tray
if python3 -c "import pystray" 2>/dev/null; then
    echo "🎤 Starte speakup GUI mit System Tray..."
    python3 speakup/gui_tray.py
else
    echo "🎤 Starte speakup GUI (ohne System Tray)..."
    echo "   Für System Tray: pip install pystray pillow"
    python3 speakup/gui.py
fi
