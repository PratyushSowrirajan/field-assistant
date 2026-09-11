@echo off
REM Starts everything the app needs: Postgres (Docker), backend API, frontend,
REM and the Leaf Check classifier. Safe to double-click any time — it checks
REM each piece first and skips anything already running instead of starting
REM duplicates.

echo === Database (Postgres) ===
docker inspect -f "{{.State.Health.Status}}" sfa_postgres 2>nul | findstr /C:"healthy" >nul
if %errorlevel%==0 (
    echo   Already running.
) else (
    echo   Starting...
    docker compose -f "%~dp0docker-compose.yml" up -d
)

echo.
echo === Backend API (port 8010) ===
curl -s -o "%TEMP%\sfa_check.txt" -w "%%{http_code}" http://127.0.0.1:8010/health > "%TEMP%\sfa_code.txt" 2>nul
set /p SFA_BACKEND_CODE=<"%TEMP%\sfa_code.txt"
if "%SFA_BACKEND_CODE%"=="200" (
    echo   Already running.
) else (
    echo   Starting in a new window...
    start "SFA Backend" cmd /k "cd /d "%~dp0backend" && call .venv\Scripts\activate.bat && uvicorn app.main:app --host 127.0.0.1 --port 8010"
)

echo.
echo === Frontend (port 5175) ===
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:5175 > "%TEMP%\sfa_code.txt" 2>nul
set /p SFA_FRONTEND_CODE=<"%TEMP%\sfa_code.txt"
if "%SFA_FRONTEND_CODE%"=="200" (
    echo   Already running.
) else (
    echo   Starting in a new window...
    start "SFA Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev -- --port 5175"
)

echo.
echo === Leaf Check classifier (port 8020) ===
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8020/health > "%TEMP%\sfa_code.txt" 2>nul
set /p SFA_CLASSIFIER_CODE=<"%TEMP%\sfa_code.txt"
if "%SFA_CLASSIFIER_CODE%"=="200" (
    echo   Already running.
) else (
    echo   Starting in a new window...
    start "SFA Classifier" cmd /k "cd /d "%~dp0experiments\plant_disease_classifier" && call .venv\Scripts\activate.bat && uvicorn app:app --host 127.0.0.1 --port 8020"
)

echo.
echo Done. Frontend: http://localhost:5175
echo (New backend/frontend/classifier windows take a few seconds to finish starting up.)
pause
