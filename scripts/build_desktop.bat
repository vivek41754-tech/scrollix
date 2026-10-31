@echo off
echo ===================================================
echo   Scrollix AI - Desktop Executable Packaging Script
echo ===================================================
echo.

cd /d "%~dp0\.."

echo [1/3] Building React + TypeScript Frontend...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo Error building frontend!
    exit /b %errorlevel%
)
cd ..

echo.
echo [2/3] Syncing distribution bundle into desktop...
if not exist "desktop\frontend_dist" mkdir "desktop\frontend_dist"
xcopy /E /I /Y "frontend\dist" "desktop\frontend_dist"

echo.
echo [3/3] Packaging Windows 64-bit Executable with Electron...
cd desktop
set NODE_TLS_REJECT_UNAUTHORIZED=0
call npx electron-packager . "Scrollix AI" --platform=win32 --arch=x64 --out=../dist --overwrite
if %errorlevel% neq 0 (
    echo Error packaging Electron app!
    exit /b %errorlevel%
)
cd ..

echo.
echo ===================================================
echo   SUCCESS! Windows Executable generated at:
echo   dist\Scrollix AI-win32-x64\Scrollix AI.exe
echo ===================================================
pause
