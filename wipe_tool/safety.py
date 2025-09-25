# wipe_tool/safety.py
import subprocess
import re
import os

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, text=True).strip()
    except Exception:
        return None

def parent_device_of(partition_device: str):
    """
    Given /dev/sda1 or /dev/nvme0n1p1, return parent device /dev/sda or /dev/nvme0n1.
    Uses lsblk -no PKNAME, falls back to regex trimming.
    """
    if not partition_device:
        return None
    # Try lsblk PKNAME first
    pk = run_cmd(["lsblk", "-no", "PKNAME", partition_device])
    if pk:
        return f"/dev/{pk}"
    # Fallback: strip trailing partition digits/pN style
    # nvme0n1p1 -> nvme0n1 ; sda1 -> sda
    m = re.match(r"(/dev/[^p\d]+)(p?\d+)?$", partition_device)
    if m:
        return m.group(1)
    return partition_device

def mount_source_for_path(path: str):
    """
    returns the block device source (e.g., /dev/sda1) for the given path using findmnt.
    """
    src = run_cmd(["findmnt", "-n", "-o", "SOURCE", "--target", path])
    return src
 
def device_has_mounted_partitions(device_path: str) -> bool:
    """
    Check if any partition of device_path is mounted (returns True if mounted partitions exist).
    """
    # lsblk -nr -o MOUNTPOINT /dev/sda
    out = run_cmd(["lsblk", "-nr", "-o", "MOUNTPOINT", device_path])
    if not out:
        return False
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    return len(lines) > 0

def is_system_or_tool_device(drive_path: str) -> dict:
    """
    Inspect if drive_path matches:
      - system root device
      - device containing this tool (current file)
    Returns dict: {"is_system": bool, "is_tool_device": bool, "root_src":..., "tool_src":..., "root_parent":..., "tool_parent":...}
    """
    root_src = mount_source_for_path("/")
    tool_path = os.path.realpath(__file__)
    tool_src = mount_source_for_path(tool_path)
    root_parent = parent_device_of(root_src) if root_src else None
    tool_parent = parent_device_of(tool_src) if tool_src else None

    return {
        "is_system": (root_parent is not None and drive_path == root_parent),
        "is_tool_device": (tool_parent is not None and drive_path == tool_parent),
        "root_src": root_src,
        "tool_src": tool_src,
        "root_parent": root_parent,
        "tool_parent": tool_parent
    }

def safety_check(drive_path: str, force: bool = False) -> None:
    """
    Raises RuntimeError if drive_path looks like system/root device or contains mounted partitions
    or is the device hosting the running tool. Use --force to override.
    """
    info = is_system_or_tool_device(drive_path)
    reasons = []

    if info["is_system"]:
        reasons.append("Selected device appears to be the system/root device (contains the live system).")

    if info["is_tool_device"]:
        reasons.append("Selected device appears to be the device hosting the running tool (tool files may be on this device).")

    # check for mounted partitions
    try:
        mounted = device_has_mounted_partitions(drive_path)
        if mounted:
            reasons.append("One or more partitions of this device are currently mounted.")
    except Exception:
        # be conservative — if lsblk fails, warn
        reasons.append("Could not determine mount status of device; aborting for safety.")

    if reasons and not force:
        msg = "Unsafe to wipe selected device:\n - " + "\n - ".join(reasons) + "\n\nIf you are absolutely sure, re-run with --force to override."
        raise RuntimeError(msg)

    # If forced, allow but still print info (logger/cli should display)
    return
