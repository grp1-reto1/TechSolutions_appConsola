import os
import json
import requests
from utils import save_config
from downloader import LOCK


def list_files(shared_files: dict):
    with LOCK:
        files = list(shared_files.get('list', []))
    if not files:
        print("No hay archivos.")
        return []
    print("\n--- Ficheros disponibles ---")
    for i, f in enumerate(files, 1):
        print(f"{i}. {os.path.basename(f)}")
    print("c. Cancelar\n")
    return files


def view_file(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print("Error al leer fichero:", e)


def delete_file(path: str, shared_files: dict):
    try:
        os.remove(path)
        with LOCK:
            shared_files["list"] = [p for p in shared_files["list"] if p != path]
        print("Archivo eliminado.")
    except Exception as e:
        print("Error:", e)


def edit_file(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            print("Claves disponibles:", list(data.keys()))
            key = input("Clave a modificar (o 'c' para cancelar): ").strip()
            if key.lower() == 'c':
                print("Edición cancelada.")
                return
            if key not in data:
                print("Clave no encontrada.")
                return
            new = input("Nuevo valor (o 'c' para cancelar): ").strip()
            if new.lower() == 'c':
                print("Edición cancelada.")
                return
            data[key] = new
        else:
            print("Solo editable si es un objeto JSON.")
            return

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Archivo actualizado correctamente.")

    except Exception as e:
        print("Error:", e)


def ping_api(url: str):
    try:
        r = requests.get(url, timeout=5)
        print("Código:", r.status_code)
    except Exception as e:
        print("Ping fallido:", e)


def menu_loop(cfg: dict, shared_files: dict, stop_event):
    while not stop_event.is_set():
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Listar ficheros")
        print("2. Ver fichero")
        print("3. Editar fichero")
        print("4. Eliminar fichero")
        print("5. Cambiar intervalo descarga")
        print("6. Cambiar API URL")
        print("7. Ping API")
        print("8. Salir")

        op = input("Opción: ").strip().lower()
        if op == "1":
            list_files(shared_files)

        elif op == "2":
            files = list_files(shared_files)
            if not files:
                continue
            sel = input("Selecciona número o 'c' para cancelar: ").strip().lower()
            if sel == 'c':
                print("Operación cancelada")
                continue
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(files):
                    view_file(files[idx])
                else:
                    print("Selección fuera de rango")
            except ValueError:
                print("Entrada inválida")

        elif op == "3":
            files = list_files(shared_files)
            if not files:
                continue
            sel = input("Selecciona número o 'c' para cancelar: ").strip().lower()
            if sel == 'c':
                print("Operación cancelada")
                continue
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(files):
                    edit_file(files[idx])
                else:
                    print("Selección fuera de rango")
            except ValueError:
                print("Entrada inválida")

        elif op == "4":
            files = list_files(shared_files)
            if not files:
                continue
            sel = input("Selecciona número o 'c' para cancelar: ").strip().lower()
            if sel == 'c':
                print("Operación cancelada")
                continue
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(files):
                    delete_file(files[idx], shared_files)
                else:
                    print("Selección fuera de rango")
            except ValueError:
                print("Entrada inválida")

        elif op == "5":
            val = input("Nuevo intervalo (minutos) o 'c' para cancelar: ").strip().lower()
            if val == 'c':
                print("Cambio cancelado")
                continue
            try:
                v = int(val)
                if v <= 0:
                    print("Debe ser un entero > 0")
                    continue
                cfg["download_interval_minutes"] = v
                save_config(cfg)
                print(f"Intervalo actualizado a {v} minutos.")
            except ValueError:
                print("Entrada inválida")

        elif op == "6":
            new = input("Nueva URL o 'c' para cancelar: ").strip()
            if new.lower() == 'c':
                print("Cambio cancelado")
                continue
            if new:
                cfg["api_url"] = new
                save_config(cfg)
                print("URL actualizada")

        elif op == "7":
            ping_api(cfg["api_url"])

        elif op == "8":
            stop_event.set()
            print("Saliendo...")

        else:
            print("Opción no válida")
