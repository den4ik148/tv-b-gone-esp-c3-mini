import os
import subprocess
from pathlib import Path
import sys
import time

# Pylance/IDE support (ignore errors in editor)
try:
    from SCons.Script import Import # type: ignore
except ImportError:
    pass

Import("env")

def merge_binaries(source, target, env):
    # --- CONFIGURATION ---
    CUSTOM_BIN_NAME = "tvgone_c3mini"
    # ---------------------

    project_dir = Path(env["PROJECT_DIR"])
    merged_bin = project_dir / f"{CUSTOM_BIN_NAME}.bin"

    # Define paths for component binaries
    build_dir = Path(env.subst("$BUILD_DIR"))
    firmware_bin = build_dir / "firmware.bin"
    bootloader_bin = build_dir / "bootloader.bin"
    partitions_bin = build_dir / "partitions.bin"

    # Search for esptool.exe in project root
    esptool_exe = project_dir / "esptool.exe"

    if not esptool_exe.exists():
        print(f"\n[CRITICAL ERROR] esptool.exe not found at: {esptool_exe}")
        print("Please place esptool.exe in your project root directory.")
        return

    # Wait for filesystem to release files after compilation
    time.sleep(1)

    # Command for ESP32-C3 merging (Note: Bootloader starts at 0x0)
    cmd = [
        str(esptool_exe),
        "--chip", "esp32c3",
        "merge_bin",
        "-o", str(merged_bin),
        "--flash_mode", "dio",
        "--flash_size", "4MB",
        "0x0000", str(bootloader_bin),
        "0x8000", str(partitions_bin),
        "0x10000", str(firmware_bin)
    ]

    print(f"\n[BUILDER] Merging binaries into: {merged_bin.name}...")

    try:
        # Run command using shell=True for Windows compatibility
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            shell=True 
        )
        
        if result.returncode != 0:
            print("\n[ESPTOOL ERROR] Merging failed:")
            print(result.stderr)
        else:
            print(f"\n[SUCCESS] Factory image created: {merged_bin}")
            print(f"[*] You can flash this file starting from address 0x0")
            
    except Exception as e:
        print(f"\n[SCRIPT ERROR] An unexpected error occurred: {str(e)}")

# Add post-action to run after firmware.bin is generated
env.AddPostAction(os.path.join("$BUILD_DIR", "${PROGNAME}.bin"), merge_binaries)