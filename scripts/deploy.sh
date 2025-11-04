#!/bin/bash
# FTP Deployment Launcher (Linux/Mac)
# Usage: ./deploy.sh -e <environment> [--host <host>] [-p <port>] [--force] [--dry-run]
# Examples:
#   ./deploy.sh -e dev
#   ./deploy.sh -e staging --dry-run
#   ./deploy.sh -e prod --force
#   ./deploy.sh -e dev --host ftp.example.com -p 21
#
# Deploys packaged site to FTP server
# Configuration: config/pipeline.toml, config/ftp_users.toml

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include utils directory for module imports
export PYTHONPATH="$SCRIPT_DIR/../utils:$PYTHONPATH"

# Set UTF-8 encoding for proper Unicode handling (emojis in console output)
export PYTHONIOENCODING=utf-8

# Run the deploy module with all arguments
python3 -m deploy "$@"
