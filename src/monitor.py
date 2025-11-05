import os
import time
import threading
from utils import ensure_data_folder

LOCK = threading.Lock()

class Monitor(threading.Thread):
    """Hilo que detecta nuevos ficheros en la carpeta de descargas."""

    def __init__(self, cfg: dict, shared_files: dict, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.cfg = cfg
        self.shared_files = shared_files
        self.stop_event = stop_event
        self.last_seen = set()

    def run(self):
        ensure_data_folder(self.cfg["data_folder"])
        while not self.stop_event.is_set():
            try:
                folder = self.cfg["data_folder"]
                files = [os.path.join(folder, f)
                         for f in os.listdir(folder) if f.endswith(".json")]
                files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
                current = set(files)
                added = current - self.last_seen
                if added:
                    print("[Monitor] Nuevos archivos detectados:")
                    for f in added:
                        print("  -", os.path.basename(f))
                self.last_seen = current
                with LOCK:
                    self.shared_files["list"] = list(files)
            except Exception as e:
                print("[Monitor] Error:", e)
            for _ in range(10):
                if self.stop_event.is_set():
                    break
                time.sleep(1)
