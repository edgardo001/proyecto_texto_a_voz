from gtts import gTTS

from modules.utils import medir_tiempo


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
