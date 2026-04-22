# Proyecto Texto a Voz

Este proyecto convierte texto en audio y opcionalmente lo fusiona con melodias de fondo.

## Script principal

El unico script de ejecucion es:

- `main.py`

## Motores disponibles

- `gtts`: genera MP3 con Google Text-to-Speech.
- `pyttsx3`: genera WAV con el motor local del sistema.
- `gemini`: genera MP3 con Gemini TTS (Google AI Studio).
- `todos`: ejecuta `gtts`, `pyttsx3` y `gemini` en secuencia.

## Requisitos

- Python 3.x
- Dependencias en `requirements.txt`
- FFmpeg/FFprobe para procesamiento de audio con `pydub`

Instalacion:

```bash
pip install -r requirements.txt
```

## Estructura de carpetas

- `in/`: archivos `.txt` de entrada
- `out/`: audios generados
- `melodias/`: pistas `.mp3` para fusion

## Configuracion para Gemini

Si usas `--motor gemini` o `--motor todos`, define tu API key:

```powershell
$env:GEMINI_API_KEY="TU_API_KEY"
```

## Uso manual (Python)

Por defecto usa `gtts`:

```bash
python main.py
```

Motor especifico:

```bash
python main.py --motor gtts
python main.py --motor pyttsx3
python main.py --motor gemini
python main.py --motor todos
```

Sin fusion con melodias:

```bash
python main.py --motor gemini --sin-fusion
```

Cambiar carpetas:

```bash
python main.py --motor gtts --in in --out out --melodias melodias
```

## Uso con `start.bat`

`start.bat` crea/activa `venv`, instala dependencias y ejecuta `main.py`.

Ejemplos:

```bat
start.bat
start.bat gtts
start.bat pyttsx3
start.bat gemini
start.bat todos
```

Nota: si eliges `gemini` o `todos` y no existe `GEMINI_API_KEY`, el script la solicita.

## Salidas esperadas

Por cada archivo `.txt` en `in/` se generan archivos en `out/` con formato:

- `nombre_gtts.mp3`
- `nombre_pyttsx3.wav`
- `nombre_gemini.mp3`
- y versiones fusionadas: `nombre_<motor>_melodia.<ext>` (si no usas `--sin-fusion`)

