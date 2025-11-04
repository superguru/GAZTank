#!/bin/bash
# GAZ Tank Build - Complete Pipeline Execution Launcher (Linux/Mac)
# Usage: ./gzbuild.sh -e <environment> [--force] [--clean-all] [--dry-run]
# Examples:
#   ./gzbuild.sh -e dev
#   ./gzbuild.sh -e staging --force
#   ./gzbuild.sh -e prod
#   ./gzbuild.sh -e dev --clean-all --dry-run
#   ./gzbuild.sh -e dev --clean-all --force
#
# Orchestrates complete build pipeline: clean, setup, lint, generate, sitemap, TOC, package, deploy
# Special mode: --clean-all removes all files and exits without running pipeline
# Configuration: config/pipeline.toml

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include utils directory for module imports
export PYTHONPATH="$SCRIPT_DIR/../utils:$PYTHONPATH"

# Set UTF-8 encoding for proper Unicode handling (emojis in console output)
export PYTHONIOENCODING=utf-8

# Run the gzbuild module with all arguments
python3 -m gzbuild "$@"
