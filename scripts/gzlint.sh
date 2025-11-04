#!/bin/bash
# GZLint - HTML, JavaScript & Config Linter (Linux/Mac)
# Usage: ./gzlint.sh [--help]
# Examples:
#   ./gzlint.sh
#   ./gzlint.sh --help
#
# Validates HTML, JavaScript, and configuration files for common issues
# Logs to: logs/dev/gzlint_YYYYMMDD.log

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include utils directory for module imports
export PYTHONPATH="$SCRIPT_DIR/../utils:$PYTHONPATH"

# Set UTF-8 encoding for proper Unicode handling (emojis in console output)
export PYTHONIOENCODING=utf-8

# Run the gzlint module with all arguments
python3 -m gzlint "$@"
