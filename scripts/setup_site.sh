#!/bin/bash
# Site Setup Wizard Launcher (Linux/Mac)
# Usage: ./setup_site.sh -e <environment> [--force] [--clean]
# Examples:
#   ./setup_site.sh -e dev
#   ./setup_site.sh -e dev --force
#   ./setup_site.sh -e staging
#   ./setup_site.sh -e dev --clean
#   ./setup_site.sh -e dev --clean --force
#
# Interactive configuration tool for customizing the site
# Configuration: config/site.toml

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include utils directory for module imports
export PYTHONPATH="$SCRIPT_DIR/../utils:$PYTHONPATH"

# Set UTF-8 encoding for proper Unicode handling (emojis in console output)
export PYTHONIOENCODING=utf-8

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH!"
    echo
    echo "Please install Python 3.11+ from: https://www.python.org/"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Run the setup module with all arguments
python3 -m setup "$@"
