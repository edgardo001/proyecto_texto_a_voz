import argparse
import os

from modules.fusion_module import fusionar_voz_con_melodias_aleatorias
from modules.gemini_module import texto_a_voz_gemini, DEFAULT_VOICE
from modules.gtts_module import texto_a_voz_gtts
from modules.pyttsx3_module import texto_a_voz_pyttsx3
from modules.kokoro_module import texto_a_voz_kokoro
from modules.qwen_module import texto_a_voz_qwen
from modules.piper_module import texto_a_voz_piper
from modules.vits_module import texto_a_voz_vits


def leer_archivo_txt(ruta_archivo):
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{ruta_archivo}' no fue encontrado.")
        return None
    except Exception as e:
        print(f"Error al leer el archivo '{ruta_archivo}': {e}")
        return None


def motores_desde_arg(motor_arg):
    if motor_arg == "todos":
        return ["gtts", "pyttsx3", "gemini", "kokoro", "qwen", "piper", "vits"]
    return [motor_arg]


def extension_por_motor(motor):
    if motor in ["pyttsx3", "kokoro", "qwen", "piper", "vits"]:
        return "wav"
    return "mp3"

def generar_audio_por_motor(motor, texto, ruta_salida, voz=None):
    if motor == "gtts":
        return texto_a_voz_gtts(texto, nombre_archivo=ruta_salida)
    if motor == "pyttsx3":
        return texto_a_voz_pyttsx3(texto, nombre_archivo=ruta_salida)
    if motor == "gemini":
        return texto_a_voz_gemini(texto, nombre_archivo=ruta_salida, voz=voz or DEFAULT_VOICE)
    if motor == "kokoro":
        if voz:
            return texto_a_voz_kokoro(texto, nombre_archivo=ruta_salida, voz=voz)
        return texto_a_voz_kokoro(texto, nombre_archivo=ruta_salida)
    if motor == "qwen":
        return texto_a_voz_qwen(texto, nombre_archivo=ruta_salida, voz=voz or "Vivian", lang="Spanish")
    if motor == "piper":
        return texto_a_voz_piper(texto, nombre_archivo=ruta_salida)
    if motor == "vits":
        return texto_a_voz_vits(texto, nombre_archivo=ruta_salida)
    print(f"Motor no soportado: {motor}")
    return False

def procesar_archivos(
    motor,
    voz=None,
    carpeta_in="in",
    carpeta_out="out",
    carpeta_melodias="melodias",
    fusionar=True,
):
    os.makedirs(carpeta_out, exist_ok=True)
    archivos_txt = [f for f in os.listdir(carpeta_in) if f.lower().endswith(".txt")]
    if not archivos_txt:
        print("No se encontraron archivos .txt en la carpeta 'in'.")
        return

    motores = motores_desde_arg(motor)
    for nombre_archivo_entrada in archivos_txt:
        ruta_archivo_entrada = os.path.join(carpeta_in, nombre_archivo_entrada)
        print(f"\nLeyendo contenido del archivo: {ruta_archivo_entrada}")
        contenido = leer_archivo_txt(ruta_archivo_entrada)
        if not contenido:
            print(
                f"No se pudo leer el archivo de entrada {nombre_archivo_entrada}. "
                "No se generara audio."
            )
            continue

        nombre_base = os.path.splitext(os.path.basename(nombre_archivo_entrada))[0]
        for motor_actual in motores:
            ext = extension_por_motor(motor_actual)
            salida_voz = os.path.join(carpeta_out, f"{nombre_base}_{motor_actual}.{ext}")
            salida_fusion = os.path.join(
                carpeta_out, f"{nombre_base}_{motor_actual}_melodia.{ext}"
            )

            print(f"\n--- Generando audio con {motor_actual} ---")
            ok_tts = generar_audio_por_motor(motor_actual, contenido, salida_voz, voz=voz)

            if fusionar and ok_tts and os.path.exists(salida_voz):
                print(f"--- Fusionando voz {motor_actual} con melodias ---")
                fusionar_voz_con_melodias_aleatorias(
                    archivo_voz=salida_voz,
                    carpeta_melodias=carpeta_melodias,
                    archivo_salida=salida_fusion,
                )
            elif fusionar:
                print("No se genero el audio de voz; se omite la fusion.")

    print("\nProceso completado. Revisa los archivos generados en la carpeta 'out'.")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Texto a voz con gTTS, pyttsx3 o Gemini TTS + fusion opcional con melodias."
    )
    parser.add_argument(
        "--motor",
        choices=["gtts", "pyttsx3", "gemini", "kokoro", "qwen", "piper", "vits", "todos"],
        default="gtts",
        help="Motor de voz a usar (default: gtts).",
    )
    parser.add_argument(
        "--voz",
        help="Nombre de la voz a usar (ej: ef_dora para Kokoro o Kore para Gemini).",
    )
    parser.add_argument(
        "--sin-fusion",
        action="store_true",
        help="No fusionar voz con melodias.",
    )
    parser.add_argument("--in", dest="carpeta_in", default="in")
    parser.add_argument("--out", dest="carpeta_out", default="out")
    parser.add_argument("--melodias", dest="carpeta_melodias", default="melodias")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    procesar_archivos(
        motor=args.motor,
        voz=args.voz,
        carpeta_in=args.carpeta_in,
        carpeta_out=args.carpeta_out,
        carpeta_melodias=args.carpeta_melodias,
        fusionar=not args.sin_fusion,
    )
