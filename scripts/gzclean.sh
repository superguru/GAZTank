#!/bin/bash
# Environment Cleaner Launcher (Linux/Mac)
# Usage: ./gzclean.sh -e <environment> [--force] [--dry-run]
# Examples:
#   ./gzclean.sh -e dev
#   ./gzclean.sh -e staging --dry-run
#   ./gzclean.sh -e prod --force
#
# Removes orphaned files from environment directories
# Configuration: config/pipeline.toml

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include utils directory for module imports
export PYTHONPATH="$SCRIPT_DIR/../utils:$PYTHONPATH"

# Set UTF-8 encoding for proper Unicode handling (emojis in console output)
export PYTHONIOENCODING=utf-8

# Run the clean module with all arguments
python3 -m clean "$@"
