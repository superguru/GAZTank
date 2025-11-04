@echo off
setlocal
REM Site Setup Wizard Launcher (Windows)
REM Usage: setup_site.cmd -e <environment> [--force] [--clean]
REM Examples: 
REM   setup_site.cmd -e dev
REM   setup_site.cmd -e dev --force
REM   setup_site.cmd -e staging
REM   setup_site.cmd -e dev --clean
REM   setup_site.cmd -e dev --clean --force
REM
REM Interactive configuration tool for customizing the site
REM Configuration: config\site.toml

REM Set PYTHONPATH to include utils directory for module imports
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%..\utils;%PYTHONPATH%"

REM Set UTF-8 encoding for proper Unicode handling (emojis in console output)
set "PYTHONIOENCODING=utf-8"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.11+ from: https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Run the setup module with all arguments
python -m setup %*

endlocal
exit /b %errorlevel%
