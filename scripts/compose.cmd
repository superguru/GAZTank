@echo off
REM Compose HTML files from source components
REM Usage: compose.cmd -e ENVIRONMENT [--force]
REM
REM Examples:
REM   .\scripts\compose.cmd -e dev
REM   .\scripts\compose.cmd -e staging --force
REM   .\scripts\compose.cmd -e prod
REM
REM Description:
REM   Assembles HTML files from source components based on compose.toml.
REM   Processes composition markers to conditionally include components
REM   based on site.toml feature flags.
REM
REM Arguments:
REM   -e ENVIRONMENT    Target environment (dev/staging/prod) [required]
REM   --force           Force recomposition even if files up-to-date

python -m utils.compose %*
