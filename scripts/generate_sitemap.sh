#!/bin/bash
# Sitemap Generator Launcher (Linux/Mac)
# Usage: ./generate_sitemap.sh -e ENVIRONMENT
# Examples:
#   ./generate_sitemap.sh -e dev
#   ./generate_sitemap.sh -e staging
#   ./generate_sitemap.sh -e prod
#
# Generates sitemap.xml for search engine optimization
# Environments: dev, staging, prod
# Configuration: config/pipeline.toml

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include utils directory for module imports
export PYTHONPATH="$SCRIPT_DIR/../utils:$PYTHONPATH"

# Set UTF-8 encoding for proper Unicode handling (emojis in console output)
export PYTHONIOENCODING=utf-8

# Run the sitemap module with all arguments
python3 -m sitemap "$@"
