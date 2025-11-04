@echo off
setlocal
REM Type Checking Script Launcher (Windows)
REM Usage: check_types.cmd [options]
REM Example: check_types.cmd -Path utils/server

REM Set script directory
set "SCRIPT_DIR=%~dp0"

REM Try pwsh first (PowerShell 7+), fall back to powershell (Windows PowerShell)
where pwsh >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    pwsh -File "%SCRIPT_DIR%check_types.ps1" %*
) else (
    powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%check_types.ps1" %*$PSVersionTable
)

endlocal
exit /b %errorlevel%
