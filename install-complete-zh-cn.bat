@echo off
setlocal
cd /d %~dp0

net session >nul 2>&1
if not %errorlevel%==0 (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

echo Claude Desktop complete zh-CN installer
echo.
echo This will:
echo   1. Close Claude Desktop if it is running
echo   2. Backup original resource and JS files
echo   3. Copy zh-CN JSON resources
echo   4. Patch hardcoded UI labels and font helper
echo.
choice /C YN /M "Continue"
if errorlevel 2 exit /b 1

taskkill /IM Claude.exe /F >nul 2>&1
taskkill /IM claude.exe /F >nul 2>&1

python scripts\install_reference_localization.py %*
if errorlevel 1 (
  echo.
  echo Install failed. Check the output above.
  pause
  exit /b 1
)

echo.
echo Install complete. Restart Claude Desktop.
pause
endlocal
