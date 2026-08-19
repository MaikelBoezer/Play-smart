@echo off
REM start_inference_service.bat
REM ─────────────────────────────────────────────────────────────────────────────
REM Run this on the GPU PC to start the inference service.
REM Double-click it, or register it with NSSM to auto-start on boot.
REM
REM NSSM (Non-Sucking Service Manager) lets you run this as a proper Windows
REM service that starts automatically on boot without needing to be logged in:
REM   1. Download nssm from https://nssm.cc
REM   2. Run: nssm install PlaySmartInference
REM   3. Set path to this .bat file
REM   4. Run: nssm start PlaySmartInference
REM ─────────────────────────────────────────────────────────────────────────────

REM Resolve venv relative to this bat file's location so it works on any machine
set VENV_PATH=%~dp0venv\Scripts\activate.bat

if not exist "%VENV_PATH%" (
    echo ERROR: venv not found at %VENV_PATH%
    echo Make sure the venv folder is in the same directory as this bat file.
    pause
    exit /b 1
)

call "%VENV_PATH%"

uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1

pause