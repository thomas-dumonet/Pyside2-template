@ECHO OFF
ECHO Generating Invoice App
cd /D "%~dp0"
..\venv\Scripts\pyinstaller.exe --noconfirm --specpath ".." --add-data "resources\\*;resources" --icon="resources\\icon.ico" --distpath "..\\dist" --workpath "..\\build" --onefile --windowed ..\main.py
ECHO Done
PAUSE