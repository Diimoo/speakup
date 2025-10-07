#!/usr/bin/env python3
"""
speakup GUI - Grafische Benutzeroberfläche
Ermöglicht Start/Stop und Konfiguration über GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
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
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Modern styling
        self.setup_modern_theme()
        
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
    
    def setup_modern_theme(self):
        """Configure modern theme and styling"""
        # Color scheme
        self.colors = {
            'bg_primary': '#1e1e2e',
            'bg_secondary': '#313244', 
            'bg_tertiary': '#45475a',
            'accent': '#89b4fa',
            'accent_hover': '#74c7ec',
            'success': '#a6e3a1',
            'warning': '#f9e2af',
            'error': '#f38ba8',
            'text_primary': '#cdd6f4',
            'text_secondary': '#bac2de',
            'text_muted': '#6c7086'
        }
        
        # Configure root
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Modern.TFrame', background=self.colors['bg_primary'])
        style.configure('Card.TFrame', background=self.colors['bg_secondary'], relief='flat', borderwidth=1)
        style.configure('Modern.TLabel', background=self.colors['bg_primary'], foreground=self.colors['text_primary'])
        style.configure('Card.TLabel', background=self.colors['bg_secondary'], foreground=self.colors['text_primary'])
        style.configure('Title.TLabel', background=self.colors['bg_primary'], foreground=self.colors['text_primary'], font=('Segoe UI', 16, 'bold'))
        style.configure('Subtitle.TLabel', background=self.colors['bg_primary'], foreground=self.colors['text_secondary'], font=('Segoe UI', 11))
        
        # Button styles
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))
        style.map('Accent.TButton', background=[('active', self.colors['accent_hover']), ('!active', self.colors['accent'])])
        
        # Notebook styles
        style.configure('Modern.TNotebook', background=self.colors['bg_primary'], borderwidth=0)
        style.configure('Modern.TNotebook.Tab', padding=[20, 10], font=('Segoe UI', 10, 'bold'))
        
        # Additional styles
        style.configure('Card.TCheckbutton', background=self.colors['bg_secondary'], foreground=self.colors['text_primary'], font=('Segoe UI', 10))
        style.map('Card.TCheckbutton', background=[('active', self.colors['bg_tertiary'])])
        
        # Entry and Combobox styles
        style.configure('TEntry', fieldbackground=self.colors['bg_tertiary'], foreground=self.colors['text_primary'], borderwidth=1, insertcolor=self.colors['accent'])
        style.configure('TCombobox', fieldbackground=self.colors['bg_tertiary'], foreground=self.colors['text_primary'], borderwidth=1)
        style.configure('TSpinbox', fieldbackground=self.colors['bg_tertiary'], foreground=self.colors['text_primary'], borderwidth=1)
        
        
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
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Notebook für Tabs
        notebook = ttk.Notebook(main_frame, style='Modern.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
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
    
    def create_header(self, parent):
        """Create modern header section"""
        header_frame = ttk.Frame(parent, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(
            header_frame, 
            text="🎤 speakup",
            style='Title.TLabel'
        )
        title_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Modern Speech-to-Text Interface",
            style='Subtitle.TLabel'
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_control_tab(self, notebook):
        """Control Tab - Start/Stop und Status"""
        frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(frame, text="🎛️ Control")
        
        # Status Card
        status_card = self.create_card(frame, "System Status")
        status_card.pack(fill=tk.X, padx=20, pady=20)
        
        # Status indicator with modern styling
        status_container = ttk.Frame(status_card, style='Card.TFrame')
        status_container.pack(fill=tk.X, pady=10)
        
        self.status_indicator = tk.Canvas(
            status_container, 
            width=20, 
            height=20, 
            bg=self.colors['bg_secondary'],
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.status_indicator.create_oval(2, 2, 18, 18, fill=self.colors['error'], outline="")
        
        self.status_label = ttk.Label(
            status_container, 
            text="Stopped",
            style='Card.TLabel',
            font=("Segoe UI", 14, "bold")
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.status_detail = ttk.Label(
            status_card,
            text="Press 'Start' to activate speakup",
            style='Card.TLabel',
            font=("Segoe UI", 10)
        )
        self.status_detail.pack(pady=(0, 10))
        
        # Control Buttons with modern styling
        button_frame = ttk.Frame(frame, style='Modern.TFrame')
        button_frame.pack(pady=30)
        
        self.start_btn = ttk.Button(
            button_frame,
            text="▶ Start Recording",
            command=self.start_speakup,
            style='Accent.TButton',
            width=25
        )
        self.start_btn.pack(side=tk.LEFT, padx=15)
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏸ Stop Recording",
            command=self.stop_speakup,
            state=tk.DISABLED,
            width=25
        )
        self.stop_btn.pack(side=tk.LEFT, padx=15)
        
        # Configuration Card
        config_card = self.create_card(frame, "Current Configuration")
        config_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.info_text = scrolledtext.ScrolledText(
            config_card,
            height=12,
            font=("JetBrains Mono", 10),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['bg_primary'],
            state=tk.DISABLED,
            relief='flat',
            borderwidth=0
        )
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.update_info_display()
    
    def create_card(self, parent, title):
        """Create a modern card-style container"""
        card_frame = ttk.Frame(parent, style='Card.TFrame')
        
        # Card title
        title_label = ttk.Label(
            card_frame,
            text=title,
            style='Card.TLabel',
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        # Content area
        content_frame = ttk.Frame(card_frame, style='Card.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        return content_frame
    
    def create_settings_tab(self, notebook):
        """Settings Tab - Grundeinstellungen"""
        frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(frame, text="⚙️ Settings")
        
        # Scrollable Frame with modern styling
        canvas = tk.Canvas(frame, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # General Settings Card
        general_card = self.create_card(scrollable_frame, "General Settings")
        general_card.pack(fill=tk.X, padx=20, pady=10)
        
        # Hotkey
        ttk.Label(general_card, text="Hotkey:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, pady=8)
        self.hotkey_var = tk.StringVar(value=self.config.get("hotkey", "ctrl+shift+space"))
        hotkey_entry = ttk.Entry(general_card, textvariable=self.hotkey_var, width=30, font=('Segoe UI', 10))
        hotkey_entry.grid(row=0, column=1, pady=8, padx=15, sticky=tk.W)
        
        # Engine
        ttk.Label(general_card, text="Engine:", style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, pady=8)
        self.engine_var = tk.StringVar(value=self.config.get("engine", "faster-whisper"))
        engine_combo = ttk.Combobox(
            general_card, 
            textvariable=self.engine_var,
            values=["faster-whisper", "whispercpp"],
            state="readonly",
            width=28,
            font=('Segoe UI', 10)
        )
        engine_combo.grid(row=1, column=1, pady=8, padx=15, sticky=tk.W)
        
        # Model
        ttk.Label(general_card, text="Model:", style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, pady=8)
        self.model_var = tk.StringVar(value=self.config.get("model", "medium"))
        model_combo = ttk.Combobox(
            general_card,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
            state="readonly",
            width=28,
            font=('Segoe UI', 10)
        )
        model_combo.grid(row=2, column=1, pady=8, padx=15, sticky=tk.W)
        
        # Device
        ttk.Label(general_card, text="Device:", style='Card.TLabel').grid(row=3, column=0, sticky=tk.W, pady=8)
        self.device_var = tk.StringVar(value=self.config.get("device", "cuda"))
        device_combo = ttk.Combobox(
            general_card,
            textvariable=self.device_var,
            values=["cuda", "cpu", "auto"],
            state="readonly",
            width=28,
            font=('Segoe UI', 10)
        )
        device_combo.grid(row=3, column=1, pady=8, padx=15, sticky=tk.W)
        
        # Language
        ttk.Label(general_card, text="Language:", style='Card.TLabel').grid(row=4, column=0, sticky=tk.W, pady=8)
        self.language_var = tk.StringVar(value=self.config.get("language", "de"))
        language_combo = ttk.Combobox(
            general_card,
            textvariable=self.language_var,
            values=["auto", "de", "en", "es", "fr", "it", "pt", "nl", "pl", "ru", "zh", "ja", "ko"],
            state="readonly",
            width=28,
            font=('Segoe UI', 10)
        )
        language_combo.grid(row=4, column=1, pady=8, padx=15, sticky=tk.W)
        
        # Insert Mode
        ttk.Label(general_card, text="Input Mode:", style='Card.TLabel').grid(row=5, column=0, sticky=tk.W, pady=8)
        self.insert_mode_var = tk.StringVar(value=self.config.get("insert_mode", "type"))
        mode_combo = ttk.Combobox(
            general_card,
            textvariable=self.insert_mode_var,
            values=["type", "clipboard"],
            state="readonly",
            width=28,
            font=('Segoe UI', 10)
        )
        mode_combo.grid(row=5, column=1, pady=8, padx=15, sticky=tk.W)
        
        # Options Card
        options_card = self.create_card(scrollable_frame, "Options")
        options_card.pack(fill=tk.X, padx=20, pady=10)
        
        self.punctuate_var = tk.BooleanVar(value=self.config.get("punctuate", True))
        ttk.Checkbutton(
            options_card,
            text="Auto Punctuation",
            variable=self.punctuate_var,
            style='Card.TCheckbutton'
        ).pack(anchor=tk.W, pady=8)
        
        self.log_var = tk.BooleanVar(value=self.config.get("log_transcripts", False))
        ttk.Checkbutton(
            options_card,
            text="Log Transcripts",
            variable=self.log_var,
            style='Card.TCheckbutton'
        ).pack(anchor=tk.W, pady=8)
        
        # Save Button
        save_frame = ttk.Frame(scrollable_frame, style='Modern.TFrame')
        save_frame.pack(pady=30)
        
        ttk.Button(
            save_frame,
            text="💾 Save Settings",
            command=self.save_settings,
            style='Accent.TButton',
            width=30
        ).pack()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_advanced_tab(self, notebook):
        """Advanced Tab - VAD und Chunk-Einstellungen"""
        frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(frame, text="🔧 Advanced")
        
        # VAD Settings Card
        vad_card = self.create_card(frame, "Voice Activity Detection (VAD)")
        vad_card.pack(fill=tk.X, padx=20, pady=20)
        
        self.vad_enable_var = tk.BooleanVar(value=self.config["vad"].get("enable", True))
        ttk.Checkbutton(
            vad_card,
            text="Enable VAD",
            variable=self.vad_enable_var,
            style='Card.TCheckbutton'
        ).pack(anchor=tk.W, pady=8)
        
        # Aggressiveness
        ttk.Label(vad_card, text="Aggressiveness (0-3):", style='Card.TLabel').pack(anchor=tk.W, pady=(15, 5))
        self.vad_aggr_var = tk.IntVar(value=self.config["vad"].get("aggressiveness", 2))
        ttk.Scale(
            vad_card,
            from_=0,
            to=3,
            variable=self.vad_aggr_var,
            orient=tk.HORIZONTAL,
            length=300
        ).pack(anchor=tk.W, pady=8)
        self.vad_aggr_label = ttk.Label(vad_card, text=f"Value: {self.vad_aggr_var.get()}", style='Card.TLabel')
        self.vad_aggr_label.pack(anchor=tk.W)
        self.vad_aggr_var.trace_add("write", self.update_vad_label)
        
        # Min speech
        ttk.Label(vad_card, text="Min. Speech Duration (ms):", style='Card.TLabel').pack(anchor=tk.W, pady=(15, 5))
        self.vad_min_var = tk.IntVar(value=self.config["vad"].get("min_speech_ms", 300))
        ttk.Spinbox(
            vad_card,
            from_=100,
            to=2000,
            textvariable=self.vad_min_var,
            width=20,
            font=('Segoe UI', 10)
        ).pack(anchor=tk.W, pady=8)
        
        # Max silence
        ttk.Label(vad_card, text="Max. Silence (ms):", style='Card.TLabel').pack(anchor=tk.W, pady=(15, 5))
        self.vad_max_var = tk.IntVar(value=self.config["vad"].get("max_silence_ms", 800))
        ttk.Spinbox(
            vad_card,
            from_=100,
            to=3000,
            textvariable=self.vad_max_var,
            width=20,
            font=('Segoe UI', 10)
        ).pack(anchor=tk.W, pady=8)
        
        # Chunk Settings Card
        chunk_card = self.create_card(frame, "Chunk Settings")
        chunk_card.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(chunk_card, text="Chunk Size (seconds):", style='Card.TLabel').pack(anchor=tk.W, pady=(10, 5))
        self.chunk_sec_var = tk.DoubleVar(value=self.config["chunk"].get("seconds", 0.8))
        ttk.Spinbox(
            chunk_card,
            from_=0.3,
            to=3.0,
            increment=0.1,
            textvariable=self.chunk_sec_var,
            width=20,
            font=('Segoe UI', 10)
        ).pack(anchor=tk.W, pady=8)
        
        ttk.Label(chunk_card, text="Overlap (seconds):", style='Card.TLabel').pack(anchor=tk.W, pady=(15, 5))
        self.chunk_overlap_var = tk.DoubleVar(value=self.config["chunk"].get("overlap", 0.2))
        ttk.Spinbox(
            chunk_card,
            from_=0.0,
            to=1.0,
            increment=0.1,
            textvariable=self.chunk_overlap_var,
            width=20,
            font=('Segoe UI', 10)
        ).pack(anchor=tk.W, pady=8)
        
        # Save Button
        save_frame = ttk.Frame(frame, style='Modern.TFrame')
        save_frame.pack(pady=30)
        
        ttk.Button(
            save_frame,
            text="💾 Save Settings",
            command=self.save_settings,
            style='Accent.TButton',
            width=30
        ).pack()
    
    def create_log_tab(self, notebook):
        """Log Tab - Ausgabe und Transkripte"""
        frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(frame, text="📋 Logs")
        
        # Log area
        log_card = self.create_card(frame, "System Logs")
        log_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.log_text = scrolledtext.ScrolledText(
            log_card,
            height=22,
            font=("JetBrains Mono", 9),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['bg_primary'],
            state=tk.DISABLED,
            relief='flat',
            borderwidth=0
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(frame, style='Modern.TFrame')
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="🗑️ Clear Log",
            command=self.clear_log,
            width=15
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame,
            text="💾 Save Log",
            command=self.save_log,
            style='Accent.TButton',
            width=15
        ).pack(side=tk.LEFT, padx=10)
    
    def create_status_bar(self):
        """Status-Leiste am unteren Rand"""
        status_frame = ttk.Frame(self.root, style='Modern.TFrame')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 10))
        
        self.status_bar = ttk.Label(
            status_frame,
            text="Ready",
            style='Modern.TLabel',
            font=('Segoe UI', 9)
        )
        self.status_bar.pack(side=tk.LEFT, pady=5)
    
    def update_vad_label(self, *args):
        """Update VAD Aggressiveness Label"""
        self.vad_aggr_label.config(text=f"Value: {self.vad_aggr_var.get()}")
    
    def update_info_display(self):
        """Update configuration display"""
        info = f"""Current Configuration:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hotkey:          {self.config.get('hotkey')}
Engine:          {self.config.get('engine')}
Model:           {self.config.get('model')}
Device:          {self.config.get('device')}
Language:        {self.config.get('language')}
Input Mode:      {self.config.get('insert_mode')}

VAD:             {'Enabled' if self.config['vad'].get('enable') else 'Disabled'}
Punctuation:     {'Yes' if self.config.get('punctuate') else 'No'}
Logging:         {'Yes' if self.config.get('log_transcripts') else 'No'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
    
    def log(self, message, level="INFO"):
        """Add message to log"""
        timestamp = __import__('time').strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        """Clear log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log("Log cleared")
    
    def save_log(self):
        """Save log to file"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log(f"Log saved: {filename}")
    
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
            
            self.log("✓ Settings saved")
            self.update_info_display()
            messagebox.showinfo("Success", "Settings have been saved!")
            
        except Exception as e:
            self.log(f"✗ Error saving: {e}", "ERROR")
            messagebox.showerror("Error", f"Settings could not be saved:\n{e}")
    
    def start_speakup(self):
        """Starte speakup"""
        try:
            self.log("Initializing STT Engine...")
            init_engine(self.config)
            
            self.log("Starting speakup...")
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
            
            self.status_label.config(text="Running")
            self.status_indicator.delete("all")
            self.status_indicator.create_oval(2, 2, 18, 18, fill=self.colors['success'], outline="")
            self.status_detail.config(text=f"Hotkey: {self.config['hotkey']}")
            self.status_bar.config(text=f"Active - Hotkey: {self.config['hotkey']}")
            
            self.log(f"✓ speakup started - Hotkey: {self.config['hotkey']}")
            
        except Exception as e:
            self.log(f"✗ Error starting: {e}", "ERROR")
            messagebox.showerror("Error", f"speakup could not be started:\n{e}")
    
    def run_speakup_loop(self):
        """Run speakup hotkey loop"""
        try:
            self.app.run_hotkey_loop()
        except Exception as e:
            self.log(f"✗ speakup loop error: {e}", "ERROR")
    
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
            
            self.status_label.config(text="Stopped")
            self.status_indicator.delete("all")
            self.status_indicator.create_oval(2, 2, 18, 18, fill=self.colors['error'], outline="")
            self.status_detail.config(text="Press 'Start' to activate speakup")
            self.status_bar.config(text="Stopped")
            
            self.log("✓ speakup stopped")
            
        except Exception as e:
            self.log(f"✗ Error stopping: {e}", "ERROR")
    
    def update_status(self):
        """Periodisches Status-Update"""
        if self.running and self.app:
            if self.app.active:
                self.status_detail.config(text="🎤 Recording...")
            else:
                self.status_detail.config(text=f"Ready - Hotkey: {self.config['hotkey']}")
        
        # Schedule next update
        self.root.after(500, self.update_status)
    
    def on_closing(self):
        """Handle window close"""
        if self.running:
            if messagebox.askokcancel("Exit", "speakup is still running. Really exit?"):
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
