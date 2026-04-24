@echo off
setlocal
cd /d %~dp0

echo ========================================
echo Claude Desktop 中文化一键启动
echo 流程: apply ^> verify
echo ========================================
echo.

echo [1/2] 正在应用中文化...
call apply.bat
if errorlevel 1 (
    echo.
    echo 应用失败，已停止后续校验。
    echo 请检查上方输出信息。
    goto end
)

echo.
echo [2/2] 正在执行校验...
call verify.bat
if errorlevel 1 (
    echo.
    echo 校验未通过，请检查上方输出信息。
    goto end
)

echo.
echo 全部完成：应用与校验均已执行完成。

:end
echo.
pause
endlocal
