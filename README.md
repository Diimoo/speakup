# 🎤 speakup

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Lokales GPU-beschleunigtes Speech-to-Text Tool mit Hotkey-Steuerung**

Drücken → Sprechen → Text erscheint direkt im aktiven Textfeld.

## 📑 Inhaltsverzeichnis

- [Features](#features)
- [Systemanforderungen](#systemanforderungen)
- [Installation](#installation)
- [Konfiguration](#konfiguration)
- [Verwendung](#verwendung)
- [Troubleshooting](#troubleshooting)
- [Architektur](#architektur)
- [Erweiterte Features](#erweiterte-features-geplant)

## Features

- ✅ **100% Lokal**: Keine Cloud, alle Modelle auf deiner SSD, GPU via CUDA
- ⚡ **Sofortstart**: Globaler Hotkey (Standard: `Ctrl+Shift+Space`)
- 🎯 **Echtzeit-STT**: Low-latency Chunks mit automatischer Punktuation & Casing
- 🖥️ **Universal**: Funktioniert in jedem Textfeld (simuliertes Tippen oder Clipboard)
- 🛡️ **Sicher**: Kein Logging standardmäßig, optional lokales Transcript-Log
- 🔇 **VAD**: Voice Activity Detection stoppt automatisch bei Stille

## Systemanforderungen

- **OS**: Linux (Windows kompatibel, macOS später)
- **GPU**: NVIDIA mit CUDA-Support (optional, läuft auch auf CPU)
- **Python**: 3.8+
- **RAM**: Mind. 4GB (8GB+ empfohlen für `medium`/`large` Modelle)

## Installation

### 1. Repository klonen & Virtual Environment erstellen

```bash
cd ~/Proj/speakup
python3 -m venv venv
source venv/bin/activate
```

### 2. PyTorch mit CUDA installieren

```bash
pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### 3. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 4. System-Abhängigkeiten (Linux)

**Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**Arch Linux:**
```bash
sudo pacman -S portaudio
```

**Fedora/RHEL:**
```bash
sudo dnf install portaudio-devel
```

## Konfiguration

Die Konfigurationsdatei befindet sich unter `speakup/config.yaml`:

```yaml
hotkey: "ctrl+shift+space"   # Hotkey zum Starten/Stoppen
engine: "faster-whisper"     # STT Engine
model: "medium"              # small/medium/large-v3
device: "cuda"               # cuda/cpu/auto
language: "de"               # de/en/auto
insert_mode: "type"          # type (simuliert) | clipboard (schneller)
```

### Modell-Auswahl

- **`small`**: Schnell, niedrige Latenz (~500 MB VRAM)
- **`medium`**: Gut balanciert (~1.5 GB VRAM) ⭐ **Empfohlen**
- **`large-v3`**: Beste Genauigkeit (~3 GB VRAM)

### VAD (Voice Activity Detection)

```yaml
vad:
  enable: true
  aggressiveness: 2          # 0 (sanft) bis 3 (aggressiv)
  min_speech_ms: 300         # Minimale Sprachdauer
  max_silence_ms: 800        # Stille-Timeout für Auto-Stop
```

## Verwendung

### Variante 1: GUI (empfohlen)

**Starten:**
```bash
./run_gui.sh
```

Die GUI bietet:
- 🏛️ **Grafische Steuerung** - Start/Stop per Knopfdruck
- ⚙️ **Einstellungs-Editor** - Alle Optionen bequem anpassen
- 📊 **Live-Status** - Echtzeit-Anzeige
- 📋 **System-Log** - Überwachung aller Aktivitäten
- 🪟 **System Tray** - Minimierung in die Taskleiste

**Siehe:** `GUI_GUIDE.md` für ausführliche GUI-Dokumentation

### Variante 2: CLI (Terminal)

**Starten:**
```bash
source venv/bin/activate
python speakup/main.py
```

Du solltest diese Ausgabe sehen:
```
[speakup] Hotkey: ctrl+shift+space – Engine: faster-whisper – Model: medium
```

### Bedienung

1. **Hotkey drücken** (`Ctrl+Shift+Space`) → Aufnahme startet
2. **Sprechen** → Text wird in Echtzeit erkannt
3. **Hotkey erneut drücken** → Aufnahme stoppt, Text wird eingefügt

**Alternativ**: Mit aktiviertem VAD stoppt die Aufnahme automatisch nach Stille.

### Tipps

- Öffne ein beliebiges Textfeld (Editor, Browser, IDE, etc.)
- Platziere den Cursor an der gewünschten Stelle
- Aktiviere speakup mit dem Hotkey und sprich klar
- Der Text erscheint direkt dort, wo dein Cursor ist

## Troubleshooting

### Kein Mikrofon gefunden

```bash
# Mikrofone auflisten
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Falls dein Mikrofon nicht das Standardgerät ist, kannst du es in `main.py` manuell setzen:
```python
sd.default.device = 1  # Device-ID aus obigem Befehl
```

### CUDA nicht verfügbar

Wenn du keine NVIDIA GPU hast, setze in `config.yaml`:
```yaml
device: "cpu"
```

Das Tool läuft auch auf CPU, allerdings mit höherer Latenz.

### Hotkey funktioniert nicht

- Stelle sicher, dass keine andere Anwendung den gleichen Hotkey verwendet
- Teste einen alternativen Hotkey in `config.yaml`, z.B.:
  ```yaml
  hotkey: "ctrl+shift+m"
  ```

### Permission-Fehler bei Tastatureingabe (Linux)

Füge deinen User zur `input`-Gruppe hinzu:
```bash
sudo usermod -a -G input $USER
# Logout/Login erforderlich
```

### Modell wird heruntergeladen

Beim ersten Start lädt `faster-whisper` das gewählte Modell automatisch herunter:
- `small`: ~470 MB
- `medium`: ~1.5 GB
- `large-v3`: ~3 GB

Die Modelle werden im Cache gespeichert (`~/.cache/huggingface/`).

## Projektstruktur

```
speakup/
├── speakup/
│   ├── __init__.py     # Modul-Metadata
│   ├── main.py        # Hauptprogramm (CLI)
│   ├── gui.py         # GUI-Anwendung
│   ├── gui_tray.py    # GUI mit System Tray
│   └── config.yaml    # Konfiguration
├── models/            # Optional: Lokale Modelle
├── venv/              # Virtual Environment
├── setup.sh           # Installations-Script
├── run.sh             # CLI-Start-Script
├── run_gui.sh         # GUI-Start-Script
├── verify.py          # System-Verifikation
├── requirements.txt   # Python-Dependencies
├── README.md          # Diese Datei
├── GUI_GUIDE.md       # GUI-Dokumentation
├── QUICKSTART.md      # Schnelleinstieg
├── SUMMARY.md         # Projekt-Übersicht
└── ROADMAP.md         # Entwicklungs-Roadmap
```

## Erweiterte Features

**Implementiert:**
- [x] GUI mit grafischer Steuerung
- [x] Einstellungs-Editor
- [x] System Tray Icon
- [x] Live-Status-Anzeige
- [x] System-Log

**Geplant:**
- [ ] Live-Preview Overlay (OSD mit erkanntem Text)
- [ ] Auto-Language Detection
- [ ] Prefix-/Suffix-Snippets (z.B. `> ` für Notizen)
- [ ] Domänen-Profile (Ticket-Jargon, E-Mail-Stil)
- [ ] Push-to-Talk Mode (Taste gedrückt halten)
- [ ] macOS Support

## Architektur

```
┌─────────────┐
│   Hotkey    │ → Ctrl+Shift+Space (global)
└──────┬──────┘
       │
┌──────▼───────────────────┐
│   Audio Input Stream     │ → sounddevice (PortAudio)
│   + WebRTC VAD           │
└──────┬───────────────────┘
       │ PCM 16kHz mono
┌──────▼───────────────────┐
│   STT Worker (async)     │ → faster-whisper (GPU)
│   Sliding Window         │
└──────┬───────────────────┘
       │ Text chunks
┌──────▼───────────────────┐
│   Typer / Clipboard      │ → pynput (simuliertes Tippen)
└──────────────────────────┘
```

## Technologien

- **STT**: [faster-whisper](https://github.com/guillaumekln/faster-whisper) (CTranslate2)
- **Audio**: [sounddevice](https://python-sounddevice.readthedocs.io/) (PortAudio)
- **VAD**: [webrtcvad](https://github.com/wiseman/py-webrtcvad)
- **Hotkeys**: [pynput](https://pynput.readthedocs.io/)
- **GPU**: CUDA via PyTorch/CTranslate2

## Lizenz

MIT License - Siehe LICENSE Datei für Details.

## Mitwirken

Contributions sind willkommen! Bitte öffne ein Issue oder Pull Request.

---

**Made with ❤️ for local-first voice input**
