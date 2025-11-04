# Markdown Structure Normaliser

Converts standalone bold text to proper markdown headings while preserving bold text used for emphasis within sentences and lists. Supports force and dry-run modes for flexible processing.

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
- [Invocation Points](#invocation-points)
- [Development](#development)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)
- [Authors](#authors)

## Purpose

This tool automates the process of converting markdown documents to use proper semantic heading structure instead of bold text for section labels.

The normaliser is integrated into the GAZTank build pipeline and can be used standalone or programmatically by other modules.

### Conversion Rules

- **Standalone bold text** (e.g., `**Windows:**`, `**Example:**`) → Converted to headings
- **Inline bold text** (e.g., text with **emphasis** in sentences) → Preserved
- **Bold in lists** (e.g., `- **Pre-flight validation**`) → Preserved
- **Code blocks** → All content inside ``` or ~~~ blocks is skipped

### Key Design Goals

- **State-Based Processing**: Tracks heading levels and code block context throughout document
- **Context-Aware**: Applies appropriate heading depth based on document structure
- **Non-Destructive**: Preserves intentional bold text usage (inline emphasis, list items)
- **Build Pipeline Integration**: Seamlessly integrates with generate module
- **Flexible Modes**: Supports force and dry-run modes for different workflows

## Build Pipeline

The normaliser is integrated into the GAZTank build pipeline:

```
Content Generation Pipeline:
  1. Read generate.toml configuration
  2. For each markdown file group:
     a. Normalise markdown structure ← This module
     b. Convert markdown to HTML
     c. Write output files
  3. Continue with packaging...
```

**Purpose:** Part of the content generation pipeline

**Location:** Called indirectly via `utils/generate/md_to_html.py`

### Workflow:
```
generate.py → reads generate.toml → delegates to md_to_html.py → calls normalise
```
### Benefits:
- Ensures consistent markdown structure across all documentation
- Automated normalization before HTML generation
- No manual intervention needed
- Clean, semantic markdown in source files

## Logging

The normaliser uses the **gzlogging** infrastructure for comprehensive operational logging.

### Log Configuration

- **Environment:** `dev` (hardcoded, no parameter needed)
- **Tool Name:** `normalise`
- **Log Location:** `logs/dev/normalise_YYYYMMDD.log`
- **Output Mode:** File-only (console has separate emoji-enhanced formatting)
- **Encoding:** UTF-8

### What Gets Logged

#### Logged to file (clean operational log):
- Markdown Structure Normaliser started
- Mode settings (DRY RUN MODE enabled, FORCE MODE enabled if applicable)
- Project root path
- Starting processing with file path
- Line-by-line debug info for each conversion (line number, heading level, before/after)
- Processing complete with modification count
- File update status (written or dry-run prepared)
- Completion message

#### Console output (emoji-enhanced, not in log):
- 📝 Banner with module title
- ⚠️ Mode indicators (DRY RUN, FORCE)
- 📁 Project root display
- 📄 File processing status
- ✅ Success messages
- ❌ Error messages
- 📊 Statistics and summaries

### Log File Example

```log
[2025-10-22 17:38:45] [dev] [INF] Markdown Structure Normaliser started
[2025-10-22 17:38:45] [dev] [INF] FORCE MODE enabled
[2025-10-22 17:38:45] [dev] [INF] Project root: D:\Projects\www\GAZTank
[2025-10-22 17:38:45] [dev] [INF] Starting processing: test_normalise.md
[2025-10-22 17:38:45] [dev] [DBG] Read 10 lines from test_normalise.md
[2025-10-22 17:38:45] [dev] [DBG] Processing 10 lines
[2025-10-22 17:38:45] [dev] [DBG] Line 3, H2: **This is standalone bold text** -> ## This is standalone bold text
[2025-10-22 17:38:45] [dev] [DBG] Line 7, H2: **Another standalone bold** -> ## Another standalone bold
[2025-10-22 17:38:45] [dev] [INF] Processing complete: 2 modifications made
[2025-10-22 17:38:45] [dev] [INF] File updated: test_normalise.md (10 lines written)
[2025-10-22 17:38:45] [dev] [INF] File processing complete: 2 modifications made
[2025-10-22 17:38:45] [dev] [INF] Markdown Structure Normaliser completed successfully
```

Note: No separator lines (no `====` banners) in log files, keeping them clean for parsing.

### Viewing Logs

```bash
# View today's log (PowerShell)
Get-Content "logs\dev\normalise_$(Get-Date -Format 'yyyyMMdd').log"

# View today's log (Linux/Mac)
cat logs/dev/normalise_$(date +%Y%m%d).log

# View most recent log entries
Get-Content "logs\dev\normalise_$(Get-Date -Format 'yyyyMMdd').log" -Tail 20  # PowerShell
tail -20 logs/dev/normalise_$(date +%Y%m%d).log  # Linux/Mac
```

## Usage

### Command Line

```bash
# Using the launcher script (recommended)
scripts\normalise.cmd docs/SETUP_SITE.md                        # Windows
scripts\normalise.cmd docs/SETUP_SITE.md --force                # Windows with force
scripts\normalise.cmd docs/SETUP_SITE.md --dry-run              # Windows dry-run
scripts\normalise.cmd docs/SETUP_SITE.md --force --dry-run      # Windows force + dry-run

./scripts/normalise.sh docs/SETUP_SITE.md                       # Linux/Mac
./scripts/normalise.sh docs/SETUP_SITE.md --force               # Linux/Mac with force
./scripts/normalise.sh docs/SETUP_SITE.md --dry-run             # Linux/Mac dry-run

# Or directly as a Python module
python -m normalise docs/SETUP_SITE.md
python -m normalise docs/SETUP_SITE.md --force
python -m normalise docs/SETUP_SITE.md --dry-run
python -m normalise --help
```

#### Launcher Scripts:
- `scripts/normalise.cmd` - Windows launcher (uses `setlocal`/`endlocal`, sets PYTHONPATH and PYTHONIOENCODING)
- `scripts/normalise.sh` - Linux/Mac launcher (exports PYTHONPATH and PYTHONIOENCODING)

Both scripts:
- Set `PYTHONPATH` to include `utils/` directory
- Set `PYTHONIOENCODING=utf-8` for proper emoji support
- Pass all arguments to the Python module with proper quoting
- Return the module's exit code

### As a Module

You can import and use the `process_file()` function in your own Python scripts:

```python
from normalise import process_file

# Process a single file
modifications = process_file("docs/SETUP_SITE.md")
print(f"Made {modifications} modifications")

# Process with force mode (always process)
modifications = process_file("docs/SETUP_SITE.md", force=True)

# Process with dry-run (show what would be done)
modifications = process_file("docs/SETUP_SITE.md", dry_run=True)
print(f"Would make {modifications} modifications")

# Process multiple files
files = ["docs/SETUP_SITE.md", "docs/RULES.md", "README.md"]
for file in files:
    try:
        count = process_file(file)
        print(f"{file}: {count} modifications")
    except FileNotFoundError as e:
        print(f"Skipping: {e}")
```

For more fine-grained control, you can use the lower-level functions:

```python
from normalise import process_lines, read_file, write_file
from pathlib import Path

filepath = Path("docs/SETUP_SITE.md")
lines = read_file(filepath)
processed_lines, modification_count = process_lines(lines)

if modification_count > 0:
    write_file(filepath, processed_lines, dry_run=False)
    print(f"Made {modification_count} modifications")
```

## Command Line Arguments

```
usage: normalise [-h] [--force] [--dry-run] filename

Markdown Structure Normaliser - Converts standalone bold text to proper markdown headings

positional arguments:
  filename              Path to the markdown file to process

options:
  -h, --help            show this help message and exit
  --force               Process file even if it appears up-to-date (always applies for normalise)
  --dry-run             Show what would be done without actually modifying files

Example: python -m normalise docs/SETUP_SITE.md --force --dry-run
```

### Argument Details

- **`filename`** (required): Path to the markdown file to normalize. Can be absolute or relative.

- **`--help`, `-h`**: Display help message with usage examples and exit.

- **`--force`**: Process file regardless of state. For normalise, this always applies since the tool needs to analyze the file content to determine if changes are needed. Included for consistency with other GAZTank modules.

- **`--dry-run`**: Preview mode - analyze the file and show what would be changed without actually writing any modifications. Useful for:
  - Checking if a file needs normalization
  - Previewing changes before applying them
  - Testing in CI/CD pipelines
  - Validating behavior without side effects

### Exit Codes

- **0**: Success (file processed or no modifications needed)
- **1**: Error (file not found, permission denied, processing failed)

### Examples

```bash
# Get help
python -m normalise --help

# Process a file
python -m normalise docs/SETUP_SITE.md

# Preview changes without modifying
python -m normalise docs/SETUP_SITE.md --dry-run

# Force processing (always applies for normalise)
python -m normalise docs/SETUP_SITE.md --force

# Combine force and dry-run
python -m normalise docs/SETUP_SITE.md --force --dry-run
```

## Module Structure

```
normalise/
├── __init__.py      # Package initialization and exports
├── __main__.py      # Entry point for python -m normalise
├── normaliser.py    # Core processing logic
└── README.md        # This file
```

### Key Functions

- **`main()`** - Command-line entry point with argparse argument handling
- **`process_file(filename, force=False, dry_run=False)`** - High-level function to process a markdown file (recommended for external scripts)
- **`process_lines(lines)`** - Process a list of lines and return modified lines + count
- **`read_file(filepath)`** - Read a markdown file into a list of lines (UTF-8)
- **`write_file(filepath, lines, dry_run=False)`** - Write lines back to a file (or skip in dry-run mode)
- **`process_line(line, state)`** - Process a single line and return modified line + boolean flag
- **`needs_processing(filepath, force=False)`** - Determine if file needs processing (always True for normalise)
- **`ProcessingState`** - Class for tracking processing state (heading level, code blocks, line number)

### Architecture

The module uses a **state machine** approach:

1. **State Tracking**: `ProcessingState` tracks:
   - Current heading level (for contextual heading depth)
   - Code block context (to skip content inside ```)
   - Current line number (for logging)

2. **Line-by-Line Processing**: Each line is processed sequentially:
   - Update code block state
   - Check if line should be skipped
   - Detect standalone bold text
   - Apply appropriate heading level
   - Track modifications

3. **Conditional Writing**: Files are only modified if changes are detected, unless dry-run mode is active.

## Features

- **State-Based Processing**: Tracks heading levels and code block context throughout document
- **Code Block Awareness**: Automatically skips content inside fenced code blocks (``` or ~~~)
- **Contextual Heading Levels**: Applies appropriate heading depth based on document structure
- **Conditional Writes**: Only modifies files when changes are detected
- **Force Mode**: Process files regardless of state (consistent with other GAZTank modules)
- **Dry-Run Mode**: Preview changes without modifying files
- **Cross-Platform**: Works on Windows, Linux, and Mac with proper UTF-8 support
- **Detailed Logging**: Shows all conversions made with line numbers in log files
- **Emoji Console Output**: User-friendly console messages with emoji indicators
- **Integrated Logging**: Uses gzlogging for standardized audit trails
- **UTF-8 Support**: Handles Unicode and emoji characters correctly throughout
- **Argparse Integration**: Professional command-line interface with --help support
- **Module API**: Can be imported and used programmatically by other tools
- **Build Pipeline Integration**: Seamlessly integrates with generate module

## Invocation Points

The normaliser is invoked from multiple places in the GAZTank project:

### 1. Direct Command-Line Usage

Users can run normalise directly via launcher scripts:

```bash
# Windows
scripts\normalise.cmd docs/SETUP_SITE.md

# Linux/Mac
./scripts/normalise.sh docs/SETUP_SITE.md
```

**Purpose:** Manual normalization of individual markdown files

**Location:** `scripts/normalise.cmd` and `scripts/normalise.sh`

### 2. Markdown-to-HTML Converter (md_to_html.py)

The generate system automatically normalizes markdown files before converting to HTML:

```python
# utils/generate/md_to_html.py (line 33)
from utils.normalise import process_file as normalize_markdown

# utils/generate/md_to_html.py (line 205)
if self.normalize:
    modifications = normalize_markdown(input_path)
```

**Purpose:** Ensure consistent markdown structure before HTML conversion

**Location:** `utils/generate/md_to_html.py`

**Invocation:** Automatic (when `--normalize` flag is used or by default)

#### Workflow:
```
Markdown File → Normalise Structure → Convert to HTML → Output HTML File
```

### 3. Generate Module (generator.py)

The general generate system uses md_to_html converter, which in turn calls normalise:

```bash
# Windows
scripts\generate.cmd

# Linux/Mac
./scripts/generate.sh
```

### Key Integration Points

| Component | Path | Description |
|-----------|------|-------------|
| **Launcher Scripts** | `scripts/normalise.*` | Direct command-line access |
| **MD to HTML** | `utils/generate/md_to_html.py` | Automatic pre-conversion normalization |
| **Generate System** | `utils/generate/generator.py` | Indirect via md_to_html converter |
| **Logging** | `utils/gzlogging/` | Centralized logging infrastructure |

### Design Decision

The normaliser is **allowed to modify source `.md` files in place**, unlike other build tools that only generate output files. This is intentional because:
- Markdown files are source files meant to be edited
- Normalization improves source file quality
- Changes are typically minimal (formatting only)
- Version control tracks all modifications
- Developers benefit from cleaner markdown structure

## Best Practices

### When to Run Normalise

1. **Before committing markdown changes**
   - Run normalise on any `.md` files you've edited
   - Ensures consistent structure across the codebase
   - Makes diffs cleaner and more meaningful

2. **After converting documentation from other formats**
   - Many converters create bold headings instead of proper markdown
   - Run normalise to fix the structure automatically

3. **As part of the build process**
   - The generate pipeline runs normalise automatically
   - No manual intervention needed for HTML generation

### Manual Usage Tips

```bash
# Process a single file
scripts\normalise.cmd docs/SETUP_SITE.md

# Preview changes before applying
scripts\normalise.cmd docs/SETUP_SITE.md --dry-run

# Process multiple files (PowerShell)
Get-ChildItem docs/*.md | ForEach-Object { scripts\normalise.cmd $_.FullName }

# Process multiple files (Bash)
for file in docs/*.md; do ./scripts/normalise.sh "$file"; done

# Process all markdown files recursively (PowerShell)
Get-ChildItem -Recurse -Filter *.md | ForEach-Object { scripts\normalise.cmd $_.FullName }

# Check which files need normalization (dry-run all)
Get-ChildItem docs/*.md | ForEach-Object { 
    scripts\normalise.cmd $_.FullName --dry-run 
} | Select-String "modifications prepared"
```

### Version Control Best Practices

- **Review changes before committing**: Normalise modifies files in place, so use `git diff` to verify changes
- **Commit normalisation separately**: Consider committing normalisation changes separately from content changes for cleaner history
- **Document in commit messages**: Note when normalisation was applied (e.g., "Apply markdown normalisation to docs/")

### Integration with Other Tools

- **Pre-commit hooks**: Add normalise to your pre-commit hooks for automatic formatting
- **CI/CD validation**: Run normalise with `--dry-run` to check for unnormalized files in CI pipelines
- **Editor integration**: Some markdown editors can be configured to run normalise on save
- **Build automation**: Integrate with generate module for automatic pre-processing

## Troubleshooting

### File Not Found Error

**Problem:** `FileNotFoundError: [Errno 2] No such file or directory: 'docs/FILE.md'`

#### Solution:
- Verify the file path is correct (use absolute or relative path from project root)
- Check file exists: `ls docs/FILE.md` (Linux/Mac) or `dir docs\FILE.md` (Windows)
- Ensure you're running from the project root directory

### No Modifications Made

**Problem:** Normalise reports "0 modifications" but you expected changes

#### Possible Causes:
1. **File already normalized** - Bold text is already in proper heading format
2. **Bold text in lists** - Intentionally preserved (not converted)
3. **Inline bold** - Bold text within sentences is intentionally preserved
4. **Inside code blocks** - Content inside ``` blocks is skipped

#### Verification:
```bash
# Check what the file contains
cat docs/FILE.md | grep "^\*\*"  # Lines starting with bold (candidates for conversion)
```

### Unexpected Conversions

**Problem:** Some bold text was converted when it shouldn't have been

#### Diagnosis:
- The normaliser converts bold text that appears at the start of a line
- If bold text is meant as emphasis (not a heading), it should be inline with other text

#### Solution:
- Move the bold text inline: `This is **important** information.`
- Or convert it to a proper heading manually if it's actually a section heading

### Permission Denied Error

**Problem:** `PermissionError: [Errno 13] Permission denied`

#### Solution:
- Check file permissions
- Ensure the file is not open in another program (especially on Windows)
- Verify write permissions on the file and directory
- Close any editors or programs with the file open
- On Windows, check if file is marked as read-only

### Unicode/Encoding Issues

**Problem:** Strange characters appear after normalization

#### Solution:
- Ensure the markdown file is UTF-8 encoded
- The shell scripts automatically set `PYTHONIOENCODING=utf-8`
- Re-save the file as UTF-8 in your editor before normalizing
- Use a UTF-8 capable editor (VS Code, Notepad++, etc.)

### Dry-Run Shows Changes But Nothing Written

**Problem:** Dry-run mode shows modifications but file wasn't changed

**Expected Behavior:** This is correct! Dry-run mode (`--dry-run`) shows what *would* be done without actually modifying files. To apply the changes, run without `--dry-run`:

```bash
# Preview changes
scripts\normalise.cmd docs/FILE.md --dry-run

# Actually apply changes
scripts\normalise.cmd docs/FILE.md
```

### Log File Not Created

**Problem:** No log file appears in `logs/dev/`

#### Solution:
- Verify `logs/dev/` directory exists (should be auto-created)
- Check write permissions on the logs directory
- Ensure `utils/gzlogging/` module is present and accessible
- Check console output for logging initialization errors

## Development

The module follows standard Python packaging conventions:

- `__init__.py` - Exports public API (`process_file`, `process_lines`, `read_file`, `write_file`)
- `__main__.py` - Command-line entry point (enables `python -m normalise`)
- `normaliser.py` - Core implementation (processing logic and state management)
- Launcher scripts in `scripts/` for cross-platform convenience

### File Locations

```
GAZTank/
├── logs/
│   └── dev/
│       └── normalise_YYYYMMDD.log   # Daily log files (audit trail)
│
├── scripts/
│   ├── normalise.cmd                # Windows launcher
│   └── normalise.sh                 # Linux/Mac launcher
│
└── utils/
    ├── gzlogging/                   # Centralized logging system
    │   └── gzlogging.py             # Used by normalise
    │
    ├── generate/                    # Calls normalise
    │   ├── md_to_html.py            # Imports and uses normalise
    │   └── generator.py             # Orchestrator (indirect usage)
    │
    └── normalise/                   # This module
        ├── __init__.py              # Package initialization
        ├── __main__.py              # Entry point
        ├── normaliser.py            # Core logic
        └── README.md                # This file
```

## Future Enhancements

Planned improvements for future versions:

### Completed ✅

- [x] **Force Mode Support** - Process files regardless of state (v1.1)
- [x] **Dry-Run Mode** - Preview changes without modifying files (v1.1)
- [x] **Argparse Integration** - Professional CLI with --help support (v1.1)
- [x] **Clean Log Format** - Removed separator lines from logs (v1.1)
- [x] **Emoji Console Output** - Enhanced user experience with visual indicators (v1.1)
- [x] **UTF-8 Shell Scripts** - Proper PYTHONIOENCODING setup in launcher scripts (v1.1)

### Short Term (v1.2)

- **Batch Processing Mode**: Process multiple files in a single command
  ```bash
  python -m normalise docs/*.md --batch
  ```
- **Configuration File**: Support for `.normaliserc` to customize heading levels and patterns
- **Statistics Summary**: Detailed report of changes across multiple files
- **Backup Option**: Create `.bak` files before modifying originals

### Medium Term (v1.3)

- **Custom Bold Patterns**: Configure additional patterns to recognize as headings
- **Heading Level Constraints**: Enforce maximum heading depth
- **Interactive Mode**: Prompt for confirmation on each change
- **Undo Support**: Ability to revert recent normalizations

### Long Term (v2.0)

- **Smart Heading Detection**: ML-based detection of semantic heading structure
- **Format Preservation**: Maintain custom spacing and line break patterns
- **Integration with Other Formats**: Support for ReStructuredText, AsciiDoc
- **VS Code Extension**: Direct integration with VS Code editor

### Under Consideration

- **Watch Mode**: Automatically normalize files on save
- **Git Integration**: Pre-commit hook generation
- **Diff Output**: Show before/after diffs in unified format
- **Configuration Profiles**: Different normalization rules for different document types

See [GitHub Issues](https://github.com/gazorper/GAZTank/issues) for tracking and discussion.

## Related Documentation

- **[Generate Module](../generate/README.md)** - Content generation pipeline that uses normalise
- **[MD to HTML Converter](../generate/md_to_html.py)** - Markdown converter (imports normalise)
- **[GZLogging Module](../gzlogging/README.md)** - Logging infrastructure
- **[Design Rules](../../docs/DESIGN_RULES.md)** - Project design principles and UTF-8 handling
- **[Module README Structure](../../dev/MODULE_README_STRUCTURE.md)** - Template for module documentation

## License

GPL-3.0-or-later

## Authors

superguru, gazorper

---

*Last updated: October 22, 2025*  
*Normaliser version: 1.1*
