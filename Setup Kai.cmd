@echo off
setlocal
set "PYTHONUTF8=1"
set "KAI_RUNTIME=%LOCALAPPDATA%\Kai\runtime"
if not exist "%KAI_RUNTIME%\Scripts\python.exe" (
    py -3.12 -m venv "%KAI_RUNTIME%"
    if errorlevel 1 (
        echo Pasang Python 3.12 x64 dahulu dari python.org.
        pause
        exit /b 1
    )
)
"%KAI_RUNTIME%\Scripts\python.exe" -m pip install -r "%~dp0kai\requirements.txt"
if errorlevel 1 (
    echo Instalasi gagal. Periksa koneksi dan pesan di atas.
) else (
    echo Selesai. Buka Kai.cmd. Mode suara nonaktif.
)
pause
