import os
import requests
import tarfile

import soundfile as sf
import sherpa_onnx

from modules.utils import medir_tiempo

# ============================================================
# Configuracion de voz VITS (Sherpa-ONNX)
# Voz default: glados-medium (Femenina, es_ES)
# Voces disponibles:
#   Femeninas:
#   - vits-piper-es_ES-glados-medium    (femenina, calidad media) — default
#   - vits-piper-es_AR-daniela-high     (femenina, argentina, calidad alta)
#   Masculinas:
#   - vits-piper-es_ES-sharvard-medium  (masculina, calidad media)
#   - vits-piper-es_ES-davefx-medium    (masculina, calidad media)
#   - vits-piper-es_ES-miro-high        (masculina, calidad alta)
#   - vits-piper-es_ES-carlfm-x_low     (masculina, calidad baja, rapida)
# ============================================================
MODEL_TARBALL = "vits-piper-es_AR-daniela-high.tar.bz2"
MODEL_FOLDER  = "vits-piper-es_AR-daniela-high"
DOWNLOAD_URL  = f"https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/{MODEL_TARBALL}"


def ensure_model(models_dir):
    folder = os.path.join(models_dir, MODEL_FOLDER)
    onnx_files = [f for f in os.listdir(folder) if f.endswith(".onnx")] if os.path.isdir(folder) else []
    
    if not onnx_files:
        tar_path = os.path.join(models_dir, MODEL_TARBALL)
        print(f"Descargando modelo VITS ({MODEL_TARBALL})...")
        
        response = requests.get(DOWNLOAD_URL, stream=True)
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        downloaded = 0
        
        with open(tar_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\r  Progreso: {pct:.1f}%", end="", flush=True)
        print()
        
        # Verificar que sea un archivo bzip2 valido
        with open(tar_path, "rb") as f:
            magic = f.read(3)
        if magic != b"BZh":
            os.remove(tar_path)
            raise RuntimeError(f"El archivo descargado no es un bzip2 valido. Magic: {magic}")
        
        print(f"Extrayendo {MODEL_TARBALL}...")
        with tarfile.open(tar_path, "r:bz2") as tar:
            tar.extractall(path=models_dir)
        os.remove(tar_path)
        print("Extraccion completada.")

    # Buscar archivos onnx y tokens dentro de la carpeta
    onnx_files = [f for f in os.listdir(folder) if f.endswith(".onnx")]
    token_files = [f for f in os.listdir(folder) if f == "tokens.txt"]
    
    if not onnx_files:
        raise FileNotFoundError(f"No se encontro archivo .onnx en {folder}")
    if not token_files:
        raise FileNotFoundError(f"No se encontro tokens.txt en {folder}")
    
    return os.path.join(folder, onnx_files[0]), os.path.join(folder, "tokens.txt"), folder

@medir_tiempo
def texto_a_voz_vits(texto, nombre_archivo="salida_vits.wav"):
    """
    Genera audio usando VITS via sherpa-onnx.
    Voz por defecto: glados-medium (femenina, es_ES).
    """
    if not texto:
        print("No hay texto para generar con VITS.")
        return False

    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)

    try:
        model_path, tokens_path, folder = ensure_model(models_dir)

        if not hasattr(texto_a_voz_vits, "tts"):
            print("Cargando motor VITS (sherpa-onnx)...")
            vits_config = sherpa_onnx.OfflineTtsVitsModelConfig(
                model=model_path,
                tokens=tokens_path,
                data_dir=os.path.join(folder, "espeak-ng-data"),
                noise_scale=0.667,
                noise_scale_w=0.8,
                length_scale=1.0,
            )
            tts_model_config = sherpa_onnx.OfflineTtsModelConfig(
                vits=vits_config,
                num_threads=4,
                debug=False,
                provider="cpu",
            )
            tts_config = sherpa_onnx.OfflineTtsConfig(model=tts_model_config)
            texto_a_voz_vits.tts = sherpa_onnx.OfflineTts(tts_config)

        print("Generando audio con VITS...")
        audio = texto_a_voz_vits.tts.generate(texto)

        if audio.samples is not None and len(audio.samples) > 0:
            sf.write(nombre_archivo, audio.samples, audio.sample_rate)
            print(f"Audio '{nombre_archivo}' generado exitosamente con VITS.")
            return True
        else:
            print("VITS no genero audio.")
            return False

    except Exception as e:
        print(f"Error al generar audio con VITS: {e}")
        import traceback
        traceback.print_exc()
        return False
