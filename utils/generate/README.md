# Static Content Generator

Environment-aware static content generation system that converts source files to HTML based on file type and outputs to specified environment directory. Reads `generate.toml` configuration and delegates to appropriate converters.

**Version:** 2.0  
**Last Updated:** October 23, 2025

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
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)

## Purpose

The Static Content Generator provides a flexible, environment-aware approach to converting source content into HTML for the GAZTank static site. It acts as an orchestrator that:

- Reads file groups from `config/generate.toml`
- Routes files to appropriate converters based on `input_type`
- Outputs to environment-specific directories (`publish/{environment}/content/`)
- Uses `gzconfig` to read pipeline configuration for environment directories
- Manages the conversion workflow for multiple file groups
- Provides intelligent timestamp-based regeneration (only converts when needed)
- Integrates with the build pipeline for automated content generation

### Environment-Aware Output

The generator requires a mandatory `-e` argument to specify the target environment:
- **dev** - Outputs to `publish/dev/content/`
- **staging** - Outputs to `publish/staging/content/`
- **prod** - Outputs to `publish/prod/content/`

Environment directories are configured in `config/pipeline.toml` and accessed via `gzconfig`.

### Supported Input Types

Currently supported:
- **markdown** - Converts `.md` files to HTML using the `md_to_html` module

Future extensibility for other types (e.g., ReStructuredText, AsciiDoc, etc.)

## Build Pipeline

The generator is a key component of the GAZTank content generation pipeline:

```
Content Generation Pipeline:
  1. Receive environment parameter (-e dev/staging/prod)
  2. Read generate.toml configuration
  3. Use gzconfig to get environment directory from pipeline.toml
  4. For each [[group]] in configuration:
     a. Validate input_type attribute
     b. Route to appropriate converter (e.g., md_to_html)
     c. Process each file in group:
        - Check if regeneration needed (timestamp comparison)
        - Normalise source structure (markdown only)
        - Convert to HTML
        - Write to publish/{environment}/content/{output_dir}/
  5. Report statistics (converted, skipped, failed)
  6. Return exit code for build automation
```

**Purpose:** Orchestrates environment-aware multi-format content generation

**Location:** Called directly via `scripts/generate.cmd -e <env>` or as part of larger build workflows

### Workflow:
```
-e environment → pipeline.toml → generate.toml → generate.py → delegates to converters → outputs to publish/{env}/content/
```

### Benefits:
- Environment-specific output directories
- Single command to regenerate all site content for an environment
- Intelligent timestamp checking (skip up-to-date files)
- Configuration-driven (add new groups without code changes)
- Extensible architecture for future input types
- Comprehensive logging and error handling

## Logging

The generator uses the **gzlogging** infrastructure for environment-aware operational logging.

### Log Configuration

- **Environment:** Specified via `-e` argument (dev/staging/prod)
- **Tool Name:** `generate`
- **Log Location:** `logs/{environment}/generate_YYYYMMDD.log`
- **Output Mode:** File-only (console has its own formatting)
- **Encoding:** UTF-8

### What Gets Logged

#### Logged to file (clean operational log):
- Static Content Generator started
- Environment specified
- Mode settings (DRY RUN MODE enabled, FORCE MODE enabled if applicable)
- Project root path
- Configuration file loaded
- Groups found and processed count
- Each file conversion or skip status with paths
- Group completion with statistics (converted, skipped counts)
- Overall generation summary
- Static Content Generator completed successfully
- Errors and warnings

#### Console output (rich formatting with emojis):
- Section headers with separators (============)
- Mode indicators: ⚠️ DRY RUN MODE, 🔄 FORCE MODE
- Progress indicators: 📁 📄 📋 📝 for different stages
- Success/failure indicators: ✅ ℹ️ ❌ ⚠️
- Statistics summary in formatted box
- Blank lines for visual spacing
- User-facing progress messages

#### Not logged (kept clean):
- No blank lines in log files
- No separator lines (===) in logs
- No emoji or formatting characters in log files

### Log File Example

```log
[2025-10-22 13:54:57] [dev] [INF] Static Content Generator started
[2025-10-22 13:54:57] [dev] [INF] FORCE MODE enabled
[2025-10-22 13:54:57] [dev] [INF] Project root: D:\Projects\www\GAZTank
[2025-10-22 13:54:57] [dev] [INF] Loaded configuration from D:\Projects\www\GAZTank\config\generate.toml
[2025-10-22 13:54:57] [dev] [INF] Found 1 groups in configuration
[2025-10-22 13:54:57] [dev] [INF] Processing markdown group 'website_setup_docs' with 7 files to src/content/setup
[2025-10-22 13:54:57] [dev] [INF] Converted SETUP_SITE.md to src\content\setup\SETUP_SITE.html
[2025-10-22 13:54:57] [dev] [INF] Converted DESIGN_RULES.md to src\content\setup\DESIGN_RULES.html
[2025-10-22 13:54:57] [dev] [INF] Converted DEVELOPER_SETUP.md to src\content\setup\DEVELOPER_SETUP.html
[2025-10-22 13:54:57] [dev] [INF] Converted SEO_IMPLEMENTATION.md to src\content\setup\SEO_IMPLEMENTATION.html
[2025-10-22 13:54:57] [dev] [INF] Converted RESPONSIVE_IMAGES.md to src\content\setup\RESPONSIVE_IMAGES.html
[2025-10-22 13:54:57] [dev] [INF] Converted README.md to src\content\setup\README.html
[2025-10-22 13:54:57] [dev] [INF] Converted PROJECT_STRUCTURE.md to src\content\setup\PROJECT_STRUCTURE.html
[2025-10-22 13:54:57] [dev] [INF] Group 'website_setup_docs' completed: 7 converted, 0 skipped
[2025-10-22 13:54:57] [dev] [INF] Generation summary: 1/1 groups processed successfully, 0 skipped
[2025-10-22 13:54:57] [dev] [INF] Static Content Generator completed successfully
```

In dry-run mode, logs show what would be done:

```log
[2025-10-22 13:54:14] [dev] [INF] Static Content Generator started
[2025-10-22 13:54:14] [dev] [INF] DRY RUN MODE enabled
[2025-10-22 13:54:14] [dev] [INF] FORCE MODE enabled
[2025-10-22 13:54:14] [dev] [INF] Project root: D:\Projects\www\GAZTank
[2025-10-22 13:54:14] [dev] [INF] Loaded configuration from D:\Projects\www\GAZTank\config\generate.toml
[2025-10-22 13:54:14] [dev] [INF] Found 1 groups in configuration
[2025-10-22 13:54:14] [dev] [INF] Processing markdown group 'website_setup_docs' with 7 files to src/content/setup
[2025-10-22 13:54:14] [dev] [INF] [DRY RUN] Would convert SETUP_SITE.md to src\content\setup\SETUP_SITE.html
[2025-10-22 13:54:14] [dev] [INF] [DRY RUN] Would convert DESIGN_RULES.md to src\content\setup\DESIGN_RULES.html
[2025-10-22 13:54:14] [dev] [INF] [DRY RUN] Group 'website_setup_docs': 7 would be converted, 0 skipped
[2025-10-22 13:54:14] [dev] [INF] [DRY RUN] Summary: 1/1 groups would be processed, 0 skipped
[2025-10-22 13:54:14] [dev] [INF] Static Content Generator completed successfully
```

### Viewing Logs

```bash
# View today's log (Linux/Mac)
cat logs/dev/generate_$(date +%Y%m%d).log

# View today's log (PowerShell)
Get-Content "logs\dev\generate_$(Get-Date -Format 'yyyyMMdd').log"

# Tail recent entries
Get-Content -Tail 20 "logs\dev\generate_$(Get-Date -Format 'yyyyMMdd').log"
```

## Usage

### Command Line

```bash
# Using the launcher script (recommended)
scripts\generate.cmd -e dev                    # Windows - dev environment
scripts\generate.cmd -e staging                # Windows - staging environment
scripts\generate.cmd -e prod                   # Windows - production environment
./scripts/generate.sh -e dev                   # Linux/Mac - dev environment

# With command-line options
scripts\generate.cmd -e dev --force            # Force regeneration of all files
scripts\generate.cmd -e dev --dry-run          # Preview without making changes
scripts\generate.cmd -e dev --force --dry-run  # Preview force regeneration

# Direct invocation
python -m generate -e dev
python -m generate -e staging --force
python -m generate -e prod --dry-run
python -m generate --help
```

#### Launcher Scripts:
- `scripts/generate.cmd` - Windows launcher with UTF-8 encoding
- `scripts/generate.sh` - Linux/Mac launcher with UTF-8 encoding

Both scripts:
- Set `PYTHONIOENCODING=utf-8` for emoji support in console
- Call `python -m generate` module pattern
- Pass all arguments (including `-e environment`) through to the Python module
- Return the module's exit code for build automation

### As a Module

You can import and use the generator functions in your own Python scripts:

```python
from utils.generate.generate import process_groups
from utils.gzconfig import get_generate_config

# Get configuration for specific environment
config = get_generate_config('dev')

# Process all groups with options
exit_code = process_groups(environment='dev', force=False, dry_run=False)

if exit_code == 0:
    print("All content generated successfully")
else:
    print("Some content generation failed")
```

For processing individual markdown groups:

```python
from pathlib import Path
from utils.generate.generate import process_markdown_group
from utils.gzconfig import get_generate_config

# Get configuration
config = get_generate_config('dev')
project_root = Path(__file__).parent.parent.parent

# Process a specific group
for group in config.groups:
    if group.name == 'my_docs':
        success = process_markdown_group(
            group, 
            project_root, 
            environment='dev',
            force=True, 
            dry_run=False
        )
        
        if success:
            print(f"Group {group.name} processed successfully")
```

## Command Line Arguments

### Required Arguments

- **`-e`, `--environment`** - Target environment for content generation (REQUIRED)
  - **Choices:** `dev`, `staging`, `prod`
  - **Purpose:** Specifies which environment directory to output content to
  - **Output:** Content is written to `publish/{environment}/content/`
  - **Examples:**
    - `-e dev` → outputs to `publish/dev/content/`
    - `-e staging` → outputs to `publish/staging/content/`
    - `-e prod` → outputs to `publish/prod/content/`

### Optional Arguments

- **`--force`** - Force regeneration of all files, ignoring timestamps
  - Regenerates all files even if output is newer than input
  - Useful for full rebuilds or when templates change
  - Example: `scripts\generate.cmd --force`

- **`--dry-run`** - Show what would be done without making changes
  - Performs all analysis and decision-making
  - Displays detailed preview of conversions/skips
  - Does not write any output files
  - Does not modify any files
  - Useful for testing configuration changes
  - Example: `scripts\generate.cmd --dry-run`

- **`--help`** - Display usage information and examples
  - Shows all available command-line options
  - Provides usage examples
  - Example: `python -m generate --help`

### Argument Combinations

```bash
# Default mode: Smart regeneration based on timestamps
scripts\generate.cmd

# Force regenerate all files
scripts\generate.cmd --force

# Preview what would be regenerated
scripts\generate.cmd --dry-run

# Preview force regeneration
scripts\generate.cmd --force --dry-run
```

### Console Output Modes

#### Default mode:
```
============================================================
Static Content Generator
============================================================
📁 Project root: D:\Projects\www\GAZTank
📄 Loading configuration from: D:\Projects\www\GAZTank\config\generate.toml
📋 Found 2 group(s) in configuration

⏸️  Group 'developer_guides' is disabled - skipping

📝 Processing markdown group: website_setup_docs
   Output directory: publish\dev\content\setup
   Files to process: 3
   ...
```

#### With disabled groups in summary:
```
============================================================
GENERATION SUMMARY
============================================================
Total groups: 2
⏸️  Disabled: 1
✅ Processed successfully: 1
```

#### Dry-run mode:
```
============================================================
Static Content Generator
============================================================
⚠️  DRY RUN MODE enabled - No files will be modified
📁 Project root: D:\Projects\www\GAZTank
...
⚠️  DRY RUN MODE - No files were modified
```

#### Force mode:
```
============================================================
Static Content Generator
============================================================
🔄 FORCE MODE enabled - Regenerating all files
📁 Project root: D:\Projects\www\GAZTank
...
```

#### Force + Dry-run mode:
```
============================================================
Static Content Generator
============================================================
⚠️  DRY RUN MODE enabled - No files will be modified
🔄 FORCE MODE enabled - Regenerating all files
📁 Project root: D:\Projects\www\GAZTank
...
⚠️  DRY RUN MODE - No files were modified
```

## Module Structure

```
generate/
├── __init__.py      # Package initialization
├── generator.py     # Main orchestrator (this module)
├── md_to_html.py    # Markdown-to-HTML converter
└── README.md        # This file
```

### Key Functions

#### generator.py

- **`main()`** - Entry point for command-line usage with argument parsing
- **`get_project_root()`** - Returns project root directory Path
- **`load_config(config_path)`** - Loads and parses generate.toml configuration
- **`process_groups(config, project_root, force, dry_run)`** - Processes all groups, returns exit code
- **`process_markdown_group(group, project_root, force, dry_run)`** - Handles markdown file group conversion

#### md_to_html.py

- **`MarkdownConverter(dry_run, normalize, force)`** - Class for converting markdown files with options
  - `convert(input_path, output_path)` - Convert a single markdown file to HTML
  - `fix_image_paths(html_content)` - Adjusts image references for content directory

## Features

### Core Features

- **Configuration-driven**: All file groups defined in `generate.toml`
- **Enable/disable groups**: Optional `enabled` flag to selectively process groups
- **Path transformation**: Flexible output path control with `path_transform` directive
  - `flatten` - Use only filenames (default)
  - `preserve_parent` - Keep immediate parent directory
  - `preserve_all` - Keep full directory structure
  - `strip_prefix` - Remove common prefix then use remaining path
- **Timestamp-aware**: Only regenerates files when source is newer than output
- **Force mode**: `--force` flag to regenerate all files regardless of timestamps
- **Dry-run mode**: `--dry-run` flag to preview changes without modifying files
- **Multi-group support**: Process multiple file groups with different output directories
- **Type routing**: Routes to appropriate converter based on `input_type`
- **Error handling**: Continues processing other files if one fails
- **Detailed statistics**: Reports converted, skipped, disabled, and failed counts
- **Exit codes**: Returns proper exit codes for build automation (0 success, 1 failure)
- **Integrated logging**: Uses gzlogging for clean audit trails
- **Command-line help**: `--help` displays usage information and examples
- **UTF-8 support**: Full Unicode and emoji support in console output
- **Rich console output**: Visual indicators with emojis for better UX
- **Clean log files**: Operational logs without formatting or blank lines

### Intelligent Regeneration

The generator compares input file modification time with output file modification time:

- **Regenerate**: When input is newer than output, or output doesn't exist
- **Skip**: When output exists and is newer than or same age as input
- **Force regeneration**: Use `--force` flag to regenerate all files regardless of timestamps
- **Preview mode**: Use `--dry-run` flag to see what would be done without making changes

This dramatically improves performance for large documentation sets.

### Dry-Run Mode

The `--dry-run` flag provides accurate preview without modifications:

#### What it does:
- Scans all configured file groups
- Checks timestamps (unless `--force` is used)
- Decides which files would be converted vs. skipped
- Displays detailed messages: "[DRY RUN] Would normalize and convert: ..."
- Shows accurate statistics: "would be converted", "already up-to-date"
- Logs all decisions with `[DRY RUN]` prefix

#### What it doesn't do:
- Write any output files
- Modify any source files
- Create any directories
- Change file timestamps
- Perform actual conversions

#### Use cases:
- Test configuration changes before committing
- Verify file selection and routing
- Understand which files are outdated
- Preview impact of `--force` flag
- Debug generation issues safely

### Extensible Architecture

The module is designed for future expansion:

```python
# Current: markdown routing
if input_type == 'markdown':
    success = process_markdown_group(group, project_root, force, dry_run)

# Future: Add more input types
elif input_type == 'restructuredtext':
    success = process_rst_group(group, project_root, force, dry_run)
elif input_type == 'asciidoc':
    success = process_asciidoc_group(group, project_root, force, dry_run)
```

## Configuration

The generator reads `config/generate.toml` which defines file groups.

### Configuration Structure

```toml
[[group]]
name = "group_identifier"           # Required: Unique name for this group
enabled = true                       # Optional: Enable/disable group (default: false)
input_type = "markdown"              # Required: Type of input files
output_dir = "destination/path"      # Required: Relative to content/
files = [                            # Required: List of input files
    "path/to/file1.md",
    "path/to/file2.md",
]
```

### Configuration Attributes

#### Required:
- `name` - Descriptive name for the group (used in logs and output)
- `input_type` - Type of input files (currently only `"markdown"` is supported)
- `output_dir` - Directory path relative to `content/` where HTML files will be saved
- `files` - List of input files relative to project root

#### Optional:
- `enabled` - Boolean flag to enable/disable the group (default: `false` if not specified)
  - Set to `true` to process this group
  - Set to `false` or omit entirely to skip the group
  - Useful for temporarily disabling groups without deleting configuration
- `path_transform` - How to transform input file paths to output paths (default: `"flatten"`)
  - `"flatten"` - Use only the filename, ignore directory structure
    - Example: `utils/clean/README.md` → `{output_dir}/README.html`
  - `"preserve_parent"` - Keep immediate parent directory from input path
    - Example: `utils/clean/README.md` → `{output_dir}/clean/README.html`
    - Example: `utils/README.md` → `{output_dir}/README.html` (no parent)
  - `"preserve_all"` - Keep full relative directory structure from input
    - Example: `utils/clean/README.md` → `{output_dir}/utils/clean/README.html`
  - `"strip_prefix"` - Remove `strip_path_prefix` then use remaining path
    - Example: `utils/README.md` → `{output_dir}/README.html` (with `strip_path_prefix = "utils/"`)
    - Example: `utils/clean/README.md` → `{output_dir}/clean/README.html` (with `strip_path_prefix = "utils/"`)
  - Useful for organizing output files when multiple input files share the same filename
- `strip_path_prefix` - Path prefix to remove when `path_transform = "strip_prefix"` (default: `""`)
  - Removes the specified prefix from all file paths before applying directory structure
  - Example: `strip_path_prefix = "utils/"` removes "utils/" from paths
  - Only used when `path_transform` is set to `"strip_prefix"`

### Example Configuration

```toml
# Active documentation group (default flatten behavior)
[[group]]
name = "website_setup_docs"
enabled = true
input_type = "markdown"
output_dir = "setup"
files = [
    "docs/SETUP_SITE.md",      # → setup/SETUP_SITE.html
    "docs/DESIGN_RULES.md",    # → setup/DESIGN_RULES.html
    "README.md",               # → setup/README.html
]

# Pipeline docs with prefix stripping
[[group]]
name = "pipeline_docs"
enabled = true
input_type = "markdown"
output_dir = "pipeline-docs"
path_transform = "strip_prefix"
strip_path_prefix = "utils/"
files = [
    "utils/README.md",         # → pipeline-docs/README.html
    "utils/clean/README.md",   # → pipeline-docs/clean/README.html
    "utils/deploy/README.md",  # → pipeline-docs/deploy/README.html
]

# Temporarily disabled developer guides
[[group]]
name = "developer_guides"
enabled = false
input_type = "markdown"
output_dir = "dev"
files = [
    "dev/MODULE_README_STRUCTURE.md",
]

# Nested API docs with full path preservation
[[group]]
name = "api_docs"
enabled = false
input_type = "markdown"
output_dir = "api"
path_transform = "preserve_all"
files = [
    "api/v1/endpoints.md",     # → api/api/v1/endpoints.html
    "api/v2/endpoints.md",     # → api/api/v2/endpoints.html
]
```

### Configuration Rules

- **Paths**: File paths relative to project root
- **Path separators**: Use forward slashes `/` (recommended) or backslashes `\\` (both work)
- **Output directory**: Relative to `src/content/` (no leading slash)
- **Multiple groups**: Add multiple `[[group]]` sections for organization
- **Comments**: Prefix with `#` (standard TOML syntax)

## Invocation Points

The generator is invoked from multiple places in the GAZTank project:

### 1. Direct Command-Line Usage

Users can run generate directly via launcher scripts:

```bash
# Windows
scripts\generate.cmd

# Linux/Mac
./scripts/generate.sh
```

**Purpose:** Manual regeneration of all configured content

**Location:** `scripts/generate.cmd` and `scripts/generate.sh`

### 2. Build System Integration

The generator is integrated into larger build workflows:

```bash
# Full pipeline build
scripts\gzbuild.cmd -e dev   # Windows
./scripts/gzbuild.sh -e dev  # Linux/Mac
```

**Purpose:** Automated content generation during full site builds

**Location:** Called by `scripts/gzbuild.*`

### 3. CI/CD Pipeline

Continuous integration systems call generate as part of deployment:

```yaml
# Example CI/CD step
- name: Generate Content
  run: scripts/generate.cmd
```

**Purpose:** Automated content generation during deployments

### Integration Points

| Component | Path | Description |
|-----------|------|-------------|
| **Launcher Scripts** | `scripts/generate.*` | Direct command-line access |
| **Configuration** | `config/generate.toml` | Defines what gets generated |
| **MD Converter** | `utils/generate/md_to_html.py` | Handles markdown conversion |
| **Normaliser** | `utils/normalise/` | Pre-processes markdown structure |
| **Logging** | `utils/gzlogging/` | Centralized logging infrastructure |
| **Output Directory** | `src/content/` | Generated HTML destination |

## Development

The module follows standard Python packaging conventions with a modular architecture for extensibility.

### File Locations

```
GAZTank/
├── config/
│   └── generate.toml                # Configuration file
│
├── logs/
│   └── dev/
│       └── generate_YYYYMMDD.log    # Daily log files
│
├── scripts/
│   ├── generate.cmd                 # Windows launcher
│   └── generate.sh                  # Linux/Mac launcher
│
├── src/
│   └── content/                     # Output directory for generated HTML
│       ├── setup/                   # Example output_dir
│       └── dev/                     # Another example output_dir
│
└── utils/
    ├── gzlogging/                   # Centralized logging system
    │
    ├── normalise/                   # Markdown normaliser (used by md_to_html)
    │
    └── generate/                    # This module
        ├── __init__.py              # Package initialization
        ├── generator.py             # Main orchestrator
        ├── md_to_html.py            # Markdown converter
        └── README.md                # This file
```

### Adding New Input Types

To add support for a new input type:

1. Create a converter function (e.g., `process_rst_group()`)
2. Add routing logic in `process_groups()`:
   ```python
   elif input_type == 'restructuredtext':
       success = process_rst_group(group, project_root, force, dry_run)
   ```
3. Follow the same signature pattern: `(group: Dict, project_root: Path, force: bool, dry_run: bool) -> bool`
4. Use the logging context for audit trails
5. Return `True` for success, `False` for failures
6. Support dry_run mode by checking flag before file writes

### Design Principles

- **Separation of concerns**: generator.py orchestrates, converters do the work
- **Configuration over code**: Add content groups via TOML, not Python code
- **Fail gracefully**: Continue processing other files/groups on error
- **Log everything**: Comprehensive audit trail for troubleshooting
- **Exit codes matter**: Return proper codes for build automation
- **Timestamp awareness**: Don't regenerate unless necessary
- **Dry-run support**: Preview changes without modifications
- **Clean logs**: Operational info only, no formatting in log files
- **Rich console**: User-friendly output with emojis and formatting

### Code Style

The module follows GAZTank Python coding standards:
- **UTF-8 encoding** with BOM markers in Python files
- **Type hints** where applicable (Path objects)
- **Docstrings** for all public functions
- **Clean logging** - no separators or blank lines in log files
- **Rich console** - emojis and formatting for user experience
- **Error handling** - try/except with proper logging
- **Exit codes** - 0 for success, 1 for failure

## Best Practices

### When to Run Generate

1. **After updating markdown documentation**
   - Run generate to update the HTML versions
   - Check console output for conversion statistics

2. **Before deploying site updates**
   - Ensure all content is regenerated
   - Part of the standard deployment workflow

3. **During development**
   - Run generate to test documentation changes
   - Use timestamp checking to speed up iterations
   - Use `--dry-run` to preview changes

### Working with Configuration

```toml
# Organize groups logically
[[group]]
name = "public_documentation"
input_type = "markdown"
output_dir = "docs"
files = ["docs/PUBLIC_*.md"]  # Note: Wildcards not supported yet

# Keep development docs separate
[[group]]
name = "developer_documentation"
input_type = "markdown"
output_dir = "dev"
files = ["dev/*.md"]  # Note: Must list files explicitly

# Use forward slashes (recommended) - works cross-platform
files = [
    "docs/SETUP.md",
    "dev/README.md",
]

# Backslashes also work (must be escaped in TOML)
files = [
    "docs\\SETUP.md",
    "dev\\README.md",
]
```

### Version Control Best Practices

- **Commit configuration changes**: Track `generate.toml` in version control
- **Don't commit generated HTML**: Generated files in `src/content/` can be rebuilt
- **.gitignore patterns**: Consider adding `src/content/**/*.html` if desired
- **Review logs**: Check log files when troubleshooting generation issues

### Performance Tips

- **Leverage timestamp checking**: The generator automatically skips up-to-date files
- **Use --dry-run first**: Preview changes before committing to regeneration
- **Force only when needed**: Use `--force` sparingly for full rebuilds
- **Group logically**: Organize file groups by update frequency
- **Monitor statistics**: Watch "converted vs skipped" counts
- **Touch source files**: Force regeneration of specific files: `(Get-Item README.md).LastWriteTime = Get-Date`

### Workflow Recommendations

```bash
# 1. Preview what needs updating
scripts\generate.cmd --dry-run

# 2. If satisfied, generate for real
scripts\generate.cmd

# 3. Force regenerate if templates changed
scripts\generate.cmd --force

# 4. Preview force regeneration first
scripts\generate.cmd --force --dry-run
```

## Troubleshooting

### Configuration File Not Found

**Problem:** `Configuration file not found: config/generate.toml`

#### Solution:
- Verify you're running from project root directory
- Check that `config/generate.toml` exists
- Use absolute path if needed: `D:\Projects\www\GAZTank\config\generate.toml`

### No Groups Found

**Problem:** `No groups found in configuration`

#### Solution:
- Open `config/generate.toml` and verify `[[group]]` sections exist
- Check TOML syntax (use TOML validator if needed)
- Ensure at least one group is uncommented

### Missing input_type Attribute

**Problem:** `Group 'name' is missing required 'input_type' attribute`

#### Solution:
- Add `input_type = "markdown"` to the group definition
- Check for typos: `input_type` not `inputtype` or `input-type`

### Unsupported input_type

**Problem:** `Group 'name' has unsupported input_type 'xyz'`

#### Solution:
- Currently only `markdown` is supported
- Check for typos in `input_type` value
- For other formats, wait for future enhancements or contribute a converter

### Input File Not Found

**Problem:** `Input file not found: path/to/file.md`

#### Solution:
- Verify file path is correct relative to project root
- Check for typos in filename or path
- Use correct path separators: `\\` for Windows in TOML
- Verify file actually exists: `ls path/to/file.md` or `dir path\to\file.md`

### All Files Skipped

**Problem:** All files report "Skipped (up-to-date)" but you expected conversions

**Cause:** Output HTML files are newer than source markdown files

#### Solution:
- Use `--force` flag to regenerate all files: `scripts\generate.cmd --force`
- Preview with dry-run first: `scripts\generate.cmd --force --dry-run`
- Touch source files to make them newer: `(Get-Item README.md).LastWriteTime = Get-Date`
- Delete output HTML files to force regeneration

### Dry-Run Shows Different Results

**Problem:** Dry-run shows files would be converted, but normal run skips them

#### Diagnosis:
- This shouldn't happen - dry-run uses same logic as normal mode
- Check if files were modified between dry-run and normal run
- Review log file for timestamp details

#### Solution:
- Run dry-run immediately before normal run
- Use `--force` if timestamp issues persist
- Check system clock accuracy

### Conversion Failures

**Problem:** Some files fail to convert

#### Diagnosis:
- Check console output for specific error messages
- Review log file: `logs/dev/generate_YYYYMMDD.log`
- Look for markdown syntax issues in source files

#### Solution:
- Fix markdown syntax errors
- Ensure required dependencies installed (mistune, beautifulsoup4)
- Check file permissions (read source, write destination)

### Permission Denied

**Problem:** `PermissionError: [Errno 13] Permission denied`

#### Solution:
- Check write permissions on `src/content/` directory
- Ensure output files aren't open in another program
- Close any editors viewing generated HTML files
- Run with appropriate permissions (avoid running as admin unless necessary)

### TOML Import Error

**Problem:** `TOML library not available`

#### Solution for Python 3.11+:
- Built-in `tomllib` should work
- Upgrade Python: `python --version`

#### Solution for Python < 3.11:
- Install tomli: `pip install tomli`
- Verify installation: `python -c "import tomli"`

### Emojis Not Displaying

**Problem:** Console shows squares or question marks instead of emojis

#### Solution:
- Launcher scripts set `PYTHONIOENCODING=utf-8` automatically
- Ensure terminal supports UTF-8 encoding
- On Windows: Use Windows Terminal or PowerShell 7+
- Check terminal font supports emoji glyphs

## Future Enhancements

### Completed Features

- ✅ **Force mode**: `--force` flag to regenerate all files regardless of timestamps (v1.1)
- ✅ **Dry-run mode**: `--dry-run` flag to preview changes without making modifications (v1.1)
- ✅ **Command-line help**: `--help` displays usage information and examples (v1.1)
- ✅ **UTF-8 support**: Proper encoding handling in launcher scripts and module (v1.1)
- ✅ **Module invocation**: Support for `python -m generate` pattern (v1.1)
- ✅ **Path flexibility**: Support for both forward slashes and backslashes in config (v1.2)
- ✅ **Rich console output**: Emojis and visual indicators for better UX (v1.2)
- ✅ **Clean logging**: Operational logs without formatting or separators (v1.2)
- ✅ **Accurate dry-run**: Correct preview with "[DRY RUN] Would convert" messaging (v1.2)

### Planned Features

- **Group selection**: Ability to generate specific groups from command line (e.g., `--group=website_setup_docs`)
- **Wildcard support**: Glob patterns in file lists (e.g., `docs/*.md`)
- **Parallel processing**: Process multiple files concurrently for improved performance
- **Custom converters**: Plugin system for user-defined converters
- **Watch mode**: Auto-regenerate on file changes during development
- **Incremental statistics**: Track generation metrics over time
- **Configuration validation**: Pre-flight check of generate.toml structure
- **Verbose mode**: `--verbose` flag for detailed operation logging
- **Environment support**: Generate for different environments (dev/staging/prod)

### Additional Input Types

- **ReStructuredText**: `.rst` file support
- **AsciiDoc**: `.adoc` file support
- **Org-mode**: `.org` file support
- **Jupyter Notebooks**: `.ipynb` conversion
- **Plain text**: `.txt` with minimal HTML wrapping

### Configuration Enhancements

- **Group-level options**: Override normalization, force regeneration per group
- **Template selection**: Choose different HTML templates per group
- **Output filename patterns**: Customize output naming convention
- **Exclusion patterns**: Skip specific files matching patterns
- **Conditional groups**: Enable/disable groups based on environment

### Performance Improvements

- **Caching**: Cache conversion results with content hashing
- **Dependency tracking**: Regenerate when templates/styles change
- **Parallel conversion**: Multi-threaded file processing
- **Progress indicators**: Real-time progress bars for large batches

## Related Documentation

### Internal Documentation
- **[MD to HTML Converter](md_to_html.py)** - Markdown converter implementation
- **[Markdown Normaliser](../normalise/README.md)** - Structure normalization (called by md_to_html)
- **[GZLogging](../gzlogging/README.md)** - Logging infrastructure
- **[Configuration Guide](../../config/generate.toml)** - Example configuration file
- **[Design Rules](../../docs/DESIGN_RULES.md)** - Project design principles
- **[Module README Structure](../../dev/MODULE_README_STRUCTURE.md)** - README template

### External Resources
- **mistune**: https://github.com/lepture/mistune - Markdown parser
- **BeautifulSoup**: https://www.crummy.com/software/BeautifulSoup/ - HTML parser
- **TOML Specification**: https://toml.io/ - Configuration file format

## License

GPL-3.0-or-later

## Authors

superguru, gazorper

---

*Last updated: October 22, 2025*  
*Generate module version: 1.2*
