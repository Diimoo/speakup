# 🖥️ speakup GUI - Benutzerhandbuch

## Übersicht

Die speakup GUI bietet eine grafische Benutzeroberfläche zur einfachen Steuerung und Konfiguration des Speech-to-Text Tools.

## Features

- ✅ **Grafische Steuerung**: Start/Stop per Knopfdruck
- ⚙️ **Einstellungs-Editor**: Alle Optionen bequem anpassen
- 📊 **Live-Status**: Echtzeit-Anzeige des aktuellen Zustands
- 📋 **System-Log**: Überwachung aller Aktivitäten
- 🔧 **Erweiterte Optionen**: VAD & Chunk-Einstellungen
- 🪟 **System Tray**: Minimierung in die Taskleiste (optional)

## Installation

### GUI-Dependencies installieren

```bash
source venv/bin/activate
pip install pystray pillow  # Für System Tray (optional)
```

Die GUI benötigt:
- **tkinter** (meist in Python vorinstalliert)
- **pystray** (optional, für System Tray)
- **Pillow** (optional, für System Tray Icon)

## Starten

### Mit System Tray Support
```bash
./run_gui.sh
```

### Alternativ direkt
```bash
source venv/bin/activate
python speakup/gui.py        # Ohne System Tray
python speakup/gui_tray.py   # Mit System Tray
```

## Benutzeroberfläche

### Tab 1: 🎛️ Steuerung

**Status-Anzeige:**
- **🟢 Läuft** - speakup ist aktiv
- **⚫ Gestoppt** - speakup ist inaktiv
- **🎤 Aufnahme läuft** - Aktuell wird aufgenommen

**Buttons:**
- **▶ Starten** - Startet speakup mit aktueller Konfiguration
- **⏸ Stoppen** - Stoppt speakup

**Info-Bereich:**
Zeigt die aktuell geladene Konfiguration an.

### Tab 2: ⚙️ Einstellungen

**Allgemeine Einstellungen:**

| Option | Beschreibung | Werte |
|--------|--------------|-------|
| **Hotkey** | Globale Tastenkombination | z.B. `ctrl+shift+space` |
| **Engine** | STT-Engine | faster-whisper, whispercpp |
| **Modell** | Whisper-Modell | tiny, base, small, medium, large-v2, large-v3 |
| **Device** | Verarbeitungsgerät | cuda, cpu, auto |
| **Sprache** | Zielsprache | auto, de, en, es, fr, it, ... |
| **Eingabemodus** | Texteinfügung | type (simuliert), clipboard |

**Optionen:**
- ✓ **Automatische Punktuation** - Fügt Satzzeichen automatisch hinzu
- ✓ **Transkripte loggen** - Speichert erkannte Texte

**💾 Speichern:**
Klicke auf "Einstellungen speichern" um Änderungen zu übernehmen.

### Tab 3: 🔧 Erweitert

**Voice Activity Detection (VAD):**

| Option | Beschreibung | Bereich |
|--------|--------------|---------|
| **VAD aktivieren** | Spracherkennung ein/aus | Checkbox |
| **Aggressivität** | Empfindlichkeit (0=sanft, 3=aggressiv) | 0-3 |
| **Min. Sprachdauer** | Minimale Aufnahmedauer | 100-2000 ms |
| **Max. Stille** | Timeout für Auto-Stop | 100-3000 ms |

**Chunk-Einstellungen:**

| Option | Beschreibung | Bereich |
|--------|--------------|---------|
| **Chunk-Größe** | Audio-Segment-Länge | 0.3-3.0 s |
| **Overlap** | Überlappung zwischen Chunks | 0.0-1.0 s |

**Empfohlene Werte:**

*Für niedrige Latenz:*
- Chunk-Größe: 0.5s
- Overlap: 0.1s
- VAD Aggressivität: 3

*Für beste Genauigkeit:*
- Chunk-Größe: 1.0s
- Overlap: 0.3s
- VAD Aggressivität: 1-2

### Tab 4: 📋 Log

**System-Log:**
Zeigt alle Aktivitäten und Ereignisse:
- Systemstart/-stop
- Einstellungsänderungen
- Fehler und Warnungen
- Status-Updates

**Funktionen:**
- **🗑️ Log löschen** - Löscht alle Log-Einträge
- **💾 Log speichern** - Exportiert Log in Textdatei

## System Tray

Wenn pystray installiert ist:

**Minimierung:**
- Klicke auf **X** → Fenster wird in System Tray minimiert
- Icon erscheint in der Taskleiste

**Tray-Menü:**
- **Fenster anzeigen** - Holt Fenster zurück
- **Start/Stop** - Toggle speakup
- **Beenden** - Schließt Anwendung komplett

## Hotkey-Konfiguration

**Format:** `modifier+modifier+key`

**Modifier:**
- `ctrl` / `control`
- `shift`
- `alt`
- `cmd` / `super` (Linux/macOS)

**Beispiele:**
- `ctrl+shift+space` (Standard)
- `ctrl+shift+m`
- `alt+shift+s`
- `ctrl+alt+r`

⚠️ **Wichtig:** Nach Änderung des Hotkeys speakup neu starten!

## Workflow

### Erste Schritte

1. **GUI starten:** `./run_gui.sh`
2. **Settings prüfen:** Tab "Einstellungen"
3. **Device anpassen:** Falls keine GPU: `cpu` wählen
4. **Speichern:** Klick auf "Einstellungen speichern"
5. **Starten:** Tab "Steuerung" → "▶ Starten"
6. **Hotkey nutzen:** Drücke konfigurierten Hotkey zum Aufnehmen

### Einstellungen anpassen

1. Zu Tab "Einstellungen" oder "Erweitert" wechseln
2. Gewünschte Werte ändern
3. "💾 Einstellungen speichern" klicken
4. Falls speakup läuft: Stoppen und neu starten für Übernahme

### Modell wechseln

1. **Stoppen** falls läuft
2. Tab "Einstellungen" → Modell auswählen
3. Speichern
4. Neu starten (lädt neues Modell beim Start)

**Download-Zeiten:**
- small: ~1 Min (470 MB)
- medium: ~3 Min (1.5 GB)
- large-v3: ~5-10 Min (3 GB)

## Fehlerbehebung

### GUI startet nicht

**Problem:** `tkinter` fehlt
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

### System Tray Icon fehlt

**Problem:** pystray/Pillow nicht installiert
```bash
source venv/bin/activate
pip install pystray pillow
```

Dann GUI neu starten mit: `python speakup/gui_tray.py`

### "Fehler beim Starten"

**Mögliche Ursachen:**
1. **Dependencies fehlen** → `python verify.py` ausführen
2. **CUDA nicht verfügbar** → Device auf `cpu` setzen
3. **Config ungültig** → Einstellungen prüfen

**Lösung:**
- Log-Tab überprüfen für Details
- Config zurücksetzen: Lösche `speakup/config.yaml` (wird neu erstellt)

### Hotkey funktioniert nicht

1. Prüfe ob andere App denselben Hotkey nutzt
2. Teste alternativen Hotkey
3. Starte speakup neu nach Hotkey-Änderung
4. Linux: Prüfe Berechtigungen (`input` Gruppe)

### Kein Mikrofon erkannt

1. Tab "Log" → Suche nach Fehlermeldung
2. Terminal öffnen:
   ```bash
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```
3. Device-ID notieren und in Code anpassen falls nötig

## Tastenkombinationen

**Im GUI:**
- `Ctrl+Q` - Beenden (falls implementiert)
- `Ctrl+S` - Einstellungen speichern (Tab-abhängig)

**Im Textfeld (während Aufnahme):**
- Konfigurierter Hotkey - Start/Stop Toggle

## Performance-Tipps

**Für flüssige GUI:**
- Modell `small` oder `medium` nutzen
- GPU aktivieren (`cuda`)
- VAD aktiviert lassen

**Bei Problemen:**
- Log-Tab beobachten
- System-Ressourcen prüfen (RAM/GPU)
- Chunk-Größe erhöhen für weniger CPU-Last

## Unterschiede CLI vs GUI

| Feature | CLI (`main.py`) | GUI (`gui.py`) |
|---------|-----------------|----------------|
| Start/Stop | Nur Hotkey | Button + Hotkey |
| Config | Manuelle YAML-Bearbeitung | Grafischer Editor |
| Status | Terminal-Output | Live-Anzeige |
| Log | Nur Console | Scrollbares Log |
| Tray | Nein | Ja (mit gui_tray) |

## Bekannte Limitationen

1. **Kein Echtzeit-Transkript:** Text wird erst nach VAD-Ende angezeigt
2. **Restart erforderlich:** Einige Änderungen (Engine, Modell) brauchen Neustart
3. **Linux-Focus:** Windows/macOS möglicherweise nicht vollständig getestet

## Tipps & Tricks

### Schneller Modell-Wechsel
Erstelle mehrere Config-Profile und lade sie bei Bedarf.

### Hintergrund-Betrieb
Mit System Tray: Minimiere und lasse im Hintergrund laufen.

### Debug-Modus
Log-Tab zeigt alle Events → hilfreich für Troubleshooting.

### Backup der Config
```bash
cp speakup/config.yaml speakup/config.yaml.backup
```

## Screenshots

*(GUI-Screenshots würden hier eingefügt)*

### Hauptfenster - Steuerung Tab
```
┌─────────────────────────────────────┐
│  🎤 speakup - Speech-to-Text       │
├─────────────────────────────────────┤
│ [Steuerung] [Einstellungen] ...    │
│                                     │
│  Status: 🟢 Läuft                   │
│  Hotkey: ctrl+shift+space           │
│                                     │
│  [▶ Starten]  [⏸ Stoppen]          │
│                                     │
│  Aktuelle Konfiguration:            │
│  ┌─────────────────────────────┐   │
│  │ Engine: faster-whisper      │   │
│  │ Model:  medium              │   │
│  │ Device: cuda                │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

**Viel Erfolg mit der speakup GUI! 🎤**

Bei Fragen siehe auch:
- `README.md` - Allgemeine Dokumentation
- `QUICKSTART.md` - Schnelleinstieg
- `SUMMARY.md` - Projekt-Übersicht
