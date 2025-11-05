import os
import json
from datetime import datetime
from pathlib import Path

CONFIG_PATH = "config.json"

def load_config() -> dict:
    """Carga el archivo config.json o crea uno por defecto."""
    default = {
        "api_url": "http://127.0.0.1:5000/api/contactos",
        "download_interval_minutes": 5,
        "data_folder": "./descargas",
        "last_ids_file": "./descargas/last_ids.json"
    }
    try:
        if not os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=4)
            return default
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in default.items():
            if k not in data:
                data[k] = v
        return data
    except Exception as e:
        print("Error leyendo config.json:", e)
        return default

def save_config(cfg: dict):
    """Guarda el archivo de configuración."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        print("Configuración guardada.")
    except Exception as e:
        print("Error guardando config:", e)

def ensure_data_folder(path: str):
    """Crea la carpeta de datos si no existe."""
    Path(path).mkdir(parents=True, exist_ok=True)

def timestamp_str() -> str:
    """Devuelve un timestamp legible para nombres de archivo."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
