import os

from google import genai
from google.genai import types
from pydub import AudioSegment

from modules.utils import medir_tiempo


GEMINI_TTS_MODEL = "gemini-3.1-flash-tts-preview"
DEFAULT_VOICE = "Kore"
MAX_CHARS_PER_CHUNK = 2500


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
