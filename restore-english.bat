@echo off
setlocal
cd /d %~dp0

net session >nul 2>&1
if not %errorlevel%==0 (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

echo Claude Desktop English restore
echo.
echo This will:
echo   1. Close Claude Desktop if it is running
echo   2. Restore files from the zh-CN backup
echo   3. Remove zh-CN locale/font mirror when config exists
echo.
choice /C YN /M "Continue"
if errorlevel 2 exit /b 1

taskkill /IM Claude.exe /F >nul 2>&1
taskkill /IM claude.exe /F >nul 2>&1

python scripts\restore_reference_localization.py %*
if errorlevel 1 (
  echo.
  echo Restore failed. Check the output above.
  pause
  exit /b 1
)

echo.
echo Restore complete. Restart Claude Desktop.
pause
endlocal
