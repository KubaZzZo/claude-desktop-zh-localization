@echo off
setlocal
cd /d %~dp0..
python scripts\rollback_localization.py
endlocal
