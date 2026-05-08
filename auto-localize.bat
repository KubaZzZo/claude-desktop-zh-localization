@echo off
setlocal
cd /d %~dp0

net session >nul 2>&1
if not %errorlevel%==0 (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -ArgumentList '%*' -Verb RunAs"
  exit /b
)

echo Claude Desktop auto localization
echo.
py -3 scripts\auto_localize.py %*
if errorlevel 1 (
  echo.
  echo Auto localization finished with issues. Check the report path above.
  pause
  exit /b 1
)

echo.
echo Auto localization complete. Restart Claude Desktop if it is already running.
pause
endlocal
