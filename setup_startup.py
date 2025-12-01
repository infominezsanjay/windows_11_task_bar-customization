import os
import sys
import shutil

def add_to_startup():
    # Path to the python script
    script_path = os.path.abspath("taskbar_widget.py")
    
    # Startup folder path
    startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    
    # Batch file path
    bat_path = os.path.join(startup_folder, "TaskbarMonitor.bat")
    
    # Python executable path (using pythonw.exe to avoid console window)
    python_exe = sys.executable.replace("python.exe", "pythonw.exe")
    
    # Content of the batch file
    # We use 'start ""' to run it without keeping the cmd window open, although pythonw should handle it.
    # But a bat file in startup is the easiest way without admin rights or registry hacking.
    bat_content = f'@echo off\nstart "" "{python_exe}" "{script_path}"'
    
    print(f"Creating startup entry at: {bat_path}")
    print(f"Target script: {script_path}")
    
    try:
        with open(bat_path, "w") as f:
            f.write(bat_content)
        print("Successfully added to startup!")
    except Exception as e:
        print(f"Failed to create startup file: {e}")

if __name__ == "__main__":
    add_to_startup()
