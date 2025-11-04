# Development Web Server

Environment-aware HTTP server for local development and testing with no-cache headers, multi-threading, and interactive admin console.

**Version:** 1.1  
**Last Updated:** October 22, 2025

## Table of Contents

- [Purpose](#purpose)
- [Build Pipeline](#build-pipeline)
- [Logging](#logging)
- [Usage](#usage)
  - [Command Line](#command-line)
  - [As a Module](#as-a-module)
- [Command Line Arguments](#command-line-arguments)
- [Module Structure](#module-structure)
- [Features](#features)
- [Configuration](#configuration)
- [Invocation Points](#invocation-points)
- [Development](#development)
- [Customisation](#customisation)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)
- [Authors](#authors)

## Purpose

The development server provides a lightweight HTTP server specifically designed for local testing of static websites. It enables rapid development iteration by serving files with no-cache headers, ensuring changes reflect immediately in the browser.

### Key Capabilities

1. **Environment-Based Configuration** - Serves from dev/staging/prod directories
2. **No-Cache Headers** - Changes reflect immediately (no browser cache issues)
3. **Multi-Threaded Handling** - Simultaneous connections supported
4. **Interactive Admin Console** - Type 'quit' to gracefully shutdown
5. **Port Management** - Configurable ports with command-line override
6. **Signal Handling** - Clean shutdown via Ctrl+C
7. **Address Reuse** - Quick restarts without "address already in use" errors

### Design Goals

- **Developer-Friendly**: Minimal setup, immediate feedback on changes
- **Environment-Aware**: Test dev/staging/prod separately without conflicts
- **Robust**: Handles signals, errors, and concurrent requests gracefully
- **Observable**: Tagged request logging shows which environment served each request

## Build Pipeline

The server module operates as a **support tool** within the GAZTank pipeline, providing local testing capabilities between build stages.

### Pipeline Integration

```
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌─────────┐
│  generate   │ --> │ gzlint   │ --> | gzserve  │ --> │ package │
│ (Build)     │     │ (Check)  │     │  (Test)  │     │ (Deploy)│
└─────────────┘     └──────────┘     └──────────┘     └─────────┘
```

### Typical Workflow

1. **Development**: Run `gzserve.cmd -e dev` after generating content
2. **Testing**: Run `gzserve.cmd -e staging` to test pre-deployment content
3. **Validation**: Run `gzserve.cmd -e prod` to validate final production build locally

**Note:** The server does NOT modify any files - it only serves them for testing.

## Logging

The server uses `gzlogging` for environment-aware logging with daily rotation.

### Log Configuration

- **Log Directory**: `logs/{environment}/` (e.g., `logs/dev/`, `logs/staging/`)
- **Log File Pattern**: `server_YYYYMMDD.log` (daily rotation)
- **Log Level**: `INFO` (configurable via gzlogging)

### Log Output Format

Console (with emoji):
```
🌐 Starting server on 0.0.0.0:7190 in dev environment
🌐 Server running at http://localhost:7190
🌐 Type 'quit' to stop the server
🌐 [dev] 127.0.0.1 - GET /index.html - 200
🛑 Shutdown signal received
🛑 Server stopped
```

Log file (clean):
```
2025-10-22 14:23:45 - INFO - Starting server on 0.0.0.0:7190 in dev environment
2025-10-22 14:23:45 - INFO - Server running at http://localhost:7190
2025-10-22 14:23:47 - INFO - [dev] 127.0.0.1 - GET /index.html - 200
2025-10-22 14:24:15 - INFO - Shutdown signal received
2025-10-22 14:24:15 - INFO - Server stopped
```

### Request Logging

Each request is logged with:
- Environment tag (e.g., `[dev]`)
- Client IP address
- HTTP method and path
- Response status code

## Usage

### Command Line

Windows (.cmd):
```powershell
# Development environment (default port from config)
.\scripts\gzserve.cmd -e dev

# Staging with custom port
.\scripts\gzserve.cmd -e staging -p 8080

# Production environment
.\scripts\gzserve.cmd -e prod
```

Linux/Mac (.sh):
```bash
# Development environment (default port from config)
./scripts/gzserve.sh -e dev

# Staging with custom port
./scripts/gzserve.sh -e staging -p 8080

# Production environment
./scripts/gzserve.sh -e prod
```

### As a Module

Python module invocation:
```bash
# Using python -m (recommended)
python -m gzserve -e dev
python -m gzserve -e staging -p 8080

# Direct script execution
python utils/gzserve/server.py -e dev
```

Programmatic usage:
```python
from gzserve.server import start_server

# Start with defaults from config
start_server(environment='dev')

# Override port
start_server(port=8080, environment='staging')

# Production
start_server(environment='prod')
```

### Interactive Control

Once started, the server accepts admin commands via console input:

```
Type 'quit' to stop the server
> quit
🛑 Shutdown signal received
🛑 Server stopped
```

## Command Line Arguments

### Required Arguments

| Argument | Short | Type | Description |
|----------|-------|------|-------------|
| `--environment` | `-e` | str | Target environment: `dev`, `staging`, or `prod` |

### Optional Arguments

| Argument | Short | Type | Default | Description |
|----------|-------|------|---------|-------------|
| `--port` | `-p` | int | (from config) | Override port number for the server |

### Examples

Show help:
```bash
python -m gzserve --help
```

Development environment (port from config):
```bash
python -m gzserve -e dev
```

Custom port:
```bash
python -m gzserve -e staging -p 9000
```

Production environment:
```bash
python -m gzserve -e prod
```

### Argument Behavior

- **Environment Selection (`-e`)**: **REQUIRED** - determines which directory under `publish/` to serve
- **Port Override (`-p`)**: Optional - if omitted, port is loaded from `config/pipeline.toml`
- **Help Display**: Automatically available via argparse (`--help` or `-h`)

**Note:** Unlike other modules, the server does not have `--force` or `--dry-run` arguments as it does not modify files.

## Module Structure

```
gzserve/
├── __init__.py      # Module initialization and exports
├── __main__.py      # Entry point for python -m gzserve
├── server.py        # Core server implementation
└── README.md        # This file
```

### Core Components

| File | Purpose | Exports |
|------|---------|---------|
| `__init__.py` | Package initialization | `start_server`, `NoCacheHTTPRequestHandler`, `ReusableTCPServer`, `DEFAULT_PORT` |
| `__main__.py` | Module entry point | N/A (executable) |
| `server.py` | Server implementation | All server classes and functions |

### Exports

The module exports the following for programmatic use:

```python
from gzserve import (
    start_server,                # Main function to start server
    NoCacheHTTPRequestHandler,   # Custom HTTP request handler
    ReusableTCPServer,           # TCP server with address reuse
    DEFAULT_PORT                 # Default port constant (7190)
)
```

## Features

### 1. Environment-Based Configuration

Each environment (dev/staging/prod) has its own:
- Serve directory under `publish/`
- Default port number
- Log directory
- Configuration in `config/pipeline.toml`

#### Example configuration:
```toml
[environments.dev]
dir = "dev"
httpd_port = 7190
description = "Development environment with verbose logging"

[environments.staging]
dir = "staging"
httpd_port = 7191
description = "Staging environment for pre-production testing"

[environments.prod]
dir = "prod"
httpd_port = 7192
description = "Production-ready build"
```

### 2. No-Cache Headers

The server adds these headers to every response:

```http
Cache-Control: no-store, no-cache, must-revalidate, max-age=0
Pragma: no-cache
Expires: 0
```

**Why?** During development, you want to see changes immediately without browser caching issues.

### 3. Multi-Threaded Request Handling

Built on Python's `socketserver.TCPServer` with threading support, allowing multiple simultaneous connections.

### 4. Interactive Admin Console

The admin console runs in a separate thread and provides:
- Command input while server runs
- Graceful shutdown capability (`quit` command)
- Help text for available commands

### 5. Signal Handling

Properly handles:
- `SIGINT` (Ctrl+C)
- `SIGTERM` (kill command)
- Clean shutdown sequence
- Resource cleanup

### 6. Address Reuse

The `ReusableTCPServer` class enables `SO_REUSEADDR`, allowing quick restarts without "address already in use" errors.

### 7. Environment-Tagged Request Logging

Every HTTP request is logged with the environment name as a prefix:

```
🌐 [dev] 127.0.0.1 - GET / - 200
🌐 [dev] 127.0.0.1 - GET /css/styles.css - 200
🌐 [staging] 127.0.0.1 - GET /index.html - 200
```

**Why?** When running multiple environments simultaneously on different ports, the environment prefix makes it immediately clear which environment each request belongs to.

## Configuration

### Pipeline Configuration

Environments are configured in `config/pipeline.toml`:

```toml
[environments.dev]
dir = "dev"
httpd_port = 7190
description = "Development environment with verbose logging"

[environments.staging]
dir = "staging"
httpd_port = 7191
description = "Staging environment for pre-production testing"

[environments.prod]
dir = "prod"
httpd_port = 7192
description = "Production-ready build"
```

### Directory Structure

Each environment serves from its own directory under `publish/`:

```
publish/
├── dev/          # Development environment (port 7190)
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── content/
├── staging/      # Staging environment (port 7191)
│   └── ...
└── prod/         # Production environment (port 7192)
    └── ...
```

### Port Configuration

The port can be specified in three ways (in order of precedence):

1. **Command line argument** (`-p PORT`)
2. **Environment config** (from `config/pipeline.toml`)
3. **Default** (7190 for dev, 7191 for staging, 7192 for prod)

## Invocation Points

### 1. Shell Scripts (Recommended)

Windows:
```powershell
.\scripts\gzserve.cmd -e dev
```

Linux/Mac:
```bash
./scripts/gzserve.sh -e dev
```

### 2. Python Module

```bash
python -m gzserve -e dev
```

### 3. Programmatic

```python
from gzserve.server import start_server
start_server(environment='dev')
```

### 4. Direct Script

```bash
python utils/gzserve/server.py -e dev
```

## Development

### Server Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    SERVER STARTUP                           │
├─────────────────────────────────────────────────────────────┤
│  [1/5] Parse Arguments (-e ENVIRONMENT, -p PORT)            │
│     └─ Environment is REQUIRED                             │
│     └─ Port is optional (overrides config)                 │
│                                                             │
│  [2/5] Load Pipeline Configuration                          │
│     └─ Read config/pipeline.toml                           │
│     └─ Validate environment exists in config               │
│                                                             │
│  [3/5] Determine Environment Directory                      │
│     └─ Get 'dir' from environment config                   │
│     └─ Resolve to publish/{dir}/ path                      │
│     └─ Verify directory exists                             │
│                                                             │
│  [4/5] Determine Port (config or override)                  │
│     └─ Use -p PORT if specified                            │
│     └─ Otherwise use port from environment config          │
│                                                             │
│  [5/5] Start HTTP Server                                    │
│     └─ Change to environment directory                     │
│     └─ Create ReusableTCPServer with NoCacheHandler        │
│     └─ Register signal handlers (SIGINT, SIGTERM)          │
│     └─ Start admin command listener thread                 │
│     └─ Process HTTP requests with no-cache headers         │
│     └─ Wait for shutdown command or signal                 │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

```
Browser Request
    ↓
[NoCacheHTTPRequestHandler]
    ├─ Add Cache-Control: no-store
    ├─ Add Pragma: no-cache
    ├─ Add Expires: 0
    └─ Serve file from publish/{environment}/ directory
    ↓
Browser Response (no caching)
```

### Shutdown Flow

```
Admin Command ('quit') OR Ctrl+C
    ↓
[Signal Handler]
    ├─ Set shutdown_requested flag
    ├─ Call httpd.shutdown()
    └─ Wait for threads to clean up
    ↓
Server Stopped
```

### Threading Model

- **Main thread:** HTTP server request handling
- **Admin thread:** Command input processing
- **Request threads:** Individual request processing (via TCPServer)

### Graceful Shutdown Sequence

1. Admin command or signal received
2. `shutdown_requested` flag set to `True`
3. `httpd.shutdown()` called
4. Server stops accepting new connections
5. Existing connections complete
6. Admin thread joins (2-second timeout)
7. Server resources released
8. Exit code returned

## Customisation

### Custom Request Handler

```python
from gzserve import NoCacheHTTPRequestHandler, ReusableTCPServer

class MyCustomHandler(NoCacheHTTPRequestHandler):
    def do_GET(self):
        # Custom GET handling
        print(f"Custom handling: {self.path}")
        super().do_GET()

# Use custom handler
httpd = ReusableTCPServer(('', 8080), MyCustomHandler)
httpd.serve_forever()
```

### Custom Port and Directory

```python
from gzserve.server import start_server
from pathlib import Path

# Custom settings
custom_dir = Path('/path/to/gzserve')
start_server(port=9000, environment='dev')
```

### Environment-Specific Behavior

```python
from gzserve.server import start_server

def custom_startup(environment):
    if environment == 'dev':
        print("🧪 Developer mode activated")
    elif environment == 'staging':
        print("📦 Staging mode - testing deployment")
    elif environment == 'prod':
        print("🚀 Production mode - final validation")
    
    start_server(environment=environment)

custom_startup('dev')
```

## Troubleshooting

### Server Won't Start

**Problem:** Port already in use

#### Solution:
```bash
# Find what's using the port (Windows)
netstat -ano | findstr :7190

# Find what's using the port (Linux/Mac)
lsof -i :7190

# Use a different port
.\scripts\gzserve.cmd -e dev -p 8080
```

### Can't Access Server from Browser

**Problem:** Firewall blocking connection

#### Solution:
- Check Windows Defender Firewall
- Allow Python through firewall
- Try `http://127.0.0.1:7190` instead of `localhost`

### Changes Not Reflecting

**Problem:** Browser still caching despite no-cache headers

#### Solution:
- Hard refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
- Clear browser cache
- Use incognito/private browsing mode

### Admin Prompt Not Responding

**Problem:** Terminal input blocked

#### Solution:
- Press `Enter` to ensure prompt is active
- Use `Ctrl+C` for force shutdown
- Close terminal window as last resort

### Environment Directory Not Found

**Problem:** `publish/{environment}/` doesn't exist

#### Solution:
```bash
# Generate content first
.\scripts\generate.cmd -e dev

# Then start server
.\scripts\server.cmd -e dev
```

### Multiple Environments Conflict

**Problem:** Running same environment on different ports

#### Solution:
- Each environment should use a unique port
- Check `config/pipeline.toml` for port assignments
- Stop existing server before starting new one

## Best Practices

### 1. Use Environment-Specific Ports

Keep environments on different ports to test simultaneously:
- Dev: 7190
- Staging: 7191
- Prod: 7192

### 2. Generate Before Serving

Always generate content before starting the server:

```bash
.\scripts\generate.cmd -e dev
.\scripts\gzserve.cmd -e dev
```

### 3. Use Shell Scripts

Prefer launcher scripts over direct Python invocation:

```bash
# Good
.\scripts\gzserve.cmd -e dev

# Also works, but less convenient
python -m gzserve -e dev
```

### 4. Test on Staging Before Production

```bash
# 1. Generate staging
.\scripts\generate.cmd -e staging

# 2. Test on staging
.\scripts\gzserve.cmd -e staging

# 3. If OK, generate production
.\scripts\generate.cmd -e prod

# 4. Validate production build
.\scripts\gzserve.cmd -e prod
```

### 5. Use Graceful Shutdown

Type `quit` instead of Ctrl+C for clean shutdown:

```
admin> quit
🛑 Shutdown signal received
🛑 Server stopped
```

### 6. Monitor Logs

Check environment-specific logs for issues:

```
logs/
├── dev/server_20251022.log
├── staging/server_20251022.log
└── prod/server_20251022.log
```

## Future Enhancements

- [ ] Add `--verbose` / `-v` flag for detailed request logging
- [ ] Add `--quiet` / `-q` flag to suppress console output
- [ ] Add HTTPS support for testing SSL configurations
- [ ] Add WebSocket support for real-time testing
- [ ] Add auto-reload on file changes (watch mode)
- [ ] Add custom MIME type configuration
- [ ] Add request/response header inspection mode
- [ ] Add bandwidth throttling for performance testing
- [ ] Add authentication support for protected environments
- [ ] Add CORS header configuration
- [ ] Add request logging to separate file (separate from gzlogging)
- [ ] Add browser auto-launch option (`--open` flag)

## Related Documentation

- **[gzlogging](../gzlogging/README.md)** - Logging infrastructure used by this module
- **[generate](../generate/README.md)** - Content generation (runs before serving)
- **[package](../package/README.md)** - Build system with minification (uses server for testing)
- **[deploy](../deploy/README.md)** - Deployment to production (after local testing)
- **[FLOW_PIPELINE.md](../FLOW_PIPELINE.md)** - Complete pipeline documentation
- **[00MODULE_MATURITY.md](../00MODULE_MATURITY.md)** - Module maturity tracking
- **[MODULE_README_STRUCTURE.md](../../dev/MODULE_README_STRUCTURE.md)** - README template structure

### Pipeline Context

```
develop → generate → gzlint → [gzserve] → package → deploy
                                   ↑
                             (testing tool)
```

## License

GPL v3.0 or later

## Authors

- superguru
- gazorper

---

**Development Web Server v1.1** | **Last Updated:** October 22, 2025
