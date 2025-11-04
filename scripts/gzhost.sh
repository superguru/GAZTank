#!/bin/bash
# FTP Host Server Launcher (Linux/Mac)
# Usage: ./gzhost.sh -e <environment> [-p <port>]
# Examples:
#   ./gzhost.sh -e dev
#   ./gzhost.sh -e staging
#   ./gzhost.sh -e prod -p 2190
#
# Starts an FTP server for simulating remote deployment hosts
# Serves files from publish/<environment> directory
# Configuration: config/pipeline.toml, config/ftp_users.toml

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include utils directory for module imports
export PYTHONPATH="$SCRIPT_DIR/../utils:$PYTHONPATH"

# Set UTF-8 encoding for proper Unicode handling (emojis in console output)
export PYTHONIOENCODING=utf-8

# Run the gzhost module with all arguments
python3 -m gzhost "$@"
