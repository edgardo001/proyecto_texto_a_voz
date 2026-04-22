@echo off
setlocal
REM Script para crear/activar entorno virtual, instalar dependencias y ejecutar main.py

REM Crear entorno virtual si no existe
if not exist venv (
    py -m venv venv
    if errorlevel 1 (
        echo No se pudo crear el entorno con "py". Probando con "python"...
        python -m venv venv
    )
)

REM Activar entorno virtual
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error al activar el entorno virtual.
    pause
    exit /b 1
)

REM Instalar dependencias desde requirements.txt
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error instalando dependencias.
    pause
    exit /b 1
)

set MOTOR=%~1
if "%MOTOR%"=="" set MOTOR=gtts

if /I "%MOTOR%"=="gemini" goto :check_gemini
if /I "%MOTOR%"=="todos" goto :check_gemini
goto :run

:check_gemini
if "%GEMINI_API_KEY%"=="" (
    echo.
    echo Estas usando el motor "%MOTOR%", que requiere GEMINI_API_KEY.
    set /p GEMINI_API_KEY=Ingresa tu GEMINI_API_KEY: 
)

:run
echo.
echo Ejecutando main.py con motor: %MOTOR%
python main.py --motor %MOTOR%
if errorlevel 1 (
    echo Ocurrio un error al ejecutar main.py
)

pause
