@ECHO OFF
ECHO Regenerating App UI
cd /D "%~dp0"
..\venv\Scripts\pyside2-uic.exe ..\ui\app.ui -o ..\AppUI.py
ECHO Done