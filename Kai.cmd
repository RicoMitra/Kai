@echo off
setlocal
pushd "%~dp0kai"
set "KAI_PYTHON=%LOCALAPPDATA%\Kai\runtime\Scripts\pythonw.exe"
if not exist "%KAI_PYTHON%" (
    echo Runtime Kai belum ada. Jalankan Setup Kai.cmd dahulu.
    pause
    popd
    exit /b 1
)
if "%~1"=="" (
    start "" "%KAI_PYTHON%" main.py --island
) else (
    start "" "%KAI_PYTHON%" main.py %*
)
popd
