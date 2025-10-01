#!/usr/bin/env python3
"""
speakup - System Verification Script
Prüft ob alle Abhängigkeiten korrekt installiert sind.
"""

import sys
import os

def check_python_version():
    """Prüfe Python-Version"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ❌ Python 3.8+ erforderlich!")
        return False
    return True

def check_imports():
    """Prüfe ob alle Pakete importierbar sind"""
    packages = {
        'numpy': 'NumPy',
        'sounddevice': 'sounddevice',
        'webrtcvad': 'webrtcvad',
        'pynput': 'pynput',
        'pyperclip': 'pyperclip',
        'yaml': 'PyYAML',
        'torch': 'PyTorch',
        'faster_whisper': 'faster-whisper'
    }
    
    all_ok = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - FEHLT!")
            all_ok = False
    
    return all_ok

def check_cuda():
    """Prüfe CUDA-Verfügbarkeit"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA verfügbar - {torch.cuda.get_device_name(0)}")
            print(f"  CUDA Version: {torch.version.cuda}")
            print(f"  Devices: {torch.cuda.device_count()}")
            return True
        else:
            print("⚠ CUDA nicht verfügbar - CPU-Modus wird verwendet")
            return False
    except Exception as e:
        print(f"⚠ CUDA-Check fehlgeschlagen: {e}")
        return False

def check_audio_devices():
    """Prüfe Audio-Geräte"""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        print(f"✓ Audio-Input-Geräte: {len(input_devices)}")
        for i, dev in enumerate(input_devices):
            print(f"  [{i}] {dev['name']}")
        return len(input_devices) > 0
    except Exception as e:
        print(f"✗ Audio-Check fehlgeschlagen: {e}")
        return False

def check_config():
    """Prüfe Konfigurationsdatei"""
    config_path = "speakup/config.yaml"
    if os.path.exists(config_path):
        print(f"✓ Konfiguration vorhanden: {config_path}")
        try:
            import yaml
            with open(config_path, 'r') as f:
                cfg = yaml.safe_load(f)
            print(f"  Hotkey: {cfg.get('hotkey')}")
            print(f"  Engine: {cfg.get('engine')}")
            print(f"  Model: {cfg.get('model')}")
            print(f"  Device: {cfg.get('device')}")
            print(f"  Language: {cfg.get('language')}")
            return True
        except Exception as e:
            print(f"✗ Konfiguration ungültig: {e}")
            return False
    else:
        print(f"✗ Konfiguration fehlt: {config_path}")
        return False

def main():
    print("=" * 50)
    print("🎤 speakup - System Verification")
    print("=" * 50)
    print()
    
    results = []
    
    print("1. Python-Version")
    results.append(check_python_version())
    print()
    
    print("2. Python-Pakete")
    results.append(check_imports())
    print()
    
    print("3. CUDA-Support")
    check_cuda()  # Nicht kritisch
    print()
    
    print("4. Audio-Geräte")
    results.append(check_audio_devices())
    print()
    
    print("5. Konfiguration")
    results.append(check_config())
    print()
    
    print("=" * 50)
    if all(results):
        print("✅ ALLES OK - speakup ist einsatzbereit!")
        print()
        print("Starten mit:")
        print("  ./run.sh")
        print("  ODER: python speakup/main.py")
    else:
        print("❌ FEHLER gefunden - bitte Dependencies installieren")
        print()
        print("Installation:")
        print("  ./setup.sh")
        print("  ODER: pip install -r requirements.txt")
    print("=" * 50)

if __name__ == "__main__":
    main()
