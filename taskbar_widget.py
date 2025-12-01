"""
Windows 11 Taskbar Widget & Traffic Monitor
-------------------------------------------
A lightweight, frameless widget for Windows 11 that displays:
- Real-time Network Traffic (Upload/Download)
- System Resource Usage (CPU/Memory)
- Universal Music Player Controls

Author: Antigravity (Generated)
License: MIT
"""

import tkinter as tk
from tkinter import ttk
import psutil
import time
import sys
import os
import threading
import logging
import traceback
from PIL import Image, ImageTk
import pyautogui

VERSION = "1.0.0"

# Setup logging
logging.basicConfig(filename='widget_debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class SystemMonitorWidget:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("System Monitor")
            
            # Remove window decorations (frameless)
            self.root.overrideredirect(True)
            
            # Keep window on top
            self.root.wm_attributes("-topmost", True)
            
            # Set background color
            self.bg_color = "#202020"
            self.fg_color = "#ffffff"
            self.accent_color = "#4cc2ff" # Light blue accent
            self.root.configure(bg=self.bg_color)
            
            # Transparency
            self.root.wm_attributes("-alpha", 0.95)

            # Main container
            # Added pady=5 to increase height to match Taskbar (~48px)
            self.main_frame = tk.Frame(self.root, bg=self.bg_color)
            self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # Font settings - Standard size 8
            self.font_style = ("Segoe UI", 8)
            self.font_bold = ("Segoe UI", 8, "bold")
            
            # --- Layout: [Music] | [Network] | [CPU/Mem] | [Close] ---
            
            # 1. Music Section
            self.music_frame = tk.Frame(self.main_frame, bg=self.bg_color)
            self.music_frame.pack(side="left", padx=5)
            
            # Album Art (Placeholder)
            self.album_art_label = tk.Label(self.music_frame, text="♫", font=("Segoe UI", 12), 
                                          bg="#333333", fg=self.fg_color, width=4)
            self.album_art_label.pack(side="left", padx=2)
            
            # Controls & Info
            self.music_info_frame = tk.Frame(self.music_frame, bg=self.bg_color)
            self.music_info_frame.pack(side="left", padx=2)
            
            self.song_title = tk.Label(self.music_info_frame, text="No Music", font=self.font_bold, 
                                     bg=self.bg_color, fg=self.fg_color, width=15, anchor="w")
            self.song_title.pack(side="top", fill="x", pady=0)
            
            self.controls_frame = tk.Frame(self.music_info_frame, bg=self.bg_color)
            self.controls_frame.pack(side="bottom", fill="x", anchor="w", pady=0)
            
            # Buttons (Prev, Play/Pause, Next)
            self.btn_prev = tk.Label(self.controls_frame, text="⏮", font=self.font_style, bg=self.bg_color, fg=self.fg_color, cursor="hand2")
            self.btn_prev.pack(side="left", padx=2)
            self.btn_prev.bind("<Button-1>", lambda e: self.media_control("prev"))
            
            self.btn_play = tk.Label(self.controls_frame, text="⏯", font=self.font_style, bg=self.bg_color, fg=self.fg_color, cursor="hand2")
            self.btn_play.pack(side="left", padx=2)
            self.btn_play.bind("<Button-1>", lambda e: self.media_control("playpause"))
            
            self.btn_next = tk.Label(self.controls_frame, text="⏭", font=self.font_style, bg=self.bg_color, fg=self.fg_color, cursor="hand2")
            self.btn_next.pack(side="left", padx=2)
            self.btn_next.bind("<Button-1>", lambda e: self.media_control("next"))

            # Separator
            tk.Frame(self.main_frame, width=1, bg="#444444").pack(side="left", fill="y", padx=5, pady=2)

            # 2. Network Section (Stacked)
            self.net_frame = tk.Frame(self.main_frame, bg=self.bg_color)
            self.net_frame.pack(side="left", padx=5)
            
            self.net_up_label = tk.Label(self.net_frame, text="▲ 0.0 MB/s", font=self.font_style, bg=self.bg_color, fg="#4caf50", anchor="w")
            self.net_up_label.pack(side="top", fill="x", pady=0)
            
            self.net_down_label = tk.Label(self.net_frame, text="▼ 0.0 MB/s", font=self.font_style, bg=self.bg_color, fg="#2196f3", anchor="w")
            self.net_down_label.pack(side="bottom", fill="x", pady=0)

            # Separator
            tk.Frame(self.main_frame, width=1, bg="#444444").pack(side="left", fill="y", padx=5, pady=2)

            # 3. CPU & Memory Section (Stacked)
            self.sys_frame = tk.Frame(self.main_frame, bg=self.bg_color)
            self.sys_frame.pack(side="left", padx=5)
            
            self.cpu_label = tk.Label(self.sys_frame, text="CPU: 0%", font=self.font_style, bg=self.bg_color, fg=self.fg_color, anchor="w")
            self.cpu_label.pack(side="top", fill="x", pady=0)
            
            self.mem_label = tk.Label(self.sys_frame, text="MEM: 0%", font=self.font_style, bg=self.bg_color, fg=self.fg_color, anchor="w")
            self.mem_label.pack(side="bottom", fill="x", pady=0)

            # 4. Close Button
            self.close_btn = tk.Label(self.main_frame, text="×", font=("Segoe UI", 10, "bold"), bg=self.bg_color, fg="#ff5555", cursor="hand2")
            self.close_btn.pack(side="right", padx=5, anchor="center")
            self.close_btn.bind("<Button-1>", lambda e: self.exit_app())

            # Draggable logic
            self.root.bind("<Button-1>", self.start_drag)
            self.root.bind("<B1-Motion>", self.do_drag)
            
            # Initial stats
            self.last_net_io = psutil.net_io_counters()
            self.last_time = time.time()
            
            # Attempt to initialize Media Manager (Async)
            self.media_manager = None
            threading.Thread(target=self.init_media_manager, daemon=True).start()
            
            # Initial Position
            self.set_initial_position()
            
            # Start updating
            self.update_stats()
            self.check_keep_on_top()
            
        except Exception as e:
            logging.error(f"Initialization error: {traceback.format_exc()}")

    def init_media_manager(self):
        # Placeholder for winsdk initialization
        # We will try to import winsdk here to avoid crashing if it's not installed
        try:
            import winsdk.windows.media.control as wmc
            # If successful, we can set up the session manager
            # This part is complex and requires async loop integration or polling
            # For now, we'll stick to basic key simulation if winsdk is missing
            pass
        except ImportError:
            logging.warning("winsdk not found. Music metadata will be unavailable.")

    def media_control(self, action):
        try:
            if action == "playpause":
                pyautogui.press("playpause")
            elif action == "next":
                pyautogui.press("nexttrack")
            elif action == "prev":
                pyautogui.press("prevtrack")
        except Exception as e:
            logging.error(f"Media control error: {e}")

    def exit_app(self):
        self.root.quit()
        sys.exit()
        
    def set_initial_position(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        screen_height = self.root.winfo_screenheight()
        
        # Position: Bottom Left (x=0)
        # "very left side of task bar"
        x_pos = 0
        y_pos = screen_height - height # Flush with bottom
        
        self.root.geometry(f'+{x_pos}+{y_pos}')

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def do_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def check_keep_on_top(self):
        # Periodically ensure window is on top
        self.root.lift()
        self.root.wm_attributes("-topmost", True)
        self.root.after(2000, self.check_keep_on_top)

    def update_stats(self):
        try:
            # CPU
            cpu_percent = psutil.cpu_percent()
            self.cpu_label.config(text=f"CPU: {cpu_percent}%")
            
            # Memory
            mem = psutil.virtual_memory()
            self.mem_label.config(text=f"MEM: {mem.percent}%")
            
            # Network
            current_net_io = psutil.net_io_counters()
            current_time = time.time()
            
            time_delta = current_time - self.last_time
            if time_delta > 0.5:
                bytes_sent = current_net_io.bytes_sent - self.last_net_io.bytes_sent
                bytes_recv = current_net_io.bytes_recv - self.last_net_io.bytes_recv
                
                # Speed in Bytes per second
                sent_speed = bytes_sent / time_delta
                recv_speed = bytes_recv / time_delta
                
                # Convert to MB/s
                sent_mb = sent_speed / (1024 * 1024)
                recv_mb = recv_speed / (1024 * 1024)
                
                self.net_up_label.config(text=f"▲ {sent_mb:.2f} MB/s")
                self.net_down_label.config(text=f"▼ {recv_mb:.2f} MB/s")
                
                self.last_net_io = current_net_io
                self.last_time = current_time
                
            # Update Music Metadata (If we had winsdk working, we'd pull it here)
            # For now, just placeholder or basic check
            
        except Exception as e:
            logging.error(f"Update stats error: {e}")
        
        # Schedule next update
        self.root.after(1000, self.update_stats)

if __name__ == "__main__":
    try:
        app = SystemMonitorWidget()
        app.root.mainloop()
    except Exception as e:
        logging.critical(f"Fatal error: {traceback.format_exc()}")

