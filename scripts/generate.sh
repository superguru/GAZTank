#!/bin/bash
# Static Content Generator Launcher (Linux/Mac)
# Usage: ./generate.sh -e <environment> [--force] [--dry-run]
# Examples:
#   ./generate.sh -e dev
#   ./generate.sh -e staging
#   ./generate.sh -e prod --force
#   ./generate.sh -e dev --dry-run
#   ./generate.sh -e dev --force --dry-run
#
# Converts source files (markdown) to HTML based on generate.toml
# Output goes to publish/<environment>/content directory
# Configuration: config/generate.toml, config/pipeline.toml

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include utils directory for module imports
export PYTHONPATH="$SCRIPT_DIR/../utils:$PYTHONPATH"

# Set UTF-8 encoding for proper Unicode handling (emojis in console output)
export PYTHONIOENCODING=utf-8

# Run the generate module with all arguments
python3 -m utils.generate "$@"
