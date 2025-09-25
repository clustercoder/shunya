# wipe_tool/wipe_logger.py

import os
import json
import time
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "../data/logs")
os.makedirs(LOG_DIR, exist_ok=True)


class WipeLogger:
    def __init__(self, drive_path: str, method: str):
        self.drive_path = drive_path
        self.method = method
        self.start_time = None
        self.end_time = None
        self.nonce = int(time.time())
        self.log_file = os.path.join(LOG_DIR, f"wipe_log_{self.nonce}.json")
        self.progress = []

    def start(self):
        self.start_time = datetime.utcnow().isoformat()
        self._write_log("Wipe started")

    def log_progress(self, message: str):
        print(message)
        self.progress.append({"time": datetime.utcnow().isoformat(), "msg": message})
        self._write_log(message)

    def end(self):
        self.end_time = datetime.utcnow().isoformat()
        self._write_log("Wipe completed")

    def _write_log(self, last_msg: str):
        log_data = {
            "drive_path": self.drive_path,
            "method": self.method,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "nonce": self.nonce,
            "progress": self.progress,
            "last_message": last_msg,
        }
        with open(self.log_file, "w") as f:
            json.dump(log_data, f, indent=4)

    def get_log_path(self):
        return self.log_file
  