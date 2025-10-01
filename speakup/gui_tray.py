#!/usr/bin/env python3
"""
speakup GUI mit System Tray Icon
Ermöglicht Minimierung in System Tray
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import yaml
from gui import SpeakupGUI
from main import App, init_engine, load_config

# Optional: pystray für System Tray
try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


class SpeakupGUIWithTray(SpeakupGUI):
    """Erweiterte GUI mit System Tray Support"""
    
    def __init__(self, root):
        super().__init__(root)
        self.tray_icon = None
        self.minimized_to_tray = False
        
        if TRAY_AVAILABLE:
            self.setup_tray()
            # Override close behavior
            self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
    def setup_tray(self):
        """Erstelle System Tray Icon"""
        # Create icon image
        icon_image = self.create_tray_icon()
        
        # Create menu
        menu = Menu(
            MenuItem("Fenster anzeigen", self.show_window),
            MenuItem("Start/Stop", self.toggle_from_tray),
            Menu.SEPARATOR,
            MenuItem("Beenden", self.quit_from_tray)
        )
        
        # Create tray icon
        self.tray_icon = Icon(
            "speakup",
            icon_image,
            "speakup - Speech-to-Text",
            menu
        )
    
    def create_tray_icon(self):
        """Erstelle Icon-Bild für Tray"""
        # Einfaches Mikrofon-Icon
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Mikrofon zeichnen
        draw.ellipse([20, 10, 44, 40], fill='black')  # Kopf
        draw.rectangle([28, 35, 36, 50], fill='black')  # Stiel
        draw.arc([15, 45, 49, 60], start=0, end=180, fill='black', width=3)  # Bogen
        draw.line([32, 55, 32, 60], fill='black', width=3)  # Basis
        
        return image
    
    def minimize_to_tray(self):
        """Minimiere zu System Tray"""
        if TRAY_AVAILABLE and not self.minimized_to_tray:
            self.root.withdraw()
            self.minimized_to_tray = True
            
            # Start tray icon in thread
            if not self.tray_icon._running:
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
            
            self.log("Minimiert in System Tray")
        else:
            self.on_closing()
    
    def show_window(self):
        """Zeige Fenster wieder an"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.minimized_to_tray = False
        self.log("Fenster wiederhergestellt")
    
    def toggle_from_tray(self):
        """Toggle Start/Stop vom Tray aus"""
        if self.running:
            self.stop_speakup()
        else:
            self.start_speakup()
    
    def quit_from_tray(self):
        """Beende App vom Tray aus"""
        if self.running:
            self.stop_speakup()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
    
    def on_closing(self):
        """Handle window close"""
        if self.running:
            if messagebox.askokcancel("Beenden", "speakup läuft noch. Wirklich beenden?"):
                self.stop_speakup()
                if self.tray_icon:
                    self.tray_icon.stop()
                self.root.destroy()
        else:
            if self.tray_icon:
                self.tray_icon.stop()
            self.root.destroy()


def main():
    """Hauptfunktion"""
    root = tk.Tk()
    
    if TRAY_AVAILABLE:
        app = SpeakupGUIWithTray(root)
        print("✓ GUI mit System Tray gestartet")
    else:
        app = SpeakupGUI(root)
        print("⚠ System Tray nicht verfügbar (pystray/Pillow fehlt)")
        print("  Installiere: pip install pystray pillow")
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
