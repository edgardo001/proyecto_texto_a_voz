import os
import random

from pydub import AudioSegment


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
