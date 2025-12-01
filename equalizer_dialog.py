"""
Simplified Equalizer GUI Dialog - More Reliable Version
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

class EqualizerDialog:
    """10-band graphic equalizer dialog - simplified version"""
    
    def __init__(self, parent, eq_manager, config_manager):
        self.eq_manager = eq_manager
        self.config = config_manager
        self.parent = parent
        
        logging.info("=== Creating Equalizer Dialog ===")
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Audio Equalizer")
        self.dialog.geometry("750x500")
        self.dialog.configure(bg="#1e1e1e")
        
        # Make it modal
        self.dialog.transient(parent)
        
        logging.info(f"Dialog created, checking Equalizer APO...")
        logging.info(f"APO Available: {self.eq_manager.is_available()}")
        
        # Check if Equalizer APO is available
        if not self.eq_manager.is_available():
            logging.warning("Equalizer APO not found")
            self.show_install_message()
            return
        
        logging.info("Building UI...")
        try:
            self.build_ui()
            logging.info("UI built successfully")
        except Exception as e:
            logging.error(f"Error building UI: {e}")
            import traceback
            logging.error(traceback.format_exc())
            messagebox.showerror("Error", f"Failed to create equalizer dialog:\n{e}")
            self.dialog.destroy()
            return
        
        # Center the dialog
        self.center_dialog()
        logging.info("Dialog ready")
    
    def build_ui(self):
        """Build the equalizer UI"""
        bg = "#1e1e1e"
        fg = "#ffffff"
        accent = "#4cc2ff"
        
        # Title
        tk.Label(self.dialog, text="🎚️ 10-Band Graphic Equalizer", 
                font=("Segoe UI", 16, "bold"), bg=bg, fg=fg).pack(pady=15)
        
        # Preset selector
        preset_frame = tk.Frame(self.dialog, bg=bg)
        preset_frame.pack(pady=10)
        
        tk.Label(preset_frame, text="Preset:", font=("Segoe UI", 11), 
                bg=bg, fg=fg).pack(side="left", padx=10)
        
        self.preset_var = tk.StringVar(value=self.config.get("eq_preset") or "Flat")
        
        preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var, 
                                   values=list(self.eq_manager.PRESETS.keys()),
                                   state="readonly", width=20, font=("Segoe UI", 10))
        preset_combo.pack(side="left", padx=5)
        preset_combo.bind("<<ComboboxSelected>>", self.load_preset)
        
        # Sliders area with canvas and scrollbar (in case of overflow)
        canvas_frame = tk.Frame(self.dialog, bg="#2e2e2e", bd=2, relief="groove")
        canvas_frame.pack(pady=15, padx=20, fill="both", expand=True)
        
        # Inner frame for sliders
        sliders_container = tk.Frame(canvas_frame, bg=bg)
        sliders_container.pack(padx=15, pady=15)
        
        self.sliders = []
        self.value_labels = []
        
        # Get current settings
        current_gains = self.eq_manager.get_current_settings() or [0] * 10
        logging.info(f"Current gains: {current_gains}")
        
        # Create sliders using pack (more reliable than grid)
        slider_row = tk.Frame(sliders_container, bg=bg)
        slider_row.pack()
        
        for i, (freq, gain) in enumerate(zip(self.eq_manager.BANDS, current_gains)):
            # Each slider in its own frame
            slider_frame = tk.Frame(slider_row, bg=bg)
            slider_frame.pack(side="left", padx=10)
            
            # Value display
            val_label = tk.Label(slider_frame, text=f"{gain:+.1f}dB", 
                                font=("Segoe UI", 10, "bold"), bg=bg, fg=accent,
                                width=7)
            val_label.pack()
            self.value_labels.append(val_label)
            
            # Slider
            slider = tk.Scale(slider_frame, from_=12, to=-12, resolution=0.5,
                            orient="vertical", length=220, width=30,
                            bg=bg, fg=accent, 
                            troughcolor="#333333",
                            activebackground=accent,
                            highlightthickness=0, bd=0, 
                            showvalue=0,
                            command=lambda val, idx=i: self.on_slider_change(idx, val))
            slider.set(gain)
            slider.pack(pady=5)
            self.sliders.append(slider)
            
            # Frequency label
            freq_text = f"{freq}Hz" if freq < 1000 else f"{freq//1000}kHz"
            tk.Label(slider_frame, text=freq_text, font=("Segoe UI", 9), 
                    bg=bg, fg=fg).pack()
        
        logging.info(f"Created {len(self.sliders)} sliders")
        
        # Buttons
        btn_frame = tk.Frame(self.dialog, bg=bg)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Reset to Flat", command=self.reset_flat,
                 bg="#555555", fg=fg, relief="flat", padx=20, pady=10,
                 font=("Segoe UI", 10), cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="✓ Apply", command=self.apply_settings,
                 bg=accent, fg="#000000", relief="flat", padx=30, pady=10,
                 font=("Segoe UI", 11, "bold"), cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Close", command=self.dialog.destroy,
                 bg="#555555", fg=fg, relief="flat", padx=20, pady=10,
                 font=("Segoe UI", 10), cursor="hand2").pack(side="left", padx=5)
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        w = self.dialog.winfo_width()
        h = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (w // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (h // 2)
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
    
    def show_install_message(self):
        """Show Equalizer APO installation instructions"""
        tk.Label(self.dialog, text="⚠️ Equalizer APO Not Found", 
                font=("Segoe UI", 18, "bold"), bg="#1e1e1e", fg="#ff9800").pack(pady=30)
        
        msg = tk.Text(self.dialog, wrap="word", height=15, width=70, 
                     bg="#2e2e2e", fg="#ffffff", font=("Segoe UI", 10),
                     relief="flat", padx=20, pady=20)
        msg.pack(pady=20, padx=30)
        msg.insert("1.0", self.eq_manager.install_instructions())
        msg.config(state="disabled")
        
        tk.Button(self.dialog, text="Close", command=self.dialog.destroy,
                 bg="#4cc2ff", fg="#000000", relief="flat", padx=40, pady=12,
                 font=("Segoe UI", 12, "bold"), cursor="hand2").pack(pady=20)
        
        self.center_dialog()
    
    def on_slider_change(self, index, value):
        """Handle slider movement - apply in real-time"""
        val = float(value)
        self.value_labels[index].config(text=f"{val:+.1f}dB")
        
        # Apply changes in real-time
        if hasattr(self, 'real_time_timer'):
            self.dialog.after_cancel(self.real_time_timer)
        
        # Debounce: apply after 100ms of no changes
        self.real_time_timer = self.dialog.after(100, self.apply_settings_silent)
    
    def load_preset(self, event=None):
        """Load preset values"""
        preset = self.preset_var.get()
        if preset in self.eq_manager.PRESETS:
            gains = self.eq_manager.PRESETS[preset]
            for slider, gain in zip(self.sliders, gains):
                slider.set(gain)
    
    def reset_flat(self):
        """Reset all to 0dB"""
        for slider in self.sliders:
            slider.set(0)
        self.preset_var.set("Flat")
    
    def apply_settings_silent(self):
        """Apply EQ settings without visual feedback (for real-time updates)"""
        gains = [slider.get() for slider in self.sliders]
        self.eq_manager.apply_settings(gains)
    
    def apply_settings(self):
        """Apply EQ settings with visual feedback"""
        gains = [slider.get() for slider in self.sliders]
        logging.info(f"Applying gains: {gains}")
        
        if self.eq_manager.apply_settings(gains):
            self.config.set("eq_preset", self.preset_var.get())
            
            # Visual feedback
            for label in self.value_labels:
                label.config(fg="#00ff00")
                self.dialog.after(300, lambda l=label: l.config(fg="#4cc2ff"))
            
            logging.info("EQ applied successfully")
        else:
            messagebox.showerror("Error", 
                "Failed to apply equalizer settings.\n\nMake sure Equalizer APO is properly installed and configured.")
