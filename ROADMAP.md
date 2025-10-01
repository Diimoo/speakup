Alles klar, Partner. Hier ist **speakup** so, wie ich ihn bauen würde – **lokal, GPU-beschleunigt, Hotkey-gesteuert, Text landet direkt im aktiven Feld.** Kurz, knackig, realistisch.

# Ziel

„**Drücken – Sprechen – Text erscheint.**“
Globaler Hotkey startet/stoppt Aufnahme. Mikro rein → Echtzeit-STT (Whisper, lokal, GPU) → Text wird **ins aktive Textfeld getippt** (oder per Clipboard eingefügt).

# Kernpunkte (ohne Bullshit)

* **Lokal only:** Keine Cloud. Modelle auf SSD, GPU via CUDA.
* **Sofortstart:** Globaler Hotkey (z. B. `Ctrl+Shift+Space`).
* **On-the-fly STT:** Low-latency Chunks (0.5–1.0 s), **Punktuation** & **Auto-Casing**.
* **Einfügen überall:** Simuliertes Tippen (fallback: Clipboard+Paste).
* **Robust:** VAD (Spracherkennung) stoppt automatisch, Noise-Toleranz.
* **Sicher:** Kein Logging standardmäßig, optional lokales Transcript-Log.

# Architektur (leicht)

* **Input:** `sounddevice` (PortAudio) + **WebRTC VAD** → Ringbuffer (PCM)
* **STT-Engine (wahlweise):**

  * **faster-whisper** (PyTorch/CUDA, sehr schnell, präzise)
  * **whisper.cpp/ggml/gguf** (C++/CUDA/Vulkan/Metal, minimaler Footprint)
* **Inferenz-Loop:** Async Worker, Sliding Window, Timestamps, Punctuation
* **Output:** Textqueue → **Typer** (pynput) **oder** Clipboard+Paste
* **Control:** Globaler Hotkey + Tray-Icon; YAML-Config

# Modelle & Latenz

* `medium`/`large-v3` für Genauigkeit; `small` für Speed.
* Ziel: **Subsekunden-Feedback** für kurze Sätze, <2–3 s für längere.

# OS-Support

* **Linux/Windows** sofort. macOS später (Hotkey/Accessibility beachten).

---

## Repo-Gerüst

```
speakup/
├─ speakup/
│  ├─ main.py
│  ├─ audio.py
│  ├─ stt.py
│  ├─ typer.py
│  ├─ hotkeys.py
│  ├─ tray.py
│  └─ config.yaml
├─ models/            # gguf od. cache für faster-whisper
├─ venv/              # optional
└─ README.md
```

## Setup (CUDA, Python, minimal)

```bash
# Linux Beispiel
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
# Variante A: faster-whisper (CUDA)
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install faster-whisper sounddevice webrtcvad pynput pyyaml pyperclip

# Variante B (alternativ): whisper.cpp Python-Binding
# pip install pywhispercpp sounddevice webrtcvad pynput pyyaml pyperclip
```

## `speakup/config.yaml`

```yaml
hotkey: "ctrl+shift+space"
engine: "faster-whisper"     # "whispercpp" möglich
model: "medium"              # small/medium/large-v3
device: "cuda"               # "auto", "cuda", "cpu"
language: "de"               # "auto" für automatischerkennung
insert_mode: "type"          # "type" | "clipboard"
vad:
  enable: true
  aggressiveness: 2          # 0..3
  min_speech_ms: 300
  max_silence_ms: 800
chunk:
  seconds: 0.8
  overlap: 0.2
punctuate: true
log_transcripts: false
```

## Vollständige Minimal-Implementierung (eine Datei, lauffähiges MVP)

**Datei:** `speakup/main.py`

```python
import queue, threading, time, yaml, sys, io
import numpy as np

# Audio
import sounddevice as sd
import webrtcvad

# Hotkeys & Typing
from pynput import keyboard
from pynput.keyboard import Controller as KeyController, Key
import pyperclip

# STT Engines
ENGINE = None
MODEL = None

def load_config(path="speakup/config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def init_engine(cfg):
    global ENGINE, MODEL
    if cfg["engine"] == "faster-whisper":
        from faster_whisper import WhisperModel
        MODEL = WhisperModel(cfg["model"], device=cfg["device"])
        ENGINE = "faster-whisper"
    elif cfg["engine"] == "whispercpp":
        from whispercpp import Whisper
        MODEL = Whisper(model=cfg["model"])  # gguf/ggml im models/
        ENGINE = "whispercpp"
    else:
        raise ValueError("Unknown engine")

class Typer:
    def __init__(self, mode="type"):
        self.kb = KeyController()
        self.mode = mode

    def emit(self, text):
        if not text: return
        if self.mode == "type":
            # Simuliertes Tippen – sicher für „jedes Textfeld“
            self.kb.type(text)
        else:
            # Clipboard + Paste (schneller, aber überschreibt Zwischenablage)
            old = pyperclip.paste()
            try:
                pyperclip.copy(text)
                self.kb.press(Key.ctrl); self.kb.press('v')
                self.kb.release('v'); self.kb.release(Key.ctrl)
            finally:
                pyperclip.copy(old)

class VADStream:
    def __init__(self, cfg, samplerate=16000, block_ms=20):
        self.vad = webrtcvad.Vad(cfg["vad"]["aggressiveness"])
        self.enabled = cfg["vad"]["enable"]
        self.samplerate = samplerate
        self.block = int(samplerate * block_ms / 1000)
        self.min_speech = cfg["vad"]["min_speech_ms"] / 1000.0
        self.max_silence = cfg["vad"]["max_silence_ms"] / 1000.0
        self.buffer = io.BytesIO()
        self.in_speech = False
        self.last_voice = 0.0
        self.start_time = None

    def process(self, pcm16, tnow):
        if not self.enabled:
            # VAD aus → kontinuierlich aufnehmen
            self.buffer.write(pcm16.tobytes())
            return False, False

        # webrtcvad erwartet 16-bit mono bytes per 10/20/30ms
        # hier chunkieren:
        bytes_ = pcm16.tobytes()
        voiced = False
        for i in range(0, len(bytes_), self.block*2):
            frame = bytes_[i:i+self.block*2]
            if len(frame) < self.block*2: break
            if self.vad.is_speech(frame, self.samplerate):
                voiced = True
                self.last_voice = tnow
                if not self.in_speech:
                    self.in_speech = True
                    self.start_time = tnow
            self.buffer.write(frame)

        start_event = False
        end_event = False
        if self.in_speech and (tnow - self.last_voice) > self.max_silence:
            # Ende erkannt
            self.in_speech = False
            # Nur ausgeben, wenn genug Sprache gesammelt
            if self.start_time and (self.last_voice - self.start_time) >= self.min_speech:
                end_event = True
        elif voiced and self.start_time and not self.in_speech:
            # reset fallback
            self.start_time = None

        return start_event, end_event

    def pop_bytes(self):
        data = self.buffer.getvalue()
        self.buffer = io.BytesIO()
        return data

class STTWorker(threading.Thread):
    def __init__(self, cfg, audio_q, out_q):
        super().__init__(daemon=True)
        self.cfg = cfg
        self.audio_q = audio_q
        self.out_q = out_q
        self.running = True
        self.lang = None if cfg["language"] == "auto" else cfg["language"]

    def run(self):
        global ENGINE, MODEL
        chunk_buf = b""
        sample_rate = 16000
        bytes_per_sec = sample_rate * 2
        target = self.cfg["chunk"]["seconds"]
        overlap = self.cfg["chunk"]["overlap"]

        # Sliding window in Bytes
        window_bytes = int(bytes_per_sec * target)
        overlap_bytes = int(bytes_per_sec * overlap)

        while self.running:
            try:
                data = self.audio_q.get(timeout=0.1)
            except queue.Empty:
                continue
            chunk_buf += data

            if len(chunk_buf) >= window_bytes:
                audio = np.frombuffer(chunk_buf, dtype=np.int16).astype(np.float32) / 32768.0

                text = ""
                if ENGINE == "faster-whisper":
                    segments, _ = MODEL.transcribe(audio, language=self.lang, vad_filter=False, condition_on_previous_text=True)
                    text = "".join(s.text for s in segments)
                else:
                    # whisper.cpp
                    text = MODEL.transcribe(audio, language=self.lang or "auto")

                if self.cfg.get("punctuate", True):
                    # faster-whisper liefert i.d.R. bereits punktuiert
                    pass

                if text.strip():
                    self.out_q.put(text.strip())

                # Keep overlap
                chunk_buf = chunk_buf[-overlap_bytes:]

class App:
    def __init__(self, cfg):
        self.cfg = cfg
        self.audio_q = queue.Queue()
        self.text_q = queue.Queue()
        self.stream = None
        self.vad = VADStream(cfg)
        self.stt = STTWorker(cfg, self.audio_q, self.text_q)
        self.typer = Typer(cfg["insert_mode"])
        self.hotkey = cfg["hotkey"]
        self.active = False
        self.listener = None

    def start_audio(self):
        sd.default.samplerate = 16000
        sd.default.channels = 1
        self.stream = sd.InputStream(callback=self._callback, dtype='int16')
        self.stream.start()
        self.stt.start()

    def stop_audio(self):
        if self.stream: self.stream.stop(); self.stream.close()
        self.stt.running = False

    def _callback(self, indata, frames, time_info, status):
        tnow = time.time()
        pcm16 = indata.copy()
        _, end_event = self.vad.process(pcm16, tnow)
        # Bei VAD-Ende kompletten Block zum STT schieben (für Satzgenauigkeit)
        # Zusätzlich kontinuierlich Chunks schieben für Near-Realtime
        self.audio_q.put(pcm16.tobytes())
        if end_event:
            self.audio_q.put(self.vad.pop_bytes())

    def toggle(self):
        self.active = not self.active
        if self.active:
            print("[speakup] Aufnahme EIN")
            self.start_audio()
        else:
            print("[speakup] Aufnahme AUS")
            self.stop_audio()

    def run_hotkey_loop(self):
        def on_press(key):
            try:
                combo = []
                if isinstance(key, keyboard.KeyCode):
                    combo.append(key.char)
                # Wir prüfen nur auf Starttaste (global registriert unten)
            except Exception:
                pass

        with keyboard.GlobalHotKeys({ self.hotkey: self.toggle }) as h:
            self.listener = h
            # Output-Loop
            while True:
                try:
                    text = self.text_q.get(timeout=0.2)
                    self.typer.emit(text + " ")
                except queue.Empty:
                    pass

def main():
    cfg = load_config()
    init_engine(cfg)
    app = App(cfg)
    print(f"[speakup] Hotkey: {cfg['hotkey']} – Engine: {cfg['engine']} – Model: {cfg['model']}")
    try:
        app.run_hotkey_loop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
```

### Starten

```bash
source venv/bin/activate
python speakup/main.py
# Im Tray/Terminal siehst du "Hotkey ...", dann: Ctrl+Shift+Space → sprechen → Text erscheint.
```

---

## Extras (wenn Zeit ist)

* **Live-Preview Overlay** (kleines OSD mit erkanntem Text)
* **Auto-Language** per LangID (z. B. fasttext)
* **Prefix-/Suffix-Snippets** (z. B. „> “ für Notizen)
* **Domänenprofile** (Ticket-Jargon, E-Mail-Stil)
* **Push-to-Talk** statt Toggle (Taste gedrückt halten)

## Warum das funktioniert

* **GPU-Inferenz** (faster-whisper/whisper.cpp) + **kurze Chunks** → niedrige Latenz.
* **Globaler Hotkey** + **Typer/Clipboard** → App-agnostisch, funktioniert überall.
* **VAD** → sinnvolle Segmentgrenzen, saubere Sätze.

Wenn du willst, passe ich das sofort an **deine Linux-Distro** und **GPU-Treiber** an (oder liefere eine **whisper.cpp-Variante** ohne PyTorch).
