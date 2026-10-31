@echo off
echo ===================================================
echo   Scrollix AI - Full Test & Packaging Pipeline
echo ===================================================
echo.

cd /d "%~dp0\.."

echo [1/3] Running Backend Automated Tests...
cd backend
python -m pytest tests\test_all_modules.py -v
if %errorlevel% neq 0 (
    echo [ERROR] Backend automated test suite failed!
    exit /b %errorlevel%
)
cd ..

echo.
echo [2/3] Building Frontend Web Application...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Frontend Vite build failed!
    exit /b %errorlevel%
)
cd ..

echo.
echo [3/3] Packaging Windows Executable with Electron...
cd desktop
set NODE_TLS_REJECT_UNAUTHORIZED=0
call npx electron-packager . "Scrollix AI" --platform=win32 --arch=x64 --out=../dist --overwrite
if %errorlevel% neq 0 (
    echo [ERROR] Executable packaging failed!
    exit /b %errorlevel%
)
cd ..

echo.
echo ===================================================
echo   COMPLETE VERIFIED BUILD READY!
echo   Executable Location:
echo   dist\Scrollix AI-win32-x64\Scrollix AI.exe
echo ===================================================
pause
