
@ECHO OFF
ECHO Generating Invoice App
..\venv\Scripts\pyinstaller.exe --noconfirm --specpath ".." --add-data "resources\\*;resources" --icon="resources\\noun_Plant.ico" --distpath "..\\dist" --workpath "..\\build" --onefile --windowed ..\main.py
ECHO Done
PAUSE