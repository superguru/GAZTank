@echo off
setlocal
REM Sitemap Generator Launcher (Windows)
REM Usage: generate_sitemap.cmd -e ENVIRONMENT
REM Examples: 
REM   generate_sitemap.cmd -e dev
REM   generate_sitemap.cmd -e staging
REM   generate_sitemap.cmd -e prod
REM
REM Generates sitemap.xml for search engine optimization
REM Environments: dev, staging, prod
REM Configuration: config\pipeline.toml

REM Set PYTHONPATH to include utils directory for module imports
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%..\utils;%PYTHONPATH%"

REM Set UTF-8 encoding for proper Unicode handling (emojis in console output)
set "PYTHONIOENCODING=utf-8"

REM Run the sitemap module with all arguments
python -m sitemap %*

endlocal
exit /b %errorlevel%
