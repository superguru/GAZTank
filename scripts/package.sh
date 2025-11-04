#!/bin/bash
# Website Packager - Linux/Mac Launcher
# Usage: package.sh -e <environment> [--force] [--dry-run]
# Examples:
#   package.sh -e dev
#   package.sh -e staging --force
#   package.sh -e prod --dry-run
#   package.sh -e dev --force --dry-run
#
# Builds, validates, and packages the website for deployment
# Configuration: config/pipeline.toml

# Set PYTHONPATH to include utils directory for module imports
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR/../utils:$PYTHONPATH"

# Set UTF-8 encoding for proper Unicode handling (emojis in console output)
export PYTHONIOENCODING=utf-8

# Run the package module with all arguments
python3 -m package "$@"
exit $?