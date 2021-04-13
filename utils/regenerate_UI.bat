@ECHO OFF
ECHO Regenerating Invoice UI
..\venv\Scripts\pyside2-uic.exe ..\ui\InvoiceGenerator.ui -o ..\invoiceUI.py
ECHO Done
PAUSE