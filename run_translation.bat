@echo off
title RE4 Translation Tool
setlocal enabledelayedexpansion

echo ============================================================
echo          RE4 REMAKE - OLLAMA TRANSLATION RUNNER
echo ============================================================

:: 1. Check if Python is installed
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)

:: 2. Check if Ollama is installed
where ollama >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Ollama is not installed or not in PATH.
    pause
    exit /b
)

:: 3. Get the current PID of this CMD window to monitor closure
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "(Get-Process -Id $PID).Parent.Id"`) do (
    set CMD_PID=%%i
)

echo [INFO] Current Window PID: !CMD_PID!

:: 4. Start Ollama if not running
tasklist /fi "imagename eq ollama.exe" 2>nul | find /i "ollama.exe" >nul
if errorlevel 1 (
    echo [INFO] Ollama is not running. Starting Ollama...
    start "" /min ollama serve
    timeout /t 5 /nobreak >nul
) else (
    echo [INFO] Ollama is already running.
)

:: 5. Start a background watcher to kill Ollama if this window is closed (including via 'X' button)
echo [INFO] Starting background process watcher...
start /b powershell -NoProfile -WindowStyle Hidden -Command ^
    "$pid_to_watch = !CMD_PID!;" ^
    "while (Get-Process -Id $pid_to_watch -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 1 };" ^
    "Stop-Process -Name 'ollama' -Force -ErrorAction SilentlyContinue;" ^
    "Stop-Process -Name 'ollama_llama_server' -Force -ErrorAction SilentlyContinue;"

:: 6. Run the translation script
echo [INFO] Running translation...
echo ------------------------------------------------------------
python translate_csv_ollama.py
echo ------------------------------------------------------------

:: 7. Cleanup Ollama on normal exit
echo [INFO] Script finished. Stopping Ollama to free VRAM/RAM...
taskkill /f /im ollama.exe >nul 2>&1
taskkill /f /im ollama_llama_server.exe >nul 2>&1
echo [INFO] Ollama stopped.

echo ============================================================
echo Dịch hoàn tất hoặc tạm dừng! Tiến trình Ollama đã được đóng.
echo ============================================================
pause
