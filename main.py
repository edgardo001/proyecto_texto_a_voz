from gtts import gTTS
import pyttsx3
import os
import time
import functools

# --- Decorador para medir tiempo de ejecución ---
def medir_tiempo(func):
    """
    Decorador que mide el tiempo de ejecución de una función.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        print(f"⏱️  Iniciando {func.__name__}...")
        
        resultado = func(*args, **kwargs)
        
        fin = time.time()
        tiempo_total = fin - inicio
        print(f"✅ {func.__name__} completado en {tiempo_total:.2f} segundos")
        
        return resultado
    return wrapper

# --- Función para leer el archivo de texto ---
def leer_archivo_txt(ruta_archivo):
    """
    Lee el contenido de un archivo de texto y lo devuelve como una cadena.
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            contenido = file.read()
        return contenido
    except FileNotFoundError:
        print(f"Error: El archivo '{ruta_archivo}' no fue encontrado.")
        return None
    except Exception as e:
        print(f"Error al leer el archivo '{ruta_archivo}': {e}")
        return None

# --- Función para texto a voz con gTTS ---
@medir_tiempo
def texto_a_voz_gtts(texto, idioma='es', nombre_archivo="salida_gtts.mp3"):
    """
    Convierte texto a voz usando gTTS y guarda el audio en un archivo MP3.
    """
    if not texto:
        print("No hay texto para generar con gTTS.")
        return

    try:
        tts = gTTS(text=texto, lang=idioma, slow=False)
        tts.save(nombre_archivo)
        print(f"Audio '{nombre_archivo}' generado exitosamente con gTTS.")
    except Exception as e:
        print(f"Error al generar audio con gTTS: {e}")

# --- Función para texto a voz con pyttsx3 ---
@medir_tiempo
def texto_a_voz_pyttsx3(texto, nombre_archivo="salida_pyttsx3.wav"): # pyttsx3 prefiere WAV
    """
    Convierte texto a voz usando pyttsx3. Puede reproducirlo directamente
    o intentar guardarlo en un archivo (usualmente WAV).
    """
    if not texto:
        print("No hay texto para generar con pyttsx3.")
        return

    try:
        engine = pyttsx3.init()

        # Opcional: Configurar la velocidad y el volumen
        engine.setProperty('rate', 200)
        engine.setProperty('volume', 0.9)

        # Para que hable directamente
        #print(f"Reproduciendo con pyttsx3...")
        #engine.say(texto)
        #engine.runAndWait()

        # Para guardar el audio en un archivo (generalmente WAV, no MP3 directo)
        engine.save_to_file(texto, nombre_archivo)
        engine.runAndWait()
        print(f"Audio '{nombre_archivo}' guardado exitosamente con pyttsx3.")

    except Exception as e:
        print(f"Error al generar audio con pyttsx3: {e}")

# --- Lógica principal ---
if __name__ == "__main__":
    nombre_archivo_entrada = "entrada.txt"
    print(f"Leyendo contenido del archivo: {nombre_archivo_entrada}")
    contenido_del_archivo = leer_archivo_txt(nombre_archivo_entrada)
    if contenido_del_archivo:
        # Extraer el nombre base del archivo (sin extensión)
        nombre_base = os.path.splitext(nombre_archivo_entrada)[0]
        
        # Generar nombres de archivo de salida
        nombre_salida_pyttsx3 = f"{nombre_base}_pyttsx3.wav"
        nombre_salida_gtts = f"{nombre_base}_gtts.mp3"
        
        # Demora unos pocos segundos para leer, el archivo es mas grande
        print("\n--- Generando audio con pyttsx3 (sin internet) ---")
        texto_a_voz_pyttsx3(contenido_del_archivo, nombre_archivo=nombre_salida_pyttsx3)

        # Demora mucho en generar el audio, pero es mas humano, el archivo es mas pequeño
        print("\n--- Generando audio con gTTS (requiere internet) ---")
        texto_a_voz_gtts(contenido_del_archivo, nombre_archivo=nombre_salida_gtts)
    else:
        print("No se pudo leer el archivo de entrada. No se generará audio.")

    print("\nProceso completado. Revisa los archivos de audio generados en tu carpeta.")