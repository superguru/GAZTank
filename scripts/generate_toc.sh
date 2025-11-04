#!/bin/bash
#
# Table of Contents Generator Launcher (Linux/Mac)
# Usage: generate_toc.sh -e ENVIRONMENT [--strip] [--dry-run] [--force]
# Examples: 
#   generate_toc.sh -e dev
#   generate_toc.sh -e staging
#   generate_toc.sh -e prod --dry-run
#   generate_toc.sh -e dev --strip
#   generate_toc.sh -e dev --force
#
# Adds IDs to headings and injects TOC HTML into content files
# Environments: dev, staging, prod
# Configuration: config/pipeline.toml

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set PYTHONPATH to include utils directory for module imports
export PYTHONPATH="$SCRIPT_DIR/../utils:$PYTHONPATH"

# Run the toc module with all arguments
python -m toc "$@"

exit $?
