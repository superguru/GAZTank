@echo off
setlocal
REM Table of Contents Generator Launcher (Windows)
REM Usage: generate_toc.cmd -e ENVIRONMENT [--strip] [--dry-run] [--force]
REM Examples: 
REM   generate_toc.cmd -e dev
REM   generate_toc.cmd -e staging
REM   generate_toc.cmd -e prod --dry-run
REM   generate_toc.cmd -e dev --strip
REM   generate_toc.cmd -e dev --force
REM
REM Adds IDs to headings and injects TOC HTML into content files
REM Environments: dev, staging, prod
REM Configuration: config\pipeline.toml

REM Set PYTHONPATH to include utils directory for module imports
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%..\utils;%PYTHONPATH%"

REM Set UTF-8 encoding for proper Unicode handling
set "PYTHONIOENCODING=utf-8"

REM Run the toc module with all arguments
python -m toc %*

endlocal
exit /b %errorlevel%
