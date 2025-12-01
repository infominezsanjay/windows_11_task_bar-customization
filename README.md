# 🚀 Windows 11 Taskbar Widget & Traffic Monitor

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%2011-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

A sleek, **Windows 11-style Taskbar Widget** that combines a **real-time Traffic Monitor**, **System Resource Stats** (CPU/RAM), and a **Universal Music Player** controller into a single, compact interface. Designed to blend perfectly with the Windows 11 taskbar aesthetics.

![Windows 11 Taskbar Widget Screenshot](screenshot.png)

## ✨ Features

*   **📊 Real-Time Traffic Monitor**: Monitor your network upload and download speeds instantly.
*   **💻 System Stats**: Keep an eye on your CPU and Memory usage with a clean, stacked layout.
*   **🎵 Advanced Music Control**: 
    *   **Now Playing**: Displays current song title, artist, and album art.
    *   **Dynamic Controls**: Play/Pause button updates based on actual playback state.
    *   **Universal Support**: Works with Spotify, YouTube (Chrome/Edge), VLC, and more.
*   **🎨 Native Aesthetics**: Designed with a dark theme, transparency, and compact dimensions that match the native Windows 11 taskbar.
*   **🚀 Auto-Startup**: Automatically launches silently in the background when you log in.
*   **🖱️ Draggable & Persistent**: Drag it anywhere (defaults to the left) and it stays on top of other windows.

## 🛠️ Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/windows-11-taskbar-widget.git
    cd windows-11-taskbar-widget
    ```

2.  **Install Dependencies**
    Ensure you have Python installed (Python 3.10+ recommended). Then run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Widget**
    ```bash
    python taskbar_widget.py
    ```

## ⚙️ Setup Auto-Start

To have the widget start automatically with Windows:

1.  Run the setup script:
    ```bash
    python setup_startup.py
    ```
2.  This will create a `TaskbarMonitor.bat` file in your Windows Startup folder.

## 🧩 Requirements

*   Windows 10 or Windows 11
*   Python 3.10 or higher
*   **Core Libraries**: `psutil`, `pillow`, `pyautogui`
*   **Windows Runtime Libraries**: `winrt-runtime`, `winrt-Windows.Media.Control`, `winrt-Windows.Storage.Streams`, `winrt-Windows.Foundation`

## ❓ Troubleshooting

*   **Music Info Not Showing?** 
    Ensure you have enabled "Show media controls" in your browser or music app settings. For Windows 11, ensure the "Global Media Transport Controls" are active (usually automatic).
*   **WinRT Installation Issues?**
    If `pip install` fails for the winrt packages, ensure you have the latest pip: `python -m pip install --upgrade pip`.

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features (like weather integration, stock tickers, or more themes), feel free to fork the repo and submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
*Keywords: Windows 11 Taskbar, Traffic Monitor, Network Speed Meter, Python Widget, System Monitor, Music Controller, Taskbar Customization, Desktop Widget, WinRT, Media Controls*
