@ECHO OFF
ECHO Regenerating Invoice UI
..\venv\Scripts\pyside2-uic.exe ..\ui\app.ui -o ..\appUI.py
ECHO Done
PAUSE