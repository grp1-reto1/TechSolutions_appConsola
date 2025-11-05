import threading
from utils import load_config, ensure_data_folder
from downloader import Downloader
from monitor import Monitor
from menu import menu_loop

def main():
    """Punto de entrada de la aplicación de consola."""
    cfg = load_config()
    ensure_data_folder(cfg["data_folder"])
    shared_files = {"list": []}
    stop_event = threading.Event()

    downloader = Downloader(cfg, stop_event)
    monitor = Monitor(cfg, shared_files, stop_event)

    downloader.start()
    monitor.start()

    try:
        menu_loop(cfg, shared_files, stop_event)
    finally:
        stop_event.set()
        downloader.join(timeout=5)
        monitor.join(timeout=5)
        print("Aplicación finalizada.")

if __name__ == "__main__":
    main()
