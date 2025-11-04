@echo off
setlocal
REM Static Content Generator Launcher (Windows)
REM Usage: generate.cmd -e <environment> [--force] [--dry-run]
REM Examples: 
REM   generate.cmd -e dev
REM   generate.cmd -e staging
REM   generate.cmd -e prod --force
REM   generate.cmd -e dev --dry-run
REM   generate.cmd -e dev --force --dry-run
REM
REM Converts source files (markdown) to HTML based on generate.toml
REM Output goes to publish\<environment>\content directory
REM Configuration: config\generate.toml, config\pipeline.toml

REM Set PYTHONPATH to include utils directory for module imports
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%..\utils;%PYTHONPATH%"

# Set UTF-8 encoding for proper Unicode handling (emojis in console output)
set "PYTHONIOENCODING=utf-8"

REM Run the generate module with all arguments
python -m utils.generate %*

endlocal
exit /b %errorlevel%
