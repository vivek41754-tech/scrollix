@echo off
echo ===================================================
echo   Scrollix AI - Local Development Launcher
echo ===================================================
echo.

cd /d "%~dp0\.."

echo [1/2] Starting Python FastAPI Backend on http://127.0.0.1:8000...
start "Scrollix AI Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend / Desktop Interface...
start "Scrollix AI Desktop" cmd /k "cd desktop && npx electron ."

echo.
echo Both services launched! You can also view the web interface in your browser at:
echo http://127.0.0.1:5173
echo.
