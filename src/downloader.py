import os
import json
import time
import threading
import requests
from typing import List, Dict
from utils import ensure_data_folder, timestamp_str
from pathlib import Path

LOCK = threading.Lock()

class Downloader(threading.Thread):
    """Hilo encargado de descargar datos nuevos desde la API."""

    def __init__(self, cfg: dict, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.cfg = cfg
        self.stop_event = stop_event
        self.known_ids = self._read_last_ids(cfg["last_ids_file"])

    def _read_last_ids(self, path: str) -> set:
        try:
            if not os.path.exists(path):
                return set()
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return set(data if isinstance(data, list) else [])
        except Exception:
            return set()

    def _write_last_ids(self, path: str):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(list(self.known_ids), f, indent=2)
        except Exception as e:
            print("Error escribiendo last_ids:", e)

    def _detect_new(self, fetched: List[Dict]) -> List[Dict]:
        new = []
        for item in fetched:
            rid = str(item.get("id") or item.get("Id") or item.get("ID") or "")
            if rid and rid not in self.known_ids:
                new.append(item)
                self.known_ids.add(rid)
        return new

    def _save_new_records(self, records: List[Dict]):
        folder = self.cfg["data_folder"]
        fname = f"contactos_{timestamp_str()}.json"
        fpath = os.path.join(folder, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        self._write_last_ids(self.cfg["last_ids_file"])
        print(f"[Downloader] {len(records)} registros nuevos guardados en {fpath}")

    def run(self):
        ensure_data_folder(self.cfg["data_folder"])
        while not self.stop_event.is_set():
            try:
                api_url = self.cfg["api_url"]
                print(f"[Downloader] Llamando a API: {api_url}")
                resp = requests.get(api_url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                if not isinstance(data, list):
                    data = data.get("data") or data.get("results") or [data]
                new = self._detect_new(data)
                if new:
                    self._save_new_records(new)
                else:
                    print("[Downloader] No hay registros nuevos.")
            except Exception as e:
                print("[Downloader] Error:", e)

            for _ in range(int(self.cfg["download_interval_minutes"]) * 60):
                if self.stop_event.is_set():
                    break
                time.sleep(1)
