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
import subprocess
from PIL import Image, ImageTk
import pyautogui
import io

import json

VERSION = "1.1.0"

# Setup logging
logging.basicConfig(filename='widget_debug.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
# Suppress PIL/Pillow debug logs
for logger_name in ['PIL', 'PIL.Image', 'PIL.PngImagePlugin']:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

class ConfigManager:
    DEFAULT_CONFIG = {
        "show_traffic": True,
        "show_system": True,
        "music_mode": "always", # "always" or "auto"
        "viz_preset": "Default", # Default, Bass, Treble, Rock, Pop
        "position": {"x": 0, "y": -1},
        "theme": "dark"
    }
    
    def __init__(self, filename="widget_config.json"):
        self.filename = filename
        self.config = self.load_config()
        
    def load_config(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
        
    def save_config(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error(f"Config save error: {e}")

    def get(self, key):
        return self.config.get(key, self.DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

class Visualizer:
    def __init__(self, parent, config_manager, bg_color, accent_color):
        self.parent = parent
        self.config = config_manager
        self.bg_color = bg_color
        self.accent_color = accent_color
        
        self.canvas = tk.Canvas(parent, width=40, height=15, bg=bg_color, highlightthickness=0)
        self.canvas.pack(side="left", padx=5)
        
        self.bars = []
        self.num_bars = 5
        self.bar_width = 5
        self.gap = 2
        
        for i in range(self.num_bars):
            x = i * (self.bar_width + self.gap)
            bar = self.canvas.create_rectangle(x, 15, x + self.bar_width, 15, fill=accent_color, outline="")
            self.bars.append(bar)
            
    def animate(self, is_playing):
        import random
        preset = self.config.get("viz_preset")
        
        if is_playing:
            for i, bar in enumerate(self.bars):
                # Base random height
                val = random.randint(3, 15)
                
                # Apply Presets
                if preset == "Bass":
                    # Boost left bars
                    if i < 2: val = min(15, val + 5)
                    else: val = max(2, val - 3)
                elif preset == "Treble":
                    # Boost right bars
                    if i > 2: val = min(15, val + 5)
                    else: val = max(2, val - 3)
                elif preset == "Rock":
                    # V-shape (Boost ends)
                    if i == 0 or i == 4: val = min(15, val + 4)
                    elif i == 2: val = max(2, val - 4)
                elif preset == "Pop":
                    # Inverted V (Boost mid)
                    if i == 2: val = min(15, val + 5)
                    elif i == 0 or i == 4: val = max(2, val - 3)
                
                # Ensure bounds
                val = max(2, min(15, val))
                
                self.canvas.coords(bar, 
                                 self.canvas.coords(bar)[0], 
                                 15-val, 
                                 self.canvas.coords(bar)[2], 
                                 15)
        else:
            # Flat line
            for bar in self.bars:
                self.canvas.coords(bar, 
                                 self.canvas.coords(bar)[0], 
                                 14, 
                                 self.canvas.coords(bar)[2], 
                                 15)

class SystemMonitorWidget:
    def __init__(self):
        try:
            self.config = ConfigManager()
            
            self.root = tk.Tk()
            self.root.title("System Monitor")
            
            # Remove window decorations (frameless)
            self.root.overrideredirect(True)
            
            # Keep window on top
            self.root.wm_attributes("-topmost", True)
            
            # Set background color
            self.bg_color = "#202020"
            self.fg_color = "#ffffff"
            self.accent_color = "#4cc2ff"
            self.root.configure(bg=self.bg_color)
            
            # Transparency
            self.root.wm_attributes("-alpha", 0.95)

            # Main container
            self.main_frame = tk.Frame(self.root, bg=self.bg_color)
            self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # Font settings
            self.font_style = ("Segoe UI", 8)
            self.font_bold = ("Segoe UI", 8, "bold")
            
            # --- Layout ---
            
            # 1. Music Section
            self.music_frame = tk.Frame(self.main_frame, bg=self.bg_color)
            self.music_frame.pack(side="left", padx=5)
            
            # Album Art
            self.album_art_label = tk.Label(self.music_frame, text="♫", font=("Segoe UI", 14), 
                                          bg="#333333", fg=self.fg_color)
            self.album_art_label.pack(side="left", padx=2)
            
            # Controls & Info
            self.music_info_frame = tk.Frame(self.music_frame, bg=self.bg_color)
            self.music_info_frame.pack(side="left", padx=5)
            
            # Song Title
            self.song_title = tk.Label(self.music_info_frame, text="No Music", font=self.font_bold, 
                                     bg=self.bg_color, fg=self.fg_color, width=20, anchor="w")
            self.song_title.pack(side="top", fill="x", pady=0)
            
            # Controls Frame
            self.controls_frame = tk.Frame(self.music_info_frame, bg=self.bg_color)
            self.controls_frame.pack(side="bottom", fill="x", anchor="w", pady=0)
            
            # Buttons
            button_font = ("Segoe UI", 12)
            self.btn_prev = tk.Label(self.controls_frame, text="⏮", font=button_font, bg=self.bg_color, fg=self.fg_color, cursor="hand2", bd=0, highlightthickness=0)
            self.btn_prev.pack(side="left", padx=3)
            self.btn_prev.bind("<Button-1>", lambda e: self.media_control("prev"))
            
            self.btn_play = tk.Label(self.controls_frame, text="⏯", font=button_font, bg=self.bg_color, fg=self.fg_color, cursor="hand2", bd=0, highlightthickness=0)
            self.btn_play.pack(side="left", padx=3)
            self.btn_play.bind("<Button-1>", lambda e: self.media_control("playpause"))
            
            self.btn_next = tk.Label(self.controls_frame, text="⏭", font=button_font, bg=self.bg_color, fg=self.fg_color, cursor="hand2", bd=0, highlightthickness=0)
            self.btn_next.pack(side="left", padx=3)
            self.btn_next.bind("<Button-1>", lambda e: self.media_control("next"))
            
            # Visualizer
            self.visualizer = Visualizer(self.controls_frame, self.config, self.bg_color, self.accent_color)

            # Separator 1
            self.sep1 = tk.Frame(self.main_frame, width=1, bg="#444444")
            self.sep1.pack(side="left", fill="y", padx=5, pady=2)

            # 2. Network Section
            self.net_frame = tk.Frame(self.main_frame, bg=self.bg_color)
            self.net_frame.pack(side="left", padx=5)
            
            self.net_up_label = tk.Label(self.net_frame, text="▲ 0.0 MB/s", font=self.font_style, bg=self.bg_color, fg="#4caf50", anchor="w")
            self.net_up_label.pack(side="top", fill="x", pady=0)
            
            self.net_down_label = tk.Label(self.net_frame, text="▼ 0.0 MB/s", font=self.font_style, bg=self.bg_color, fg="#2196f3", anchor="w")
            self.net_down_label.pack(side="bottom", fill="x", pady=0)

            # Separator 2
            self.sep2 = tk.Frame(self.main_frame, width=1, bg="#444444")
            self.sep2.pack(side="left", fill="y", padx=5, pady=2)

            # 3. CPU & Memory Section
            self.sys_frame = tk.Frame(self.main_frame, bg=self.bg_color)
            self.sys_frame.pack(side="left", padx=5)
            
            self.cpu_label = tk.Label(self.sys_frame, text="CPU: 0%", font=self.font_style, bg=self.bg_color, fg=self.fg_color, anchor="w")
            self.cpu_label.pack(side="top", fill="x", pady=0)
            
            self.mem_label = tk.Label(self.sys_frame, text="MEM: 0%", font=self.font_style, bg=self.bg_color, fg=self.fg_color, anchor="w")
            self.mem_label.pack(side="bottom", fill="x", pady=0)

            # 4. Close Button
            self.close_btn = tk.Label(self.main_frame, text="×", font=("Segoe UI", 10, "bold"), bg=self.bg_color, fg="#ff5555", cursor="hand2", bd=0, highlightthickness=0)
            self.close_btn.pack(side="right", padx=5, anchor="center")
            self.close_btn.bind("<Button-1>", lambda e: self.exit_app())

            # Draggable logic
            self.root.bind("<Button-1>", self.start_drag)
            self.root.bind("<B1-Motion>", self.do_drag)
            
            # Context Menu
            self.create_context_menu()
            self.root.bind("<Button-3>", self.show_context_menu)
            for widget in [self.main_frame, self.music_frame, self.net_frame, self.sys_frame, 
                         self.song_title, self.album_art_label, self.net_up_label, self.net_down_label,
                         self.cpu_label, self.mem_label]:
                widget.bind("<Button-3>", self.show_context_menu)
            
            # Initial stats
            self.last_net_io = psutil.net_io_counters()
            self.last_time = time.time()
            
            # Attempt to initialize Media Manager (Async)
            self.media_manager = MediaManager(self.update_media_ui, self.update_playback_state)
            self.media_manager.start()
            
            # Initial Position
            self.set_initial_position()
            
            # Apply Config Visibility
            self.apply_visibility()
            
            # Start updating
            self.update_stats()
            self.check_keep_on_top()
            self.animate_visualizer()
            
        except Exception as e:
            logging.error(f"Initialization error: {traceback.format_exc()}")
            
        except Exception as e:
            logging.error(f"Initialization error: {traceback.format_exc()}")

    def update_media_ui(self, title, artist, image_data):
        self.last_title = title
        self.last_artist = artist
        
        # Check Auto-Hide Logic
        if self.config.get("music_mode") == "auto" and not title:
            self.music_frame.pack_forget()
            self.sep1.pack_forget()
            return
        
        # Ensure visible if it was hidden
        if not self.music_frame.winfo_ismapped():
            self.apply_visibility()
            
        # Update Title
        display_text = f"{title} - {artist}" if title else "No Music"
        if len(display_text) > 25:
            display_text = display_text[:22] + "..."
        self.song_title.config(text=display_text)
        
        # Update Image
        if image_data:
            try:
                image = Image.open(io.BytesIO(image_data))
                # Increased size to 40x40
                image = image.resize((40, 40), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.album_art_label.config(image=photo, text="", width=0) # Reset width
                self.album_art_label.image = photo # Keep reference
            except Exception as e:
                logging.error(f"Image update error: {e}")
        else:
            self.album_art_label.config(image="", text="♫", width=4) # Restore width for text
    
    def update_playback_state(self, is_playing):
        """Update play/pause button based on playback state"""
        self.is_playing = is_playing
        if is_playing:
            self.btn_play.config(text="⏸")  # Pause icon when playing
        else:
            self.btn_play.config(text="▶")  # Play icon when paused

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
        if self.media_manager:
            self.media_manager.stop()
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

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        
        # Visibility
        self.context_menu.add_checkbutton(label="Show Traffic", command=self.toggle_traffic, 
                                        variable=tk.BooleanVar(value=self.config.get("show_traffic")))
        self.context_menu.add_checkbutton(label="Show System Stats", command=self.toggle_system, 
                                        variable=tk.BooleanVar(value=self.config.get("show_system")))
        self.context_menu.add_separator()
        
        # Music Mode
        self.music_mode_var = tk.StringVar(value=self.config.get("music_mode"))
        self.context_menu.add_radiobutton(label="Always Show Music", variable=self.music_mode_var, 
                                        value="always", command=self.toggle_music_mode)
        self.context_menu.add_radiobutton(label="Auto-Hide Music", variable=self.music_mode_var, 
                                        value="auto", command=self.toggle_music_mode)
        
        self.context_menu.add_separator()
        
        # Visualizer Style
        self.viz_menu = tk.Menu(self.context_menu, tearoff=0)
        self.context_menu.add_cascade(label="Visualizer Style", menu=self.viz_menu)
        
        self.viz_preset_var = tk.StringVar(value=self.config.get("viz_preset"))
        presets = ["Default", "Bass", "Treble", "Rock", "Pop"]
        for p in presets:
            self.viz_menu.add_radiobutton(label=p, variable=self.viz_preset_var, value=p, command=self.change_viz_preset)
            
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Reset Position", command=self.set_initial_position)
        self.context_menu.add_command(label="Exit", command=self.exit_app)

    def show_context_menu(self, event):
        # Update checkmarks dynamically
        self.context_menu.entryconfigure(0, variable=tk.BooleanVar(value=self.config.get("show_traffic")))
        self.context_menu.entryconfigure(1, variable=tk.BooleanVar(value=self.config.get("show_system")))
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def toggle_traffic(self):
        new_val = not self.config.get("show_traffic")
        self.config.set("show_traffic", new_val)
        self.apply_visibility()

    def toggle_system(self):
        new_val = not self.config.get("show_system")
        self.config.set("show_system", new_val)
        self.apply_visibility()

    def toggle_music_mode(self):
        self.config.set("music_mode", self.music_mode_var.get())
        if hasattr(self, 'last_title'):
             self.update_media_ui(self.last_title, self.last_artist, None)
             
    def change_viz_preset(self):
        self.config.set("viz_preset", self.viz_preset_var.get())

    def apply_visibility(self):
        # Unpack all optional frames first to avoid order issues
        self.net_frame.pack_forget()
        self.sys_frame.pack_forget()
        self.sep1.pack_forget()
        self.sep2.pack_forget()
        self.close_btn.pack_forget()
        
        # Music is handled by update_media_ui mostly, but we ensure it's first if visible
        # We assume music_frame is packed LEFT.
        
        # Determine what is visible
        show_traffic = self.config.get("show_traffic")
        show_system = self.config.get("show_system")
        music_visible = self.music_frame.winfo_ismapped()
        
        # Re-pack in order: Music -> Sep1 -> Net -> Sep2 -> Sys -> Close
        
        if music_visible and (show_traffic or show_system):
            self.sep1.pack(side="left", fill="y", padx=5, pady=2)
            
        if show_traffic:
            self.net_frame.pack(side="left", padx=5)
            if show_system:
                self.sep2.pack(side="left", fill="y", padx=5, pady=2)
                
        if show_system:
            self.sys_frame.pack(side="left", padx=5)
            
        self.close_btn.pack(side="right", padx=5, anchor="center")

    def animate_visualizer(self):
        if hasattr(self, 'visualizer'):
            is_playing = getattr(self, 'is_playing', False)
            self.visualizer.animate(is_playing)
        self.root.after(100, self.animate_visualizer)

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
                
        except Exception as e:
            logging.error(f"Update stats error: {e}")
        
        # Schedule next update
        self.root.after(1000, self.update_stats)

class MediaManager:
    """Fetches media info using winrt (official)"""
    def __init__(self, callback, playback_callback):
        self.callback = callback
        self.playback_callback = playback_callback
        self.thread = None
        self.running = False

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _run_loop(self):
        """Poll media info using winrt"""
        try:
            import asyncio
            from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
            from winrt.windows.storage.streams import DataReader, Buffer, InputStreamOptions
            
            async def get_media_info():
                try:
                    # Request session manager
                    manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
                    session = manager.get_current_session()
                    
                    if session:
                        # Get media properties
                        info = await session.try_get_media_properties_async()
                        title = info.title
                        artist = info.artist
                        
                        # Get playback info
                        playback_info = session.get_playback_info()
                        playback_status = playback_info.playback_status if playback_info else None
                        # PlaybackStatus: 4 is Playing, 5 is Paused
                        is_playing = (playback_status == 4)
                        
                        # Get thumbnail
                        thumbnail_data = None
                        if info.thumbnail:
                            try:
                                stream = await info.thumbnail.open_read_async()
                                size = stream.size
                                if size > 0:
                                    buffer = Buffer(size)
                                    await stream.read_async(buffer, size, InputStreamOptions.NONE)
                                    reader = DataReader.from_buffer(buffer)
                                    byte_arr = bytearray(size)
                                    reader.read_bytes(byte_arr)
                                    thumbnail_data = bytes(byte_arr)
                            except Exception as e:
                                logging.error(f"Thumbnail error: {e}")
                                
                        return title, artist, thumbnail_data, is_playing
                    
                    return None, None, None, None
                except Exception as e:
                    logging.error(f"Async media error: {e}")
                    return None, None, None, None

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            while self.running:
                try:
                    title, artist, thumb, is_playing = loop.run_until_complete(get_media_info())
                    self.callback(title, artist, thumb)
                    if is_playing is not None:
                        self.playback_callback(is_playing)
                except Exception as e:
                    logging.error(f"Loop error: {e}")
                
                time.sleep(2)  # Poll every 2 seconds
                
        except ImportError as e:
            logging.warning(f"winrt not installed: {e}. Media features disabled.")
        except Exception as e:
            logging.error(f"Media Manager fatal error: {e}")



if __name__ == "__main__":
    try:
        app = SystemMonitorWidget()
        app.root.mainloop()
    except Exception as e:
        logging.critical(f"Fatal error: {traceback.format_exc()}")

