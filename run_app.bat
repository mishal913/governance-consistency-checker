@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=C:\Users\H & S\AppData\Local\Programs\Python\Python313\python.exe"

if not exist "%PYTHON%" (
    echo Python was not found at:
    echo %PYTHON%
    pause
    exit /b 1
)

echo Starting University Governance Consistency Checker...
"%PYTHON%" -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo The application failed to start. Review the error above.
    pause
)