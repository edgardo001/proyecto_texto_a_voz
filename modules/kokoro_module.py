import os

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

from modules.utils import medir_tiempo, download_file

# URLs oficiales para descargar el modelo y las voces si no existen
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

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
