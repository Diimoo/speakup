#!/bin/bash
# Install system dependencies for speakup

echo "📦 Installiere System-Abhängigkeiten für speakup..."
echo ""

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ Konnte Linux-Distribution nicht erkennen"
    exit 1
fi

case $OS in
    ubuntu|debian|pop)
        echo "✓ Erkannt: Ubuntu/Debian-basiert"
        echo ""
        echo "Installiere:"
        echo "  - python3-tk (für GUI)"
        echo "  - portaudio19-dev (für Audio)"
        echo ""
        sudo apt-get update
        sudo apt-get install -y python3-tk portaudio19-dev python3-dev
        ;;
    
    fedora|rhel|centos)
        echo "✓ Erkannt: Fedora/RHEL-basiert"
        echo ""
        sudo dnf install -y python3-tkinter portaudio-devel python3-devel
        ;;
    
    arch|manjaro)
        echo "✓ Erkannt: Arch-basiert"
        echo ""
        sudo pacman -S --noconfirm tk portaudio python
        ;;
    
    opensuse*)
        echo "✓ Erkannt: openSUSE"
        echo ""
        sudo zypper install -y python3-tk portaudio-devel python3-devel
        ;;
    
    *)
        echo "⚠️  Unbekannte Distribution: $OS"
        echo ""
        echo "Bitte installiere manuell:"
        echo "  - Python3 tkinter"
        echo "  - PortAudio development libraries"
        exit 1
        ;;
esac

echo ""
echo "✅ System-Abhängigkeiten installiert!"
echo ""
echo "Nächster Schritt:"
echo "  ./setup_auto.sh"
