@echo off
setlocal
REM FTP Deployment Launcher (Windows)
REM Usage: deploy.cmd -e <environment> [--host <host>] [-p <port>] [--force] [--dry-run]
REM Examples: 
REM   deploy.cmd -e dev
REM   deploy.cmd -e staging --dry-run
REM   deploy.cmd -e prod --force
REM   deploy.cmd -e dev --host ftp.example.com -p 21
REM
REM Deploys packaged site to FTP server
REM Configuration: config\pipeline.toml, config\ftp_users.toml

REM Set PYTHONPATH to include utils directory for module imports
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%..\utils;%PYTHONPATH%"

REM Set UTF-8 encoding for proper Unicode handling (emojis in console output)
set "PYTHONIOENCODING=utf-8"

REM Run the deploy module with all arguments
python -m deploy %*

endlocal
exit /b %errorlevel%
