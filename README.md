# Proyecto Texto a Voz

Este proyecto convierte texto en archivos de audio utilizando Python. Permite transformar el contenido de un archivo de texto en voz, generando archivos de audio en diferentes formatos.

## Descripción

El proyecto lee el texto desde un archivo (`entrada.txt`) y lo convierte en audio usando diferentes librerías de síntesis de voz, como `gtts` y `pyttsx3`. Los archivos de audio generados pueden ser utilizados para diferentes propósitos, como accesibilidad o automatización.

## Requisitos

- Python 3.x

## Instalación y uso de entorno virtual (venv)

Se recomienda ejecutar este proyecto dentro de un entorno virtual de Python para evitar conflictos de dependencias. Para crear y activar un entorno virtual en Windows, sigue estos pasos:

1. Abre una terminal (PowerShell o CMD) en la carpeta del proyecto.
2. Crea el entorno virtual:

```
python -m venv venv
```

3. Activa el entorno virtual:

- En PowerShell:
```
.\venv\Scripts\Activate.ps1
```
- En CMD:
```
venv\Scripts\activate.bat
```

4. Instala las dependencias necesarias desde el archivo requirements.txt:

```
pip install -r requirements.txt
```

## Ejecución en Windows

### Opción 1: Manual

1. Asegúrate de tener el archivo `entrada.txt` con el texto que deseas convertir a voz.
2. Con el entorno virtual activado, ejecuta el script principal:

```
python main.py
```

3. Se generarán archivos de audio (por ejemplo, `entrada_gtts.mp3` y `entrada_pyttsx3.wav`) en la misma carpeta.

### Opción 2: Usando el script start.bat

Puedes automatizar todo el proceso ejecutando el archivo `start.bat` incluido en el proyecto. Este script creará y activará el entorno virtual, instalará las dependencias y ejecutará la aplicación automáticamente.

Para usarlo:

1. Haz doble clic en `start.bat` o ejecútalo desde la terminal con:
```
start.bat
```

## Notas

- Puedes modificar el archivo `main.py` para ajustar la voz, el idioma o el formato de salida según tus necesidades.
- Si tienes problemas con las voces en `pyttsx3`, asegúrate de tener instalados los motores de voz de Windows.
