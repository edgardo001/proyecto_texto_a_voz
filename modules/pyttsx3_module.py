import pyttsx3

from modules.utils import medir_tiempo


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
