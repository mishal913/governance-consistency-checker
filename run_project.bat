@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=C:\Users\H & S\AppData\Local\Programs\Python\Python313\python.exe"

if not exist "%PYTHON%" (
    echo Python was not found at:
    echo %PYTHON%
    echo.
    echo Install Python or update the PYTHON path in run_project.bat.
    pause
    exit /b 1
)

echo Building governance knowledge graph...
"%PYTHON%" build_knowledge_graph.py
if errorlevel 1 goto :failed

echo.
echo Running consistency checker...
"%PYTHON%" consistency_checker.py
if errorlevel 1 goto :failed

echo.
echo Running relationship analysis...
"%PYTHON%" analyze_governance.py
if errorlevel 1 goto :failed

echo.
echo Success.
echo Created RDF graphs and consistency relationship reports.
pause
exit /b 0

:failed
echo.
echo The project failed to run. Review the error shown above.
pause
exit /b 1