@ECHO OFF
ECHO Freezing pip dependencies
cd /D "%~dp0"
call ..\venv\Scripts\activate.bat
pip freeze > ..\requirements.txt
ECHO Done