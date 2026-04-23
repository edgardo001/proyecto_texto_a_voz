import functools
import os
import time

import requests


def medir_tiempo(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        print(f"Iniciando {func.__name__}...")
        resultado = func(*args, **kwargs)
        fin = time.time()
        print(f"{func.__name__} completado en {fin - inicio:.2f} segundos")
        return resultado
    return wrapper


def download_file(url, filename):
    if os.path.exists(filename):
        return
    print(f"Descargando {filename} desde {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Descarga de {filename} completada.")
    except Exception as e:
        if os.path.exists(filename):
            os.remove(filename)
        print(f"Error al descargar {filename}: {e}")
        raise e
