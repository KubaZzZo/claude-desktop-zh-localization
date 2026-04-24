@echo off
setlocal
cd /d %~dp0..
python scripts\verify_localization.py
endlocal
