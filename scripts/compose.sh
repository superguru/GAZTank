#!/usr/bin/env bash
# Compose HTML files from source components
# Usage: ./compose.sh -e ENVIRONMENT [--force]
#
# Examples:
#   ./scripts/compose.sh -e dev
#   ./scripts/compose.sh -e staging --force
#   ./scripts/compose.sh -e prod
#
# Description:
#   Assembles HTML files from source components based on compose.toml.
#   Processes composition markers to conditionally include components
#   based on site.toml feature flags.
#
# Arguments:
#   -e ENVIRONMENT    Target environment (dev/staging/prod) [required]
#   --force           Force recomposition even if files up-to-date

python -m utils.compose "$@"
