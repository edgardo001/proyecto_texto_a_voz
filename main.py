from gtts import gTTS
import pyttsx3
import os
import time
import functools
import random
from pydub import AudioSegment
from pydub.playback import play

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

# --- Función para repetir la melodía con crossfade ---
def bucle_melodia_crossfade(melodia, duracion_objetivo, crossfade_ms=2000):
    """
    Repite la melodía hasta alcanzar la duración objetivo, aplicando crossfade solo entre repeticiones completas.
    """
    if len(melodia) == 0:
        return AudioSegment.silent(duration=duracion_objetivo)
    repeticiones = max(1, (duracion_objetivo // len(melodia)))
    resultado = melodia
    for _ in range(1, repeticiones):
        resultado = resultado.append(melodia, crossfade=crossfade_ms)
    restante = duracion_objetivo - len(resultado)
    if restante > 0:
        resultado += melodia[:restante]
    return resultado[:duracion_objetivo]

# --- Función para fusionar la voz generada con una melodía en bucle ---
def fusionar_voz_con_melodia(archivo_voz, archivo_melodia, archivo_salida, fade_ms=5000, crossfade_ms=2000):
    """
    Fusiona la voz generada con una melodía en bucle, aplicando fade in/out y crossfade entre repeticiones.
    """
    try:
        voz = AudioSegment.from_file(archivo_voz)
        voz = voz + 6
        melodia = AudioSegment.from_file(archivo_melodia)
        duracion_voz = len(voz)
        # Repetir la melodía con crossfade
        melodia_bucle = bucle_melodia_crossfade(melodia, duracion_voz, crossfade_ms)
        # Bajar el volumen de la melodía a la mitad (~-20 dB)
        melodia_bucle = melodia_bucle - 20
        # Aplicar fade in y fade out
        melodia_bucle = melodia_bucle.fade_in(fade_ms).fade_out(fade_ms)
        # Mezclar la melodía con la voz (voz en primer plano)
        combinado = melodia_bucle.overlay(voz)
        combinado.export(archivo_salida, format="mp3" if archivo_salida.endswith(".mp3") else "wav")
        print(f"Archivo fusionado generado: {archivo_salida}")
    except Exception as e:
        print(f"Error al fusionar audio: {e}")

# --- Función para fusionar la voz con varias melodías aleatorias ---
def fusionar_voz_con_melodias_aleatorias(archivo_voz, carpeta_melodias, archivo_salida, fade_ms=5000, crossfade_ms=2000):
    """
    Fusiona la voz con varias melodías aleatorias, usando cada melodía completa y cambiando a otra diferente cuando se acabe.
    """
    try:
        voz = AudioSegment.from_file(archivo_voz)
        voz = voz + 6
        duracion_voz = len(voz)
        melodias_disponibles = [f for f in os.listdir(carpeta_melodias) if f.endswith(".mp3")]
        if not melodias_disponibles:
            print("No hay melodías disponibles en la carpeta de melodías.")
            return
        melodia_final = AudioSegment.empty()
        usados = set()
        while len(melodia_final) < duracion_voz:
            posibles = [m for m in melodias_disponibles if m not in usados]
            if not posibles:
                usados = set()
                posibles = melodias_disponibles
            melodia_nombre = random.choice(posibles)
            usados.add(melodia_nombre)
            melodia = AudioSegment.from_file(os.path.join(carpeta_melodias, melodia_nombre))
            # Bajar el volumen de la melodía a la mitad (~-20 dB)
            melodia = melodia - 20
            # Solo aplicar crossfade si ambos segmentos son suficientemente largos
            if len(melodia_final) > crossfade_ms and len(melodia) > crossfade_ms:
                melodia_final = melodia_final.append(melodia, crossfade=crossfade_ms)
            else:
                melodia_final += melodia
        melodia_final = melodia_final[:duracion_voz].fade_in(fade_ms).fade_out(fade_ms)
        combinado = melodia_final.overlay(voz)
        combinado.export(archivo_salida, format="mp3" if archivo_salida.endswith(".mp3") else "wav")
        print(f"Archivo fusionado generado: {archivo_salida}")
    except Exception as e:
        print(f"Error al fusionar audio con melodías aleatorias: {e}")

# --- Lógica principal ---
if __name__ == "__main__":
    carpeta_melodias = "melodias"
    carpeta_in = "in"
    carpeta_out = "out"
    # Procesar todos los archivos .txt en la carpeta de entrada
    archivos_txt = [f for f in os.listdir(carpeta_in) if f.endswith('.txt')]
    if not archivos_txt:
        print("No se encontraron archivos .txt en la carpeta 'in'.")
    for nombre_archivo_entrada in archivos_txt:
        ruta_archivo_entrada = os.path.join(carpeta_in, nombre_archivo_entrada)
        print(f"\nLeyendo contenido del archivo: {ruta_archivo_entrada}")
        contenido_del_archivo = leer_archivo_txt(ruta_archivo_entrada)
        if contenido_del_archivo:
            nombre_base = os.path.splitext(os.path.basename(nombre_archivo_entrada))[0]
            nombre_salida_pyttsx3 = os.path.join(carpeta_out, f"{nombre_base}_pyttsx3.wav")
            nombre_salida_gtts = os.path.join(carpeta_out, f"{nombre_base}_gtts.mp3")
            
            # Demora unos pocos segundos para leer, el archivo es mas grande
            #print("\n--- Generando audio con pyttsx3 (sin internet) ---")
            #texto_a_voz_pyttsx3(contenido_del_archivo, nombre_archivo=nombre_salida_pyttsx3)

            # Demora mucho en generar el audio, pero es mas humano, el archivo es mas pequeño
            print("\n--- Generando audio con gTTS (requiere internet) ---")
            texto_a_voz_gtts(contenido_del_archivo, nombre_archivo=nombre_salida_gtts)
            
            # Seleccionar una melodía aleatoria
            melodias_disponibles = [f for f in os.listdir(carpeta_melodias) if f.endswith(".mp3")]
            if melodias_disponibles:
                archivo_melodia = os.path.join(carpeta_melodias, random.choice(melodias_disponibles))
                print(f"Melodía seleccionada: {os.path.basename(archivo_melodia)}")
            else:
                archivo_melodia = None
                print("No se encontró ninguna melodía en la carpeta 'in'.")
            archivo_voz_gtts = nombre_salida_gtts
            archivo_voz_pyttsx3 = nombre_salida_pyttsx3
            archivo_salida_fusion_gtts = os.path.join(carpeta_out, f"{nombre_base}_gtts_melodia.mp3")
            archivo_salida_fusion_pyttsx3 = os.path.join(carpeta_out, f"{nombre_base}_pyttsx3_melodia.wav")
            if archivo_melodia and os.path.exists(archivo_melodia):
                if os.path.exists(archivo_voz_gtts):
                    print("\n--- Fusionando voz gTTS con melodía ---")
                    fusionar_voz_con_melodias_aleatorias(archivo_voz_gtts, carpeta_melodias, archivo_salida_fusion_gtts)
                if os.path.exists(archivo_voz_pyttsx3):
                    print("\n--- Fusionando voz pyttsx3 con melodía ---")
                    fusionar_voz_con_melodias_aleatorias(archivo_voz_pyttsx3, carpeta_melodias, archivo_salida_fusion_pyttsx3)
            else:
                print("No se encontró el archivo de melodía para fusionar.")
        else:
            print(f"No se pudo leer el archivo de entrada {nombre_archivo_entrada}. No se generará audio.")
    print("\nProceso completado. Revisa los archivos de audio generados en la carpeta 'out'.")
