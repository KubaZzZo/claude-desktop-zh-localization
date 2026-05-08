@echo off
setlocal
cd /d %~dp0
py -3 scripts\verify_localization.py %*
endlocal
