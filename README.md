# Proyecto Texto a Voz (TTS) Profesional

Este proyecto es una solución integral para convertir texto en audio utilizando múltiples motores, desde servicios en la nube hasta modelos de inteligencia artificial locales de última generación.

## Características Principales
- **Motores Híbridos**: Soporte para Google TTS, Gemini AI, Kokoro, Qwen3-TTS, Piper y VITS.
- **IA Local de Alto Rendimiento**: Optimizado para procesadores Intel Core Ultra (Meteor Lake).
- **Formatos ONNX**: Máxima eficiencia con Kokoro, Piper y VITS (vía sherpa-onnx).
- **Fusión de Audio**: Mezcla automática de la voz generada con melodías de fondo.

---

## Motores Disponibles

1.  **`kokoro` (Equilibrado)**:
    *   Genera audio de alta fidelidad (WAV) totalmente en local.
    *   Optimizado mediante ONNX para CPU/NPU.
2.  **`piper` (Eficiencia ONNX)**:
    *   Motor ultrarrápido optimizado para sistemas embebidos y escritorio.
    *   Voz por defecto: `Carl (es_ES-carl-medium)`.
3.  **`vits` (sherpa-onnx)**:
    *   Usa la arquitectura VITS para una entonación natural y rápida.
    *   Voz por defecto: `Pau (es_ES-pau-medium)`.
4.  **`qwen` (Máxima Calidad Local)**:
    *   Usa la familia **Qwen3-TTS** de Alibaba (0.6B o 1.7B).
    *   Procesa el texto por fragmentos para evitar saturación de memoria.
5.  **`gemini` (Nube - Google AI Studio)**:
    *   Usa el modelo `gemini-3.1-flash-tts-preview`.
6.  **`gtts`**: Genera MP3 usando Google Text-to-Speech (requiere internet).
7.  **`todos`**: Ejecuta todos los motores anteriores en secuencia.

---

## Benchmark de Rendimiento

Tiempos medidos con un archivo de **201 palabras** en un Intel Core Ultra (Windows 11). Los tiempos incluyen solo la generación de voz, sin fusión con melodías.

| Motor | Primera ejecución (con descarga) | Tiempo (con cache) | Velocidad relativa |
|-------|----------------------------------|-------------------|--------------------|
| `pyttsx3` | 1.90 s | 0.78 s | Instantáneo |
| `gtts` | 4.54 s | 5.07 s | Muy rápido (requiere internet) |
| `piper` | 11.19 s | 5.32 s | Muy rápido |
| `vits` | 30.04 s | 12.79 s | Rápido |
| `kokoro` | 36.80 s | 20.56 s | Moderado |
| `gemini` | 51.54 s | 47.03 s | Lento (requiere internet + API key) |
| `qwen` | 9 min 23 s | 8 min 32 s | Muy lento (máxima calidad local) |

> **Nota:** La primera ejecución de `piper`, `vits`, `kokoro` y `qwen` incluye la descarga de modelos, que se almacenan en `models/` para ejecuciones posteriores. `gtts`, `pyttsx3` y `gemini` no descargan modelos locales. Los tiempos varían según el hardware y escalan proporcionalmente con la cantidad de palabras.

---

## Configuración y Requisitos

### Requisitos Técnicos
- **Python 3.10+** (Recomendado 3.12 o superior).
- **FFmpeg/FFprobe**: Necesario para el procesamiento de audio.
- **espeak-ng**: Necesario para el soporte de español en Kokoro y Piper.

### Estructura de Carpetas
- `in/`: Archivos `.txt` de entrada.
- `out/`: Audios generados.
- `models/`: Almacenamiento local de los modelos de IA.
- `melodias/`: Pistas `.mp3` para la música de fondo.

---

## Cómo usar el proyecto

```powershell
# Ejecutar con Piper (Voz Masculina Española)
.\start.bat piper

# Ejecutar con VITS (Voz Española)
.\start.bat vits

### Motor Piper (ONNX)
- **Voz activa**: `mls_9972-low` (**Femenina**, Español España) — *default*
- **Para voz masculina**: edita `MODEL_VOICE` en `piper_module.py`:
  - `es_ES-sharvard-medium` (masculina, calidad media)
  - `es_ES-davefx-medium` (masculina, calidad media)
- **Catálogo completo**: [Piper Voices (Hugging Face)](https://huggingface.co/rhasspy/piper-voices/tree/main/es/es_ES)

### Motor VITS (sherpa-onnx)
- **Voz activa**: `glados-medium` (**Femenina**, Español España) — *default*
- **Voces femeninas disponibles**:
  - `vits-piper-es_ES-glados-medium` (femenina, es_ES) — *default*
  - `vits-piper-es_AR-daniela-high` (femenina, es_AR, calidad alta)
- **Voces masculinas disponibles**:
  - `vits-piper-es_ES-sharvard-medium` (masculina, calidad media)
  - `vits-piper-es_ES-davefx-medium` (masculina, calidad media)
  - `vits-piper-es_ES-miro-high` (masculina, calidad alta)
  - `vits-piper-es_ES-carlfm-x_low` (masculina, calidad baja, rápida)
- **Para cambiar voz**: edita `MODEL_TARBALL` y `MODEL_FOLDER` en `vits_module.py`
- **Modelos Sherpa**: [k2-fsa/sherpa-onnx (GitHub)](https://github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models)

### Motor Qwen (Transformers)
- **Modelos**: Se puede alternar entre el modelo `0.6B` (Rápido) y `1.7B` (Alta fidelidad) editando la variable `MODEL_ID` al inicio de `qwen_module.py`.
- **Documentación**: [Qwen3-TTS-12Hz-1.7B-CustomVoice](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice)
- **Voces**: `Vivian` (Femenina), `Ryan` (Masculina).

# Ejecutar con Qwen (IA Avanzada)
.\start.bat qwen Vivian
```
