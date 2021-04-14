@ECHO OFF
ECHO Initializing dev environment
cd /D "%~dp0"
py -m venv ..\venv
call ..\venv\Scripts\activate.bat
pip install -r ..\requirements.txt
ECHO Done