@echo off
echo Instalowanie/Aktualizowanie wymagan...
python -m pip install --upgrade pyinstaller ffmpeg-python customtkinter

echo Czyszczenie starych buildow...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo Budowanie programu .exe...
:: --collect-all customtkinter jest kluczowe dla wygladu
python -m PyInstaller --noconsole --onefile --name "AudioNormalizerUltra" --collect-all customtkinter --icon=NONE audio_app.py

echo.
echo ========================================================
echo SUKCES! 
echo Program znajduje sie w folderze: dist/AudioNormalizerUltra.exe
echo ========================================================
pause