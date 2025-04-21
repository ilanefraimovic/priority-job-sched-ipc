@echo off
setlocal

REM Start PowerShell windows for tailing with window titles we can find later
start "TAIL_TERMINAL" powershell -NoExit -Command "Get-Content shared_terminal.txt -Wait"
start "TAIL_LOG" powershell -NoExit -Command "Get-Content log.txt -Wait"


REM Run Python main program
python main.py

REM Kill tailing windows by window title
taskkill /FI "WINDOWTITLE eq TAIL_TERMINAL*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq TAIL_LOG*" /T /F >nul 2>&1

pause
