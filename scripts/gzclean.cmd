@echo off
setlocal
REM Environment Cleaner Launcher (Windows)
REM Usage: gzclean.cmd -e <environment> [--force] [--dry-run]
REM Examples: 
REM   gzclean.cmd -e dev
REM   gzclean.cmd -e staging --dry-run
REM   gzclean.cmd -e prod --force
REM
REM Removes orphaned files from environment directories
REM Configuration: config\pipeline.toml

REM Set PYTHONPATH to include utils directory for module imports
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%..\utils;%PYTHONPATH%"

REM Set UTF-8 encoding for proper Unicode handling (emojis in console output)
set "PYTHONIOENCODING=utf-8"

REM Run the clean module with all arguments
python -m clean %*

endlocal
exit /b %errorlevel%
