@echo off
setlocal
REM FTP Host Server Launcher (Windows)
REM Usage: gzhost.cmd -e <environment> [-p <port>]
REM Examples: 
REM   gzhost.cmd -e dev
REM   gzhost.cmd -e staging
REM   gzhost.cmd -e prod -p 2190
REM
REM Starts an FTP server for simulating remote deployment hosts
REM Serves files from publish\<environment> directory
REM Configuration: config\pipeline.toml, config\ftp_users.toml

REM Set PYTHONPATH to include utils directory for module imports
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%..\utils;%PYTHONPATH%"

REM Set UTF-8 encoding for proper Unicode handling (emojis in console output)
set "PYTHONIOENCODING=utf-8"

REM Run the gzhost module with all arguments
python -m gzhost %*

endlocal
exit /b %errorlevel%
