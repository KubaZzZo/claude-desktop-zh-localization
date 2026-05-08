@echo off
setlocal
cd /d %~dp0
py -3 scripts\rollback_localization.py %*
endlocal
