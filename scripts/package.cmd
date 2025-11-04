@echo off
setlocal
REM Website Packager - Windows Launcher
REM Usage: package.cmd -e <environment> [--force] [--dry-run]
REM Examples: 
REM   package.cmd -e dev
REM   package.cmd -e staging --force
REM   package.cmd -e prod --dry-run
REM   package.cmd -e dev --force --dry-run
REM
REM Builds, validates, and packages the website for deployment
REM Configuration: config\pipeline.toml

REM Set PYTHONPATH to include utils directory for module imports
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%..\utils;%PYTHONPATH%"

REM Set UTF-8 encoding for proper Unicode handling (emojis in console output)
set "PYTHONIOENCODING=utf-8"

REM Run the package module with all arguments
python -m package %*

endlocal
exit /b %errorlevel%
