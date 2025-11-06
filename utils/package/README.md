# Website Packager

Environment-aware packaging system that prepares website files for deployment by synchronizing, minifying, and archiving the specified environment directory.

**Version:** 1.4  
**Last Updated:** November 6, 2025

## Table of Contents

- [Purpose](#purpose)
- [Build Pipeline](#build-pipeline)
- [Logging](#logging)
- [Usage](#usage)
- [Command Line Arguments](#command-line-arguments)
- [Module Structure](#module-structure)
- [Features](#features)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Exit Codes](#exit-codes)
- [Performance](#performance)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)

## Purpose

The Website Packager is a focused packaging tool that prepares environment directories for deployment. It operates on **already-generated content in `src/`** and performs:

- **File synchronization** - Copies new/modified files from `src/` to `publish/{env}/`
- **Asset minification** - Optimizes CSS and JavaScript file sizes
- **Archive creation** - Creates timestamped backup packages
- **Backup management** - Maintains rolling archive retention

**Important:** All generated content (HTML from markdown, sitemaps, etc.) must be in the `src/` directory tree **before** running the packager. The packager treats `src/` as the source of truth.

**Note:** For removing orphaned files (files that exist in `publish/{env}/` but not in `src/`), use the `clean` module **before** running the packager.

### Important: Packaging vs Generation

The package module **does NOT** perform:
- Content validation (use `gzlint` module)
- Markdown to HTML conversion (use `generate` module)
- Sitemap generation (use `sitemap` module)

These are separate pipeline steps that must run **before** packaging. The correct build order is:

```
clean -> generate -> compose -> setup -> gzlint -> normalise -> sitemap -> toc -> package -> deploy
```

## Build Pipeline

The packager fits into the GAZTank deployment pipeline as the final preparation step before deployment.

Package Module Workflow:

```
Stage 1: COPY & MINIFY
  - Copy modified/new files from src/ to publish/{env}/
  - Skip unchanged files (compare modification times)
  - Minify CSS files in-place (using rcssmin)
  - Minify JavaScript files in-place (using rjsmin)
  - Create/update .metainfo/<env>.txt with environment name
  - Note: Generated content must be in src/ tree before packaging

Stage 2: ARCHIVE
  - Create timestamped zip file in publish/packages/
  - Format: package_{environment}_YYYYMMDD_HHMMSS.zip
  - Keep only 4 most recent packages (cleanup old archives)
```

**Note:** Use the `clean` module before packaging to remove orphaned files (files in `publish/{env}/` that don't exist in `src/`).

## Logging

The packager uses the **gzlogging** infrastructure for environment-aware logging.

- **Environment:** User-specified via `-e` argument (dev/staging/prod)
- **Tool Name:** `package`
- **Log Location:** `logs/{environment}/package_YYYYMMDD.log`
- **Encoding:** UTF-8

## Usage

### Command Line

```bash
# Using the launcher script (recommended)
scripts\package.cmd -e dev              # Windows
./scripts/package.sh -e staging         # Linux/Mac

# With options
scripts\package.cmd -e dev --force      # Force packaging all files
scripts\package.cmd -e dev --dry-run    # Preview without changes
python -m package --help                # Show help
```

### As a Module

```python
from utils.package.packager import package_site

# Package an environment
success = package_site(environment='dev', force=False, dry_run=False)
```

## Command Line Arguments

### Required

- **`-e, --environment {dev,staging,prod}`** - Target environment to package

### Optional

- **`--force`** - Force packaging of all files, ignoring timestamps
- **`--dry-run`** - Preview changes without modifying files
- **`--help`** - Display usage information

## Module Structure

```
package/
├── __init__.py      # Package initialization
├── __main__.py      # Entry point for python -m package
├── packager.py      # Core packaging logic
└── README.md        # This file
```

### Key Functions

- `package_site()` - Main packaging orchestrator
- `minify_assets()` - Minifies CSS and JS files
- `backup_previous_package()` - Creates timestamped backup
- `cleanup_old_backups()` - Removes old packages

## Features

- **Environment-aware**: Supports dev, staging, and prod environments
- **Configuration-driven exclusions**: Customize excluded files/directories in `config/package.toml`
- **Timestamp-aware**: Only copies files when source is newer
- **Force mode**: `--force` flag to package all files
- **Dry-run mode**: `--dry-run` flag to preview changes
- **Asset minification**: Optimizes CSS and JavaScript (rcssmin, rjsmin)
- **Package metadata**: Creates `.metainfo/<env>.txt` with environment name and timestamp
- **Backup creation**: Timestamped zip archives
- **Configurable backup retention**: Max backups set in `config/package.toml`
- **Exit codes**: 0 for success, 1 for failure
- **Integrated logging**: Uses gzlogging infrastructure

**Note:** For orphaned file removal, use the `clean` module before running `package`.

## Configuration

The package module uses two configuration files:

### Environment Configuration (`config/pipeline.toml`)

Defines environment-specific settings:

```toml
[environments.dev]
dir = "dev"
httpd_port = 7190
description = "Development environment"

[environments.staging]
dir = "staging"
httpd_port = 7191
description = "Staging environment"

[environments.prod]
dir = "prod"
httpd_port = 7192
description = "Production environment"
```

### Package Configuration (`config/package.toml`)

Defines packaging behavior and exclusions:

```toml
[package]
# Maximum number of backup packages to retain per environment
max_backups = 4

[exclusions]
# Directories to exclude from packaging (relative to src/ directory)
directories = [
    "components",      # HTML source components (composition sources)
    "pages",          # Page templates (composition sources)
]

# File patterns to exclude (glob patterns)
files = [
    "*.psd",          # Photoshop files
    "*.ai",           # Adobe Illustrator files
    "*.sketch",       # Sketch files
    "*.fig",          # Figma files
    "*.xcf",          # GIMP files
    "*.pdn",          # Paint.NET files
    ".DS_Store",      # macOS metadata
    "Thumbs.db",      # Windows thumbnails
    "desktop.ini",    # Windows folder settings
]
```

#### Exclusion Rules

- **Directories**: Matched at any level in the `src/` tree
  - Example: `"components"` excludes `src/components/` and `src/subfolder/components/`
- **File Patterns**: Use glob syntax (`*` = any characters, `?` = single character)
  - Example: `"*.psd"` excludes all Photoshop files
- **Case Sensitivity**: Case-sensitive on Linux/Mac, case-insensitive on Windows

#### Adding Custom Exclusions

To exclude additional files or directories, edit `config/package.toml`:

```toml
[exclusions]
directories = [
    "components",
    "pages",
    "drafts",          # Add your custom directory
    "temp",            # Add another custom directory
]

files = [
    "*.psd",
    "*.bak",           # Add backup files
    "*.tmp",           # Add temporary files
]
```

## Best Practices

1. **Always run after content generation** - Packaging requires generated content
2. **Use dry-run for testing** - Preview changes before committing
3. **Monitor package sizes** - Large packages may indicate issues
4. **Leverage timestamp checking** - Automatic skipping of up-to-date files
5. **Force mode sparingly** - Only when necessary (branch switches, refactoring)

## Package Metadata

Every time the package module runs (except in dry-run mode), it creates/updates a metadata file to track when the environment was last packaged:

**Location:** `publish/{environment}/.metainfo/{environment}.txt`

**Content:** The environment name (e.g., `dev`, `staging`, `prod`)

**File Timestamp:** Updated every package run, even when no files are copied

### Purpose

The metadata file serves multiple purposes:

1. **Deployment Verification**: Check if an environment has been packaged
2. **Last Package Time**: File modification timestamp shows when packaging occurred
3. **Environment Identification**: File content confirms which environment was packaged

### Example

After running `python -m package -e dev`:

```
publish/dev/.metainfo/dev.txt
  Content: dev
  Modified: 2025-10-23 20:37:12
```

This metadata is useful for:
- Deployment scripts to verify packaging completion
- Monitoring systems to track deployment pipelines
- Troubleshooting to identify when environments were last updated

## Troubleshooting

### "Configuration Error"

Check that `config/pipeline.toml` exists and is valid TOML.

### "Minification libraries not installed"

```bash
pip install rcssmin rjsmin
```

Note: Optional - files copied without minification if unavailable.

### "Source directory not found"

Ensure running from project root and `src/` directory exists.

### "Package Configuration Error"

Check that `config/package.toml` exists and is valid TOML. Copy from the template if missing.

### Files unexpectedly excluded

Check `config/package.toml` exclusions section. Verify directory names and file patterns match your intent.

### No files copied

Normal if all files up-to-date. Use `--force` to copy regardless.

## Exit Codes

- **0** - Success
- **1** - Failure (configuration error, file errors)

## Performance

| Site Size | Files | Build Time |
|-----------|-------|------------|
| Small     | ~50   | 1-2 sec    |
| Medium    | ~200  | 3-5 sec    |
| Large     | ~500  | 8-12 sec   |

## Future Enhancements

- [ ] Parallel minification for faster processing
- [ ] Additional minification options (source maps)
- [ ] Support for additional asset types (images)
- [ ] Checksum verification
- [ ] Package manifest generation with exclusion statistics
- [ ] CDN invalidation integration
- [ ] Pre-compression (gzip, brotli)
- [ ] Package comparison tool
- [ ] Configurable exclusion patterns per environment

## Related Documentation

- [Package Configuration](../../config/package.toml) - Exclusions and settings
- [Generate Module](../generate/README.md) - Content generation
- [GZLogging Module](../gzlogging/README.md) - Logging infrastructure
- [GZConfig Module](../gzconfig/README.md) - Configuration management
- [Pipeline Configuration](../../config/pipeline.toml) - Environment definitions

## License

GPL v3.0 or later

## Authors

superguru, gazorper

---

*Last updated: November 6, 2025*  
*Package module version: 1.4*
