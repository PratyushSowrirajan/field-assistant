@echo off
REM Wipes the demo account back to nothing (no farm, no field, no rover, no
REM history). Only needs Postgres running, not the backend API — safe to run
REM even if you've shut everything else down after trying it out.
REM
REM Run demo_fresh.bat afterwards to rebuild a populated demo state.

cd /d "%~dp0backend"
call .venv\Scripts\activate.bat

python scripts\clear_demo_data.py
if errorlevel 1 (
    echo.
    echo Something failed above. Is Postgres running? Try run_all.bat first.
    pause
    exit /b 1
)

echo.
echo Cleared. Run demo_fresh.bat when you're ready to repopulate it.
pause
