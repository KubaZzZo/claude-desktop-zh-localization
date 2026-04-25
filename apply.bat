@echo off
setlocal
cd /d %~dp0

echo [1/2] 检查 app.asar 完整性...
python scripts\restore_asar.py
if errorlevel 1 (
    echo.
    echo 请修复 app.asar 后重新运行 apply.bat
    pause
    exit /b 1
)

echo.
echo [2/2] 应用汉化...
python scripts\apply_localization.py
endlocal
