@echo off
setlocal
REM GAZ Tank Build - Complete Pipeline Execution Launcher (Windows)
REM Usage: gzbuild.cmd -e <environment> [--force] [--clean-all] [--dry-run]
REM Examples: 
REM   gzbuild.cmd -e dev
REM   gzbuild.cmd -e staging --force
REM   gzbuild.cmd -e prod
REM   gzbuild.cmd -e dev --clean-all --dry-run
REM   gzbuild.cmd -e dev --clean-all --force
REM
REM Orchestrates complete build pipeline: clean, setup, lint, generate, sitemap, TOC, package, deploy
REM Special mode: --clean-all removes all files and exits without running pipeline
REM Configuration: config\pipeline.toml

REM Set PYTHONPATH to include utils directory for module imports
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%..\utils;%PYTHONPATH%"

REM Set UTF-8 encoding for proper Unicode handling (emojis in console output)
set "PYTHONIOENCODING=utf-8"

REM Run the gzbuild module with all arguments
python -m gzbuild %*

endlocal
exit /b %errorlevel%