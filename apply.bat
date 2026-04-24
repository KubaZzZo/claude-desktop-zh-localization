@echo off
setlocal
cd /d %~dp0..
python scripts\apply_localization.py
endlocal
