@echo off
REM Script para crear y activar el entorno virtual, instalar dependencias y ejecutar el proyecto

REM Crear entorno virtual si no existe
if not exist venv (
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Instalar dependencias desde requirements.txt
pip install --upgrade pip
pip install -r requirements.txt

REM Ejecutar el script principal
python main.py

pause
