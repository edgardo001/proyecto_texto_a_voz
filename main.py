import argparse
import functools
import os
import random
import time

from gtts import gTTS
import pyttsx3
from google import genai
from google.genai import types
from pydub import AudioSegment


GEMINI_TTS_MODEL = "gemini-3.1-flash-tts-preview"
DEFAULT_VOICE = "Kore"
MAX_CHARS_PER_CHUNK = 2500


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


@medir_tiempo
def texto_a_voz_gtts(texto, idioma="es", nombre_archivo="salida_gtts.mp3"):
    if not texto:
        print("No hay texto para generar con gTTS.")
        return False
    try:
        tts = gTTS(text=texto, lang=idioma, slow=False)
        tts.save(nombre_archivo)
        print(f"Audio '{nombre_archivo}' generado exitosamente con gTTS.")
        return True
    except Exception as e:
        print(f"Error al generar audio con gTTS: {e}")
        return False


@medir_tiempo
def texto_a_voz_pyttsx3(texto, nombre_archivo="salida_pyttsx3.wav"):
    if not texto:
        print("No hay texto para generar con pyttsx3.")
        return False
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 200)
        engine.setProperty("volume", 0.9)
        engine.save_to_file(texto, nombre_archivo)
        engine.runAndWait()
        print(f"Audio '{nombre_archivo}' guardado exitosamente con pyttsx3.")
        return True
    except Exception as e:
        print(f"Error al generar audio con pyttsx3: {e}")
        return False


def dividir_texto(texto, max_chars=MAX_CHARS_PER_CHUNK):
    texto = (texto or "").strip()
    if not texto:
        return []

    partes = []
    actual = []
    actual_len = 0
    for palabra in texto.split():
        extra = len(palabra) + (1 if actual else 0)
        if actual_len + extra > max_chars:
            partes.append(" ".join(actual))
            actual = [palabra]
            actual_len = len(palabra)
        else:
            actual.append(palabra)
            actual_len += extra

    if actual:
        partes.append(" ".join(actual))
    return partes


def _pcm_a_audio_segment(pcm_bytes):
    return AudioSegment(
        data=pcm_bytes,
        sample_width=2,
        frame_rate=24000,
        channels=1,
    )


@medir_tiempo
def texto_a_voz_gemini(
    texto,
    nombre_archivo="salida_gemini_tts.mp3",
    modelo=GEMINI_TTS_MODEL,
    voz=DEFAULT_VOICE,
):
    if not texto:
        print("No hay texto para generar con Gemini TTS.")
        return False

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Falta configurar la variable de entorno GEMINI_API_KEY.")
        return False

    try:
        client = genai.Client(api_key=api_key)
        segmentos = dividir_texto(texto)
        if not segmentos:
            print("El texto no contiene contenido util para sintetizar.")
            return False

        audio_final = AudioSegment.empty()
        for i, segmento in enumerate(segmentos, start=1):
            print(f"Generando segmento {i}/{len(segmentos)} con Gemini...")
            response = client.models.generate_content(
                model=modelo,
                contents=segmento,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voz
                            )
                        )
                    ),
                ),
            )
            pcm = response.candidates[0].content.parts[0].inline_data.data
            audio_final += _pcm_a_audio_segment(pcm)

        formato = "mp3" if nombre_archivo.lower().endswith(".mp3") else "wav"
        audio_final.export(nombre_archivo, format=formato)
        print(f"Audio '{nombre_archivo}' generado exitosamente con Gemini TTS.")
        return True
    except Exception as e:
        print(f"Error al generar audio con Gemini TTS: {e}")
        return False


def fusionar_voz_con_melodias_aleatorias(
    archivo_voz,
    carpeta_melodias,
    archivo_salida,
    fade_ms=5000,
    crossfade_ms=2000,
):
    try:
        voz = AudioSegment.from_file(archivo_voz) + 6
        duracion_voz = len(voz)
        melodias_disponibles = [
            f for f in os.listdir(carpeta_melodias) if f.lower().endswith(".mp3")
        ]
        if not melodias_disponibles:
            print("No hay melodias disponibles en la carpeta de melodias.")
            return False

        melodia_final = AudioSegment.empty()
        usados = set()
        while len(melodia_final) < duracion_voz:
            posibles = [m for m in melodias_disponibles if m not in usados]
            if not posibles:
                usados = set()
                posibles = melodias_disponibles

            melodia_nombre = random.choice(posibles)
            usados.add(melodia_nombre)
            melodia = AudioSegment.from_file(
                os.path.join(carpeta_melodias, melodia_nombre)
            )
            melodia = melodia - 20

            if len(melodia_final) > crossfade_ms and len(melodia) > crossfade_ms:
                melodia_final = melodia_final.append(melodia, crossfade=crossfade_ms)
            else:
                melodia_final += melodia

        melodia_final = melodia_final[:duracion_voz].fade_in(fade_ms).fade_out(fade_ms)
        combinado = melodia_final.overlay(voz)
        formato = "mp3" if archivo_salida.lower().endswith(".mp3") else "wav"
        combinado.export(archivo_salida, format=formato)
        print(f"Archivo fusionado generado: {archivo_salida}")
        return True
    except Exception as e:
        print(f"Error al fusionar audio con melodias aleatorias: {e}")
        return False


def motores_desde_arg(motor_arg):
    if motor_arg == "todos":
        return ["gtts", "pyttsx3", "gemini"]
    return [motor_arg]


def extension_por_motor(motor):
    if motor == "pyttsx3":
        return "wav"
    return "mp3"


def generar_audio_por_motor(motor, texto, ruta_salida):
    if motor == "gtts":
        return texto_a_voz_gtts(texto, nombre_archivo=ruta_salida)
    if motor == "pyttsx3":
        return texto_a_voz_pyttsx3(texto, nombre_archivo=ruta_salida)
    if motor == "gemini":
        return texto_a_voz_gemini(texto, nombre_archivo=ruta_salida)
    print(f"Motor no soportado: {motor}")
    return False


def procesar_archivos(
    motor,
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
            ok_tts = generar_audio_por_motor(motor_actual, contenido, salida_voz)

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
        choices=["gtts", "pyttsx3", "gemini", "todos"],
        default="gtts",
        help="Motor de voz a usar (default: gtts).",
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
        carpeta_in=args.carpeta_in,
        carpeta_out=args.carpeta_out,
        carpeta_melodias=args.carpeta_melodias,
        fusionar=not args.sin_fusion,
    )
