import os
import requests
import time
import functools
import wave
import io
from piper.voice import PiperVoice

# ============================================================
# Configuracion de voz Piper (ONNX)
# Voz femenina (default): mls_9972-low
# Para voz masculina: cambia MODEL_VOICE a una de estas:
#   - es_ES-sharvard-medium  (masculina, calidad media)
#   - es_ES-davefx-medium    (masculina, calidad media)
# ============================================================
MODEL_VOICE = "es_ES-mls_9972-low"
MODEL_URL   = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/mls_9972/low/{MODEL_VOICE}.onnx"
CONFIG_URL  = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/mls_9972/low/{MODEL_VOICE}.onnx.json"

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

@medir_tiempo
def texto_a_voz_piper(texto, nombre_archivo="salida_piper.wav"):
    """
    Genera audio usando Piper TTS (ONNX).
    """
    if not texto:
        print("No hay texto para generar con Piper.")
        return False

    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    model_path  = os.path.join(models_dir, f"{MODEL_VOICE}.onnx")
    config_path = os.path.join(models_dir, f"{MODEL_VOICE}.onnx.json")

    try:
        # Asegurarse de que los archivos existan
        download_file(MODEL_URL, model_path)
        download_file(CONFIG_URL, config_path)

        if not hasattr(texto_a_voz_piper, "voice"):
            print("Cargando modelo Piper ONNX...")
            texto_a_voz_piper.voice = PiperVoice.load(model_path, config_path)
        
        # Generar audio
        print(f"Generando audio con Piper...")
        
        chunks_recibidos = 0
        with wave.open(nombre_archivo, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(texto_a_voz_piper.voice.config.sample_rate)
            
            # synthesize() devuelve objetos AudioChunk; audio_int16_bytes contiene los bytes PCM
            for chunk in texto_a_voz_piper.voice.synthesize(texto):
                audio_data = chunk.audio_int16_bytes if hasattr(chunk, "audio_int16_bytes") else bytes(chunk.audio_int16_array)
                wav_file.writeframes(audio_data)
                chunks_recibidos += 1
        
        if chunks_recibidos > 0:
            print(f"Audio '{nombre_archivo}' generado exitosamente con Piper ({chunks_recibidos} fragmentos).")
            return True
        else:
            print("ADVERTENCIA: Piper no devolvio ningun fragmento de audio.")
            print("IMPORTANTE: Asegúrate de tener 'espeak-ng' instalado en el sistema y en el PATH.")
            print("Puedes descargarlo de: https://github.com/espeak-ng/espeak-ng/releases")
            return False

    except Exception as e:
        print(f"Error critico en Piper: {e}")
        import traceback
        traceback.print_exc()
        return False
