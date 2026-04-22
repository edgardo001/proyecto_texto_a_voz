import os
import requests
import time
import functools
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

# URLs oficiales para descargar el modelo y las voces si no existen
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

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
        print(f"Error al descargar {filename}: {e}")

@medir_tiempo
def texto_a_voz_kokoro(texto, nombre_archivo="salida_kokoro.wav", voz="ef_dora", speed=1.0, lang="es"):
    """
    Genera audio usando el modelo Kokoro ONNX.
    Para idiomas distintos al inglés (como español 'es'), es NECESARIO tener instalado
    espeak-ng en el sistema y en el PATH.
    """
    if not texto:
        print("No hay texto para generar con Kokoro.")
        return False

    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, "kokoro-v1.0.onnx")
    voices_path = os.path.join(models_dir, "voices-v1.0.bin")

    # Asegurarse de que los archivos existan
    download_file(MODEL_URL, model_path)
    download_file(VOICES_URL, voices_path)

    try:
        if not hasattr(texto_a_voz_kokoro, "onnx"):
            print("Cargando modelo Kokoro ONNX...")
            texto_a_voz_kokoro.onnx = Kokoro(model_path, voices_path)
        
        # Generar audio con el idioma especificado
        print(f"Generando audio en idioma: {lang} con voz: {voz}...")
        samples, sample_rate = texto_a_voz_kokoro.onnx.create(
            texto, 
            voice=voz, 
            speed=speed, 
            lang=lang
        )

        # Guardar el archivo de audio
        sf.write(nombre_archivo, samples, sample_rate)
        print(f"Audio '{nombre_archivo}' generado exitosamente con Kokoro.")
        return True

    except Exception as e:
        print(f"Error al generar audio con Kokoro: {e}")
        if "espeak" in str(e).lower():
            print("\nAVISO: Parece que falta 'espeak-ng'.")
            print("Para usar español en Kokoro localmente necesitas instalar espeak-ng:")
            print("1. Descarga el instalador (.msi) desde: https://github.com/espeak-ng/espeak-ng/releases")
            print("2. Instálalo y asegúrate de añadirlo al PATH de Windows.")
        return False
