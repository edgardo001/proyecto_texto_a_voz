@echo off
REM Script para crear y activar el entorno virtual, instalar dependencias y ejecutar el proyecto

REM Crear entorno virtual si no existe
if not exist venv (
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Instalar dependencias
pip install --upgrade pip
pip install gtts pyttsx3

REM Ejecutar el script principal
python main.py

pause
