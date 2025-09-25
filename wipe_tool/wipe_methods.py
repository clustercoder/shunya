# wipe_tool/wipe_methods.py

import subprocess
import platform
import time
from wipe_tool.wipe_logger import WipeLogger


def run_wipe(drive_path: str, method: str, dry_run: bool = False, safe_demo: bool = False, force: bool = False) -> str:
    """
    Run wipe with logging. Returns path to wipe log.
    """ 
    logger = WipeLogger(drive_path, method)
    logger.start()

    if method == "standard":
        zero_fill(drive_path, logger, dry_run)
    elif method == "quantum":  # our "random" method
        random_fill(drive_path, logger, dry_run)
    elif method == "eco":
        eco_quick_erase(drive_path, logger, dry_run)
    else:
        logger.log_progress(f"[!] Unknown wipe method: {method}")

    logger.end()
    return logger.get_log_path()


def zero_fill(drive_path: str, logger: WipeLogger, dry_run: bool = False):
    logger.log_progress("Starting zero-fill wipe...")
    if platform.system() == "Linux":
        cmd = ["dd", "if=/dev/zero", f"of={drive_path}", "bs=1M", "status=progress", "conv=fdatasync"]
        if dry_run:
            logger.log_progress(f"[DRY RUN] Would execute: {' '.join(cmd)}")
            return
        try:
            subprocess.run(cmd, check=True)
            logger.log_progress("Zero-fill completed successfully.")
        except Exception as e:
            logger.log_progress(f"[!] Error: {e}")
    else:
        simulate(logger, "zero-fill", dry_run)


def random_fill(drive_path: str, logger: WipeLogger, dry_run: bool = False):
    logger.log_progress("Starting random-fill wipe...")
    if platform.system() == "Linux":
        cmd = ["dd", "if=/dev/urandom", f"of={drive_path}", "bs=1M", "status=progress", "conv=fdatasync"]
        if dry_run:
            logger.log_progress(f"[DRY RUN] Would execute: {' '.join(cmd)}")
            return
        try:
            subprocess.run(cmd, check=True)
            logger.log_progress("Random-fill completed successfully.")
        except Exception as e:
            logger.log_progress(f"[!] Error: {e}")
    else:
        simulate(logger, "random-fill", dry_run)


def eco_quick_erase(drive_path: str, logger: WipeLogger, dry_run: bool = False):
    logger.log_progress("Starting eco (quick) erase...")
    if platform.system() == "Linux":
        cmd = ["blkdiscard", drive_path]
        if dry_run:
            logger.log_progress(f"[DRY RUN] Would execute: {' '.join(cmd)}")
            return
        try:
            subprocess.run(cmd, check=True)
            logger.log_progress("Eco erase (blkdiscard) completed.")
        except Exception as e:
            logger.log_progress(f"[!] Error: {e}")
    else:
        simulate(logger, "eco-erase", dry_run)


def simulate(logger: WipeLogger, label: str, dry_run: bool):
    if dry_run:
        logger.log_progress(f"[DRY RUN] Would {label} wipe (simulation mode)")
    else:
        for pct in range(0, 101, 25):
            time.sleep(0.5)
            logger.log_progress(f"Simulated {label}: {pct}% complete")
