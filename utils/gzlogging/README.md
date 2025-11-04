# GZLogging Module

Environment-aware logging infrastructure for the GAZTank project with automatic configuration and daily log rotation.

**Version:** 1.2  
**Last Updated:** December 19, 2024

## Table of Contents

- [Purpose](#purpose)
- [Build Pipeline](#build-pipeline)
- [Logging](#logging)
  - [How GZLogging Logs Itself](#how-gzlogging-logs-itself)
  - [Log Format](#log-format)
  - [Log Levels](#log-levels)
- [Log Rotation](#log-rotation)
  - [How Rotation Works](#how-rotation-works)
  - [Configuration](#configuration)
  - [Directory Structure](#directory-structure)
  - [Rotation Behavior](#rotation-behavior)
  - [Examples](#examples)
- [Usage](#usage)
  - [Installation](#installation)
  - [Basic Example](#basic-example)
  - [Log Output Format](#log-output-format)
  - [Available Log Methods](#available-log-methods)
  - [Read-Only Properties](#read-only-properties)
  - [Multiple Tools](#multiple-tools)
  - [Multiple Environments](#multiple-environments)
  - [Console Output](#console-output)
- [Command Line Arguments](#command-line-arguments)
- [Module Structure](#module-structure)
  - [Architecture](#architecture)
  - [Internal State Management](#internal-state-management)
- [Features](#features)
- [Invocation Points](#invocation-points)
- [Configuration](#configuration-1)
  - [Log File Locations](#log-file-locations)
- [Customisation](#customisation)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Development](#development)
  - [Testing](#testing)
  - [Integration Example](#integration-example)
  - [Error Handling](#error-handling)
  - [File Locations](#file-locations)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)
- [Authors](#authors)

## Purpose

GZLogging provides centralized logging infrastructure for all GAZTank modules and tools. It automatically routes logs to environment-specific directories, handles daily log file rotation, and provides a simple API for modules to use.

### Key Design Goals

- **Environment-Aware**: Automatically routes logs to environment-specific directories (dev, staging, prod)
- **Configuration-Driven**: Reads log directories from `config/tools.toml`
- **Automatic Log Rotation**: Old log files are automatically rotated, compressed, and cleaned up
- **UTF-8 Support**: All log files use UTF-8 encoding with emoji support
- **Read-Only Context**: Environment settings are immutable once created
- **Daily Rotation**: Logs are written to files named `{tool_name}_{YYYYMMDD}.log`
- **Standard Logging**: Built on Python's standard `logging` module
- **Singleton Pattern**: Configuration loaded once, loggers reused efficiently

## Build Pipeline

GZLogging is a foundational module used by all other GAZTank tools and modules:

```
GAZTank Build Pipeline:
  ├─ gzlint → uses gzlogging
  ├─ normalise → uses gzlogging
  ├─ generate → uses gzlogging
  ├─ setup → uses gzlogging
  └─ package → uses gzlogging

All tools log to:
  logs/{environment}/{tool}_YYYYMMDD.log
```

### Purpose in Pipeline:
- Provides consistent logging across all tools
- Centralizes log file management
- Enables environment-specific log routing
- Facilitates debugging and audit trails

## Logging

### How GZLogging Logs Itself

GZLogging is a meta-logging module - it provides logging for other modules but minimally logs its own operations:

#### What gets logged:
- Configuration loading errors (stderr)
- Missing environment definitions (stderr)
- Log directory creation (stderr)

#### What doesn't get logged:
- Successful initialization (silent)
- Logger creation (silent)
- Normal operations (silent)

This design keeps log files focused on the actual tool's activities, not the logging infrastructure itself.

### Log Format

Each log entry is formatted as:
```
[YYYY-MM-DD HH:MM:SS] [environment] [LEVEL] message
```

Example:
```log
[2025-10-22 16:32:54] [dev] [INF] Application started
[2025-10-22 16:32:54] [dev] [WRN] Configuration file is outdated
[2025-10-22 16:32:54] [dev] [ERR] Failed to connect to database
```

### Log Levels

| Level | Method | Purpose |
|-------|--------|---------|
| `DBG` | `.dbg()` | Detailed debugging information |
| `INF` | `.inf()` | General informational messages |
| `WRN` | `.wrn()` | Warning messages (unexpected but not critical) |
| `ERR` | `.err()` | Error messages (operation failed) |

## Log Rotation

GZLogging includes automatic log file management that runs transparently whenever a logging context is created.

### How Rotation Works

1. **Automatic Rotation**: When a logger is created, old log files (not today's active log) are automatically rotated
2. **Rotated Directory**: Old logs are moved to `logs/00rotated/`
3. **Compression**: Old logs can be compressed to `.zip` format (configurable)
4. **Cleanup**: When rotated log count exceeds the limit, oldest files are deleted

### Configuration

Log rotation is configured in `config/gzlogrotate.toml`:

```toml
[rotation]
# Compress old log files when rotating (true/false)
compress = true

# Maximum number of rotated log files to keep per tool
# Both .log and .zip files count toward this limit
rotation_count = 30
```

### Global Defaults

- **compress**: `true` - Old logs are compressed to `.zip` format
- **rotation_count**: `30` - Keep up to 30 rotated logs per tool

### Tool-Specific Overrides

Individual tools can override global settings in `config/tools.toml`:

```toml
[tools.server]
compress = false         # Don't compress server logs
rotation_count = 60      # Keep 60 days of server logs

[tools.deploy]
compress = true          # Compress deploy logs
rotation_count = 90      # Keep 90 days of deploy logs
```

### Directory Structure

```
logs/
├── dev/
│   ├── myapp_20251022.log      # Today's active log
│   └── (old logs are rotated)
│
├── staging/
│   └── (same structure)
│
├── prod/
│   └── (same structure)
│
└── 00rotated/                  # Rotated logs from all environments
    ├── myapp_20251021.zip
    ├── myapp_20251020.zip
    ├── myapp_20251019.zip
    └── ...
```

### Rotation Behavior

#### What gets rotated:
- Log files older than today (not matching current date)
- Files matching pattern: `{tool_name}_YYYYMMDD.log`

#### What doesn't get rotated:
- Today's active log file
- Files already in the `00rotated` directory

#### When rotation happens:
- Automatically when `get_logging_context()` is called
- First logger creation of the day triggers rotation
- Completely transparent to client code

#### Cleanup rules:
- Counts both `.log` and `.zip` files in `00rotated/`
- Active log NOT included in count
- Deletes oldest files when count exceeds `rotation_count`
- Sorting by file modification time (oldest first)

### Examples

#### Default behavior (compress=true, rotation_count=30):
```
Day 1:  myapp_20251021.log created
Day 2:  myapp_20251021.log → 00rotated/myapp_20251021.zip
        myapp_20251022.log created (active)
Day 31: Oldest rotated logs deleted to maintain count=30
```

#### With compression disabled (compress=false):
```
Day 1:  myapp_20251021.log created
Day 2:  myapp_20251021.log → 00rotated/myapp_20251021.log
        myapp_20251022.log created (active)
```

#### Mixed compressed and uncompressed:
- If `compress` setting changes over time, both `.log` and `.zip` files can exist
- Rotation count includes both types
- Oldest files (by modification time) are deleted first, regardless of type

## Usage

### Installation

No installation needed - `gzlogging` is part of the GAZTank utils.

#### Requirements:
- Python 3.11+ (uses built-in `tomllib`)
- Python 3.7-3.10 (requires `tomli` package: `pip install tomli`)

### Basic Example

```python
from gzlogging import get_logging_context

# Create a logging context
ctx = get_logging_context('dev', 'myapp')

# Log messages
ctx.inf("Application started")
ctx.wrn("Configuration file is outdated")
ctx.err("Failed to connect to database")
```

This creates a log file at `logs/dev/myapp_20251022.log` with the entries.

### Log Output Format

```log
[2025-10-22 16:32:54] [dev] [INF] Application started
[2025-10-22 16:32:54] [dev] [WRN] Configuration file is outdated
[2025-10-22 16:32:54] [dev] [ERR] Failed to connect to database
```

### Available Log Methods

```python
ctx.dbg("Detailed debugging information")    # DBG level
ctx.inf("General informational message")     # INF level
ctx.wrn("Warning message")                   # WRN level
ctx.err("Error message")                     # ERR level
```

**Note:** Only these four log levels are supported. The internal `_log()` method is private and should not be used by clients.

### Read-Only Properties

```python
ctx = get_logging_context('dev', 'myapp')

# You can read these properties
print(ctx.environment)  # 'dev'
print(ctx.tool_name)    # 'myapp'

# But you cannot modify them
ctx.environment = 'prod'  # Raises AttributeError
```

### Multiple Tools

```python
# Different tools can log to the same environment
setup_ctx = get_logging_context('dev', 'setup')
deploy_ctx = get_logging_context('dev', 'deploy')

setup_ctx.inf("Setup started")
deploy_ctx.inf("Deployment started")
```

### Multiple Environments

```python
# Same tool can log to different environments
dev_ctx = get_logging_context('dev', 'myapp')
prod_ctx = get_logging_context('prod', 'myapp')

dev_ctx.inf("Testing new feature")
prod_ctx.inf("Production deployment complete")
```

### Console Output

GZLogging supports optional dual output (file + console):

```python
# Console output disabled (default) - logs only to file
ctx = get_logging_context('dev', 'myapp', console=False)

# Console output enabled - logs to both file and console
ctx = get_logging_context('dev', 'myapp', console=True)
ctx.inf("This appears in both log file and console")
```

This is useful for interactive tools where users need immediate feedback.

## Command Line Arguments

gzlogging is a library module and does not provide command-line arguments. It is imported and used by other tools (gzlint, normalise, generate, etc.).

For command-line usage, see the documentation for the tools that use gzlogging.

## Module Structure

```
gzlogging/
├── __init__.py          # Module exports (get_logging_context, LoggingContext)
├── gzlogging.py         # Core implementation
├── test_gzlogging.py    # Test/demonstration script
└── README.md            # This file
```

### Architecture

#### Components

1. **LoggingContext**: Public API for client code
   - Provides logging methods (`.dbg()`, `.inf()`, `.wrn()`, `.err()`)
   - Maintains environment and tool name (read-only)
   - Prevents accidental modification of settings

2. **_LoggingManager**: Internal singleton (private, not exported)
   - Loads and caches `tools.toml` configuration
   - Manages log directories per environment
   - Creates and caches logger instances
   - Handles all internal state

3. **get_logging_context()**: Factory function
   - Main entry point for client code
   - Creates/retrieves LoggingContext instances
   - Parameters: `environment`, `tool_name`, `console=False`

#### Internal State Management

The `_LoggingManager` singleton maintains:
- **_config**: Parsed tools.toml configuration
- **_log_dirs**: Cache of resolved log directories per environment
- **_loggers**: Cache of configured logger instances
- **_project_root**: Resolved project root directory

This design ensures:
- Configuration is loaded only once
- Log directories are created on-demand
- Logger instances are reused efficiently
- Client code doesn't need to know about internal paths

## Features

- **Environment-Aware Routing**: Automatically directs logs to environment-specific directories
- **Configuration-Driven**: Reads `config/tools.toml` for environment definitions
- **Automatic Log Rotation**: Old log files are rotated, compressed, and cleaned up automatically
- **Configurable Retention**: Control how many old logs to keep and whether to compress them
- **Tool-Specific Overrides**: Individual tools can override global rotation settings
- **UTF-8 Support**: All log files use UTF-8 encoding with emoji support (✓ ❌ ⚠️ ℹ️)
- **Daily Log Rotation**: New log file each day (`{tool}_{YYYYMMDD}.log`)
- **Multiple Log Levels**: DBG, INF, WRN, ERR with distinct formatting
- **Dual Output**: Optional console output alongside file logging
- **Read-Only Context**: Immutable environment settings prevent accidental changes
- **Singleton Pattern**: Efficient resource usage (config loaded once, loggers cached)
- **Error Handling**: Clear exceptions for missing environments or configuration
- **Standard Logging**: Built on Python's `logging` module
- **Minimal Dependencies**: Uses stdlib (except `tomli` for Python < 3.11)

## Invocation Points

GZLogging is used by all major GAZTank tools:

### 1. GZLint (HTML/JS/Config Linter)

```python
# utils/gzlint/gzlinter.py
from utils.gzlogging import get_logging_context

log = get_logging_context('dev', 'gzlint', console=True)
log.inf("Linting HTML file: src/content/about.html")
```

**Location:** `utils/gzlint/gzlinter.py`  
**Usage:** Logs file validation activities with dual output

### 2. Normalise (Markdown Normalizer)

```python
# utils/normalise/normaliser.py
from utils.gzlogging import get_logging_context

log = get_logging_context('dev', 'normalise', console=True)
log.inf("Processing file: docs/SETUP_SITE.md")
```

**Location:** `utils/normalise/normaliser.py`  
**Usage:** Logs markdown file processing with dual output

### 3. Generate (Content Generation)

```python
# utils/generate/generator.py
from utils.gzlogging import get_logging_context

log = get_logging_context('dev', 'generate', console=True)
log.inf("Converting markdown to HTML")
```

**Location:** `utils/generate/generator.py`  
**Usage:** Logs content generation pipeline activities

### 4. Setup Site (Site Configuration)

```python
# utils/setup/setup.py
from utils.gzlogging import get_logging_context

log = get_logging_context('dev', 'setup', console=True)
log.inf("Initializing site configuration")
```

**Location:** `utils/setup/setup.py`  
**Usage:** Logs site setup and configuration activities

### 5. Package (Build/Deployment)

**Location:** `utils/package/packager.py` (planned)  
**Usage:** Logs packaging and deployment activities

### Log File Structure

All tools log to:
```
logs/
├── dev/
│   ├── gzlint_20251022.log
│   ├── normalise_20251022.log
│   ├── generate_20251022.log
│   └── setup_20251022.log
├── staging/
│   └── (same structure)
├── prod/
│   └── (same structure)
└── 00rotated/
    ├── gzlint_20251021.zip
    ├── normalise_20251020.zip
    └── (older rotated logs)
```

## Configuration

## Configuration

Log directories are configured in `config/tools.toml`:

```toml
[environments.dev]
log_dir = "dev"
description = "Development environment logs"

[environments.staging]
log_dir = "staging"
description = "Staging environment logs"

[environments.prod]
log_dir = "prod"
description = "Production environment logs"

# Tool-specific rotation overrides (optional)
[tools.server]
compress = false
rotation_count = 60
```

### Configuration Requirements:
- Each environment must have a `log_dir` attribute
- The `log_dir` values are relative to the `logs/` directory
- The `description` attribute is optional
- Missing environments will raise `ValueError` when accessed
- Tool-specific rotation settings override global defaults from `gzlogrotate.toml`

### Log File Locations

Logs are written to:
```
{project_root}/logs/{environment}/{tool_name}_{YYYYMMDD}.log
```

Examples:
- `logs/dev/myapp_20251022.log`
- `logs/staging/deploy_20251022.log`
- `logs/prod/server_20251022.log`

Each day creates a new log file automatically.

## Customisation

GZLogging supports customisation through the configuration file and code extensions:

### Configuration-Based Customisation

Edit `config/tools.toml` to modify log directories:

```toml
[logging]
dev_log_dir = "logs/dev"
staging_log_dir = "logs/staging"
prod_log_dir = "logs/prod"
```

### Code-Based Customisation

#### Custom Log Formatters

To use a custom log format, modify `gzlogging.py`:

```python
# In _LoggingManager._create_logger()
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

#### Additional Log Handlers

Add extra handlers (email, syslog, etc.):

```python
from utils.gzlogging import get_logging_context
import logging
import logging.handlers

# Get standard logging context
ctx = get_logging_context('dev', 'myapp')

# Access the underlying logger (use with caution)
logger = logging.getLogger(f"myapp_dev")

# Add email handler for errors
email_handler = logging.handlers.SMTPHandler(
    mailhost='localhost',
    fromaddr='logger@example.com',
    toaddrs=['admin@example.com'],
    subject='Application Error'
)
email_handler.setLevel(logging.ERROR)
logger.addHandler(email_handler)
```

#### Custom Environment Detection

For environments beyond dev/staging/prod, modify the calling code:

```python
# Detect custom environment
import os
env = os.environ.get('APP_ENV', 'dev')  # Could be 'test', 'qa', etc.

# Use appropriate log directory
if env == 'test':
    ctx = get_logging_context('dev', 'myapp')  # Map test → dev logs
elif env == 'qa':
    ctx = get_logging_context('staging', 'myapp')  # Map qa → staging logs
else:
    ctx = get_logging_context(env, 'myapp')
```

### Extending LoggingContext

For additional functionality, subclass `LoggingContext`:

```python
from utils.gzlogging import get_logging_context

class AuditLoggingContext:
    def __init__(self, env, tool_name, console=False):
        self._ctx = get_logging_context(env, tool_name, console)
        
    def audit(self, action, user, details):
        """Log audit events with structured format"""
        msg = f"AUDIT | User: {user} | Action: {action} | Details: {details}"
        self._ctx.inf(msg)
        
    # Delegate standard methods
    def inf(self, msg): return self._ctx.inf(msg)
    def wrn(self, msg): return self._ctx.wrn(msg)
    def err(self, msg): return self._ctx.err(msg)
    def dbg(self, msg): return self._ctx.dbg(msg)

# Usage
audit_log = AuditLoggingContext('prod', 'admin', console=False)
audit_log.audit('login', 'admin@example.com', 'Successful authentication')
audit_log.audit('config_change', 'admin@example.com', 'Updated timeout setting')
```

## Best Practices

1. **Create context once**: Create the logging context at the start of your application
   ```python
   ctx = get_logging_context('dev', 'myapp')
   # Use ctx throughout your application
   ```

2. **Use descriptive tool names**: Keep them short but meaningful
   ```python
   # Good
   ctx = get_logging_context('dev', 'setup')
   ctx = get_logging_context('dev', 'deploy')
   
   # Less good
   ctx = get_logging_context('dev', 'tool1')
   ctx = get_logging_context('dev', 'script')
   ```

3. **Match environment to actual deployment**: Use the same environment name as your deployment
   ```python
   # In development
   ctx = get_logging_context('dev', 'myapp')
   
   # In staging
   ctx = get_logging_context('staging', 'myapp')
   
   # In production
   ctx = get_logging_context('prod', 'myapp')
   ```

4. **Use appropriate log levels**:
   - `DBG`: Detailed diagnostic information
   - `WRN`: Warning messages (something unexpected but not critical)
   - `INF`: General informational messages
   - `ERR`: Error messages (operation failed but application continues)

5. **Enable console output for interactive tools**: Use `console=True` when users need immediate feedback
   ```python
   # For batch/background processes
   log = get_logging_context('dev', 'myapp', console=False)
   
   # For interactive tools
   log = get_logging_context('dev', 'myapp', console=True)
   ```

## Troubleshooting

### ImportError: No module named 'tomllib' or 'tomli'

**Problem:** Python version doesn't have TOML support

#### Solution:
```bash
# For Python < 3.11
pip install tomli
```

### ValueError: Environment 'xyz' not found in tools.toml

**Problem:** Trying to use an environment that isn't defined in `config/tools.toml`

#### Solution:
1. Check `config/tools.toml` for available environments
2. Add the missing environment to `tools.toml`:
   ```toml
   [xyz]
   log_dir = "logs/xyz"
   description = "XYZ environment logs"
   ```

### FileNotFoundError: tools.toml not found

**Problem:** Cannot find `config/tools.toml`

#### Solution:
1. Ensure you're running from the project root
2. Verify `config/tools.toml` exists
3. Check file permissions

### PermissionError: Cannot create log directory

**Problem:** No write permissions for log directory

#### Solution:
1. Check permissions on `logs/` directory
2. Verify disk space available
3. On Linux/Mac: `chmod 755 logs/`

### Log files not created

**Problem:** Logs not appearing in expected location

#### Solution:
1. Check that `log_dir` in `tools.toml` is correct
2. Verify the tool name is correct (check for typos)
3. Confirm project root is detected correctly
4. Check console for error messages

### Unicode/Emoji not displaying in logs

**Problem:** Garbled characters in log files

#### Solution:
1. Ensure log files are viewed with UTF-8 encoding
2. Use a modern text editor or terminal
3. On Windows: Use Windows Terminal or VS Code terminal

## Development

### Testing

Run the test script to experiment with the logging module:

```bash
# Test with default environment (dev) and tool name (test)
python utils/gzlogging/test_gzlogging.py

# Test with specific environment
python utils/gzlogging/test_gzlogging.py staging

# Test with specific environment and tool name
python utils/gzlogging/test_gzlogging.py prod myapp
```

The test script demonstrates:
- Creating logging contexts
- All log levels (DBG, INF, WRN, ERR)
- Unicode and emoji support
- Multiple contexts (tools and environments)
- Error handling
- Read-only properties
- Console output toggling

### Integration Example

```python
#!/usr/bin/env python3
"""My Application"""

from gzlogging import get_logging_context

def main():
    # Get environment from command line or config
    environment = 'dev'  # or from args/env vars
    
    # Create logging context
    log = get_logging_context(environment, 'myapp', console=True)
    
    log.inf("Application starting")
    
    try:
        # Your application logic
        log.dbg("Initializing components")
        # ...
        log.inf("Components initialized successfully")
        
    except Exception as e:
        log.err(f"Fatal error: {e}")
        return 1
    
    log.inf("Application finished successfully")
    return 0

if __name__ == '__main__':
    exit(main())
```

### Error Handling

```python
try:
    ctx = get_logging_context('invalid_env', 'myapp')
except ValueError as e:
    print(f"Invalid environment: {e}")
except FileNotFoundError as e:
    print(f"Configuration not found: {e}")
except ImportError as e:
    print(f"TOML library not available: {e}")
```

### File Locations

```
GAZTank/
├── config/
│   └── tools.toml              # Environment configuration
│
├── logs/
│   ├── dev/
│   │   ├── gzlint_YYYYMMDD.log
│   │   ├── normalise_YYYYMMDD.log
│   │   ├── generate_YYYYMMDD.log
│   │   └── setup_YYYYMMDD.log
│   ├── staging/
│   │   └── (same structure)
│   ├── prod/
│   │   └── (same structure)
│   └── 00rotated/
│       ├── gzlint_YYYYMMDD.zip
│       ├── normalise_YYYYMMDD.zip
│       └── (older rotated logs)
│
└── utils/
    ├── gzlogging/              # This module
    │   ├── __init__.py
    │   ├── gzlogging.py
    │   ├── test_gzlogging.py
    │   └── README.md
    │
    ├── gzlint/                 # Uses gzlogging
    ├── normalise/              # Uses gzlogging
    ├── generate/               # Uses gzlogging
    └── setup/                  # Uses gzlogging
```

## Future Enhancements

Planned improvements for future versions:

### Short Term (v1.2)
- **Structured Logging**: Add JSON output format for machine parsing
- **Log Level Configuration**: Per-tool log level configuration in `tools.toml`
- **Console Color Coding**: Colored output for different log levels (DEBUG=gray, INFO=white, WARNING=yellow, ERROR=red)

### Medium Term (v1.3)
- **Custom Formatters**: Support for custom log formatters via configuration
- **Log Compression**: Automatic gzip compression of rotated log files
- **Performance Metrics**: Built-in timing decorators for performance logging

### Long Term (v2.0)
- **Remote Logging**: Support for sending logs to remote logging services (syslog, cloud services)
- **Log Filtering**: Configure filters to exclude certain messages or patterns
- **Contextual Logging**: Thread-local context for request tracking (correlation IDs)
- **Async Logging**: Non-blocking log writes for high-performance applications

### Under Consideration
- **Log Aggregation**: Tools for searching across multiple log files
- **Alert Integration**: Hooks for error alerting via email/Slack/webhooks
- **Log Retention Policies**: Automatic cleanup of old logs based on age/size
- **Multi-Process Safety**: Enhanced file locking for concurrent writers

See [GitHub Issues](https://github.com/gazorper/GAZTank/issues) for tracking and discussion.

## Related Documentation

- **[GZLint Module](../gzlint/README.md)** - HTML/JS/Config linter (uses gzlogging)
- **[Normalise Module](../normalise/README.md)** - Markdown normalizer (uses gzlogging)
- **[Generate Module](../generate/README.md)** - Content generation (uses gzlogging)
- **[Setup Module](../setup/README.md)** - Site setup (uses gzlogging)
- **Python logging:** https://docs.python.org/3/library/logging.html
- **TOML specification:** https://toml.io/

## License

GPL-3.0-or-later

## Authors

superguru, gazorper

---

*Last updated: December 19, 2024*  
*GZLogging version: 1.2*
