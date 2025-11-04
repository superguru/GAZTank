@echo off
setlocal
REM GZLint - HTML, JavaScript & Config Linter (Windows)
REM Usage: gzlint.cmd [--help]
REM Examples:
REM   gzlint.cmd
REM   gzlint.cmd --help
REM
REM Validates HTML, JavaScript, and configuration files for common issues
REM Logs to: logs\dev\gzlint_YYYYMMDD.log

REM Set PYTHONPATH to include utils directory for module imports
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%..\utils;%PYTHONPATH%"

REM Set UTF-8 encoding for proper Unicode handling (emojis in console output)
set "PYTHONIOENCODING=utf-8"

REM Run the gzlint module with all arguments
python -m gzlint %*

endlocal
exit /b %errorlevel%
