@echo off
REM Wipes the demo account and rebuilds it from scratch: farm, field with a
REM drawn boundary, and a rover scan sweep with realistic detections/alerts/
REM environment data. Run this right before a demo for a clean, consistent
REM starting point every time.
REM
REM Requires: run_all.bat already run (backend API must be reachable).

cd /d "%~dp0backend"
call .venv\Scripts\activate.bat

echo === Clearing existing demo data ===
python scripts\clear_demo_data.py
if errorlevel 1 goto :error

echo.
echo === Rebuilding fresh demo data ===
python scripts\seed_demo.py
if errorlevel 1 goto :error

echo.
echo Demo is ready. Log in at http://localhost:5175 as farmer2@example.com / pass1234
pause
exit /b 0

:error
echo.
echo Something failed above. Is the backend running? Try run_all.bat first.
pause
exit /b 1
