# wipe_tool/health_check.py
 
def run_smart_test(device_path: str) -> str:
    """
    Stub for disk health check.
    In Ubuntu (demo machine), we can use smartctl from smartmontools.
    On macOS (dev machine), just return 'Unknown/Skipped'.
    """
    import platform
    import subprocess

    if platform.system() == "Linux":
        try:
            result = subprocess.run(
                ["smartctl", "-H", device_path],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except Exception as e:
            return f"SMART check failed: {e}"

    return "SMART check not supported on this OS"
