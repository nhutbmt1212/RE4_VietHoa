@echo off
title RE4 Translation Tool
setlocal enabledelayedexpansion

echo ============================================================
echo          RE4 REMAKE - OLLAMA & NVIDIA TRANSLATION RUNNER
echo ============================================================
echo.
echo Select Translation Mode:
echo  [1] Local AI (Ollama - gemma3:12b)
echo  [2] Cloud AI (NVIDIA NIM API - Llama 3.3 70B [Free & High Quality])
echo.
set /p CHOICE="Enter your choice (1 or 2): "

if "%CHOICE%"=="2" (
    echo.
    echo ============================================================
    echo           RUNNING VIA NVIDIA NIM API (CLOUD)
    echo ============================================================
    
    :: 1. Check if Python is installed
    where python >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not in PATH.
        pause
        exit /b
    )
    
    :: 2. Check or Prompt for API Key
    if not exist nvidia_key.txt (
        echo You need an API Key from build.nvidia.com to run this mode.
        echo It is completely free and provides a 70B parameter model.
        set /p API_KEY="Please paste your NVIDIA API Key (nvapi-...): "
        echo !API_KEY!>nvidia_key.txt
        echo API Key saved to nvidia_key.txt
        echo.
    )
    
    :: 3. Run NVIDIA translation
    python translate_csv_nvidia_batch.py
    
    echo ============================================================
    echo Translation complete or paused.
    echo ============================================================
    pause
    exit /b
)

:: Else: Default to Local Ollama
echo.
echo ============================================================
echo           RUNNING VIA LOCAL OLLAMA (gemma3:12b)
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
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "gwmi Win32_Process | ? ProcessId -eq $pid | select -Expand ParentProcessId"`) do (
    set CMD_PID=%%i
)

echo [INFO] Current Window PID: !CMD_PID!

:: 4. Start Ollama if not running
tasklist /fi "imagename eq ollama.exe" 2>nul | find /i "ollama.exe" >nul
if errorlevel 1 (
    echo [INFO] Ollama is not running. Starting Ollama...
    start "" /min ollama serve
    ping 127.0.0.1 -n 6 >nul
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
echo Dich hoan tat hoac tam dung! Tien trinh Ollama da duoc dong.
echo ============================================================
pause
