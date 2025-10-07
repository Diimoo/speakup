#!/usr/bin/env python3
"""
Test script for the modernized speakup GUI
Shows the new modern interface without requiring full speakup functionality
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add speakup directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'speakup'))

# Mock the main module to avoid dependencies
class MockApp:
    def __init__(self, config):
        self.active = False
    
    def run_hotkey_loop(self):
        pass
    
    def toggle(self):
        pass
    
    def stop_audio(self):
        pass

def mock_init_engine(config):
    pass

def mock_load_config(path):
    return {
        "hotkey": "ctrl+shift+space",
        "engine": "faster-whisper", 
        "model": "medium",
        "device": "cuda",
        "language": "en",
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

# Mock the main module
import sys
from unittest.mock import MagicMock
sys.modules['main'] = MagicMock()
sys.modules['main'].App = MockApp
sys.modules['main'].init_engine = mock_init_engine
sys.modules['main'].load_config = mock_load_config

# Now import the GUI
from speakup.gui import SpeakupGUI

def main():
    """Test the modern GUI"""
    root = tk.Tk()
    app = SpeakupGUI(root)
    
    # Add some test log entries to show the modern log styling
    app.log("🎤 Modern GUI initialized successfully!")
    app.log("✨ Dark theme with modern colors applied")
    app.log("🎨 Card-based layout with improved spacing")
    app.log("🔧 Enhanced typography and visual feedback")
    app.log("⚡ Ready for speech-to-text processing", "SUCCESS")
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
