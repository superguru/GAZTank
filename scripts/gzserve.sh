#!/bin/bash
# Development Web Server Launcher (Linux/Mac)
# Usage: ./gzserve.sh -e ENVIRONMENT [-p PORT]
# Examples:
#   ./gzserve.sh -e dev
#   ./gzserve.sh -e staging -p 8080
#   ./gzserve.sh -e prod
#
# Environments: dev, staging, prod
# Configuration: config/pipeline.toml

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Set PYTHONPATH to project root for module imports
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run the server module with all arguments
python -m utils.gzserve "$@"