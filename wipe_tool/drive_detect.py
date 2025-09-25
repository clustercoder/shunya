# wipe_tool/drive_detect.py

import subprocess
import json
import platform

def list_drives():
    """
    Cross-platform drive detection:
    - Linux: uses lsblk
    - macOS: uses diskutil
    """
    system = platform.system()

    if system == "Linux":
        try:
            result = subprocess.run(
                ["lsblk", "-J", "-o", "NAME,SIZE,TYPE,MOUNTPOINT"],
                capture_output=True,
                text=True,
                check=True
            )
            data = json.loads(result.stdout)
            drives = []
            for device in data.get("blockdevices", []):
                drives.append({
                    "name": f"/dev/{device['name']}",
                    "size": device.get("size", "Unknown"),
                    "type": device.get("type", "Unknown"),
                    "mountpoint": device.get("mountpoint", None)
                })
            return drives
        except Exception as e:
            print(f"[!] Error running lsblk: {e}")
            return []

    elif system == "Darwin":  # macOS
        try:
            result = subprocess.run(
                ["diskutil", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            drives = []
            for line in result.stdout.splitlines():
                if line.strip().startswith("/dev/disk"):
                    parts = line.split()
                    if len(parts) >= 2:
                        drives.append({
                            "name": parts[0],
                            "size": parts[-1] if parts[-1].endswith("B") else "Unknown",
                            "type": "disk",
                            "mountpoint": None  # diskutil doesn't show mountpoint in list
                        })
            return drives
        except Exception as e:
            print(f"[!] Error running diskutil: {e}")
            return []
 
    else:
        print("[!] Unsupported OS for drive detection")
        return []


if __name__ == "__main__":
    drives = list_drives()
    if not drives:
        print("No drives detected.")
    else:
        print("Detected drives:")
        for d in drives:
            print(f"{d['name']} | {d['size']} | {d['type']} | Mounted at: {d['mountpoint']}")
