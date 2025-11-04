@echo off
setlocal
REM Development Web Server Launcher (Windows)
REM Usage: gzserve.cmd -e ENVIRONMENT [-p PORT]
REM Examples: 
REM   gzserve.cmd -e dev
REM   gzserve.cmd -e staging -p 8080
REM   gzserve.cmd -e prod
REM
REM Environments: dev, staging, prod
REM Configuration: config\pipeline.toml

REM Set PYTHONPATH to project root for module imports
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

REM Run the server module with all arguments
python -m utils.gzserve %*

endlocal
exit /b %errorlevel%
