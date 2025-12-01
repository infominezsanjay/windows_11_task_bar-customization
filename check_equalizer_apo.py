# Equalizer APO Setup Check
# This script verifies that Equalizer APO is properly configured

import os
from pathlib import Path

print("=" * 60)
print("Equalizer APO Configuration Checker")
print("=" * 60)

# Check installation
apo_path = Path("C:\\Program Files\\EqualizerAPO")
if not apo_path.exists():
    print("❌ Equalizer APO is NOT installed")
    print("\nPlease install from: https://sourceforge.net/projects/equalizerapo/")
    input("\nPress Enter to exit...")
    exit(1)

print(f"✓ Equalizer APO found at: {apo_path}")

# Check config directory
config_dir = apo_path / "config"
if not config_dir.exists():
    print("❌ Config directory not found")
    input("\nPress Enter to exit...")
    exit(1)

print(f"✓ Config directory exists")

# Check config file
config_file = config_dir / "config.txt"
if config_file.exists():
    print(f"✓ Config file exists: {config_file}")
    print("\nCurrent config content:")
    print("-" * 60)
    with open(config_file, 'r') as f:
        print(f.read())
    print("-" * 60)
else:
    print("⚠ Config file doesn't exist yet (will be created)")

# Check for device configuration
device_txt = apo_path / "device.txt"
if device_txt.exists():
    print(f"\n✓ Device configuration found")
    with open(device_txt, 'r') as f:
        devices = f.read().strip().split('\n')
        print(f"   Configured devices: {len(devices)}")
        for dev in devices[:3]:  # Show first 3
            print(f"   - {dev}")
else:
    print("\n⚠ WARNING: No devices configured!")
    print("   Please run Configurator.exe from Equalizer APO folder")
    print("   and select your audio playback device")

print("\n" + "=" * 60)
print("IMPORTANT NOTES:")
print("=" * 60)
print("1. Equalizer APO only works on devices you've selected")
print("2. After installing APO, you MUST restart your computer")
print("3. Changes to config.txt are auto-loaded (may take 1-2 seconds)")
print("4. Make sure NO other apps are using exclusive mode on your audio device")
print("5. If sound doesn't change, try:")
print("   - Restart audio playback")
print("   - Check Windows Sound settings")
print("   - Run Configurator.exe to verify device selection")
print("=" * 60)

input("\nPress Enter to exit...")
