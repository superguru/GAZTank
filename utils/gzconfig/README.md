# GZConfig - Configuration Management Module

Clean, abstracted access to project configuration files with no implementation details exposed to users. Provides a simple Python API to access pipeline configuration without needing to know about file locations, TOML formats, or internal structure.

**Version:** 1.0.0  
**Last Updated:** October 23, 2025

## Table of Contents

- [Purpose](#purpose)
- [Build Pipeline](#build-pipeline)
- [Logging](#logging)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Access All Environments](#access-all-environments)
  - [Real-World Example](#real-world-example)
- [Command Line Arguments](#command-line-arguments)
- [Module Structure](#module-structure)
- [Features](#features)
- [API Reference](#api-reference)
  - [Functions](#functions)
  - [Classes](#classes)
- [Configuration File](#configuration-file)
- [Error Handling](#error-handling)
- [Migration Guide](#migration-guide)
- [Development](#development)
  - [Testing](#testing)
  - [Integration](#integration)
- [Customisation](#customisation)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)
- [Authors](#authors)

## Purpose

GZConfig provides centralized configuration management for all GAZTank modules and tools. It abstracts away the complexity of reading TOML configuration files, finding project roots, and navigating configuration structures.

### Key Design Goals

- **Clean Abstraction**: Hide all implementation details (file paths, TOML format, project structure)
- **Simple API**: Single function to access configuration
- **Type Safety**: Full type hints with dataclasses for IDE support
- **Automatic Caching**: Configuration loaded once, reused efficiently
- **Property-Based Access**: Clean, pythonic attribute access (`.port`, `.dir`, `.directory_path`)
- **Helpful Errors**: Clear messages when environments are missing or config is invalid
- **No Dependencies**: Uses standard library (tomllib for Python 3.11+, tomli fallback for older versions)
- **Library Pattern**: Similar design philosophy to gzlogging - import and use, no CLI interface

### Currently Supported

- **Pipeline Configuration** (`pipeline.toml`) - Environment definitions and build configuration
  - Environment names (dev, staging, prod)
  - Directory paths for build artifacts
  - HTTP server ports (httpd_port) for development servers
  - FTP server ports (ftpd_port) for FTP simulation servers
  - Human-readable descriptions
- **Deploy Configuration** (`deploy.toml`) - FTP/FTPS deployment settings
  - Server connection details (host, port, credentials)
  - FTPS security settings
  - Upload subdirectory formatting with timestamps
  - Target directory paths
- **Package Configuration** (`package.toml`) - Website packaging settings
  - Maximum backup retention count
  - Directory exclusion rules (e.g., components/, pages/)
  - File pattern exclusions (e.g., *.psd, .DS_Store, Thumbs.db)
  - Glob pattern support for flexible filtering
- **Generate Configuration** (`generate.toml`) - Content generation rules
- **Tools Configuration** (`tools.toml`) - Tool-specific settings (logging, etc.)
- **FTP Users Configuration** (`ftp_users.toml`) - FTP server user accounts
  - Automatic file change detection and hot-reload
  - Timestamp tracking for zero-overhead caching

### Future Support Planned

- Site configuration (`site.toml`) - Site metadata, URLs, SEO settings
- Unified configuration API across all config files

## Build Pipeline

GZConfig is a foundational library module used by all GAZTank tools that need configuration:

```
GAZTank Build Pipeline:
  ├─ gzserve → uses gzconfig (environment directories, ports)
  ├─ setup → uses gzconfig (environment directories)
  ├─ sitemap → uses gzconfig (environment directories)
  ├─ package → uses gzconfig (environment directories, exclusions)
  ├─ generate → will use gzconfig (environment directories)
  └─ deploy → will use gzconfig (environment directories)

All tools read from:
  config/pipeline.toml
  config/package.toml
```

### Purpose in Pipeline:
- Provides consistent configuration access across all tools
- Eliminates duplicate TOML-reading code (~150+ lines removed from existing modules)
- Centralizes configuration logic for easier maintenance
- Enables tools to focus on their core functionality
- Abstracts away project structure details

## Logging

### How GZConfig Handles Logging

GZConfig is a low-level library module that intentionally does **not** use gzlogging to avoid circular dependencies and keep the module simple:

#### What gets logged:
- Configuration errors → `FileNotFoundError`, `ValueError`, `ImportError` exceptions
- Missing environments → `ValueError` with helpful error messages
- Invalid TOML → `ValueError` with parse error details

#### What doesn't get logged:
- Successful configuration loading (silent)
- Cache hits (silent)
- Normal operations (silent)

#### Design Decision:
- GZConfig raises exceptions for errors rather than logging them
- Calling code decides how to handle/log errors
- Keeps gzconfig independent and reusable
- Avoids logging infrastructure in a configuration library

This design keeps gzconfig focused, lightweight, and usable by any module (including gzlogging itself if needed in the future).

## Usage

### Basic Usage

```python
from gzconfig import get_pipeline_config

# Get configuration for a specific environment
dev_env = get_pipeline_config('dev')
print(dev_env.port)           # 7190
print(dev_env.dir)            # 'dev'
print(dev_env.name)           # 'dev'
print(dev_env.directory_path) # Path('D:/Projects/www/GAZTank/publish/dev')
print(dev_env.description)    # 'Development environment with verbose logging...'
```

#### Result:
```
7190
dev
dev
D:\Projects\www\GAZTank\publish\dev
Development environment with verbose logging and live reload
```

### Access All Environments

```python
from gzconfig import get_pipeline_config

# Get full configuration object
config = get_pipeline_config()

# List all environment names
print(config.environment_names)  # ['dev', 'staging', 'prod']

# Access specific environment
staging = config.get_environment('staging')
print(staging.port)  # 7191

# Iterate through all environments
for env_name, env in config.environments.items():
    print(f"{env_name}: port {env.port}, path {env.directory_path}")
```

#### Result:
```
['dev', 'staging', 'prod']
7191
dev: port 7190, path D:\Projects\www\GAZTank\publish\dev
staging: port 7191, path D:\Projects\www\GAZTank\publish\staging
prod: port 7192, path D:\Projects\www\GAZTank\publish\prod
```

### Real-World Example

```python
from gzconfig import get_pipeline_config
from http.server import HTTPServer
import os

def start_server(environment: str):
    """Start development server for specified environment."""
    
    # Get environment configuration - simple, clean, one line
    env = get_pipeline_config(environment)
    
    # Use configuration properties
    print(f"Starting {env.description}")
    print(f"Serving from: {env.directory_path}")
    print(f"Port: {env.port}")
    
    # Start server using the configuration
    os.chdir(env.directory_path)
    server = HTTPServer(('localhost', env.port), Handler)
    server.serve_forever()
```

### Deploy Configuration Example

```python
from gzconfig import get_deploy_config

# Get FTP deployment configuration
deploy = get_deploy_config()

print(f"FTP Server: {deploy.server}:{deploy.port}")
print(f"Use FTPS: {deploy.use_ftps}")
print(f"Target Directory: {deploy.target_dir}")
print(f"Subdir Format: {deploy.upload_subdir_fmt}")
print(f"Username: {deploy.username}")
# Password is masked in repr for security
print(deploy)  # DeployConfig(server='ftp.example.com', ..., password='***', ...)
```

#### Result:
```
FTP Server: ftp.example.com:21
Use FTPS: True
Target Directory: /public_html
Subdir Format: %Y%m%d_%H%M%S_%j
Username: your-username
DeployConfig(server='ftp.example.com', port=21, use_ftps=True, username='your-username', password='***', ...)
```

## Command Line Arguments

GZConfig is a library module and does not provide command-line arguments. It is imported and used by other tools (gzserve, setup, sitemap, etc.).

For command-line usage, see the documentation for the tools that use gzconfig:
- [gzserve](../gzserve/README.md) - Development server
- [setup](../setup/README.md) - Site setup wizard
- [sitemap](../sitemap/README.md) - Sitemap generator

## Module Structure

```
gzconfig/
├── __init__.py          # Module exports
├── pipeline.py          # Pipeline configuration (environments, ports, directories)
├── deploy.py            # Deploy configuration (FTP/FTPS settings)
├── package.py           # Package configuration (exclusions, backups)
├── generate.py          # Generate configuration (content generation rules)
├── tools.py             # Tools configuration (tool-specific settings)
├── ftp_users.py         # FTP users configuration (FTP server accounts)
├── example.py           # Usage examples
└── README.md            # This file
```

### Architecture

#### Components

1. **PipelineEnvironment** (dataclass): Represents a single environment
   - Properties: `name`, `dir`, `httpd_port`, `ftpd_port`, `description`, `directory_path`
   - Immutable once created
   - Provides computed property `directory_path` (full path to publish/{dir}/)

2. **PipelineConfig** (class): Full configuration manager
   - Properties: `environments`, `environment_names`
   - Method: `get_environment(name)` - retrieve specific environment
   - Validates environment existence
   - Manages collection of PipelineEnvironment instances

3. **get_pipeline_config()**: Main entry point
   - Parameters: `environment` (optional str), `reload` (optional bool)
   - Returns: `PipelineConfig` or `PipelineEnvironment` depending on parameters
   - Implements caching for performance
   - Raises helpful exceptions for errors

#### Internal Design

- **Automatic project root detection**: Searches upward for `config/` directory
- **Configuration caching**: Loads `pipeline.toml` once, reuses for subsequent calls
- **TOML library abstraction**: Handles both tomllib (Python 3.11+) and tomli (older versions)
- **Lazy loading**: Only loads configuration when first accessed
- **Thread-safe**: Uses module-level cache (singleton pattern)

## Features

- **Clean API**: One function to access all configuration
- **Type Safety**: Full type hints with dataclasses (PipelineEnvironment, PipelineConfig)
- **Property-Based Access**: `env.httpd_port`, `env.ftpd_port`, `env.dir`, `env.directory_path`, `env.description`
- **Automatic Caching**: Configuration loaded once, reused efficiently
- **No File Paths Exposed**: Users don't need to know where `pipeline.toml` is located
- **No Format Details Exposed**: Users don't need to know about TOML
- **Helpful Error Messages**: Clear exceptions for missing environments or configuration
- **Automatic Project Root Detection**: Finds project root by searching for `config/` directory
- **Computed Paths**: `directory_path` property returns full path to environment directory
- **Environment Validation**: Raises `ValueError` if environment doesn't exist
- **Configuration Validation**: Checks for required structure and provides clear errors
- **Optional Reload**: Force reload configuration with `reload=True` parameter
- **Multiple Access Patterns**: Get all environments or specific environment
- **Standard Library**: Minimal dependencies (only TOML library)
- **Cross-Platform**: Works on Windows, Linux, macOS
- **Automatic Hot-Reload**: FTP users configuration automatically reloads when file changes (timestamp tracking)
- **Zero-Overhead Caching**: File change detection using `st_mtime` with no performance impact

## API Reference

### Functions

#### `get_pipeline_config(environment=None, reload=False)`

Main entry point for accessing pipeline configuration.

##### Parameters:
- `environment` (str, optional): Environment name. If provided, returns `PipelineEnvironment` for that environment. If None, returns full `PipelineConfig` object.
- `reload` (bool): If True, force reload configuration from file. Default: False (use cached).

##### Returns:
- `PipelineConfig` if `environment` is None
- `PipelineEnvironment` if `environment` is specified

##### Raises:
- `ValueError`: If environment is specified but not defined in pipeline.toml
- `FileNotFoundError`: If `pipeline.toml` is not found in project
- `ImportError`: If TOML library is not available (Python < 3.11 without tomli)

##### Examples:
```python
# Get full configuration
config = get_pipeline_config()
print(config.environment_names)  # ['dev', 'staging', 'prod']

# Get specific environment
dev = get_pipeline_config('dev')
print(dev.httpd_port)  # 7190
print(dev.ftpd_port)   # 2190

# Force reload from file (useful if config changed)
config = get_pipeline_config(reload=True)
```

### Classes

#### `PipelineEnvironment`

Represents a single environment configuration. Immutable dataclass.

##### Properties:
- `name` (str): Environment name (e.g., 'dev', 'staging', 'prod')
- `dir` (str): Directory name under `publish/` for build artifacts
- `httpd_port` (int): Default port for HTTP development server
- `ftpd_port` (int): Default port for FTP simulation server
- `description` (str): Human-readable description of environment
- `directory_path` (Path): Full path to environment directory (`{project_root}/publish/{dir}/`)

##### Example:
```python
env = get_pipeline_config('dev')
print(env.name)           # 'dev'
print(env.dir)            # 'dev'
print(env.httpd_port)     # 7190
print(env.ftpd_port)      # 2190
print(env.description)    # 'Development environment...'
print(env.directory_path) # Path('D:/Projects/www/GAZTank/publish/dev')

# Check if directory exists
if not env.directory_path.exists():
    print(f"Environment directory not found: {env.directory_path}")
```

#### `PipelineConfig`

Full pipeline configuration manager. Contains all environments.

##### Properties:
- `environments` (dict[str, PipelineEnvironment]): Dictionary mapping environment names to PipelineEnvironment objects
- `environment_names` (list[str]): List of available environment names

##### Methods:
- `get_environment(name: str) -> PipelineEnvironment`: Get specific environment configuration. Raises `ValueError` if environment not found.

##### Example:
```python
config = get_pipeline_config()

# List all environments
print(config.environment_names)  # ['dev', 'staging', 'prod']

# Get specific environment
dev = config.get_environment('dev')
print(dev.httpd_port)  # 7190

# Iterate through all environments
for env_name, env in config.environments.items():
    print(f"{env_name}: httpd_port {env.httpd_port}, ftpd_port {env.ftpd_port}")
```

#### `get_deploy_config()`

Load and access FTP/FTPS deployment configuration.

##### Parameters:
- None

##### Returns:
- `DeployConfig` object with deployment settings

##### Raises:
- `FileNotFoundError`: If `deploy.toml` doesn't exist (provides helpful message to copy from example)
- `ValueError`: If required fields are missing or validation fails

##### Examples:
```python
# Get deployment configuration
deploy = get_deploy_config()

# Access FTP settings
print(f"Server: {deploy.server}:{deploy.port}")
print(f"FTPS Enabled: {deploy.use_ftps}")
print(f"Username: {deploy.username}")
print(f"Target: {deploy.target_dir}")

# Subdirectory settings
print(f"Format: {deploy.upload_subdir_fmt}")
print(f"Postfix Length: {deploy.upload_subdir_postfix_len}")

# Password is masked in repr
print(deploy)  # password='***'
```

#### `DeployConfig`

Deployment configuration from deploy.toml. Immutable dataclass.

##### Properties:
- `server` (str): FTP server hostname or IP address
- `port` (int): FTP server port (default: 21)
- `username` (str): FTP username for authentication
- `password` (str): FTP password for authentication
- `target_dir` (str): Target directory on FTP server (e.g., '/public_html')
- `use_ftps` (bool): Use FTPS (FTP over TLS) for secure connection (default: True)
- `upload_subdir_fmt` (str): Python strftime format for upload subdirectory (default: '%Y%m%d_%H%M%S_%j')
- `upload_subdir_postfix_len` (int): Length of random alphanumeric postfix (1-10, default: 5)

##### Validation:
- All required fields must be non-empty (server, username, password, target_dir)
- Port must be between 1 and 65535
- upload_subdir_postfix_len must be between 1 and 10
- Password is masked in `__repr__` for security

##### Example:
```python
deploy = get_deploy_config()

# Connection details
print(f"Connecting to {deploy.server}:{deploy.port}")
print(f"Using {'FTPS (secure)' if deploy.use_ftps else 'FTP (insecure)'}")

# Upload settings
from datetime import datetime
subdir = datetime.now().strftime(deploy.upload_subdir_fmt)
print(f"Upload subdirectory: {subdir}")  # e.g., 20251023_143052_296

# Security note: password is available but masked in repr
ftp_password = deploy.password  # Actual password value
print(deploy)  # DeployConfig(..., password='***', ...)
```

#### `get_ftp_users_config()`

Load and access FTP server user configuration.

##### Parameters:
- `environment` (str, optional): Environment name ('dev', 'staging', 'prod'). If provided, returns user config for that environment. If None, returns all users.
- `reload` (bool): If True, force reload configuration from file. Default: False (use cached).

##### Returns:
- `FTPUsersConfig` if `environment` is None
- `FTPUserEnvironment` if `environment` is specified

##### Raises:
- `FileNotFoundError`: If `ftp_users.toml` doesn't exist
- `ValueError`: If environment is specified but not defined or required fields are missing

##### Automatic Reload on File Changes:
- Tracks file modification timestamp (`st_mtime`)
- Automatically reloads configuration when `ftp_users.toml` changes
- Zero performance impact when file hasn't changed
- Useful for hot-reloading during development

##### Examples:
```python
# Get FTP user config for specific environment
dev_user = get_ftp_users_config('dev')
print(f"Username: {dev_user.username}")
print(f"Password: {dev_user.password}")
print(f"Home Directory: {dev_user.home_directory}")
print(f"Permissions: {dev_user.permissions}")

# Get all FTP users
config = get_ftp_users_config()
for env_name in config.environment_names:
    user = config.get_environment(env_name)
    print(f"{env_name}: {user.username}")

# Configuration automatically reloads when ftp_users.toml changes
user1 = get_ftp_users_config('dev')
# ... edit ftp_users.toml ...
user2 = get_ftp_users_config('dev')  # Automatically reloaded if file changed
```

#### `get_package_config()`

Load and access package module configuration.

##### Parameters:
- None

##### Returns:
- `PackageConfig` object with packaging settings

##### Raises:
- `FileNotFoundError`: If `package.toml` doesn't exist
- `ValueError`: If required fields are missing or validation fails

##### Note:
Configuration is read fresh each time (no caching).

##### Examples:
```python
# Get package configuration
config = get_package_config()

# Access backup settings
print(f"Max backups: {config.max_backups}")

# Access exclusion rules
print(f"Excluded directories: {config.exclusions.directories}")
print(f"Excluded file patterns: {config.exclusions.files}")

# Use in packaging logic
for directory in config.exclusions.directories:
    print(f"Skipping directory: {directory}")

for pattern in config.exclusions.files:
    if fnmatch.fnmatch(filename, pattern):
        print(f"Excluding file: {filename} (matches {pattern})")
```

#### `FTPUserEnvironment`

FTP user configuration for a specific environment. Immutable dataclass.

##### Properties:
- `username` (str): FTP username
- `password` (str): FTP password (masked in `__repr__` for security)
- `home_directory` (Path): FTP user's home directory path
- `permissions` (str): FTP permissions string (e.g., 'elradfmwMT')

##### Validation:
- All fields must be non-empty
- Password is masked in `__repr__` for security

##### Example:
```python
user = get_ftp_users_config('dev')
print(f"Username: {user.username}")        # devup
print(f"Home: {user.home_directory}")      # Path('D:/Projects/www/GAZTank/publish/dev')
print(f"Permissions: {user.permissions}")  # elradfmwMT
# Password is masked in repr for security
print(user)  # FTPUserEnvironment(username='devup', password='***', ...)
```

#### `FTPUsersConfig`

Full FTP users configuration manager. Contains all environment users.

##### Properties:
- `environments` (dict[str, FTPUserEnvironment]): Dictionary mapping environment names to user configs
- `environment_names` (list[str]): List of available environment names

##### Methods:
- `get_environment(name: str) -> FTPUserEnvironment`: Get specific user configuration. Raises `ValueError` if environment not found.

##### Example:
```python
config = get_ftp_users_config()

# List all users
print(config.environment_names)  # ['dev', 'staging', 'prod']

# Get specific user
dev_user = config.get_environment('dev')
print(dev_user.username)  # devup

# Iterate through all users
for env_name, user in config.environments.items():
    print(f"{env_name}: {user.username} -> {user.home_directory}")
```

#### `PackageConfig`

Package module configuration from package.toml. Immutable dataclass.

##### Properties:
- `max_backups` (int): Maximum number of package backups to retain (default: 4, minimum: 1)
- `exclusions` (PackageExclusions): File and directory exclusion rules

##### Validation:
- `max_backups` must be a positive integer (>= 1)

##### Example:
```python
config = get_package_config()

print(f"Maximum backups: {config.max_backups}")
print(f"Excluded directories: {config.exclusions.directories}")
print(f"Excluded file patterns: {config.exclusions.files}")

# Use in rotation logic
if backup_count > config.max_backups:
    remove_old_backups()
```

#### `PackageExclusions`

Package exclusion rules. Immutable dataclass.

##### Properties:
- `directories` (list[str]): List of directory names to exclude from packaging (e.g., ['components', 'pages'])
- `files` (list[str]): List of file glob patterns to exclude (e.g., ['*.psd', '*.pdn', '.DS_Store'])

##### Pattern Matching:
- Uses Python `fnmatch` module for glob pattern matching
- Supports wildcards: `*` (any characters), `?` (single character)
- Patterns are case-sensitive on Unix-like systems, case-insensitive on Windows

##### Example:
```python
import fnmatch
from pathlib import Path

config = get_package_config()

# Check if directory should be excluded
def is_excluded_directory(dir_name: str) -> bool:
    return dir_name in config.exclusions.directories

# Check if file should be excluded
def is_excluded_file(file_path: Path) -> bool:
    filename = file_path.name
    return any(fnmatch.fnmatch(filename, pattern) 
               for pattern in config.exclusions.files)

# Usage
if is_excluded_directory("components"):
    print("Skipping components/ directory")

if is_excluded_file(Path("design.psd")):
    print("Excluding design.psd (matches *.psd)")
```

## Configuration Files

### Pipeline Configuration (`config/pipeline.toml`)

GZConfig finds this file by:
1. Starting from the module file location
2. Searching upward through parent directories
3. Looking for a directory containing `config/pipeline.toml`
4. Using that directory as the project root

### Structure

```toml
# Build Pipeline Configuration
# Each environment has:
# - dir: Directory name under publish/ where build artifacts are stored
# - httpd_port: Default port for the HTTP development server
# - ftpd_port: Default port for the FTP simulation server
# - description: Human-readable description of the environment

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

### Adding New Environments

1. Add a new `[environments.NAME]` section to `pipeline.toml`
2. Specify required fields: `dir`, `httpd_port`, `ftpd_port`, `description`
3. Configuration is automatically reloaded on next use (or use `reload=True`)

#### Example:
```toml
[environments.test]
dir = "test"
httpd_port = 7193
ftpd_port = 2193
description = "Automated testing environment"
```

Then use it:
```python
test_env = get_pipeline_config('test')
print(test_env.httpd_port)  # 7193
print(test_env.ftpd_port)   # 2193
```

**Note:** Users of gzconfig don't need to know this structure - it's all abstracted away through the API.

### Deploy Configuration (`config/deploy.toml`)

**Location:** `config/deploy.toml` (automatically located from project root)

**Note:** `deploy.toml` is in `.gitignore` and should not be committed (contains credentials).

#### Structure:
```toml
# Deploy Configuration
# Copy from config/deploy.example.toml and fill in your FTP details

[ftp]
server = "ftp.example.com"
port = 21
use_ftps = true
username = "your-username"
password = "your-password"
target_dir = "/public_html"

# Upload subdirectory configuration
# Creates timestamped subdirectories for each upload
upload_subdir_fmt = "%Y%m%d_%H%M%S_%j"  # Python strftime format
upload_subdir_postfix_len = 5           # Random alphanumeric postfix (1-10)
```

#### Setup:
1. Copy `config/deploy.example.toml` to `config/deploy.toml`
2. Fill in your FTP server details
3. Never commit `deploy.toml` (it's in `.gitignore`)

#### Field Descriptions:
- `server`: FTP server hostname or IP address
- `port`: FTP server port (default: 21, common: 21 for FTP/FTPS, 990 for implicit FTPS)
- `use_ftps`: Enable FTPS (FTP over TLS) for secure connections (default: true, recommended)
- `username`: FTP username for authentication
- `password`: FTP password (masked in logs and repr)
- `target_dir`: Target directory on FTP server (e.g., '/public_html', '/htdocs')
- `upload_subdir_fmt`: strftime format for timestamped subdirectories (empty "" to disable)
- `upload_subdir_postfix_len`: Length of random alphanumeric suffix (1-10)

#### Example Subdirectory Names:
```python
# With upload_subdir_fmt = "%Y%m%d_%H%M%S_%j" and postfix_len = 5:
# .20251023_143052_296_a3f9k
# .20251023_150315_296_x7b2m

# With upload_subdir_fmt = "%Y-%m-%d":
# .2025-10-23_k3p9a
```

**Note:** Subdirectory names are prefixed with a dot (.) to distinguish deployment uploads from other content.

### Package Configuration (`config/package.toml`)

**Location:** `config/package.toml` (automatically located from project root)

**Purpose:** Defines packaging behavior, exclusion rules, and backup retention for the package module.

#### Structure:
```toml
# Package Configuration
# Controls website packaging behavior and exclusions

[package]
# Maximum number of package backups to retain
max_backups = 4

[exclusions]
# Directories to exclude from packaging (by name)
directories = [
    "components",  # Source component files (not needed in package)
    "pages"        # Base page templates (not needed in package)
]

# File patterns to exclude (glob patterns)
files = [
    "*.psd",       # Photoshop files
    "*.pdn",       # Paint.NET files
    ".DS_Store",   # macOS metadata
    "Thumbs.db",   # Windows thumbnails
    "desktop.ini", # Windows folder config
    "*.tmp",       # Temporary files
    "*.bak"        # Backup files
]
```

#### Field Descriptions:
- `max_backups` (int): Maximum number of backup packages to keep. Older backups are automatically deleted. Default: 4, Minimum: 1
- `exclusions.directories` (list[str]): Directory names to exclude from packaging (exact match)
- `exclusions.files` (list[str]): File patterns to exclude using glob syntax (supports `*`, `?` wildcards)

#### Glob Pattern Examples:
```python
# Pattern matching examples
"*.psd"        # Matches: design.psd, photo.psd
"test_*.py"    # Matches: test_main.py, test_utils.py
"file?.txt"    # Matches: file1.txt, fileA.txt (single character)
".*"           # Matches: .gitignore, .DS_Store (hidden files)
```

#### Setup:
1. Create `config/package.toml` or copy from example
2. Customize exclusions based on your project needs
3. Adjust `max_backups` based on available disk space

#### Best Practices:
- **Exclude source files**: Components, templates, design files that aren't needed in final package
- **Exclude system files**: OS-specific files (`.DS_Store`, `Thumbs.db`, `desktop.ini`)
- **Exclude work files**: Temporary files, backups, cache files
- **Keep backups reasonable**: Set `max_backups` based on disk space and rollback needs
- **Use glob patterns**: Leverage wildcards for flexible file matching

**Note:** The package module automatically uses these exclusions when copying files to the package directory.

### FTP Users Configuration (`config/ftp_users.toml`)

**Location:** `config/ftp_users.toml` (automatically located from project root)

**Note:** `ftp_users.toml` is in `.gitignore` and should not be committed (contains passwords).

**Purpose:** Defines FTP user accounts for the local FTP server (gzhost) used for testing deployment workflows.

#### Structure:
```toml
# FTP Users Configuration
# User accounts for local FTP server (gzhost)
# Copy from config/ftp_users.example.toml and customize

[users.dev]
username = "devup"
password = "devup"
home_directory = "publish/dev"
permissions = "elradfmwMT"

[users.staging]
username = "stagingup"
password = "stagingup"
home_directory = "publish/staging"
permissions = "elradfmwMT"

[users.prod]
username = "produp"
password = "produp"
home_directory = "publish/prod"
permissions = "elradfmwMT"
```

#### Setup:
1. Copy `config/ftp_users.example.toml` to `config/ftp_users.toml`
2. Customize usernames and passwords as needed
3. Never commit `ftp_users.toml` (it's in `.gitignore`)

#### Field Descriptions:
- `username`: FTP username for this environment
- `password`: FTP password (masked in logs and repr)
- `home_directory`: FTP user's home directory (relative to project root)
- `permissions`: FTP permission string (see pyftpdlib documentation)
  - `e`: Change directory (CWD, CDUP)
  - `l`: List files (LIST, NLST, STAT, MLSD, MLST, SIZE)
  - `r`: Retrieve files from server (RETR)
  - `a`: Append data to existing files (APPE)
  - `d`: Delete files and directories (DELE, RMD)
  - `f`: Rename files and directories (RNFR, RNTO)
  - `m`: Create directories (MKD)
  - `w`: Store files (STOR, STOU)
  - `M`: Change file mode/permissions (SITE CHMOD)
  - `T`: Change file modification time (SITE MFMT)

#### Automatic File Change Detection:
The `get_ftp_users_config()` function automatically detects when `ftp_users.toml` has been modified and reloads the configuration without requiring application restart. This is useful during development when testing different user configurations.

#### Example:
```python
# First load - reads from file
user1 = get_ftp_users_config('dev')
print(f"Username: {user1.username}")  # devup

# Edit ftp_users.toml and save...

# Next call automatically detects file change and reloads
user2 = get_ftp_users_config('dev')
print(f"Username: {user2.username}")  # Updated value if changed
```

#### Use Cases:
- **Local FTP Testing**: Test deployment workflows without touching production servers
- **CI/CD Pipelines**: Automated testing of FTP upload functionality
- **Development**: Quick iteration on deployment scripts with local FTP server
- **Integration Tests**: Verify FTP client code works correctly before production deployment

## Error Handling

GZConfig provides clear, actionable error messages for common problems:

### Environment Not Found

```python
try:
    env = get_pipeline_config('production')  # Typo: should be 'prod'
except ValueError as e:
    print(e)
    # "Environment 'production' is not defined in pipeline.toml. 
    #  Available environments: dev, staging, prod"
```

### Configuration File Missing

```python
# Pipeline config missing
try:
    config = get_pipeline_config()
except FileNotFoundError as e:
    print(e)
    # "Pipeline configuration not found: D:/Projects/www/GAZTank/config/pipeline.toml
    #  Expected location: config/pipeline.toml in project root"

# Deploy config missing
try:
    deploy = get_deploy_config()
except FileNotFoundError as e:
    print(e)
    # "Deploy configuration not found: D:/Projects/www/GAZTank/config/deploy.toml
    #  Copy config/deploy.example.toml to config/deploy.toml and fill in your FTP details"
```

### TOML Library Not Available

```python
try:
    config = get_pipeline_config()
except ImportError as e:
    print(e)
    # "No TOML library available. Please install Python 3.11+ or install tomli: 
    #  pip install tomli"
```

### Invalid Configuration Structure

```python
# If pipeline.toml is missing [environments] section or is empty
try:
    config = get_pipeline_config()
except ValueError as e:
    print(e)
    # "Invalid pipeline.toml: missing 'environments' section"
    # or
    # "Invalid pipeline.toml: 'environments' section is empty"

# If deploy.toml is missing required fields
try:
    deploy = get_deploy_config()
except ValueError as e:
    print(e)
    # "deploy.toml must contain [ftp] section"
    # or
    # "Missing required fields in [ftp] section: server, username"
```

### Validation Errors

```python
# Invalid port number
try:
    # If deploy.toml has port = 99999
    deploy = get_deploy_config()
except ValueError as e:
    print(e)
    # "Invalid port number: 99999"

# Invalid postfix length
try:
    # If deploy.toml has upload_subdir_postfix_len = 20
    deploy = get_deploy_config()
except ValueError as e:
    print(e)
    # "upload_subdir_postfix_len must be between 1 and 10, got 20"

# Invalid max_backups
try:
    # If package.toml has max_backups = -1
    config = get_package_config()
except ValueError as e:
    print(e)
    # "max_backups must be a positive integer, got -1"
```

## Migration Guide

GZConfig eliminates the need for duplicate TOML-reading code. Here's how to migrate existing code:

### Before (Direct TOML Access)

```python
# Old way - lots of boilerplate (40+ lines)
import tomllib
from pathlib import Path

def get_environment_directory(environment: str) -> Path:
    # Find project root
    current_file = Path(__file__).resolve()
    if current_file.parent.name == 'gzserve':
        project_root = current_file.parent.parent.parent
    else:
        project_root = current_file.parent.parent
    
    # Load TOML file
    config_path = project_root / 'config' / 'pipeline.toml'
    
    if not config_path.exists():
        raise FileNotFoundError(f"Pipeline configuration not found: {config_path}")
    
    try:
        with open(config_path, 'rb') as f:
            config = tomllib.load(f)
    except Exception as e:
        raise ValueError(f"Failed to parse pipeline.toml: {e}")
    
    # Validate structure
    if 'environments' not in config:
        raise ValueError("pipeline.toml must contain [environments] section")
    
    # Extract environment config
    if environment not in config['environments']:
        available = ', '.join(config['environments'].keys())
        raise ValueError(
            f"Environment '{environment}' not defined. "
            f"Available environments: {available}"
        )
    
    env_config = config['environments'][environment]
    env_dir_name = env_config.get('dir')
    
    if not env_dir_name:
        raise ValueError(f"Environment '{environment}' missing 'dir' configuration")
    
    # Build path
    return project_root / 'publish' / env_dir_name
```

### After (Using gzconfig)

```python
# New way - clean and simple (2 lines)
from gzconfig import get_pipeline_config

def get_environment_directory(environment: str) -> Path:
    env = get_pipeline_config(environment)
    return env.directory_path
```

### Benefits of Migration

- **95% less code**: From 40+ lines to 2 lines
- **No path manipulation**: Project root detection handled automatically
- **No TOML knowledge required**: Abstracted away completely
- **Automatic error handling**: Clear exceptions with helpful messages
- **Cached for performance**: Configuration loaded once, reused efficiently
- **Type hints**: Full IDE support with autocomplete
- **No imports**: Don't need to import `tomllib`, `Path`, handle exceptions manually
- **Maintainable**: Configuration logic centralized in one place

### Real-World Migration Examples

#### GZServe Module (server.py):
```python
# Before: ~70 lines of config code
# After: 1 line
env_config = get_pipeline_config(environment)
serve_dir = env_config.directory_path
port = env_config.port
```

#### Setup Module (file_tracker.py):
```python
# Before: ~60 lines of config code
# After: 2 lines
env = get_pipeline_config(environment)
env_dir = env.directory_path
```

#### Sitemap Module (sitemapper.py):
```python
# Before: ~55 lines of config code
# After: 2 lines
env = get_pipeline_config(args.environment)
env_dir = env.directory_path
```

**Total savings:** ~185 lines of duplicate code eliminated across three modules.

## Development

### Testing

Run the example script to experiment with gzconfig:

```bash
# Run the example demonstrating all usage patterns
python utils/gzconfig/example.py
```

The example script demonstrates:
- Getting full configuration
- Accessing all environments
- Getting specific environment
- Property access (name, dir, port, description, directory_path)
- Typical application usage patterns
- Type safety with type hints

#### Example Output:
```
============================================================
GZConfig Pipeline Configuration Example
============================================================

Example 1: Get full pipeline configuration
------------------------------------------------------------
Available environments: ['dev', 'staging', 'prod']

Example 2: Iterate through all environments
------------------------------------------------------------
  dev:
    Directory: dev
    Port: 7190
    Path: D:\Projects\www\GAZTank\publish\dev
    Description: Development environment with verbose logging and live reload
  ...

Example 3: Get specific environment
------------------------------------------------------------
Environment: dev
Directory: dev
Port: 7190
Full path: D:\Projects\www\GAZTank\publish\dev
Description: Development environment with verbose logging and live reload

Example 4: Typical application usage
------------------------------------------------------------
Starting server for staging environment
Serving from: D:\Projects\www\GAZTank\publish\staging
Server will listen on port: 7191

============================================================
✓ All examples completed successfully!
============================================================
```

### Integration

#### Using in Your Module

```python
#!/usr/bin/env python3
"""My Application using gzconfig"""

import sys
from gzconfig import get_pipeline_config

def main():
    # Get environment from command line
    if len(sys.argv) < 2:
        print("Usage: myapp <environment>")
        return 1
    
    environment = sys.argv[1]
    
    try:
        # Get environment configuration
        env = get_pipeline_config(environment)
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except FileNotFoundError as e:
        print(f"Configuration error: {e}")
        return 1
    
    # Use the configuration
    print(f"Environment: {env.name}")
    print(f"Directory: {env.directory_path}")
    print(f"Port: {env.port}")
    
    # Your application logic here
    # ...
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

#### Error Handling Patterns

```python
from gzconfig import get_pipeline_config

# Pattern 1: Let it raise (for fatal errors)
def initialize():
    env = get_pipeline_config('dev')  # Will raise if config broken
    return env

# Pattern 2: Catch and handle specific errors
def safe_initialize(environment):
    try:
        env = get_pipeline_config(environment)
        return env
    except ValueError as e:
        print(f"Invalid environment: {e}")
        return None
    except FileNotFoundError as e:
        print(f"Configuration missing: {e}")
        return None
    except ImportError as e:
        print(f"TOML library error: {e}")
        return None

# Pattern 3: Provide defaults
def initialize_with_default(environment):
    try:
        return get_pipeline_config(environment)
    except Exception:
        print("Using default development environment")
        return get_pipeline_config('dev')
```

#### Type Safety

```python
from gzconfig import get_pipeline_config, PipelineEnvironment, PipelineConfig
from typing import Optional

def process_environment(env: PipelineEnvironment) -> None:
    """Process a single environment with full type safety."""
    print(f"Processing {env.name}")
    print(f"  Port: {env.port}")
    print(f"  Directory: {env.directory_path}")

def get_env_by_name(name: str) -> Optional[PipelineEnvironment]:
    """Get environment with error handling."""
    try:
        return get_pipeline_config(name)
    except ValueError:
        return None

# Usage with type checking
config: PipelineConfig = get_pipeline_config()
for env_name in config.environment_names:
    env: PipelineEnvironment = config.get_environment(env_name)
    process_environment(env)
```

## Customisation

### Custom Configuration Paths

While gzconfig automatically finds `config/pipeline.toml`, you can modify the search logic if needed:

```python
# In pipeline.py, modify _find_project_root() for custom search logic
def _find_project_root() -> Path:
    # Add custom search locations
    custom_locations = [
        Path('/path/to/custom/config'),
        Path.home() / '.gaztank',
    ]
    
    for location in custom_locations:
        if (location / 'pipeline.toml').exists():
            return location
    
    # Fall back to default search
    # ... existing code
```

### Adding New Configuration Properties

To add new properties to environments, update `pipeline.toml` and the `PipelineEnvironment` class:

#### 1. Update pipeline.toml:
```toml
[environments.dev]
dir = "dev"
httpd_port = 7190
ftpd_port = 2190
description = "Development environment"
base_url = "http://localhost:7190"  # New property
debug = true                          # New property
```

#### 2. Update PipelineEnvironment class in pipeline.py:
```python
class PipelineEnvironment:
    def __init__(self, name: str, config: dict):
        self._name = name
        self._config = config
    
    # Existing properties...
    
    @property
    def base_url(self) -> str:
        """Base URL for the environment."""
        return self._config.get('base_url', f'http://localhost:{self.httpd_port}')
    
    @property
    def debug(self) -> bool:
        """Debug mode flag."""
        return self._config.get('debug', False)
```

#### 3. Use the new properties:
```python
env = get_pipeline_config('dev')
print(env.base_url)  # http://localhost:7190
print(env.debug)     # True
```

### Custom Environment Classes

For advanced use cases, create specialized environment classes:

```python
from gzconfig import get_pipeline_config, PipelineEnvironment

class DeploymentEnvironment:
    """Extended environment with deployment-specific properties."""
    
    def __init__(self, env: PipelineEnvironment):
        self._env = env
        self._remote_host = None  # Load from deployment config
    
    @property
    def name(self) -> str:
        return self._env.name
    
    @property
    def directory_path(self) -> Path:
        return self._env.directory_path
    
    @property
    def remote_host(self) -> str:
        """Get deployment host for this environment."""
        if self._remote_host is None:
            # Load from deployment config
            self._remote_host = self._load_remote_host()
        return self._remote_host
    
    def _load_remote_host(self) -> str:
        # Custom logic to load deployment host
        hosts = {'dev': 'dev.example.com', 'prod': 'example.com'}
        return hosts.get(self.name, 'localhost')

# Usage
base_env = get_pipeline_config('prod')
deploy_env = DeploymentEnvironment(base_env)
print(deploy_env.remote_host)  # example.com
```

## Troubleshooting

### ImportError: No TOML library

**Problem:** `No TOML library available. Please install Python 3.11+ or install tomli`

#### Solution:
```bash
# Option 1: Upgrade to Python 3.11+ (includes tomllib)
python --version  # Check current version

# Option 2: Install tomli for Python < 3.11
pip install tomli
```

### FileNotFoundError: Configuration not found

**Problem:** `Pipeline configuration not found: D:/Projects/.../config/pipeline.toml`

#### Solutions:
1. Ensure `config/pipeline.toml` exists in project root
2. Verify you're running from correct directory
3. Check file permissions (must be readable)
4. Verify project structure:
   ```
   GAZTank/
   ├── config/
   │   └── pipeline.toml  ← Must exist here
   └── utils/
       └── gzconfig/
   ```

### ValueError: Environment not defined

**Problem:** `Environment 'xyz' is not defined in pipeline.toml`

#### Solutions:
1. Check spelling of environment name (case-sensitive)
2. List available environments:
   ```python
   config = get_pipeline_config()
   print(config.environment_names)  # ['dev', 'staging', 'prod']
   ```
3. Add environment to `pipeline.toml`:
   ```toml
   [environments.xyz]
   dir = "xyz"
   port = 7193
   description = "XYZ environment"
   ```

### ValueError: Invalid pipeline.toml

**Problem:** `Invalid pipeline.toml: missing 'environments' section`

#### Solutions:
1. Verify TOML file has `[environments]` sections:
   ```toml
   [environments.dev]
   dir = "dev"
   httpd_port = 7190
   ftpd_port = 2190
   description = "Development"
   ```
2. Check TOML syntax is valid (use TOML validator)
3. Ensure file is not empty
4. Check file encoding is UTF-8

### AttributeError: PipelineConfig has no attribute

**Problem:** `Cannot access attribute "directory_path" for class "PipelineConfig"`

**Solution:** You're calling `get_pipeline_config()` without an environment parameter, which returns `PipelineConfig` (all environments), not `PipelineEnvironment` (single environment).

```python
# Wrong - returns PipelineConfig
config = get_pipeline_config()
print(config.httpd_port)  # Error! PipelineConfig doesn't have this property

# Right - returns PipelineEnvironment
env = get_pipeline_config('dev')
print(env.httpd_port)  # Works! Returns 7190
print(env.ftpd_port)   # Works! Returns 2190

# Or access via config object
config = get_pipeline_config()
env = config.get_environment('dev')
print(env.port)  # Works!
```

### Type Checker Warnings

**Problem:** Type checker complains about union types (`PipelineConfig | PipelineEnvironment`)

**Solution:** Add type annotations:
```python
from gzconfig import get_pipeline_config, PipelineEnvironment, PipelineConfig

# Annotate the return type
env: PipelineEnvironment = get_pipeline_config('dev')  # type: ignore

# Or use explicit typing
config: PipelineConfig = get_pipeline_config()
env: PipelineEnvironment = config.get_environment('dev')
```

## Best Practices

### 1. Get Configuration Once

```python
# Good - get once, reuse
env = get_pipeline_config('dev')
for item in range(100):
    process_item(item, env.directory_path, env.port)

# Bad - unnecessary repeated lookups
for item in range(100):
    env = get_pipeline_config('dev')  # Cached, but wasteful
    process_item(item, env.directory_path, env.port)
```

### 2. Use Property Access

```python
# Good - clean property access
env = get_pipeline_config('dev')
port = env.port
directory = env.directory_path

# Bad - don't access internal attributes
env = get_pipeline_config('dev')
port = env._config['port']  # Don't do this!
directory = env._project_root / 'publish' / env._config['dir']  # Don't do this!
```

### 3. Handle Errors Appropriately

```python
# Good - specific error handling for user input
def start_server(user_environment: str):
    try:
        env = get_pipeline_config(user_environment)
    except ValueError as e:
        print(f"Invalid environment: {e}")
        sys.exit(1)
    
    # ... start server

# Also good - let it raise for developer errors
def initialize():
    env = get_pipeline_config('dev')  # If this fails, it's a bug
    return env
```

### 4. Use Type Hints

```python
# Good - full type safety
from gzconfig import get_pipeline_config, PipelineEnvironment

def serve_directory(env: PipelineEnvironment) -> None:
    """Host files from environment directory."""
    print(f"Serving on port {env.port}")
    print(f"Directory: {env.directory_path}")

# Usage
dev_env = get_pipeline_config('dev')
serve_directory(dev_env)  # IDE provides autocomplete and type checking
```

### 5. Check Directory Existence

```python
# Good - verify directory exists before using
env = get_pipeline_config('dev')
if not env.directory_path.exists():
    print(f"Environment directory not found: {env.directory_path}")
    print(f"Please run: python -m generate -e {env.name}")
    sys.exit(1)

os.chdir(env.directory_path)
# ... continue
```

### 6. Validate Environment Parameter Early

```python
# Good - validate environment early in your main()
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--environment', required=True,
                       choices=['dev', 'staging', 'prod'])
    args = parser.parse_args()
    
    # This will work because we validated choices
    env = get_pipeline_config(args.environment)
    # ... rest of code
```

### 7. Don't Cache PipelineConfig Objects Manually

```python
# Good - let gzconfig handle caching
def get_env_port(environment: str) -> int:
    env = get_pipeline_config(environment)
    return env.port

# Bad - unnecessary manual caching
_config_cache = None
def get_env_port(environment: str) -> int:
    global _config_cache
    if _config_cache is None:
        _config_cache = get_pipeline_config()
    return _config_cache.get_environment(environment).port
```

### 8. Use reload=True Only When Needed

```python
# Good - reload only when config actually changed
def reload_config_if_changed():
    config_path = Path('config/pipeline.toml')
    last_modified = config_path.stat().st_mtime
    
    if last_modified > last_check_time:
        config = get_pipeline_config(reload=True)
        return config
    
    return get_pipeline_config()  # Use cached

# Bad - always reloading
def get_config():
    return get_pipeline_config(reload=True)  # Wastes time parsing TOML
```

## Future Enhancements

Planned improvements for future versions:

### Short Term (v1.1)
- [ ] **Site Configuration**: Add support for `site.toml` (site metadata, base URLs, SEO settings)
- [ ] **Generator Configuration**: Add support for `generate.toml` (content generation rules, markdown settings)
- [ ] **Tool Configuration**: Add support for `tools.toml` (tool-specific settings beyond logging)

### Medium Term (v1.2)
- [ ] **Unified Configuration API**: Single interface to access all config files (`get_config('site')`, `get_config('pipeline')`)
- [ ] **Environment Variables**: Support environment variable overrides (e.g., `GAZTANK_ENV=prod`)
- [ ] **Configuration Validation**: JSON Schema or similar for validating configuration files
- [ ] **Configuration Merging**: Support for local overrides (e.g., `pipeline.local.toml`)

### Long Term (v2.0)
- [ ] **Watch Mode**: Automatically reload configuration when files change
- [ ] **Configuration Migrations**: Tools for migrating config between versions
- [ ] **Multi-Project Support**: Support for multiple project configurations
- [ ] **Configuration Export**: Export configuration to JSON/YAML for tools

### Under Consideration
- [ ] **Remote Configuration**: Load configuration from URLs or remote servers
- [ ] **Encrypted Secrets**: Support for encrypted configuration values
- [ ] **Configuration Diff**: Tools for comparing configurations across environments
- [ ] **Configuration Templates**: Template system for generating configurations

See [GitHub Issues](https://github.com/gazorper/GAZTank/issues) for tracking and discussion.

## Related Documentation

- **[gzlogging](../gzlogging/README.md)** - Logging infrastructure (similar library module design)
- **[gzserve](../gzserve/README.md)** - Development server (uses gzconfig)
- **[setup](../setup/README.md)** - Site setup wizard (uses gzconfig)
- **[sitemap](../sitemap/README.md)** - Sitemap generator (uses gzconfig)
- **[package](../package/README.md)** - Website packager (uses gzconfig)
- **[generate](../generate/README.md)** - Content generator (will use gzconfig)
- **Python tomllib:** https://docs.python.org/3/library/tomllib.html
- **Python fnmatch:** https://docs.python.org/3/library/fnmatch.html
- **TOML specification:** https://toml.io/

## License

GPL-3.0-or-later

## Authors

superguru, gazorper

---

*Last updated: October 23, 2025*  
*GZConfig version: 1.0.0*
