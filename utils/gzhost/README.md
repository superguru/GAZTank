# GZHost - FTP Host Server Module

FTP server for simulating remote deployment hosts during local development using pyftpdlib.

**Version:** 1.0.0  
**Last Updated:** October 23, 2025

## Table of Contents

- [Purpose](#purpose)
- [Build Pipeline](#build-pipeline)
- [Logging](#logging)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Custom Port](#custom-port)
  - [Different Environments](#different-environments)
- [Command Line Arguments](#command-line-arguments)
- [Module Structure](#module-structure)
- [Features](#features)
- [Configuration Files](#configuration-files)
  - [pipeline.toml](#pipelinetoml)
  - [ftp_users.toml](#ftp_userstoml)
- [FTP Permissions](#ftp-permissions)
- [Testing FTP Connection](#testing-ftp-connection)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Related Documentation](#related-documentation)
- [License](#license)
- [Authors](#authors)

## Purpose

GZHost provides a local FTP server for testing deployment workflows without needing actual remote servers. It simulates the target environment where the `deploy` module would upload files via FTP.

### Use Cases

- **Test FTP Deployments Locally**: Verify deploy scripts work before using real servers
- **Simulate Remote Hosts**: Test deployment workflows in isolated environments
- **Development Testing**: Validate FTP upload logic without network dependencies
- **Pipeline Integration**: Complete the local dev → staging → prod deployment cycle

### Key Features

- Environment-specific FTP servers (dev/staging/prod)
- Configurable user authentication per environment
- Per-environment permission management
- Serves files from `publish/{environment}/` directories
- Interactive admin command prompt for server control
- Graceful shutdown handling (Ctrl+C, admin commands)
- Integrates with gzconfig for configuration management
- Uses gzlogging for comprehensive logging

## Build Pipeline

GZHost is a tools module that simulates remote deployment targets:

```
GAZTank Build Pipeline:
  ├─ generate → generates content
  ├─ package → packages for deployment
  ├─ gzhost → simulates remote FTP host (THIS MODULE)
  └─ deploy → deploys via FTP to remote host (or gzhost for testing)

Integration:
  1. gzhost -e dev          # Start FTP server
  2. deploy -e dev          # Deploy to local FTP server
  3. Verify deployment worked
```

### Purpose in Pipeline:
- Simulates remote FTP deployment targets
- Enables local testing of deploy module
- Provides isolated test environments
- No need for actual remote servers during development

## Logging

### How GZHost Logs

GZHost uses gzlogging to output to both log file and console:

**Tool name:** `gzhost`

#### What gets logged:
- Server startup and configuration (INFO)
- FTP user authentication (DEBUG)
- Connection events (INFO)
- File operations (INFO)
- Server shutdown (INFO)
- Errors and warnings (ERROR/WARNING)

#### What goes to console:
- Server information banner
- Configuration summary
- FTP URL and connection details
- User instructions
- Shutdown messages

#### What goes to log file:
- All operational information
- Configuration loaded
- User authentication events
- Error messages without emojis
- Success/failure status

### Log File Locations

Based on `config/tools.toml`:
- **dev**: `logs/dev/gzhost_YYYYMMDD_HHMMSS.log`
- **staging**: `logs/staging/gzhost_YYYYMMDD_HHMMSS.log`
- **prod**: `logs/prod/gzhost_YYYYMMDD_HHMMSS.log`

## Usage

### Basic Usage

Start FTP server for dev environment:

```bash
# Windows
.\scripts\gzhost.cmd -e dev

# Linux/Mac
./scripts/gzhost.sh -e dev

# Direct Python
python -m utils.gzhost -e dev
```

#### Output:
```
============================================================
FTP HOST SERVER
============================================================
Environment: dev
Description: Development environment with verbose logging and live reload
Port: 2190
FTP URL: ftp://localhost:2190
Home Directory: D:\Projects\www\GAZTank\publish\dev
FTP User: devup
Permissions: elradfmwMT

Available commands:
  'stop' or 'quit' - Stop the server
  'help' - Show this help
============================================================

Server is running...
Press Ctrl+C to stop the server or type 'quit' in the admin prompt.

[dev] admin> 
```

### Stopping the Server

The server provides multiple ways to shut down gracefully:

#### Interactive Admin Commands:
- Type `quit`, `stop`, `exit`, or `q` at the admin prompt
- Type `help` to see available commands

#### Keyboard Shortcuts:
- Press `Ctrl+C` for immediate shutdown
- Press `Ctrl+D` (Unix) for EOF shutdown

#### Example Session:
```
[dev] admin> help

Available commands:
  stop, quit, exit, q - Stop the server
  help - Show this help

[dev] admin> quit

Shutting down FTP server...
Shutting down FTP server...

============================================================
FTP server stopped
============================================================
```

### Custom Port

Override the configured port:

```bash
.\scripts\gzhost.cmd -e dev -p 3000
```

### Different Environments

Each environment has its own configuration:

```bash
# Development (port 2190)
.\scripts\gzhost.cmd -e dev

# Staging (port 2191)
.\scripts\gzhost.cmd -e staging

# Production (port 2192)
.\scripts\gzhost.cmd -e prod
```

## Command Line Arguments

```
python -m utils.gzhost [OPTIONS]

Required Arguments:
  -e, --environment ENV   Environment to host (dev/staging/prod)

Optional Arguments:
  -p, --port PORT        Port number (overrides config)
  -h, --help             Show help message

Examples:
  python -m utils.gzhost -e dev                 # Host dev on configured port
  python -m utils.gzhost -e staging -p 2190     # Host staging on port 2190
  python -m utils.gzhost -e prod                # Host production environment
```

## Module Structure

```
gzhost/
├── __init__.py          # Module exports (start_ftp_server, main)
├── __main__.py          # Module entry point
├── host.py              # Core FTP server implementation
└── README.md            # This file
```

### Architecture

#### Components

1. **admin_command_listener()**: Interactive admin prompt
   - Runs in separate thread for non-blocking input
   - Accepts commands: `quit`, `stop`, `exit`, `q`, `help`
   - Handles EOF (Ctrl+D) and KeyboardInterrupt (Ctrl+C)
   - Gracefully shuts down server on exit commands
   - Shows environment prefix in prompt (e.g., `[dev] admin>`)

2. **start_ftp_server()**: Core FTP server function
   - Loads pipeline and FTP users configuration
   - Creates pyftpdlib authorizer with user credentials
   - Configures FTP handler and server
   - Starts admin command listener thread
   - Starts server and handles signals
   - Parameters: `port` (optional), `environment` (required)

3. **main()**: Command-line entry point
   - Parses arguments
   - Validates environment
   - Calls `start_ftp_server()`
   - Returns exit code

#### Internal Design

- **pyftpdlib Integration**: Uses DummyAuthorizer and FTPHandler
- **Configuration Loading**: Uses gzconfig for pipeline and FTP users
- **Logging Integration**: Uses gzlogging with tool name 'gzhost'
- **Admin Thread**: Non-daemon thread for interactive command prompt
- **Signal Handling**: Graceful shutdown on Ctrl+C (SIGINT/SIGTERM)
- **Multiple Shutdown Methods**: Admin commands, signals, or EOF
- **Thread Cleanup**: Admin thread joins with timeout on shutdown
- **Home Directory**: Serves files from `publish/{environment}/`
- **User Authentication**: Per-environment credentials from ftp_users.toml

## Configuration Files

### pipeline.toml

Defines environment directories and FTP ports:

```toml
[environments.dev]
dir = "dev"
httpd_port = 7190
ftpd_port = 2190
description = "Development environment with verbose logging and live reload"

[environments.staging]
dir = "staging"
httpd_port = 7191
ftpd_port = 2191
description = "Staging environment for pre-production testing and validation"

[environments.prod]
dir = "prod"
httpd_port = 7192
ftpd_port = 2192
description = "Production-ready build for deployment"
```

#### Attributes:
- `dir`: Directory name under `publish/` for environment
- `httpd_port`: Port for HTTP server (gzserve module)
- `ftpd_port`: Port for FTP server (gzhost module)
- `description`: Human-readable description

### ftp_users.toml

Defines FTP user credentials per environment:

```toml
[environments.dev]
username = "dev_user"
password = "dev_pass"
permissions = "elradfmwMT"

[environments.staging]
username = "staging_user"
password = "staging_pass"
permissions = "elradfmwMT"

[environments.prod]
username = "prod_user"
password = "prod_pass"
permissions = "elr"
```

#### Attributes:
- `username`: FTP login username
- `password`: FTP login password (plain text, local development only)
- `permissions`: Permission string for pyftpdlib (see below)

## FTP Permissions

The `permissions` attribute uses pyftpdlib permission characters:

| Character | Permission | Description |
|-----------|------------|-------------|
| `e` | change directory | CWD, CDUP commands |
| `l` | list files | LIST, NLST, STAT, MLSD, MLST, SIZE |
| `r` | retrieve file | RETR command |
| `a` | append data | APPE command |
| `d` | delete | DELE, RMD commands |
| `f` | rename | RNFR, RNTO commands |
| `m` | create directory | MKD command |
| `w` | store file | STOR, STOU commands |
| `M` | change permissions | SITE CHMOD command |
| `T` | change modification time | SITE MFMT command |

### Common Permission Sets

- **Read-only**: `"elr"` - Can browse and download only
- **Full access**: `"elradfmwMT"` - Can do everything
- **Read/Write**: `"elrw"` - Can browse, download, and upload
- **Upload only**: `"elw"` - Can only upload files

### Example Use Cases

```toml
# Development: Full access for testing
[environments.dev]
permissions = "elradfmwMT"

# Staging: Full access for deployment testing
[environments.staging]
permissions = "elradfmwMT"

# Production: Read-only for verification
[environments.prod]
permissions = "elr"
```

## Testing FTP Connection

### Using Command-Line FTP Client

#### Windows:
```bash
ftp localhost 2190
# Enter username: dev_user
# Enter password: dev_pass
ls
cd content
get index.html
put test.txt
quit
```

#### Linux/Mac:
```bash
ftp localhost 2190
# Enter username: dev_user
# Enter password: dev_pass
ls
cd content
get index.html
put test.txt
quit
```

### Using FileZilla

1. Open FileZilla
2. Host: `localhost`
3. Port: `2190` (or configured port)
4. Protocol: `FTP`
5. Username: `dev_user` (from config)
6. Password: `dev_pass` (from config)
7. Click "Quickconnect"

### Using Python ftplib

```python
from ftplib import FTP

# Connect to local FTP server
ftp = FTP()
ftp.connect('localhost', 2190)
ftp.login('dev_user', 'dev_pass')

# List files
print(ftp.nlst())

# Download file
with open('local_file.html', 'wb') as f:
    ftp.retrbinary('RETR index.html', f.write)

# Upload file
with open('local_file.txt', 'rb') as f:
    ftp.storbinary('STOR uploaded.txt', f)

# Disconnect
ftp.quit()
```

## Troubleshooting

### Server Won't Stop with Ctrl+C

#### Symptoms:
- Pressing Ctrl+C doesn't stop the server
- Server hangs on shutdown

#### Solutions:
1. Use admin command: Type `quit` or `stop` at the `admin>` prompt
2. Press Ctrl+C multiple times
3. Press Ctrl+D (Unix) or Ctrl+Z (Windows) for EOF signal
4. As last resort, kill process: Find PID with `netstat -ano | findstr :<port>` and use `taskkill /PID <pid> /F`

**Note:** The admin command prompt provides the most reliable shutdown method.

### Admin Prompt Not Responding

#### Symptoms:
- Cannot type commands at admin prompt
- Prompt appears frozen

#### Solutions:
1. Try pressing Enter to get a fresh prompt
2. Use Ctrl+C to interrupt and trigger shutdown
3. Check if server is processing FTP requests (may block briefly)
4. Restart terminal if completely unresponsive

### Port Already in Use

#### Error:
```
✗ Error: Port 2190 is already in use
  Try a different port: python -m utils.gzhost -e dev -p <port>
```

#### Solutions:
1. Check if another gzhost instance is running
2. Use a different port: `.\scripts\gzhost.cmd -e dev -p 3000`
3. Change default port in `config/pipeline.toml`

### Environment Directory Not Found

#### Error:
```
✗ Error: Environment directory not found: D:\Projects\www\GAZTank\publish\dev
Please create the directory or run a build for environment 'dev'
```

#### Solutions:
1. Create the directory: `mkdir publish\dev`
2. Run package module: `.\scripts\package.cmd -e dev`
3. Verify `pipeline.toml` has correct `dir` attribute

### Cannot Connect to FTP Server

#### Symptoms:
- FTP client times out
- Connection refused errors

#### Solutions:
1. Verify server is running (check console output)
2. Check firewall allows connections to port
3. Verify correct port number
4. Try `localhost` instead of `127.0.0.1` or vice versa

### Authentication Failed

#### Symptoms:
- "530 Authentication failed" error
- Login rejected

#### Solutions:
1. Verify username/password in `config/ftp_users.toml`
2. Check correct environment configuration loaded
3. Ensure no typos in credentials

### Permission Denied

#### Symptoms:
- "550 Permission denied" errors
- Cannot upload/download files

#### Solutions:
1. Check `permissions` attribute in `ftp_users.toml`
2. For upload: ensure permissions include `w` (write)
3. For download: ensure permissions include `r` (read)
4. For delete: ensure permissions include `d` (delete)

### pyftpdlib Not Installed

#### Error:
```
✗ Error: pyftpdlib is not installed
  Install it with: pip install pyftpdlib
```

#### Solution:
```bash
pip install pyftpdlib
```

## Security Considerations

### Local Development Only

**⚠️ IMPORTANT**: This module is designed for **local development only**.

#### Security Limitations:
- Passwords stored in plain text
- No encryption (FTP, not FTPS/SFTP)
- No SSL/TLS support
- Binds to all interfaces (0.0.0.0)
- Minimal authentication

### Safe Usage

✅ **DO:**
- Use only on local development machines
- Use only for testing deployment workflows
- Keep `ftp_users.toml` out of version control if using sensitive data
- Use different credentials per environment

❌ **DO NOT:**
- Expose to internet
- Use in production environments
- Store real credentials in configuration
- Use for actual remote deployments

### Production Deployments

For production deployments:
- Use proper SFTP/FTPS with encryption
- Use SSH keys instead of passwords
- Use proper authentication services
- Follow security best practices
- Use the `deploy` module with secure configuration

## Related Documentation

- [gzserve module](../gzserve/README.md) - HTTP development server
- [deploy module](../deploy/README.md) - FTP deployment (future)
- [package module](../package/README.md) - Package site for deployment
- [gzconfig](../gzconfig/README.md) - Configuration management
- [gzlogging](../gzlogging/README.md) - Logging infrastructure
- [pipeline.toml](../../config/pipeline.toml) - Environment configuration
- [ftp_users.toml](../../config/ftp_users.toml) - FTP user credentials

## License

GPL v3.0 or later

## Authors

superguru, gazorper
