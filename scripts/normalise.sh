#!/bin/bash
# Markdown Structure Normaliser Launcher (Linux/Mac)
# Usage: ./normalise.sh <filename> [--force] [--dry-run]
# Examples:
#   ./normalise.sh docs/SETUP_SITE.md
#   ./normalise.sh docs/SETUP_SITE.md --force
#   ./normalise.sh docs/SETUP_SITE.md --dry-run
#   ./normalise.sh docs/SETUP_SITE.md --force --dry-run
#
# Converts standalone bold text to proper markdown headings

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include utils directory for module imports
export PYTHONPATH="$SCRIPT_DIR/../utils:$PYTHONPATH"

# Set UTF-8 encoding for proper Unicode handling (emojis in console output)
export PYTHONIOENCODING=utf-8

# Run the normalise module with all arguments
python3 -m normalise "$@"
