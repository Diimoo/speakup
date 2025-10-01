#!/usr/bin/env python3
"""
speakup GUI - Grafische Benutzeroberfläche
Ermöglicht Start/Stop und Konfiguration über GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
import yaml
import os
import sys
from pathlib import Path

# Import from main.py
from main import App, init_engine, load_config

class SpeakupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 speakup - Speech-to-Text")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # State
        self.app = None
        self.config = None
        self.running = False
        self.config_path = "speakup/config.yaml"
        
        # Load config
        self.load_configuration()
        
        # Create UI
        self.create_widgets()
        
        # Status update timer
        self.update_status()
        
    def load_configuration(self):
        """Lade Konfiguration aus YAML"""
        try:
            self.config = load_config(self.config_path)
        except Exception as e:
            messagebox.showerror("Fehler", f"Config konnte nicht geladen werden:\n{e}")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """Standard-Konfiguration"""
        return {
            "hotkey": "ctrl+shift+space",
            "engine": "faster-whisper",
            "model": "medium",
            "device": "cuda",
            "language": "de",
            "insert_mode": "type",
            "vad": {
                "enable": True,
                "aggressiveness": 2,
                "min_speech_ms": 300,
                "max_silence_ms": 800
            },
            "chunk": {
                "seconds": 0.8,
                "overlap": 0.2
            },
            "punctuate": True,
            "log_transcripts": False
        }
    
    def create_widgets(self):
        """Erstelle alle UI-Komponenten"""
        
        # Notebook für Tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Control
        self.create_control_tab(notebook)
        
        # Tab 2: Settings
        self.create_settings_tab(notebook)
        
        # Tab 3: Advanced
        self.create_advanced_tab(notebook)
        
        # Tab 4: Log
        self.create_log_tab(notebook)
        
        # Bottom status bar
        self.create_status_bar()
    
    def create_control_tab(self, notebook):
        """Control Tab - Start/Stop und Status"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🎛️ Steuerung")
        
        # Status Frame
        status_frame = ttk.LabelFrame(frame, text="Status", padding=20)
        status_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.status_label = ttk.Label(
            status_frame, 
            text="⚫ Gestoppt",
            font=("Arial", 24, "bold"),
            foreground="red"
        )
        self.status_label.pack(pady=10)
        
        self.status_detail = ttk.Label(
            status_frame,
            text="Drücke 'Starten' um speakup zu aktivieren",
            font=("Arial", 11)
        )
        self.status_detail.pack()
        
        # Control Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        self.start_btn = ttk.Button(
            button_frame,
            text="▶ Starten",
            command=self.start_speakup,
            width=20
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏸ Stoppen",
            command=self.stop_speakup,
            state=tk.DISABLED,
            width=20
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Info Frame
        info_frame = ttk.LabelFrame(frame, text="Aktuelle Konfiguration", padding=15)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.info_text = scrolledtext.ScrolledText(
            info_frame,
            height=15,
            font=("Courier", 10),
            state=tk.DISABLED
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        self.update_info_display()
    
    def create_settings_tab(self, notebook):
        """Settings Tab - Grundeinstellungen"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="⚙️ Einstellungen")
        
        # Scrollable Frame
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # General Settings
        general_frame = ttk.LabelFrame(scrollable_frame, text="Allgemein", padding=15)
        general_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Hotkey
        ttk.Label(general_frame, text="Hotkey:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.hotkey_var = tk.StringVar(value=self.config.get("hotkey", "ctrl+shift+space"))
        ttk.Entry(general_frame, textvariable=self.hotkey_var, width=30).grid(row=0, column=1, pady=5, padx=10)
        
        # Engine
        ttk.Label(general_frame, text="Engine:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.engine_var = tk.StringVar(value=self.config.get("engine", "faster-whisper"))
        engine_combo = ttk.Combobox(
            general_frame, 
            textvariable=self.engine_var,
            values=["faster-whisper", "whispercpp"],
            state="readonly",
            width=28
        )
        engine_combo.grid(row=1, column=1, pady=5, padx=10)
        
        # Model
        ttk.Label(general_frame, text="Modell:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value=self.config.get("model", "medium"))
        model_combo = ttk.Combobox(
            general_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
            state="readonly",
            width=28
        )
        model_combo.grid(row=2, column=1, pady=5, padx=10)
        
        # Device
        ttk.Label(general_frame, text="Device:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.device_var = tk.StringVar(value=self.config.get("device", "cuda"))
        device_combo = ttk.Combobox(
            general_frame,
            textvariable=self.device_var,
            values=["cuda", "cpu", "auto"],
            state="readonly",
            width=28
        )
        device_combo.grid(row=3, column=1, pady=5, padx=10)
        
        # Language
        ttk.Label(general_frame, text="Sprache:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.language_var = tk.StringVar(value=self.config.get("language", "de"))
        language_combo = ttk.Combobox(
            general_frame,
            textvariable=self.language_var,
            values=["auto", "de", "en", "es", "fr", "it", "pt", "nl", "pl", "ru", "zh", "ja", "ko"],
            state="readonly",
            width=28
        )
        language_combo.grid(row=4, column=1, pady=5, padx=10)
        
        # Insert Mode
        ttk.Label(general_frame, text="Eingabemodus:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.insert_mode_var = tk.StringVar(value=self.config.get("insert_mode", "type"))
        mode_combo = ttk.Combobox(
            general_frame,
            textvariable=self.insert_mode_var,
            values=["type", "clipboard"],
            state="readonly",
            width=28
        )
        mode_combo.grid(row=5, column=1, pady=5, padx=10)
        
        # Options
        options_frame = ttk.LabelFrame(scrollable_frame, text="Optionen", padding=15)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.punctuate_var = tk.BooleanVar(value=self.config.get("punctuate", True))
        ttk.Checkbutton(
            options_frame,
            text="Automatische Punktuation",
            variable=self.punctuate_var
        ).pack(anchor=tk.W, pady=5)
        
        self.log_var = tk.BooleanVar(value=self.config.get("log_transcripts", False))
        ttk.Checkbutton(
            options_frame,
            text="Transkripte loggen",
            variable=self.log_var
        ).pack(anchor=tk.W, pady=5)
        
        # Save Button
        save_frame = ttk.Frame(scrollable_frame)
        save_frame.pack(pady=20)
        
        ttk.Button(
            save_frame,
            text="💾 Einstellungen speichern",
            command=self.save_settings,
            width=30
        ).pack()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_advanced_tab(self, notebook):
        """Advanced Tab - VAD und Chunk-Einstellungen"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🔧 Erweitert")
        
        # VAD Settings
        vad_frame = ttk.LabelFrame(frame, text="Voice Activity Detection (VAD)", padding=15)
        vad_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.vad_enable_var = tk.BooleanVar(value=self.config["vad"].get("enable", True))
        ttk.Checkbutton(
            vad_frame,
            text="VAD aktivieren",
            variable=self.vad_enable_var
        ).pack(anchor=tk.W, pady=5)
        
        # Aggressiveness
        ttk.Label(vad_frame, text="Aggressivität (0-3):").pack(anchor=tk.W, pady=(10, 0))
        self.vad_aggr_var = tk.IntVar(value=self.config["vad"].get("aggressiveness", 2))
        ttk.Scale(
            vad_frame,
            from_=0,
            to=3,
            variable=self.vad_aggr_var,
            orient=tk.HORIZONTAL,
            length=300
        ).pack(anchor=tk.W, pady=5)
        self.vad_aggr_label = ttk.Label(vad_frame, text=f"Wert: {self.vad_aggr_var.get()}")
        self.vad_aggr_label.pack(anchor=tk.W)
        self.vad_aggr_var.trace_add("write", self.update_vad_label)
        
        # Min speech
        ttk.Label(vad_frame, text="Min. Sprachdauer (ms):").pack(anchor=tk.W, pady=(10, 0))
        self.vad_min_var = tk.IntVar(value=self.config["vad"].get("min_speech_ms", 300))
        ttk.Spinbox(
            vad_frame,
            from_=100,
            to=2000,
            textvariable=self.vad_min_var,
            width=20
        ).pack(anchor=tk.W, pady=5)
        
        # Max silence
        ttk.Label(vad_frame, text="Max. Stille (ms):").pack(anchor=tk.W, pady=(10, 0))
        self.vad_max_var = tk.IntVar(value=self.config["vad"].get("max_silence_ms", 800))
        ttk.Spinbox(
            vad_frame,
            from_=100,
            to=3000,
            textvariable=self.vad_max_var,
            width=20
        ).pack(anchor=tk.W, pady=5)
        
        # Chunk Settings
        chunk_frame = ttk.LabelFrame(frame, text="Chunk-Einstellungen", padding=15)
        chunk_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(chunk_frame, text="Chunk-Größe (Sekunden):").pack(anchor=tk.W, pady=(5, 0))
        self.chunk_sec_var = tk.DoubleVar(value=self.config["chunk"].get("seconds", 0.8))
        ttk.Spinbox(
            chunk_frame,
            from_=0.3,
            to=3.0,
            increment=0.1,
            textvariable=self.chunk_sec_var,
            width=20
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Label(chunk_frame, text="Overlap (Sekunden):").pack(anchor=tk.W, pady=(10, 0))
        self.chunk_overlap_var = tk.DoubleVar(value=self.config["chunk"].get("overlap", 0.2))
        ttk.Spinbox(
            chunk_frame,
            from_=0.0,
            to=1.0,
            increment=0.1,
            textvariable=self.chunk_overlap_var,
            width=20
        ).pack(anchor=tk.W, pady=5)
        
        # Save Button
        ttk.Button(
            frame,
            text="💾 Einstellungen speichern",
            command=self.save_settings,
            width=30
        ).pack(pady=20)
    
    def create_log_tab(self, notebook):
        """Log Tab - Ausgabe und Transkripte"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📋 Log")
        
        # Log area
        log_frame = ttk.LabelFrame(frame, text="System-Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=25,
            font=("Courier", 9),
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame,
            text="🗑️ Log löschen",
            command=self.clear_log
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="💾 Log speichern",
            command=self.save_log
        ).pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self):
        """Status-Leiste am unteren Rand"""
        self.status_bar = ttk.Label(
            self.root,
            text="Bereit",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_vad_label(self, *args):
        """Update VAD Aggressiveness Label"""
        self.vad_aggr_label.config(text=f"Wert: {self.vad_aggr_var.get()}")
    
    def update_info_display(self):
        """Aktualisiere Info-Anzeige"""
        info = f"""Aktuelle Konfiguration:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hotkey:          {self.config.get('hotkey')}
Engine:          {self.config.get('engine')}
Modell:          {self.config.get('model')}
Device:          {self.config.get('device')}
Sprache:         {self.config.get('language')}
Eingabemodus:    {self.config.get('insert_mode')}

VAD:             {'Aktiviert' if self.config['vad'].get('enable') else 'Deaktiviert'}
Punktuation:     {'Ja' if self.config.get('punctuate') else 'Nein'}
Logging:         {'Ja' if self.config.get('log_transcripts') else 'Nein'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
    
    def log(self, message, level="INFO"):
        """Füge Nachricht zum Log hinzu"""
        timestamp = __import__('time').strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        """Lösche Log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log("Log gelöscht")
    
    def save_log(self):
        """Speichere Log in Datei"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log(f"Log gespeichert: {filename}")
    
    def save_settings(self):
        """Speichere Einstellungen in config.yaml"""
        try:
            # Update config dict
            self.config["hotkey"] = self.hotkey_var.get()
            self.config["engine"] = self.engine_var.get()
            self.config["model"] = self.model_var.get()
            self.config["device"] = self.device_var.get()
            self.config["language"] = self.language_var.get()
            self.config["insert_mode"] = self.insert_mode_var.get()
            self.config["punctuate"] = self.punctuate_var.get()
            self.config["log_transcripts"] = self.log_var.get()
            
            self.config["vad"]["enable"] = self.vad_enable_var.get()
            self.config["vad"]["aggressiveness"] = self.vad_aggr_var.get()
            self.config["vad"]["min_speech_ms"] = self.vad_min_var.get()
            self.config["vad"]["max_silence_ms"] = self.vad_max_var.get()
            
            self.config["chunk"]["seconds"] = self.chunk_sec_var.get()
            self.config["chunk"]["overlap"] = self.chunk_overlap_var.get()
            
            # Save to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            
            self.log("✓ Einstellungen gespeichert")
            self.update_info_display()
            messagebox.showinfo("Erfolg", "Einstellungen wurden gespeichert!")
            
        except Exception as e:
            self.log(f"✗ Fehler beim Speichern: {e}", "ERROR")
            messagebox.showerror("Fehler", f"Einstellungen konnten nicht gespeichert werden:\n{e}")
    
    def start_speakup(self):
        """Starte speakup"""
        try:
            self.log("Initialisiere STT-Engine...")
            init_engine(self.config)
            
            self.log("Starte speakup...")
            self.app = App(self.config)
            
            # Start in thread
            self.speakup_thread = threading.Thread(
                target=self.run_speakup_loop,
                daemon=True
            )
            self.speakup_thread.start()
            
            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.status_label.config(text="🟢 Läuft", foreground="green")
            self.status_detail.config(text=f"Hotkey: {self.config['hotkey']}")
            self.status_bar.config(text=f"Aktiv - Hotkey: {self.config['hotkey']}")
            
            self.log(f"✓ speakup gestartet - Hotkey: {self.config['hotkey']}")
            
        except Exception as e:
            self.log(f"✗ Fehler beim Starten: {e}", "ERROR")
            messagebox.showerror("Fehler", f"speakup konnte nicht gestartet werden:\n{e}")
    
    def run_speakup_loop(self):
        """Führe speakup Hotkey-Loop aus"""
        try:
            self.app.run_hotkey_loop()
        except Exception as e:
            self.log(f"✗ speakup-Loop Fehler: {e}", "ERROR")
    
    def stop_speakup(self):
        """Stoppe speakup"""
        try:
            if self.app:
                if self.app.active:
                    self.app.toggle()  # Stop recording if active
                self.app.stop_audio()
                
            self.running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            
            self.status_label.config(text="⚫ Gestoppt", foreground="red")
            self.status_detail.config(text="Drücke 'Starten' um speakup zu aktivieren")
            self.status_bar.config(text="Gestoppt")
            
            self.log("✓ speakup gestoppt")
            
        except Exception as e:
            self.log(f"✗ Fehler beim Stoppen: {e}", "ERROR")
    
    def update_status(self):
        """Periodisches Status-Update"""
        if self.running and self.app:
            if self.app.active:
                self.status_detail.config(text="🎤 Aufnahme läuft...")
            else:
                self.status_detail.config(text=f"Bereit - Hotkey: {self.config['hotkey']}")
        
        # Schedule next update
        self.root.after(500, self.update_status)
    
    def on_closing(self):
        """Handle window close"""
        if self.running:
            if messagebox.askokcancel("Beenden", "speakup läuft noch. Wirklich beenden?"):
                self.stop_speakup()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """Hauptfunktion"""
    root = tk.Tk()
    app = SpeakupGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
