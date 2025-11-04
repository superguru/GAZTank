@echo off
setlocal
REM Markdown Structure Normaliser Launcher (Windows)
REM Usage: normalise.cmd <filename> [--force] [--dry-run]
REM Examples: 
REM   normalise.cmd docs\SETUP_SITE.md
REM   normalise.cmd docs\SETUP_SITE.md --force
REM   normalise.cmd docs\SETUP_SITE.md --dry-run
REM   normalise.cmd docs\SETUP_SITE.md --force --dry-run
REM
REM Converts standalone bold text to proper markdown headings

REM Set PYTHONPATH to include utils directory for module imports
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%..\utils;%PYTHONPATH%"

REM Set UTF-8 encoding for proper Unicode handling (emojis in console output)
set "PYTHONIOENCODING=utf-8"

REM Run the normalise module with all arguments
python -m normalise %*

endlocal
exit /b %errorlevel%
