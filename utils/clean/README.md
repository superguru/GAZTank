# Environment Cleaner Module

**Version**: 1.2  
**Last Updated**: November 4, 2025  
**Maturity Level**: Stable (✅ All criteria met)

## Purpose

The **clean module** identifies and optionally removes orphaned files from environment directories (`publish/dev/`, `publish/staging/`, `publish/prod/`) to keep them synchronized with the source directory (`src/`).

**Orphaned files** are files that exist in the environment directory but no longer exist in the source directory. These can accumulate when:
- Files are deleted or renamed in `src/`
- Content structure is reorganized
- Files are moved between directories

The cleaner ensures `src/` remains the single source of truth by identifying files in environment directories that no longer have corresponding source files, and optionally removing them when requested.

## Module Structure

```
utils/clean/
├── __init__.py         # Module exports
├── __main__.py         # Module entry point
└── cleaner.py          # Main cleaning logic
```

## Build Pipeline Integration

The clean module is used **before** the package module runs to ensure the environment is clean before syncing and packaging:

```
┌────────────────────────────────────────────────────────┐
│ Generate → Normalize → Clean → Package → Deploy        │
└────────────────────────────────────────────────────────┘
```

### Usage in Pipeline:
1. **Clean**: Remove orphaned files from environment
2. **Package**: Sync modified files, minify assets, create archive

This separation ensures:
- Clean module focuses solely on orphaned file removal
- Package module focuses on file synchronization, minification, and archiving
- No circular dependencies between modules

## Features

### Core Functionality

- **Orphaned File Detection**: Compares environment directory against source directory
- **Deploy Backup Cleanup**: Automatically removes old deploy backup directories (always runs)
- **Identify-Only Mode** (default): Lists orphaned files without removing them
- **Clean-Orphaned Mode**: Removes orphaned files with confirmation prompt (`--clean-orphaned`)
- **Clean-All Mode**: Remove ALL files from environment directory (`--clean-all`)
- **Safe Removal**: Removes files and their empty parent directories
- **Confirmation Prompts**: Asks for confirmation before deletion (unless `--force` is used)
- **Dry-Run Mode**: Preview changes without modifying files (`--dry-run`)
- **Force Mode**: Skip confirmation prompts (`--force`)
- **Environment-Aware**: Works with dev/staging/prod environments
- **Structured Logging**: Logs to `logs/{environment}/clean_YYYYMMDD.log`
- **Console Output**: Emoji-decorated progress indicators and summaries

### Deploy Backup Cleanup

The clean module **automatically removes old deploy backup directories** every time it runs, regardless of operating mode or arguments. This cleanup:

- **Runs automatically**: No flags needed, no prompts shown
- **Targets backup directories**: Removes directories starting with `.2` (date-based deploy backups)
- **Examples of removed directories**: `.20251105_092533_309_tnfs2`, `.20251105_092921_309_iom87`
- **Preserved directories**: `.metainfo` and other dot-directories not starting with `.2`
- **Created by**: Deploy module when uploading files via FTP
- **Safe to remove**: These are temporary backup directories from deployment operations
- **Always logged**: Backup removal is logged and included in statistics

Deploy backups are created by the deploy module during FTP uploads to prevent data loss. Once confirmed successful, these backups can be safely removed to save disk space. The clean module specifically targets date-based backup directories (starting with `.2` for year 2xxx) while preserving system directories like `.metainfo`.

### Orphaned File Detection Logic

The cleaner determines orphaned files by:

1. **Scanning source directory** (`src/`): Build a set of all file paths relative to src/
2. **Scanning environment directory** (`publish/{environment}/`): Check each file's relative path
3. **Comparing paths**: If a file exists in environment but not in source → orphaned
4. **Removing orphaned files**: Delete files and clean up empty directories

#### Example:
```
src/
├── index.html          ✓ Keep in environment
├── about.html          ✓ Keep in environment
└── css/
    └── style.css       ✓ Keep in environment

publish/dev/
├── index.html          → Keep (exists in src/)
├── about.html          → Keep (exists in src/)
├── old-page.html       → Remove (orphaned)
└── css/
    ├── style.css       → Keep (exists in src/)
    └── old-style.css   → Remove (orphaned)
```

Result: `old-page.html` and `css/old-style.css` are removed from `publish/dev/`

### Operating Modes

The clean module has three distinct operating modes:

#### 1. Identify-Only Mode (Default)

**Usage**: Run without `--clean-orphaned` or `--clean-all` flags

By default, the module only **identifies** orphaned files without removing them. This is the safest mode for inspection.

```bash
scripts\gzclean.cmd -e dev
```

**Output**:
- Lists orphaned files found
- Shows message: "Use --clean-orphaned to remove these files"
- Does not modify any files

**Use when**:
- You want to see what files are orphaned
- You're inspecting the environment state
- You need to verify before deletion

#### 2. Clean-Orphaned Mode

**Usage**: Use `--clean-orphaned` flag

Removes **only orphaned files** (files that don't exist in `src/`). Prompts for confirmation before deletion unless `--force` is used.

```bash
# Preview orphaned file removal
scripts\gzclean.cmd -e dev --clean-orphaned --dry-run

# Remove with confirmation prompt
scripts\gzclean.cmd -e dev --clean-orphaned
# Prompts: "Type 'yes' to confirm deletion:"

# Remove without confirmation (use in automated scripts)
scripts\gzclean.cmd -e dev --clean-orphaned --force
```

**Safety Features**:
- Shows list of files to be deleted in confirmation prompt
- Requires typing "yes" to proceed (unless `--force` is used)
- Use `--dry-run` to preview without modifications

**Use when**:
- You want to remove files that are no longer in `src/`
- You need to clean up after reorganizing content
- Running in automated pipeline with `--force`

#### 3. Clean-All Mode

**Usage**: Use `--clean-all` flag

The "nuclear option" that removes **ALL files** from the environment directory, not just orphaned ones. Prompts for confirmation before deletion unless `--force` is used.

```bash
# Preview complete removal
scripts\gzclean.cmd -e dev --clean-all --dry-run

# Remove all with confirmation prompt
scripts\gzclean.cmd -e dev --clean-all
# Prompts: "Type 'yes' to confirm deletion:"

# Remove all without confirmation (use with extreme caution!)
scripts\gzclean.cmd -e dev --clean-all --force
```

**Use when**:
- You want to completely rebuild an environment from scratch
- You need to ensure a clean slate before regenerating content
- You're troubleshooting issues and want to eliminate all cached/stale files

**⚠️ WARNING**: `--clean-all --force` is destructive and cannot be undone! Always use `--dry-run` first to preview changes.

## Configuration

The clean module reads environment configuration from `config/pipeline.toml`:

```toml
[environments.dev]
dir = "publish/dev"
description = "Development environment"
port = 3000

[environments.staging]
dir = "publish/staging"
description = "Staging environment"
port = 3001

[environments.prod]
dir = "publish/prod"
description = "Production environment"
port = 3002
```

## Usage

### Command Line

#### Basic Usage (Identify Only):
```bash
# Identify orphaned files without removing them (Windows)
scripts\gzclean.cmd -e dev

# Linux/Mac
./scripts/gzclean.sh -e dev
```

#### Clean Orphaned Files:
```bash
# Remove orphaned files with confirmation prompt
scripts\gzclean.cmd -e dev --clean-orphaned

# Remove orphaned files without confirmation
scripts\gzclean.cmd -e dev --clean-orphaned --force

# Preview orphaned file removal
scripts\gzclean.cmd -e dev --clean-orphaned --dry-run
```

#### Clean All Files:
```bash
# Remove ALL files with confirmation prompt
scripts\gzclean.cmd -e dev --clean-all

# Remove ALL files without confirmation
scripts\gzclean.cmd -e dev --clean-all --force

# Preview complete removal
scripts\gzclean.cmd -e dev --clean-all --dry-run
```

#### Direct Python Module:
```bash
# Identify only (default)
python -m clean -e dev

# Remove orphaned files
python -m clean -e dev --clean-orphaned

# Remove orphaned files without confirmation
python -m clean -e dev --clean-orphaned --force

# Remove all files without confirmation
python -m clean -e prod --clean-all --force
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `-e`, `--environment` | ✅ Yes | Environment to clean: `dev`, `staging`, or `prod` |
| `--clean-orphaned` | ❌ No | Remove orphaned files from environment. Requires confirmation unless `--force` is also specified |
| `--clean-all` | ❌ No | Remove ALL files from environment (not just orphaned). Requires confirmation unless `--force` is also specified |
| `--force` | ❌ No | Skip confirmation prompts when using `--clean-orphaned` or `--clean-all` |
| `--dry-run` | ❌ No | Preview changes without modifying files |
| `--help` | ❌ No | Show help message and examples |

**Note**: If neither `--clean-orphaned` nor `--clean-all` is specified, the module runs in identify-only mode (lists orphaned files without removing them).

### Python API

```python
from utils.clean import clean_site, get_orphaned_files, remove_orphaned_files, remove_all_files

# Identify orphaned files only (no deletion)
success = clean_site('dev', force=False, dry_run=False, clean_orphaned=False, clean_all=False)

# Remove orphaned files with confirmation
success = clean_site('dev', force=False, dry_run=False, clean_orphaned=True, clean_all=False)

# Remove orphaned files without confirmation
success = clean_site('dev', force=True, dry_run=False, clean_orphaned=True, clean_all=False)

# Remove ALL files from environment (with confirmation)
success = clean_site('dev', force=False, dry_run=False, clean_orphaned=False, clean_all=True)

# Remove ALL files without confirmation
success = clean_site('dev', force=True, dry_run=False, clean_orphaned=False, clean_all=True)

# Get list of orphaned files
from pathlib import Path
src_dir = Path('src')
env_dir = Path('publish/dev')
orphaned = get_orphaned_files(src_dir, env_dir)

# Remove orphaned files (with confirmation)
dirs_removed = remove_orphaned_files(env_dir, orphaned, dry_run=False, force=False)

# Remove orphaned files (without confirmation)
dirs_removed = remove_orphaned_files(env_dir, orphaned, dry_run=False, force=True)

# Remove all files
files_removed, dirs_removed = remove_all_files(env_dir, dry_run=False, force=False)
```

## Output Examples

### Identify-Only Mode (Default)

```
============================================================
  GAZ Tank - Environment Cleaner
============================================================

Identifying orphaned files...
  ℹ️  Found 3 orphaned file(s)
    • old-page.html
    • css/old-style.css
    • js/deprecated.js

  ℹ️  Use --clean-orphaned to remove these files

============================================================
✅ CLEANING COMPLETED
============================================================
  Environment directory: D:\Projects\www\GAZTank\publish\dev
  Found: 3 orphaned file(s)
```

### Clean-Orphaned Mode (With Confirmation)

```
============================================================
  GAZ Tank - Environment Cleaner
============================================================
ℹ️  CLEAN ORPHANED MODE - Will remove orphaned files

Identifying orphaned files...

⚠️  WARNING: This will DELETE 3 orphaned file(s)
  from: D:\Projects\www\GAZTank\publish\dev
    • old-page.html
    • css/old-style.css
    • js/deprecated.js

  Type 'yes' to confirm deletion: yes

  🗑️  Removing 3 orphaned file(s)...
  ✓ Removed 3 file(s) and 1 empty directory(ies)

============================================================
✅ CLEANING COMPLETED
============================================================
  Environment directory: D:\Projects\www\GAZTank\publish\dev
  Removed: 3 orphaned file(s)
  Removed: 1 directory(ies)
```

### Clean-Orphaned Mode (Cancelled)

```
============================================================
  GAZ Tank - Environment Cleaner
============================================================
ℹ️  CLEAN ORPHANED MODE - Will remove orphaned files

Identifying orphaned files...

⚠️  WARNING: This will DELETE 3 orphaned file(s)
  from: D:\Projects\www\GAZTank\publish\dev
    • old-page.html
    • css/old-style.css
    • js/deprecated.js

  Type 'yes' to confirm deletion: no

  ❌ Operation cancelled

============================================================
✅ CLEANING COMPLETED
============================================================
  Environment directory: D:\Projects\www\GAZTank\publish\dev
  Removed: 3 orphaned file(s)
```

### Clean-Orphaned Mode (Force, No Confirmation)

```
============================================================
  GAZ Tank - Environment Cleaner
============================================================
ℹ️  CLEAN ORPHANED MODE - Will remove orphaned files
🔄 FORCE MODE enabled

Identifying orphaned files...
  🗑️  Removing 3 orphaned file(s)...
  ✓ Removed 3 file(s) and 1 empty directory(ies)

============================================================
✅ CLEANING COMPLETED
============================================================
  Environment directory: D:\Projects\www\GAZTank\publish\dev
  Removed: 3 orphaned file(s)
  Removed: 1 directory(ies)
```

### Dry-Run Mode (Identify Only)

```
============================================================
  GAZ Tank - Environment Cleaner
============================================================
⚠️  DRY RUN MODE enabled - No files will be modified

Identifying orphaned files...
  ℹ️  Found 3 orphaned file(s)
    • old-page.html
    • css/old-style.css
    • js/deprecated.js

  ℹ️  Use --clean-orphaned to remove these files

============================================================
ℹ️  DRY RUN COMPLETED
============================================================
  No files were modified
  Found: 3 orphaned file(s)
```

### Dry-Run Mode (Clean-Orphaned)

```
============================================================
  GAZ Tank - Environment Cleaner
============================================================
ℹ️  CLEAN ORPHANED MODE - Will remove orphaned files
⚠️  DRY RUN MODE enabled - No files will be modified

Identifying orphaned files...
  🗑️  [DRY RUN] Would remove 3 orphaned file(s)
    • old-page.html
    • css/old-style.css
    • js/deprecated.js

============================================================
ℹ️  DRY RUN COMPLETED
============================================================
  No files were modified
  Would remove: 3 orphaned file(s)
```

### No Orphaned Files

```
============================================================
  GAZ Tank - Environment Cleaner
============================================================

Identifying orphaned files...
  ✓ No orphaned files found

============================================================
✅ CLEANING COMPLETED
============================================================
  Environment directory: D:\Projects\www\GAZTank\publish\dev
  Removed: 0 file(s)
```

### Clean-All Mode (Dry-Run)

```
============================================================
  GAZ Tank - Environment Cleaner
============================================================
⚠️  CLEAN ALL MODE - Will remove ALL files in environment
⚠️  DRY RUN MODE enabled - No files will be modified

Removing ALL files from environment directory...
  🗑️  [DRY RUN] Would remove ALL 42 file(s) and 8 directory(ies)
    • index.html
    • about.html
    • css/style.css
    • js/main.js
    • images/logo.png
    ... and 37 more

============================================================
ℹ️  DRY RUN COMPLETED
============================================================
  No files were modified
  Would remove: ALL 42 file(s)
```

### Clean-All Mode (With Confirmation)

```
============================================================
  GAZ Tank - Environment Cleaner
============================================================
⚠️  CLEAN ALL MODE - Will remove ALL files in environment

Removing ALL files from environment directory...

⚠️  WARNING: This will DELETE ALL 42 file(s) and 8 directory(ies)
  from: D:\Projects\www\GAZTank\publish\dev

  Type 'yes' to confirm deletion: yes

  🗑️  Removing ALL 42 file(s) and 8 directory(ies)...
  ✓ Removed 42 file(s) and 8 directory(ies)

============================================================
✅ CLEANING COMPLETED
============================================================
  Environment directory: D:\Projects\www\GAZTank\publish\dev
  Removed: ALL 42 file(s)
  Removed: 8 directory(ies)
```

### Clean-All Mode (Cancelled)

```
============================================================
  GAZ Tank - Environment Cleaner
============================================================
⚠️  CLEAN ALL MODE - Will remove ALL files in environment

Removing ALL files from environment directory...

⚠️  WARNING: This will DELETE ALL 42 file(s) and 8 directory(ies)
  from: D:\Projects\www\GAZTank\publish\dev

  Type 'yes' to confirm deletion: no

  ❌ Operation cancelled

============================================================
✅ CLEANING COMPLETED
============================================================
  Environment directory: D:\Projects\www\GAZTank\publish\dev
  Removed: ALL 0 file(s)
  Removed: 0 directory(ies)
```

## Logging

### Log File Location

Logs are written to: `logs/{environment}/clean_YYYYMMDD.log`

Examples:
- `logs/dev/clean_20250123.log`
- `logs/staging/clean_20250123.log`
- `logs/prod/clean_20250123.log`

### Log Format

```
2025-01-23 14:30:15 - clean - INF - Environment Cleaner started
2025-01-23 14:30:15 - clean - INF - Environment: dev
2025-01-23 14:30:15 - clean - DBG - Pipeline configuration loaded successfully
2025-01-23 14:30:15 - clean - INF - Target directory: D:\Projects\www\GAZTank\publish\dev
2025-01-23 14:30:15 - clean - INF - Identifying orphaned files
2025-01-23 14:30:15 - clean - INF - Removing 3 orphaned files
2025-01-23 14:30:15 - clean - DBG - Removed: old-page.html
2025-01-23 14:30:15 - clean - DBG - Removed: css/old-style.css
2025-01-23 14:30:15 - clean - DBG - Removed: js/deprecated.js
2025-01-23 14:30:15 - clean - DBG - Removed empty directory: js
2025-01-23 14:30:15 - clean - INF - Removed 3 files and 1 empty directories
2025-01-23 14:30:15 - clean - INF - Environment Cleaner completed successfully
```

**Note**: Console output includes emojis (✓, 🗑️, ❌), but log files contain plain text without formatting for better parsing.

### Log Rotation

Log files are automatically rotated by the `gzlogging` module based on `config/gzlogrotate.toml`. Old logs are moved to `logs/00rotated/` with timestamps.

## Error Handling

### Common Errors

#### Missing Environment Argument:
```
usage: __main__.py [-h] -e {dev,staging,prod} [--force] [--dry-run]
__main__.py: error: the following arguments are required: -e/--environment
```

#### Invalid Environment:
```
❌ Configuration Error: Environment 'invalid' not found in pipeline.toml
```

#### Source Directory Missing:
```
❌ ERROR: Source directory not found: D:\Projects\www\GAZTank\src
```

#### Configuration File Missing:
```
❌ Configuration Error: config/pipeline.toml not found
```

### Warnings

#### File Removal Failed:
```
⚠️  Warning: Could not remove old-page.html: Permission denied
```

## Dependencies

### Python Modules (Standard Library)
- `pathlib` - File system path handling
- `argparse` - Command-line argument parsing
- `sys` - System operations

### Internal Modules
- `utils.gzlogging` - Structured logging infrastructure
- `utils.gzconfig` - Configuration management (reads `pipeline.toml`)

### Configuration Files
- `config/pipeline.toml` - Environment definitions

## Development

### Running Tests

```bash
# Run with dry-run to test without modifications
python -m clean -e dev --dry-run

# Test all environments
python -m clean -e dev --dry-run
python -m clean -e staging --dry-run
python -m clean -e prod --dry-run
```

### Code Structure

**`cleaner.py`** - Main module containing:
- `get_orphaned_files(src_dir, env_dir)` - Identifies orphaned files
- `remove_orphaned_files(env_dir, orphaned_files, dry_run)` - Removes orphaned files and empty directories
- `clean_site(environment, force, dry_run)` - Main orchestrator function
- `main()` - Command-line entry point with argparse

**`__init__.py`** - Module exports:
- `clean_site` - Main public API
- `get_orphaned_files` - Low-level file detection
- `remove_orphaned_files` - Low-level file removal

**`__main__.py`** - Module execution entry point

## Best Practices

### When to Use Clean Module

✅ **Check for orphaned files (identify only)**:
```bash
scripts\gzclean.cmd -e dev
# Lists orphaned files without removing them
```

✅ **Clean orphaned files before package**:
```bash
scripts\gzclean.cmd -e dev --clean-orphaned
scripts\package.cmd -e dev
```

✅ **Use dry-run to preview removal**:
```bash
scripts\gzclean.cmd -e prod --clean-orphaned --dry-run
# Review output
scripts\gzclean.cmd -e prod --clean-orphaned
```

✅ **Clean after major src/ restructuring**:
```bash
# After deleting/moving many files in src/
scripts\gzclean.cmd -e dev --clean-orphaned
scripts\gzclean.cmd -e staging --clean-orphaned
```

✅ **Automated pipeline with force mode**:
```bash
# In automated scripts, skip confirmation
scripts\gzclean.cmd -e dev --clean-orphaned --force
```

### When NOT to Use

❌ **Don't run clean on fresh environment**:
- If environment directory doesn't exist, cleaner skips and reports success
- Run package module first to populate environment

❌ **Don't use --clean-all --force without dry-run preview**:
- Always preview with `--dry-run` first
- `--clean-all --force` is destructive and cannot be undone

❌ **Don't use --clean-all in production without backup**:
- Clean-all deletes everything in the environment
- Ensure you can regenerate content or have backups

## Module Maturity Checklist

This module meets all maturity criteria from `dev/01PROMPTS_MODULE_MATURITY.md`:

### Must Have (✅ All Present)
- ✅ Mandatory `-e` environment argument (dev/staging/prod)
- ✅ Uses `gzconfig` to read `config/pipeline.toml`
- ✅ Uses `gzlogging` for environment-aware logging
- ✅ Supports `--force` flag (for consistency with other modules)
- ✅ Supports `--dry-run` flag for safe preview
- ✅ Shell script launchers (`gzclean.cmd`, `gzclean.sh`)
- ✅ UTF-8 handling in scripts (PYTHONIOENCODING=utf-8)
- ✅ PYTHONPATH setup in shell scripts

### Should Have (✅ All Present)
- ✅ Structured console output with emojis
- ✅ Plain text log output (no emojis in log files)
- ✅ Error handling with descriptive messages
- ✅ Help text with examples (`--help`)
- ✅ Type hints for all functions
- ✅ Docstrings for all functions
- ✅ Module-level docstring

### Nice to Have (✅ All Present)
- ✅ Comprehensive README.md
- ✅ Usage examples in documentation
- ✅ Clear separation of concerns
- ✅ No circular dependencies
- ✅ Follows project conventions

## Changelog

### Version 1.2 (November 4, 2025)
- **Breaking Change**: Default behavior now only identifies orphaned files without removing them
- Added `--clean-orphaned` flag to explicitly remove orphaned files
- Added confirmation prompt for clean-orphaned mode (skipped with `--force`)
- Updated `--force` to work with both `--clean-orphaned` and `--clean-all` confirmations
- Enhanced safety by requiring explicit flag for file removal
- Updated documentation with new operating modes and examples

### Version 1.1 (October 24, 2025)
- Added `--clean-all` flag to remove ALL files from environment
- Added confirmation prompt for clean-all mode (skipped with `--force`)
- Updated `--force` to work with clean-all confirmation
- Added `remove_all_files()` function to API
- Enhanced documentation with clean-all examples

### Version 1.0 (October 23, 2025)
- Initial release
- Extracted orphaned file cleanup from package module
- Added environment-aware logging
- Implemented dry-run mode
- Created shell launcher scripts
- Added comprehensive documentation

## Future Enhancements

Potential improvements for future versions:

1. **Selective Cleaning**: Option to clean specific directories only
2. **Backup Before Clean**: Optional backup of orphaned files before removal
3. **Interactive Mode**: Prompt for confirmation before removing each file
4. **Report Generation**: Create detailed report of removed files
5. **Whitelist Support**: Configuration to preserve specific patterns from removal

## License

GPL v3.0

## Authors

- superguru
- gazorper

---

**Note**: This module is part of the GAZ Tank static site generator pipeline. For complete pipeline documentation, see `docs/` directory.
