# Site Setup Tool

Configuration tool for applying site.toml settings to project files. Reads configuration from `config/site.toml` and applies it to CSS, HTML, and JavaScript files without modifying the TOML file itself.

**Version:** 1.2  
**Last Updated:** October 28, 2025

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
  - [Setup Workflow](#setup-workflow)
  - [Interactive Wizard Flow](#interactive-wizard-flow)
- [Customisation](#customisation)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)
- [Authors](#authors)

## Purpose

The Setup Module applies configuration from `config/site.toml` to your project files. It reads the TOML configuration and updates CSS, HTML, and JavaScript files accordingly. The module does not modify `site.toml` itself - you must edit that file manually or with a text editor.

### Key Capabilities

1. **CSS Generation** - Creates `src/css/variables.css` from theme colors
2. **Site Branding** - Updates site name, tagline, and description in HTML/JS files
3. **Domain References** - Updates domain URLs across project files
4. **Image References** - Updates logo and favicon paths in HTML
5. **Feature Toggles** - Enables/disables syntax highlighting based on config
6. **File Tracking** - Copies modified files to environment directory
7. **Backup Management** - Creates timestamped backups with manifests

### Design Goals

- **Read-Only Config**: Never modifies `config/site.toml`
- **Timestamp-Aware**: Only updates files when needed (unless `--force`)
- **Environment-Aware**: Separate backups and file tracking per environment
- **Safe**: Creates backups before making changes
- **Auditable**: Detailed manifests of all file operations
- **Modular**: 8 focused modules for maintainability

## Build Pipeline

The setup tool runs as a **configuration application step** in the GAZTank pipeline, applying site.toml settings to project files before content generation.

### Pipeline Integration

```
┌─────────┐     ┌──────────┐     ┌─────────┐     ┌─────────┐
│  setup  │ --> │ generate │ --> │ gzlint  │ --> │ package │
│ (Apply) │     │ (Build)  │     │ (Check) │     │ (Deploy)│
└─────────┘     └──────────┘     └─────────┘     └─────────┘
```

### Typical Workflow

1. **Edit Config**: Manually edit `config/site.toml` with desired settings
2. **Apply Settings**: Run `setup -e dev` to apply config to project files
3. **Force Update**: Use `--force` to update all files regardless of timestamps
4. **Environment Deploy**: Use the separate `clean` module to reset environment directory

**Note:** Setup reads from `site.toml` and applies settings to source files, then copies modified files to the environment directory (`publish/<environment>/`).

## Logging

The setup module uses **console output with rich formatting** for user feedback, not traditional file logging.

### Output Modes

#### Default Mode:
- Color-coded sections and status messages
- Emojis for visual feedback (✓ ℹ ⚠ ✗)
- File operation progress
- Backup confirmations
- Copy statistics

#### Force Mode (`--force`):
- Streamlined output for automation
- Updates all files regardless of timestamps
- File operation summaries
- Manifest generation

### Console Output Example

```
============================================================
SITE SETUP TOOL
============================================================
Environment: dev

Reading configuration from config/site.toml...

Applying Configuration to Project Files
---------------------------------------
ℹ Backed up config to: publish\backups\config_dev_202510281314.zip
✓ CSS variables generated: src\css\variables.css
ℹ Updating domain references in all files...
✓ Updated branding: src\index.html
✓ Setup completed successfully!
```

**Design Decision:** Setup provides immediate console feedback for file operations. The generated manifest provides audit trails within backup archives.

## Usage

### Command Line

#### Using Launcher Scripts (Recommended):

Windows:
```cmd
.\scripts\setup_site.cmd -e dev                # Apply config (skip up-to-date files)
.\scripts\setup_site.cmd -e dev --force        # Update all files
.\scripts\setup_site.cmd -e staging            # Staging environment
```

Linux/Mac:
```bash
./scripts/setup_site.sh -e dev                 # Apply config (skip up-to-date files)
./scripts/setup_site.sh -e dev --force         # Update all files
./scripts/setup_site.sh -e staging             # Staging environment
```

### As a Module

#### Python module invocation:

```bash
# Using python -m (from project root)
python -m setup -e dev
python -m setup -e production --force

# Direct script (from project root)
python utils/setup/setup.py -e dev
```

#### Programmatic usage:

```python
# Import for automation
from setup import config_io, file_generators

# Load existing config
config = config_io.load_existing_config()

# Modify config dictionary (not saved to file)
config['site_name'] = 'New Site Name'
config['header_text_color'] = '#FFFFFF'

# Regenerate CSS variables from modified config
file_generators.generate_css_variables(config)

# Note: To persist changes, manually edit config/site.toml
```

## Command Line Arguments

### Required Arguments

| Argument | Short | Type | Description |
|----------|-------|------|-------------|
| `--environment` | `-e` | str | Target environment: `dev`, `staging`, or `prod` |

### Optional Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--force` | flag | False | Update all files regardless of timestamps |
| `--dry-run` | flag | False | Ignored (accepted for compatibility with other modules) |

### Argument Behavior

#### Environment (`-e`):
- **REQUIRED** for all operations
- Determines backup file naming: `config_<environment>_YYYYMMDDHHMM.zip`
- Specifies target directory: `publish/<environment>/`
- Maintains separate backup history per environment

#### Force (`--force`):
- Updates all files regardless of timestamps
- Copies all files to environment directory
- Useful for ensuring consistency or after manual config changes

#### Dry-run (`--dry-run`):
- Preview operations without making changes
- Not yet fully implemented
- Accepted for compatibility with build pipeline

### Examples

Show help:
```bash
python -m setup --help
```

Apply configuration (skip up-to-date files):
```bash
python -m setup -e dev
```

Force update all files:
```bash
python -m setup -e dev --force
```

Preview without changes (not fully implemented):
```bash
python -m setup -e dev --dry-run
```

### Parameter Combinations

#### Valid:
- `-e dev` (apply config, skip up-to-date files)
- `-e dev --force` (update all files)
- `-e dev --dry-run` (preview mode - not fully implemented)

## Module Structure

```
setup/
├── __init__.py           # Package initialization and exports
├── __main__.py           # Entry point for python -m setup
├── setup.py              # Main entry point (orchestration)
├── file_tracker.py       # Track and copy modified files to environment
├── ui_helpers.py         # Terminal colors and printing utilities
├── validators.py         # Input validation (colors, etc.)
├── backup_manager.py     # File backup and cleanup
├── config_io.py          # TOML config loading and saving
├── user_interaction.py   # Interactive prompts and wizard
├── file_generators.py    # CSS, HTML, and file updates
└── README.md             # This file
```

### Core Components

| File | Lines | Purpose |
|------|-------|---------|
| `setup.py` | ~150 | Main orchestration and argument parsing |
| `user_interaction.py` | ~400 | Validators and prompts (legacy - minimal use) |
| `config_io.py` | ~440 | TOML I/O operations (preserves comments) |
| `file_generators.py` | ~1,220 | File generation and updates (CSS, HTML) |
| `file_tracker.py` | ~837 | File tracking, copying, manifest generation |
| `ui_helpers.py` | ~120 | Terminal UI utilities (colors, formatting) |
| `backup_manager.py` | ~125 | Backup creation and cleanup |
| `validators.py` | ~65 | Input validation (hex colors, domains) |
| `__init__.py` | ~75 | Package exports |
| `__main__.py` | ~16 | Module entry point |
| **Total** | **~3,498** | |

### Exports

The module exports the following for programmatic use:

```python
from setup import (
    # UI Helpers
    Colors, print_header, print_section, print_success,
    print_error, print_warning, print_info,
    
    # Validators
    get_color, hex_to_rgba,
    
    # Backup Manager
    create_backup, cleanup_old_backups,
    
    # Config I/O
    load_existing_config, backup_all_config_files,
    
    # User Interaction
    get_input, get_yes_no, interactive_setup,
    
    # File Generators
    generate_css_variables, update_domain_references,
    update_image_references, update_stylesheet_integration,
    update_site_branding,
    
    # File Tracker
    track_modified_file, get_modified_files,
    clear_tracked_files, copy_modified_files_to_environment,
)
```

## Features

### 1. Configuration Application

Reads `config/site.toml` and applies settings to project files:

#### CSS Generation (src/css/variables.css):
- Auto-generated from theme colors
- Includes all color definitions
- RGB + Alpha variations calculated automatically
- Timestamp and regeneration instructions in header

#### Domain Updates:
- `src/index.html`: canonical, og:url, meta tags
- `src/robots.txt`: domain references
- `src/humans.txt`: domain references
- Documentation files: links and examples

#### Site Branding:
- Site name in `README.md`, `index.html`, `humans.txt`
- Consistent branding across all files
- Automated updates prevent inconsistencies

#### Image References:
- Logo and favicon paths in HTML
- `srcset` attributes for responsive images
- Logo alt text for accessibility

#### Syntax Highlighting:
- Adds/removes Prism.js references based on config toggle
- Updates CSS and script tags in HTML
- Theme integration

#### Stylesheet Integration:
- Injects CSS variable imports into `styles.css`
- Ensures proper import order
- Prevents duplicate imports

### 2. Configuration Management

#### TOML Preservation:
- Uses `tomlkit` library to read TOML
- Never modifies `config/site.toml`
- Manual editing required for config changes

#### Backup System:
- Timestamped backups: `config_<environment>_YYYYMMDDHHMM.zip`
- Includes all config files from `config/` directory
- Separate backup history per environment
- Keeps 5 most recent backups per environment
- Automatic cleanup of old backups
- Manifest included in backup archive

#### Local Backups:
- Creates `.backup.TIMESTAMP` copies before modifications
- Located next to original files in `src/`
- Provides immediate rollback capability

### 3. File Tracking and Copying

#### Modification Tracking:
- Tracks all files modified during setup
- Includes source files, images, and generated files
- Maintains file paths and timestamps

#### Environment Copying:
- Copies modified files to `publish/<environment>/`
- Preserves directory structure
- Timestamp comparison (skip up-to-date files unless `--force`)
- Handles favicon and logo files separately

#### Manifest Generation:
- Creates `setup_manifest.md` for each run
- Two tables: copied files and skipped files
- Columns: Source Path, Filename, Destination Path, Size, Modified
- Smart sorting: files before subdirectories
- Paths relative to common root with leading separator
- Timestamps with timezone offset
- Included in backup ZIP for audit trail

## Configuration

### Site Configuration

Primary configuration file: `config/site.toml`

**Important:** Setup reads this file but never modifies it. You must edit `config/site.toml` manually with a text editor to change configuration values.

Contains all site settings:
- Site information (name, domain, description)
- Theme colors (header, footer, sidebar)
- Image paths (logos, favicons)
- Feature toggles (breadcrumbs, TOC, lazy loading)
- SEO and analytics codes

#### Example:
```toml
# Site Information
site_name = "GAZTank"
site_tagline = "Your Site Tagline"
domain = "example.com"

# Theme Colors
header_text_color = "#212529"
header_background_color = "#f8f9fa"
footer_text_color = "#6c757d"

# Features
enable_breadcrumbs = true
enable_toc = true
enable_lazy_loading = true
```

### Environment Configuration

Environment directories configured in `config/pipeline.toml`:

```toml
[environments.dev]
dir = "dev"
description = "Development environment"

[environments.staging]
dir = "staging"
description = "Staging environment for pre-production testing"

[environments.prod]
dir = "prod"
description = "Production-ready build"
```

### Directory Structure

```
GAZTank/
├── config/
│   ├── site.toml                    # Main site configuration
│   ├── site.toml.backup.TIMESTAMP   # Local backups
│   └── pipeline.toml                # Environment definitions
├── publish/
│   ├── backups/
│   │   ├── config_dev_202510221430.zip
│   │   ├── config_staging_202510221430.zip
│   │   └── config_prod_202510221430.zip
│   ├── dev/                         # Dev environment files
│   ├── staging/                     # Staging environment files
│   └── prod/                        # Prod environment files
└── src/
    ├── css/
    │   ├── variables.css            # Generated CSS variables
    │   └── styles.css               # Main stylesheet (updated)
    ├── images/
    │   ├── logos/                   # Logo files
    │   └── favicons/                # Favicon files
    └── index.html                   # Updated with branding
```

## Invocation Points

### 1. Shell Scripts (Recommended)

Windows:
```powershell
.\scripts\setup_site.cmd -e dev
```

Linux/Mac:
```bash
./scripts/setup_site.sh -e dev
```

### 2. Python Module

```bash
python -m setup -e dev
```

### 3. Programmatic

```python
from setup import config_io, file_generators

config = config_io.load_existing_config()
# Note: Direct config writing is handled by specific functions like update_canonical_base()
# To update site.toml, edit the file directly or use gzconfig module (future)
file_generators.generate_css_variables(config)
```

### 4. Build Automation

```bash
# In gzbuild.cmd or CI/CD pipeline
.\scripts\setup_site.cmd -e staging --force
.\scripts\generate.cmd -e staging
.\scripts\package.cmd -e staging
```

## Development

### Setup Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                  SETUP INITIALIZATION                       │
├─────────────────────────────────────────────────────────────┤
│  [1/3] Parse Arguments                                      │
│     └─ Validate -e (required)                               │
│     └─ Check --force flag                                   │
│     └─ Validate parameter combinations                      │
│                                                             │
│  [2/3] Load Configuration                                   │
│     └─ Read config/site.toml                                │
│     └─ Validate configuration structure                     │
│     └─ Display environment and mode                         │
│                                                             │
│  [3/3] File Operations                                      │
│     └─ Backup config files                                  │
│     └─ Generate files (CSS, HTML updates)                   │
│     └─ Track modified files                                 │
│     └─ Copy to environment directory                        │
│     └─ Generate manifest                                    │
│     └─ Cleanup old backups                                  │
└─────────────────────────────────────────────────────────────┘
```

### Configuration Application Flow

```
Read site.toml → Validate Config → Apply to Files
     ↓
1. Backup Config Files
   └─ Create timestamped ZIP with all config files
   └─ Skip .backup.* and .example.* files

2. Generate CSS Variables
   └─ Create src/css/variables.css
   └─ Calculate RGB + alpha variations

3. Update Domain References
   └─ Search and replace in HTML, JS, TXT, MD files

4. Update Site Branding
   └─ Replace site name across multiple files

5. Update Image References
   └─ Update logo/favicon paths in HTML

6. Update Syntax Highlighting
   └─ Add/remove Prism.js references

7. Update Stylesheet Integration
   └─ Inject variable imports into styles.css

8. Copy Modified Files
   └─ Track all modified files
   └─ Copy to publish/<environment>/
   └─ Generate manifest

9. Cleanup
   └─ Remove old backups (keep 5 most recent)
```

### Module Architecture

The setup was refactored from a 1,575-line monolith into 9 focused modules:

#### Benefits:
- ✅ Single Responsibility Principle
- ✅ Easy to locate functionality
- ✅ Smaller, understandable files
- ✅ Changes isolated to specific modules
- ✅ Can test each module independently
- ✅ Modules reusable in other scripts
- ✅ Non-interactive, configuration-driven approach

## Customisation

### Custom Validators

Add new validation functions in `validators.py`:

```python
from . import ui_helpers

def get_email(prompt, default, get_input_fn):
    """Get and validate email address"""
    while True:
        value = get_input_fn(prompt, default)
        if '@' in value and '.' in value:
            return value
        ui_helpers.print_error("Invalid email format")
```

### Custom File Generators

Add new generators in `file_generators.py`:

```python
def update_email_template(config_data):
    """Update email template with config values"""
    template_path = Path('src/templates/email.html')
    content = template_path.read_text(encoding='utf-8')
    content = content.replace('{{SITE_NAME}}', config_data['site_name'])
    template_path.write_text(content, encoding='utf-8')
    track_modified_file(template_path)
```

### Extend Backup System

Customize backup behavior in `backup_manager.py`:

```python
# Change number of backups to keep
cleanup_old_backups(keep_count=10, environment='dev')

# Exclude additional file patterns
def should_skip_file(file_path):
    name = file_path.name
    return (name.endswith('.backup') or 
            name.endswith('.example') or
            name.endswith('.secret'))
```

## Troubleshooting

### Config File Not Found

**Problem:** `Failed to load config/site.toml`

#### Solution:
```bash
# Create from example if available
cp config/site.toml.example config/site.toml

# Or verify path
ls config/site.toml
```

### Config File Corrupted

**Problem:** TOML parsing errors

#### Solution 1 - Restore from local backup:
```bash
cd config
cp site.toml.backup.YYYYMMDDHHMM site.toml
```

#### Solution 2 - Restore from ZIP backup:
```bash
cd publish/backups
unzip config_dev_YYYYMMDDHHMM.zip -d restored
cd restored
cp site.toml ../../../config/
```

#### Solution 3 - Start fresh:
```bash
cp config/site.toml.example config/site.toml
.\scripts\setup_site.cmd -e dev
```

### Files Not Copying to Environment

**Problem:** Modified files not appearing in `publish/<environment>/`

#### Solution:
- Check that environment exists in `config/pipeline.toml`
- Verify source files were actually modified
- Use `--force` to copy regardless of timestamps
- Check console output for error messages

### Backups Not Created

**Problem:** No backup ZIP files in `publish/backups/`

#### Solution:
- Check `publish/backups/` directory exists
- Verify write permissions
- Check disk space
- Look for error messages in console output

### Import Errors After Update

**Problem:** `ImportError` or `AttributeError` after module changes

#### Solution:
```bash
# Clear Python cache
cd utils/setup
Remove-Item -Recurse -Force __pycache__

# Re-run setup
cd ../..
.\scripts\setup_site.cmd -e dev
```

## Best Practices

### 1. Edit site.toml First

Always edit `config/site.toml` before running setup:

```bash
# Edit configuration manually
notepad config\site.toml  # Windows
nano config/site.toml      # Linux/Mac

# Then apply changes
.\scripts\setup_site.cmd -e dev
```

### 2. Use Environments Appropriately

- **dev**: For active development and testing
- **staging**: For pre-production validation
- **prod**: For final production builds

```bash
# Development
.\scripts\setup_site.cmd -e dev

# Staging validation
.\scripts\setup_site.cmd -e staging

# Production deployment
.\scripts\setup_site.cmd -e prod
```

### 3. Backup Before Manual Changes

While backups are automatic, consider manual backups before major changes:

```bash
# Manual backup of config
cd config
copy site.toml site.toml.manual.backup  # Windows
cp site.toml site.toml.manual.backup    # Linux/Mac
```

### 4. Use Force Mode After Manual Edits

After editing source files manually, use `--force` to ensure consistency:

```bash
# Made manual changes to src/css/styles.css
.\scripts\setup_site.cmd -e dev --force
```

### 5. Verify Configuration Format

Ensure your site.toml is valid TOML before running setup:

```bash
# Use a TOML validator or linter
python -c "import tomlkit; tomlkit.load(open('config/site.toml'))"
```

### 6. Test After Configuration

After running setup, test the changes:

```bash
.\scripts\setup_site.cmd -e dev
.\scripts\generate.cmd -e dev
.\scripts\server.cmd -e dev
# Open browser to http://localhost:7190
```

### 7. Keep Backups Organized

Backup system automatically maintains 5 most recent per environment:
- `config_dev_*.zip` - Development backups
- `config_staging_*.zip` - Staging backups
- `config_prod_*.zip` - Production backups

### 8. Clean Environment When Needed

Use the separate `clean` module to reset environment:
```bash
# Clean orphaned files
.\scripts\clean.cmd -e dev

# Clean all files (full reset)
.\scripts\clean.cmd -e dev --clean-all
```

### 9. Document Configuration Changes

When editing site.toml, add comments to document changes:
```toml
# config/site.toml
# Custom modification: Changed header color for better contrast
# Date: 2025-10-28
# Reason: Accessibility improvement
header_background_color = "#1a1a1a"
```

### 10. Use Version Control

Commit site.toml changes to track configuration history:
```bash
git add config/site.toml
git commit -m "Update header colors for better contrast"
```

## Future Enhancements

- [ ] Add `--dry-run` mode to preview changes without applying
- [ ] Support for dark mode theme configuration
- [ ] Configuration validation command
- [ ] Diff view showing what will be changed
- [ ] Rollback to specific backup by timestamp
- [ ] Custom CSS injection from config
- [ ] Font configuration from TOML
- [ ] Multi-site configuration management
- [ ] Configuration templates (blog, portfolio, documentation)
- [ ] Automated accessibility checks for color contrast
- [ ] Real-time preview during development
- [ ] Configuration API for external tools

## Related Documentation

- **[clean](../clean/README.md)** - Environment cleanup (orphaned files and full reset)
- **[gzlogging](../gzlogging/README.md)** - Logging infrastructure (not used in setup - see design decision)
- **[generate](../generate/README.md)** - Content generation (runs after setup)
- **[package](../package/README.md)** - Build system with minification
- **[deploy](../deploy/README.md)** - Deployment to production
- **[gzserve](../gzserve/README.md)** - Local development server for testing
- **[FLOW_PIPELINE.md](../FLOW_PIPELINE.md)** - Complete pipeline documentation
- **[00MODULE_MATURITY.md](../00MODULE_MATURITY.md)** - Module maturity tracking
- **[MODULE_README_STRUCTURE.md](../../dev/MODULE_README_STRUCTURE.md)** - README template structure

### Pipeline Context

```
clean → [setup] → generate → gzlint → gzserve → package → deploy
          ↑
   (configuration application)
```

## License

GPL v3.0 or later

## Authors

- superguru
- gazorper

---

**Site Setup Tool v1.2** | **Last Updated:** October 28, 2025
