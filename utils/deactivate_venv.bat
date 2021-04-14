@ECHO OFF
ECHO Deactivate venv
cd /D "%~dp0"
call ..\venv\Scripts\deactivate.bat
ECHO Done