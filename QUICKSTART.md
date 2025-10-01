# 🚀 Quick Start Guide - speakup

## Installation in 4 Schritten

### 1. Setup ausführen

```bash
./setup.sh
```

Das Script:
- Erstellt ein Virtual Environment
- Installiert PyTorch (mit CUDA-Unterstützung falls verfügbar)
- Installiert alle Dependencies

### 2. Konfiguration anpassen (optional)

```bash
nano speakup/config.yaml
```

**Wichtige Settings:**
- `device: "cuda"` → auf `"cpu"` ändern falls keine NVIDIA GPU
- `model: "medium"` → `"small"` für schnellere Performance
- `language: "de"` → `"en"` oder `"auto"` für andere Sprachen

### 3. System verifizieren (optional)

```bash
python verify.py
```

Prüft:
- Python-Version
- Alle Dependencies
- CUDA-Verfügbarkeit
- Audio-Geräte
- Konfiguration

### 4. Starten

**Option A: GUI (empfohlen)**
```bash
./run_gui.sh
```

**Option B: CLI (Terminal)**
```bash
./run.sh
```

Oder manuell:
```bash
source venv/bin/activate
python speakup/main.py     # CLI
python speakup/gui.py      # GUI
```

## Verwendung

### GUI-Modus

1. **GUI starten**: `./run_gui.sh`
2. **Tab "Einstellungen"**: Konfiguration prüfen/anpassen
3. **Tab "Steuerung"**: ▶ Starten klicken
4. **Hotkey nutzen**: `Ctrl+Shift+Space` zum Aufnehmen
5. **Sprechen**: Text erscheint automatisch

📚 **Siehe `GUI_GUIDE.md` für ausführliche GUI-Dokumentation**

### CLI-Modus

1. **Hotkey drücken**: `Ctrl+Shift+Space`
2. **Sprechen**: Klar und deutlich
3. **Hotkey erneut drücken**: Oder warten bis VAD automatisch stoppt
4. **Text erscheint**: Direkt im aktiven Textfeld

## Probleme?

### Mikrofon testen
```bash
source venv/bin/activate
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### CUDA nicht verfügbar
In `config.yaml`:
```yaml
device: "cpu"
```

### Hotkey-Konflikt
In `config.yaml`:
```yaml
hotkey: "ctrl+shift+m"  # Alternative
```

### Permission-Fehler (Linux)
```bash
sudo usermod -a -G input $USER
# Dann logout/login
```

## Modell-Download beim ersten Start

Beim ersten Start lädt `faster-whisper` das Modell automatisch:
- `small`: ~470 MB
- `medium`: ~1.5 GB (empfohlen)
- `large-v3`: ~3 GB (beste Qualität)

## Performance-Tipps

**Für niedrige Latenz:**
```yaml
model: "small"
chunk:
  seconds: 0.5
  overlap: 0.1
```

**Für beste Genauigkeit:**
```yaml
model: "large-v3"
device: "cuda"
chunk:
  seconds: 1.0
  overlap: 0.3
```

**Für mehrsprachig:**
```yaml
language: "auto"
```

## Tipps & Tricks

- **Lautstärke**: Spreche mit normaler Lautstärke, nicht zu laut/leise
- **Hintergrundgeräusche**: VAD filtert Stille, aber minimiere Störgeräusche
- **Mikrofon-Position**: 15-30 cm Abstand optimal
- **Satzpausen**: Kurze Pausen für bessere Segmentierung
- **GPU-Monitoring**: `nvidia-smi` um VRAM-Nutzung zu checken

---

**Weitere Infos**: Siehe `README.md` für vollständige Dokumentation
