#!/bin/bash
# speakup Auto-Setup Script (ohne Interaktion)

set -e

echo "🎤 speakup Auto-Setup"
echo "=================="
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

# Check for CUDA
echo ""
if command -v nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA GPU gefunden - installiere PyTorch mit CUDA..."
    pip install torch --index-url https://download.pytorch.org/whl/cu121
else
    echo "⚠️  Keine NVIDIA GPU gefunden - installiere CPU-Version..."
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
echo "   1. GUI starten: ./run_gui.sh"
echo "   2. Oder CLI: ./run.sh"
echo "   3. Oder Konfiguration prüfen: python3 verify.py"
echo ""
