@echo off
echo ===================================================
echo   Scrollix AI - Full Development Mode Launcher
echo ===================================================
echo.

cd /d "%~dp0\.."

echo [1/3] Starting Python FastAPI Backend (http://127.0.0.1:8000)...
start "Scrollix AI Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Starting Vite Frontend Dev Server (http://127.0.0.1:5173)...
start "Scrollix AI Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo [3/3] Launching Desktop Window (NODE_ENV=development)...
start "Scrollix AI Desktop" cmd /k "cd desktop && set NODE_ENV=development && npx electron ."

echo.
echo ===================================================
echo   Scrollix AI is running in LIVE DEVELOPMENT MODE!
echo   Web URL:      http://localhost:5173
echo   Backend API:  http://localhost:8000/docs
echo ===================================================
echo.
