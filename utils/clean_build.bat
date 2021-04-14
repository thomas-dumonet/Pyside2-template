@ECHO OFF
Echo Cleaning PyInstaller Build folders
cd /D "%~dp0"
rmdir /s /q "..\\build"
rmdir /s /q "..\\output"
rmdir /s /q "..\\dist"
del /s /q "..\\main.spec"
ECHO Done
PAUSE