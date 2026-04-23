import os
import sys

# Forzar a Hugging Face a usar nuestra carpeta de models ANTES de cualquier importacion de transformers
models_dir = os.path.abspath("models")
os.makedirs(models_dir, exist_ok=True)
os.environ["HF_HOME"] = models_dir
os.environ["HUGGINGFACE_HUB_CACHE"] = models_dir

import torch
import soundfile as sf
import traceback
import re
import numpy as np

from modules.utils import medir_tiempo

# Configuración del modelo Qwen (descomenta el que quieras usar)
# MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"  # Alta fidelidad (pesado)
MODEL_ID = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"    # Rápido (ligero)

# Intentar importar qwen-tts
try:
    from qwen_tts import Qwen3TTSModel
    HAS_QWEN = True
except ImportError:
    HAS_QWEN = False


def dividir_en_oraciones(texto):
    """
    Divide un texto largo en oraciones individuales para un procesamiento mas fluido.
    """
    # Expresion regular para dividir por puntos, signos de exclamacion o interrogacion
    oraciones = re.split(r'(?<=[.!?])\s+', texto)
    return [o.strip() for o in oraciones if o.strip()]

@medir_tiempo
def texto_a_voz_qwen(texto, nombre_archivo="salida_qwen.wav", voz="Vivian", lang="Spanish"):
    """
    Genera audio usando el modelo Qwen3-TTS, procesando el texto por oraciones
    para evitar bloqueos y optimizar la memoria en CPU.
    """
    if not texto:
        print("No hay texto para generar con Qwen.")
        return False

    if not HAS_QWEN:
        print("ERROR: El paquete 'qwen-tts' no esta instalado.")
        return False

    try:
        # Cargamos el modelo
        if not hasattr(texto_a_voz_qwen, "model"):
            print(f"Cargando modelo Qwen3-TTS ({MODEL_ID}) en CPU...")
            
            # Forzar CPU para maxima estabilidad en este hardware
            device = "cpu"
            dtype = torch.float32
            
            # Cargar modelo seleccionado
            texto_a_voz_qwen.model = Qwen3TTSModel.from_pretrained(
                MODEL_ID,
                device_map=device,
                dtype=dtype,
                cache_dir=models_dir,
                trust_remote_code=True
            )

        print(f"Dividiendo texto en fragmentos para procesamiento optimizado...")
        oraciones = dividir_en_oraciones(texto)
        print(f"Total de fragmentos a procesar: {len(oraciones)}")

        todos_los_audios = []
        sample_rate = 24000 # Default SR para Qwen3-TTS

        with torch.no_grad():
            for i, oracion in enumerate(oraciones):
                print(f"Procesando fragmento {i+1}/{len(oraciones)}: {oracion[:50]}...")
                
                # Generar audio para la oracion actual
                wavs, sr = texto_a_voz_qwen.model.generate_custom_voice(
                    text=oracion,
                    language=lang,
                    speaker=voz
                )
                
                if wavs is not None and len(wavs) > 0:
                    todos_los_audios.append(wavs[0])
                    sample_rate = sr
                else:
                    print(f"Advertencia: No se genero audio para el fragmento {i+1}")

        if todos_los_audios:
            print("Concatenando fragmentos de audio...")
            # Unir todos los fragmentos
            audio_final = np.concatenate(todos_los_audios)
            
            # Guardar el audio final
            sf.write(nombre_archivo, audio_final, sample_rate)
            print(f"Audio '{nombre_archivo}' generado exitosamente con Qwen3-TTS ({len(oraciones)} fragmentos).")
            return True
        else:
            print("Error: No se pudo generar ningun fragmento de audio.")
            return False

    except Exception as e:
        print(f"Error critico al generar audio con Qwen: {e}")
        traceback.print_exc()
        return False
