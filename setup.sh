#!/bin/bash
# speakup Setup Script for Linux

set -e

echo "🎤 speakup Setup"
echo "================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ Python 3.8+ erforderlich. Gefunden: Python $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION gefunden"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Erstelle Virtual Environment..."
    python3 -m venv venv
    echo "✓ Virtual Environment erstellt"
else
    echo "✓ Virtual Environment existiert bereits"
fi

# Activate virtual environment
source venv/bin/activate

echo ""
echo "📦 Installiere Dependencies..."

# Upgrade pip
pip install --upgrade pip -q

# Install PyTorch with CUDA support
echo ""
echo "⚙️  Installiere PyTorch mit CUDA-Support..."
read -p "Hast du eine NVIDIA GPU mit CUDA? (y/n): " has_cuda

if [ "$has_cuda" = "y" ] || [ "$has_cuda" = "Y" ]; then
    pip install torch --index-url https://download.pytorch.org/whl/cu121
else
    echo "⚠️  CPU-Version wird installiert (langsamer)..."
    pip install torch
fi

# Install other requirements
echo ""
echo "📦 Installiere weitere Pakete..."
pip install -r requirements.txt

echo ""
echo "✅ Installation abgeschlossen!"
echo ""
echo "📋 Nächste Schritte:"
echo "   1. Konfiguration anpassen: speakup/config.yaml"
echo "   2. Starten: python speakup/main.py"
echo "   3. Hotkey drücken: Ctrl+Shift+Space"
echo ""
echo "💡 Tipp: Falls du Probleme mit dem Mikrofon hast:"
echo "   python -c 'import sounddevice as sd; print(sd.query_devices())'"
echo ""
