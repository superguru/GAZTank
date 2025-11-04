# Design Rules - GAZ Tank Project

**Version:** 1.0  
**Last Updated:** October 19, 2025

This document defines the high-level structural and design rules that must be followed when creating files, code, and actions in this project.

---

## 📋 Table of Contents

- [Core Principles](#core-principles)
- [File Organization](#file-organization)
- [Code Standards](#code-standards)
- [Python Conventions](#python-conventions)
- [HTML/CSS/JavaScript Conventions](#htmlcssjavascript-conventions)
- [Configuration Management](#configuration-management)
- [Documentation Requirements](#documentation-requirements)
- [Build and Deployment](#build-and-deployment)
- [Version Control](#version-control)
- [Testing and Validation](#testing-and-validation)

---

## 🎯 Core Principles

### 1. Single Source of Truth
- **Configuration**: All site configuration lives in `config/site.toml`
- **No Hardcoded Values**: Never hardcode site-specific values in code
- **Generated Files**: CSS variables, sitemaps, and configuration-driven files are generated, not manually edited

### 2. Idempotency
- **Setup Scripts**: Must be safely re-runnable without side effects
- **Build Scripts**: Running multiple times produces same result
- **Force-Apply Mode**: Configuration can be re-applied without user prompts

### 3. Modularity
- **Separation of Concerns**: Each module/file has a single, clear responsibility
- **No God Objects**: Break large files (>600 lines) into focused modules
- **Reusable Components**: Shared functionality lives in separate modules

### 4. Cross-Platform Compatibility
- **Windows & Unix**: All scripts must work on both platforms
- **Paired Launchers**: Every `.cmd` file MUST have a matching `.sh` file (and vice versa)
- **Scripts Directory**: All `.cmd` and `.sh` launcher scripts MUST be created in the `scripts/` directory (exception: dev-specific tools in `dev/`)
- **Identical Functionality**: Both launchers must perform the same operations
- **Path Handling**: Use `pathlib.Path` for cross-platform paths
- **No Platform-Specific Code**: Isolate platform differences in launcher scripts only

### 5. Fail-Fast Philosophy
- **Validation First**: Always validate before processing
- **Proper Exit Codes**: Return 0 (success) or 1 (failure)
- **Clear Error Messages**: Tell user what failed and how to fix it

---

## 📁 File Organization

### Directory Structure

For a comprehensive directory structure with detailed descriptions, see [PROJECT_STRUCTURE.md](#setup/PROJECT_STRUCTURE).

#### Quick Reference:
- **`config/`** - TOML configuration files
- **`dev/`** - Development tools (linter, TODO)
- **`docs/`** - Markdown documentation
- **`src/`** - Source files (HTML, CSS, JS, images, content)
- **`utils/`** - Python utility modules
- **`publish/`** - Build outputs (gitignored)
- **`scripts/`** - Cross-platform launcher scripts

### File Naming Conventions

#### Python Scripts:
- Use snake_case: `setup_site.py`, `sitemap module`
- Descriptive names: `backup_manager.py` not `bm.py`
- Module names match functionality

#### HTML Content:
- Use snake_case: `home.html`, `mods_7_days_to_die.html`
- Hierarchical: Parent pages before child pages alphabetically
- No version prefixes: Use descriptive names, not `page_01.html`

#### Documentation:
- UPPERCASE for root: `README.md`, `LICENSE`
- UPPERCASE for important docs in subdirs: `RULES.md`, `SETUP.md`
- Use underscores for multi-word: `DESIGN_RULES.md`

#### Configuration:
- Lowercase extensions: `.toml`, `.ini`, `.config`
- Template files: `file.template` or `file.config.template`

#### Shell Script Launchers:
- **Always provide both platforms**: Every `.cmd` file must have a corresponding `.sh` file
- **Identical functionality**: Both scripts must perform the same operations
- **Same base name**: `script.cmd` and `script.sh`
- Examples:
  - ✅ `scripts\setup_site.cmd` + `setup_site.sh`
  - ✅ `scripts\deploy.cmd` + `deploy.sh`
  - ✅ `scripts\gzserve.cmd` + `gzserve.sh`
  - ❌ Having only `scripts\package.cmd` without `package.sh`

### Windows Batch Script Standards

#### Variable Scope Isolation with `setlocal`/`endlocal`

##### All Windows batch script launchers (`.cmd` files) MUST use `setlocal` and `endlocal` for environment variable isolation.

#### Required Pattern:

```batch
@echo off
setlocal
REM Script commands here
REM Set environment variables (PYTHONPATH, etc.)
REM Run Python modules
endlocal
exit /b %errorlevel%
```

#### Why This Matters:

1. **Environment Isolation**: Prevents `PYTHONPATH` and other variable changes from persisting after script exits
2. **Clean Testing**: Each script run starts fresh without accumulated changes from previous runs
3. **No Side Effects**: User's command prompt environment remains unchanged
4. **Parallel Execution**: Multiple scripts can run safely without interfering with each other
5. **Professional Practice**: Standard pattern in well-written production batch scripts

#### Rules:

- ✅ Place `setlocal` immediately after `@echo off` (before any variable setting)
- ✅ Place `endlocal` before `exit /b %errorlevel%` (after all script operations)
- ✅ All environment variable changes (`set PYTHONPATH=...`) happen between `setlocal` and `endlocal`
- ❌ Never modify environment variables without `setlocal`/`endlocal` protection
- ❌ Don't use `goto` to bypass `endlocal` - it must always execute

#### Example - Server Launcher:

```batch
@echo off
setlocal
REM Development Web Server Launcher (Windows)
REM Usage: gzserve.cmd [port]

REM Set PYTHONPATH to project root for module imports
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

REM Run the server module
python -m utils.gzserve %*

endlocal
exit /b %errorlevel%
```

#### What Happens:

##### WITHOUT `setlocal`/`endlocal`:
```batch
C:\> echo %PYTHONPATH%
(empty or existing value)

C:\> gzserve.cmd
(Server runs)

C:\> echo %PYTHONPATH%
D:\Projects\www\GAZTank;(previous value)  <-- POLLUTION!
```

##### WITH `setlocal`/`endlocal`:
```batch
C:\> echo %PYTHONPATH%
(empty or existing value)

C:\> gzserve.cmd
(Server runs)

C:\> echo %PYTHONPATH%
(empty or existing value)  <-- CLEAN!
```

#### Historical Context:

This project previously had inconsistent usage:
- 4 scripts used `setlocal`/`endlocal`: `generate_toc.cmd`, `package.cmd`, `normalise.cmd`, `gzlint.cmd`
- 5 scripts didn't: `gzserve.cmd`, `deploy.cmd`, `generate_sitemap.cmd`, `md_to_html.cmd`, `setup_site.cmd`

**As of October 21, 2025**: All launcher scripts now use `setlocal`/`endlocal` for consistency and reliability.

---

### Python Subprocess Unicode Handling

#### All Python scripts that run subprocesses with captured output MUST set `PYTHONIOENCODING='utf-8'` in the environment.

#### The Problem:

On Windows, when Python runs a subprocess with `capture_output=True`, stdout/stderr are captured through **pipes**. Python defaults pipe encoding to the **system encoding** (cp1252 on Windows), NOT UTF-8. This causes `UnicodeEncodeError` when the subprocess tries to output Unicode characters (emojis, special symbols).

**Direct execution works**:
```bash
.\scripts\gzlint.cmd  # Python inherits console encoding (UTF-8 capable) ✅
```

**Subprocess with captured output fails**:
```python
result = subprocess.run([sys.executable, '-m', 'gzlint'], 
                       capture_output=True)  # Pipe defaults to cp1252 ❌
# UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'
```

#### Required Pattern:

```python
import subprocess
import os

def run_subprocess_with_unicode():
    """Run a subprocess that may output Unicode characters"""
    
    # Set up environment with UTF-8 encoding
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'  # ← CRITICAL for Windows pipes
    
    result = subprocess.run(
        [sys.executable, '-m', 'some_module'],
        capture_output=True,
        text=True,
        encoding='utf-8',      # Decode captured output as UTF-8
        errors='replace',      # Replace unencodable characters gracefully
        env=env                # Pass environment with PYTHONIOENCODING
    )
    
    # Safe printing with fallback
    if result.stdout:
        try:
            print(result.stdout)
        except UnicodeEncodeError:
            # Fallback for edge cases
            safe = result.stdout.encode('ascii', errors='replace').decode('ascii')
            print(safe)
    
    return result.returncode
```

#### Why This Matters:

1. **Cross-Platform Consistency**: Windows pipe encoding differs from Unix
2. **Unicode Support**: Enables emoji, symbols, and international characters in output
3. **Build Pipeline Reliability**: Prevents crashes in automated packaging/validation
4. **Professional UX**: Users expect Unicode characters to work correctly

#### Rules:

- ✅ Set `env['PYTHONIOENCODING'] = 'utf-8'` before any subprocess that captures output
- ✅ Use `encoding='utf-8'` and `errors='replace'` in `subprocess.run()`
- ✅ Add try/except around `print()` of captured output for extra safety
- ❌ Never run subprocess with `capture_output=True` without setting `PYTHONIOENCODING`
- ❌ Don't assume console encoding will propagate to subprocess pipes

#### Examples in This Project:

**utils/package/packager.py** - Runs validation, conversion, and sitemap generation:
```python
def run_validation():
    env = os.environ.copy()
    env['PYTHONPATH'] = str(utils_dir)
    env['PYTHONIOENCODING'] = 'utf-8'  # ← Essential for gzlint Unicode output
    
    result = subprocess.run(
        [sys.executable, '-m', 'gzlint'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=env
    )
```

#### Historical Issue:

Before October 21, 2025:
- `.\scripts\gzlint.cmd` worked fine (direct console execution)
- `.\scripts\package.cmd` crashed with `UnicodeEncodeError` (subprocess with pipes)
- Same `gzlint` code, different execution context = different behavior

After fix: Both execution methods work reliably by setting `PYTHONIOENCODING`.

---

## 💻 Code Standards

### General Rules

1. **UTF-8 Encoding**: All text files must be UTF-8 without BOM
2. **Line Endings**: LF (Unix) preferred, but Git handles CRLF conversion
3. **No Trailing Whitespace**: Clean up trailing spaces
4. **Consistent Indentation**: 4 spaces for Python, 4 spaces for HTML/JS
5. **Maximum Line Length**: 
   - Python: 100 characters (soft limit, 120 hard limit)
   - HTML: No limit (but use readable formatting)
   - JavaScript: 100 characters

### Comments and Documentation

1. **Docstrings**: All Python functions/classes must have docstrings
2. **Inline Comments**: Use sparingly, code should be self-documenting
3. **TODOs**: Use standard format: `# TODO: Description`
4. **License Headers**: All Python files must include standard header

---

## 🐍 Python Conventions

### File Headers

#### Standard header format for all Python files:

All Python scripts must include the following header structure:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Module Title
============
Brief description of the module's purpose and functionality.

Authors: superguru, gazorper
License: GPL v3.0
"""
```

#### Header Components:

1. **Shebang Line** (`#!/usr/bin/env python3`)
   - Enables direct script execution on Unix-like systems
   - Must be the very first line (no blank lines before)
   - Exactly one shebang line per file

2. **Encoding Declaration** (`# -*- coding: utf-8 -*-`)
   - Specifies UTF-8 encoding for the file
   - Required for files containing non-ASCII characters
   - Standard practice for consistency across all files

3. **SPDX License Identifier** (`# SPDX-License-Identifier: GPL-3.0-or-later`)
   - Machine-readable license identifier
   - Follows [SPDX specification](https://spdx.org/)
   - Indicates GPL v3.0 or later licensing

4. **Module Docstring**
   - Triple-quoted string with module title and description
   - Title underlined with `=` characters (matching title length)
   - Clear description of module purpose
   - Must include `Authors:` and `License:` lines
   - Optional: `Usage:` section for command-line scripts

#### Rules:

- ✅ All four components must be present in this exact order
- ✅ One blank line between shebang section and docstring
- ✅ No duplicate shebang or encoding declarations
- ✅ Docstring must include Authors and License information
- ❌ No content before the shebang line
- ❌ No duplicate headers or sections

#### Example for Command-Line Scripts:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Site Setup Wizard
=================
Interactive configuration tool for customizing the site.

This script guides you through the setup process and generates
configuration files, updates branding, and customizes the site
for your specific use case.

Usage:
    python utils/setup/setup_site.py
    python utils/setup/setup_site.py --force-apply

Options:
    --force-apply    Skip all prompts and apply current site.toml configuration

Authors: superguru, gazorper
License: GPL v3.0
"""
```

#### Example for Package `__init__.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Setup Package
=============
Site setup wizard modular package.

Authors: superguru, gazorper
License: GPL v3.0
"""
```

### Import Organization

```python
# 1. Standard library imports
import os
import sys
from pathlib import Path

# 2. Third-party imports
import tomlkit
from InquirerPy import inquirer

# 3. Local application imports
import ui_helpers
from config_io import load_config
```

### Module Structure

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Module Title
============
Brief description of module purpose.
"""

# Imports

# Constants
DEFAULT_PORT = 7190

# Functions/Classes

def main():
    """Main entry point"""
    pass

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

### Python Best Practices

1. **Use pathlib.Path**: Not `os.path` for file operations
2. **Use f-strings**: For string formatting (Python 3.6+)
3. **Type Hints**: Optional but encouraged for clarity
4. **Error Handling**: Use try/except with specific exceptions
5. **Context Managers**: Use `with` for file operations
6. **List Comprehensions**: For simple iterations, not complex logic

### Parsing and Data Processing

#### Use proper parsers, not regex, for structured data:

1. **HTML/XML Processing**
   - ✅ Use: `BeautifulSoup` from `bs4` package
   - ❌ Avoid: `re.findall()`, `re.sub()` on HTML
   - Example: `soup.find('title')` not `re.search(r'<title>(.*?)</title>')`

2. **JavaScript/Code Processing**
   - ✅ Use: Node.js with Babel AST parser (`@babel/parser`, `@babel/traverse`)
   - ✅ Fallback: Simple string methods for configuration blocks
   - ❌ Avoid: Regex on JavaScript code (fragile and dangerous)
   - Project: See `utils/setup/js_updater.mjs` for AST implementation

3. **URL Processing**
   - ✅ Use: `urllib.parse.urlparse()` and `urllib.parse.urlunparse()`
   - ❌ Avoid: Regex patterns like `r'https://[^/]+'`
   - Example: `parsed.netloc` not `re.match(r'https://([^/]+)', url)`

4. **Text File Processing**
   - ✅ Use: Line-by-line processing with string methods
   - ✅ Methods: `.startswith()`, `.contains()`, `.replace()`, `.split()`
   - ❌ Avoid: `re.sub()` with `re.MULTILINE` for simple replacements
   - Example: `if line.startswith('#'):` not `re.sub(r'^#.*', ...)`

5. **JSON Processing**
   - ✅ Use: `json` module
   - ❌ Avoid: Regex on JSON strings

6. **CSV Processing**
   - ✅ Use: `csv` module
   - ❌ Avoid: `re.split()` on CSV data

#### When regex IS appropriate:
- Simple validation (email format, phone numbers)
- Pattern matching in unstructured text (logs, prose)
- When used in a **documented fallback** for unavailable parsers

#### Project Example:
```python
# ❌ BAD - Fragile regex on HTML
content = re.sub(r'<meta name="description" content=".*?"', 
                 f'<meta name="description" content="{desc}"', 
                 html_content)

# ✅ GOOD - BeautifulSoup for HTML
soup = BeautifulSoup(html_content, 'html.parser')
meta_desc = soup.find('meta', {'name': 'description'})
if meta_desc:
    meta_desc['content'] = desc
```

### Absolute Imports

- Use absolute imports: `import module_name`
- Not relative imports: `from . import module`
- Enables direct script execution without package complications

---

## 🌐 HTML/CSS/JavaScript Conventions

### HTML Structure

1. **Semantic HTML5**: Use appropriate tags (`<nav>`, `<article>`, `<section>`)
2. **Single H1**: Exactly one `<h1>` per page (SEO requirement)
3. **Heading Hierarchy**: No skipping levels (h2 → h3, not h2 → h4)
4. **Accessibility**: Include `aria-label`, `alt` text, and ARIA attributes
5. **Data Attributes**: Use for dynamic content: `data-content="page_name"`

### CSS Organization

1. **CSS Variables**: Use variables from `variables.css` (generated)
2. **No Hardcoded Colors**: Always use CSS custom properties
3. **Mobile-First**: Design for mobile, enhance for desktop
4. **BEM Naming**: Use Block-Element-Modifier when appropriate

### JavaScript Rules

1. **Vanilla JS**: No frameworks (project requirement)
2. **ES6+**: Use modern JavaScript features
3. **No console.log()**: Remove before production (GZLint enforces)
4. **Error Handling**: Use console.error() for intentional logging
5. **Async/Await**: Prefer over promise chains for readability

---

## 🏗️ Module Architecture Standards

### Module Categories

The project has **12 Python modules** in `utils/` organized into two categories:

#### Foundational Modules (2)
1. **gzconfig** - Configuration management library
2. **gzlogging** - Centralized logging infrastructure

#### Pipeline Modules (10)
3. **clean** - Orphaned file cleanup
4. **deploy** - FTP/FTPS deployment
5. **generate** - Environment-aware content generation
6. **gzlint** - HTML/JS/Config validation
7. **normalise** - Markdown structure normalization
8. **package** - Build packaging and archiving
9. **gzserve** - Development web server
10. **setup** - Interactive site configuration wizard
11. **sitemap** - XML sitemap generation
12. **toc** - Table of contents generation

**Status:** 10/12 complete (83%), 1 WIP (package), 1 incomplete (deploy)

### Module Maturity Checklist

All modules must meet these 12 criteria (see `utils/00MODULE_MATURITY.md`):

1. ✅ Is a proper module that can run with `python -m <modulename>`
2. ✅ Has `-e <env>` command line param, or has a specific design decision to default to dev environment
3. ✅ Has `--help` command line param
4. ✅ Uses gzconfig for all config operations
5. ✅ Uses gzlogging
6. ✅ Uses an appropriate `.\config\*.toml` file
7. ✅ Has shell invocation scripts for cmd and sh
8. ✅ Has `--force` command line param, or a specific design choice not to have it
9. ✅ Has `--dry-run` command line param, or a specific design choice not to have it
10. ✅ Consistently and correctly log appropriate items to log and to console
11. ✅ Is verified to be UTF-8 compliant
12. ✅ Is generic in design so it can be easily extended in future
13. ✅ Has updated README.md that conforms to `.\dev\MODULE_README_STRUCTURE.md`

### Environment-Aware Design (v2.0)

**Breaking Change:** As of October 23, 2025, all pipeline modules are environment-aware.

#### Required: `-e` Environment Argument

All pipeline modules MUST accept a mandatory `-e` or `--environment` argument:

```bash
# Required pattern for all pipeline modules
python -m utils.generate -e dev
python -m utils.clean -e staging
python -m utils.package -e prod
```

**Valid environments:** `dev`, `staging`, `prod` (defined in `config/pipeline.toml`)

#### Exception: Foundational Modules

**gzconfig** and **gzlogging** are library modules and do NOT have command-line interfaces:
- No `-e` argument (imported, not executed)
- No shell scripts (used via `from gzconfig import ...`)
- No `--help`, `--force`, or `--dry-run` (not CLI tools)

### Configuration Management with gzconfig

#### All modules MUST use gzconfig for configuration access:

```python
# ✅ CORRECT - Use gzconfig
from gzconfig import get_pipeline_config, get_generate_config

def my_function(environment: str):
    # Get environment-specific configuration
    env = get_pipeline_config(environment)
    print(f"Output directory: {env.directory_path}")
    print(f"Server port: {env.port}")
```

```python
# ❌ INCORRECT - Direct TOML reading
import tomlkit
from pathlib import Path

def my_function(environment: str):
    # Don't do this!
    config_file = Path("config/pipeline.toml")
    with open(config_file) as f:
        config = tomlkit.load(f)
    dir_path = Path(config['environments'][environment]['dir'])
```

#### Benefits of gzconfig:

1. **Centralized logic**: Configuration reading in one place
2. **Type safety**: Returns typed objects, not raw dicts
3. **Clean properties**: `env.directory_path` instead of `config['environments'][env]['dir']`
4. **Caching**: Configuration loaded once, reused across modules
5. **Validation**: Ensures environment exists before returning
6. **No circular dependencies**: Low-level library, no imports from other modules

### Logging with gzlogging

#### All modules MUST use gzlogging for output:

```python
from gzlogging import Logger

# Initialize logger with tool name and environment
log = Logger(tool_name="generate", environment="dev")

# Use log methods for file logging
log.inf("Processing file: example.md")
log.wrn("File timestamp unchanged, skipping")
log.err("Failed to parse HTML file")

# Use print() for console-only output
print("=" * 60)
print("✅ Generation Complete!")
print(f"📁 Output: {output_path}")
```

#### What goes where:

##### Log file only (`log.inf()`, `log.wrn()`, `log.err()`):
- Operational information (files processed, configuration loaded)
- Error messages (without emojis)
- Success/failure status
- Concise summaries
- No blank lines

##### Console only (`print()`):
- Headers and decorative lines
- Emojis and visual formatting
- Blank lines for spacing
- Summary boxes
- User-facing messages

#### Log format standard:

```
[YYYY-MM-DD HH:MM:SS] [environment] [LEVEL] Message
```

Example:
```
[2025-10-23 13:20:27] [dev] [INF] Loaded configuration from config/generate.toml
[2025-10-23 13:20:28] [dev] [INF] Processing group: setup_docs
[2025-10-23 13:20:29] [dev] [INF] Converted: DEVELOPER_SETUP.md → DEVELOPER_SETUP.html
[2025-10-23 13:20:30] [dev] [INF] Static Content Generator completed successfully
```

### Command Line Argument Standards

#### Required Arguments (Pipeline Modules):

```python
parser.add_argument(
    '-e', '--environment',
    required=True,
    choices=['dev', 'staging', 'prod'],
    help='Target environment'
)
```

#### Standard Optional Arguments:

```python
# Force mode - regenerate regardless of timestamps
parser.add_argument(
    '--force',
    action='store_true',
    help='Force regeneration regardless of file timestamps'
)

# Dry-run mode - show what would happen without making changes
parser.add_argument(
    '--dry-run',
    action='store_true',
    help='Show what would be done without making changes'
)
```

#### Design Decision: When to Omit Arguments

Some modules may intentionally omit `--force` or `--dry-run`:
- Document the design decision in `utils/00MODULE_MATURITY.md`
- Provide clear reasoning (e.g., "gzserve module runs continuously, force mode not applicable")

### Module Directory Structure

```
utils/{module}/
├── __init__.py          # Module exports and version
├── __main__.py          # Entry point for python -m execution
├── {module}.py          # Core implementation logic
├── README.md            # Comprehensive documentation
└── example.py           # Usage examples (optional, for libraries)
```

#### Example - generate module:
```
utils/generate/
├── __init__.py          # Exports generate() function
├── __main__.py          # Argument parsing, calls generate()
├── generator.py         # Core generation logic
└── README.md            # Full documentation
```

### Shell Script Standards

#### Every module MUST have both Windows and Unix launchers in `scripts/`:

```bash
scripts/
├── generate.cmd         # Windows launcher
├── generate.sh          # Unix launcher
├── gzclean.cmd          # Windows launcher
├── gzclean.sh           # Unix launcher
└── ...
```

#### Shell script template (Windows):

```batch
@echo off
setlocal
REM
REM Module Name - Brief Description
REM

REM Set PYTHONPATH to project root
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

REM Run the module, passing all arguments
python -m utils.modulename %*

endlocal
exit /b %errorlevel%
```

#### Shell script template (Unix):

```bash
#!/bin/bash
#
# Module Name - Brief Description
#

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run the module, passing all arguments
python3 -m utils.modulename "$@"

exit $?
```

### Dry-Run Mode Implementation

When implementing `--dry-run`, ensure:

1. **No file modifications**: Check flag before any write operations
2. **Accurate reporting**: Log messages reflect dry-run state
3. **Consistent language**: Use "would" verbs
4. **Statistics accuracy**: Show what would happen

```python
# ✅ CORRECT - Clear dry-run messaging
if args.dry_run:
    log.inf(f"Dry-run: Would convert {file_path} to {output_path}")
    print(f"  [DRY-RUN] Would write: {output_path}")
else:
    log.inf(f"Converting {file_path} to {output_path}")
    output_path.write_text(content)
    print(f"  ✅ Wrote: {output_path}")

# Final summary
if args.dry_run:
    log.inf(f"Dry-run complete: {count} files prepared (not written)")
else:
    log.inf(f"Conversion complete: {count} files written")
```

```python
# ❌ INCORRECT - Misleading dry-run messaging
if args.dry_run:
    log.inf(f"Wrote {output_path}")  # FALSE - nothing was written!
```

### Pipeline Execution Order

The complete build pipeline (`scripts/gzbuild.cmd|sh`) runs modules in this order:

```
1. clean -e {env}           # Remove orphaned files
2. setup -e {env} --force   # Apply site configuration  
3. gzlint -e {env}          # Validate code quality
4. generate -e {env}        # Generate content files
5. sitemap -e {env}         # Generate sitemap.xml
6. toc -e {env}             # Add table of contents
7. package -e {env}         # Sync, minify, archive
8. deploy -e {env}          # Deploy to environment
```

See `utils/FLOW_PIPELINE.md` for detailed execution flow documentation.

### Module Dependencies

```
gzconfig (configuration library)
    ↓
gzlogging (logging foundation)
    ↓
    ├─→ All pipeline modules use both gzconfig and gzlogging
    ├─→ normalise (called internally by generate)
    └─→ No circular dependencies allowed
```

#### Rules:
- ✅ gzconfig and gzlogging are foundational - all modules can import them
- ✅ Pipeline modules can call each other if documented
- ❌ Never create circular dependencies
- ❌ gzconfig and gzlogging must not import from other project modules

---

## ⚙️ Configuration Management

### Configuration Principles

1. **TOML Format**: Use TOML for configuration files
2. **Comment Preservation**: Setup scripts must preserve user comments
3. **Default Values**: Provide sensible defaults for all settings
4. **Validation**: Validate all configuration values before use
5. **Backward Compatibility**: Old configs should still work after updates

### Configuration Hierarchy

```
config/site.toml          # Main configuration (source of truth)
    ↓
src/css/variables.css     # Generated CSS variables
    ↓
src/index.html            # Generated meta tags, titles
    ↓
src/sitemap.xml           # Generated sitemap
```

### Generated Files

#### Never manually edit these files:
- `src/css/variables.css` - Generated by setup wizard
- `src/sitemap.xml` - Generated by sitemap generator
- Files in `publish/` - Generated by build system

---

## 📚 Documentation Requirements

### When to Create Documentation

1. **New Features**: Document usage, configuration, and examples
2. **Breaking Changes**: Update all affected documentation
3. **Complex Logic**: Add inline comments or separate design docs
4. **User-Facing Tools**: Comprehensive guides with examples

### Documentation Structure

**README.md** - Project overview and quick start  
**docs/SETUP_SITE.md** - Comprehensive setup guide  
**docs/RESPONSIVE_IMAGES.md** - Image optimization guide  
**utils/gzlint/GZ_LINT_RULES.md** - Linter rules and usage  
**DESIGN_RULES.md** - This file (design principles)

### Documentation Style

1. **Markdown Format**: Use standard Markdown
2. **Table of Contents**: For docs > 200 lines
3. **Code Examples**: Include both good and bad examples
4. **Platform-Specific**: Show commands for Windows and Unix
5. **Visual Aids**: Use icons (✅, ❌, ⚠️, 💡) for clarity

---

## 🏗️ Build and Deployment

### Pipeline Architecture (Environment-Based)

**Version 2.0** - Environment-aware build pipeline completed October 23, 2025.

**Status:** ✅ Complete - All 10 pipeline modules are environment-aware.

For detailed execution flow, see `utils/FLOW_PIPELINE.md`.

#### Environment Structure

```
src/                          # SOURCE ONLY (hand-written files)
├── content/                  # Hand-written HTML/Markdown
├── css/                      # Hand-written CSS
├── js/                       # Hand-written JavaScript
└── images/                   # Original images

publish/
├── dev/                      # Development environment (port 7190)
│   ├── content/              # Generated + processed files
│   ├── css/                  # Variables + source CSS
│   ├── js/                   # Source JavaScript
│   ├── images/               # Optimized images
│   ├── index.html            # Updated with config
│   ├── sitemap.xml           # Generated
│   └── gzlint-issues.txt     # Validation report
├── staging/                  # Staging environment (port 7191)
│   └── ...                   # Same structure as dev
└── prod/                     # Production environment (port 7192)
    └── ...                   # Same structure as dev

config/
├── pipeline.toml             # Environment definitions (paths, ports)
├── generate.toml             # Content generation configuration
├── site.toml                 # Site settings (colors, branding, SEO)
├── tools.toml                # Tools configuration (logging, etc.)
└── deploy.toml               # Deployment credentials (gitignored)
```

#### Key Architectural Changes (v2.0)

##### Old Design (pre-October 23, 2025):
- generate → `src/content/`
- package → copies from `src/` to `publish/staging/`
- package → includes orphaned file cleanup

##### New Design (current):
- generate -e {env} → `publish/{env}/content/`
- clean -e {env} → removes orphaned files from `publish/{env}/`
- package -e {env} → syncs, minifies, and archives `publish/{env}/`
- **Separation of concerns**: Each module has single responsibility
- **Centralized configuration**: All modules use gzconfig
- **Centralized logging**: All modules use gzlogging

#### Environment Configuration

Environments are defined in `config/pipeline.toml`:

```toml
[environments.dev]
dir = "dev"
port = 7190
description = "Development environment"

[environments.staging]
dir = "staging"
port = 7191
description = "Staging environment"

[environments.prod]
dir = "prod"
port = 7192
description = "Production build"
```

#### Development Server

The development server requires an environment parameter:

```bash
# Required: specify environment
.\scripts\gzserve.cmd -e dev

# Different environments, different ports (from pipeline.toml)
.\scripts\gzserve.cmd -e staging    # Uses port 7191

# Error: no environment specified
.\scripts\gzserve.cmd              # ❌ WILL FAIL - Missing -e argument
```

### Build Pipeline Order

Complete pipeline via `scripts/gzbuild.cmd|sh -e <environment>`:

```
PREPARATION
  ├─ [1] clean -e {env}
  │      └─ Remove orphaned files from publish/{env}/
  └─ [2] setup -e {env} --force
         ├─ Apply site configuration
         └─ Regenerate config-driven files (CSS variables, etc.)

VALIDATION & GENERATION
  ├─ [3] gzlint -e {env}
  │      ├─ Validate HTML structure
  │      ├─ Validate JavaScript code
  │      └─ Validate configuration files
  └─ [4] generate -e {env}
         ├─ Convert markdown to HTML
         ├─ Output to publish/{env}/content/
         └─ Call normalise internally for heading structure

POST-PROCESSING
  ├─ [5] sitemap -e {env}
  │      └─ Generate sitemap.xml with SEO metadata
  └─ [6] toc -e {env}
         └─ Add table of contents to HTML files with heading IDs

PACKAGING & DEPLOYMENT
  ├─ [7] package -e {env}
  │      ├─ Sync files within publish/{env}/
  │      ├─ Minify CSS and JS files
  │      └─ Create timestamped archive in publish/packages/
  └─ [8] deploy -e {env}
         ├─ Verify package freshness
         ├─ Confirm with user (interactive)
         └─ Upload to FTP/FTPS server

```

#### Run complete pipeline:
```bash
# Windows
.\scripts\gzbuild.cmd -e dev

# Linux/Mac
./scripts/gzbuild.sh -e dev
```

**For detailed flow diagrams and module relationships, see:** `utils/FLOW_PIPELINE.md`

### Deployment Principles

1. **Validate Before Deploy**: Never deploy untested code
2. **Backup Before Upload**: Create backup of previous version
3. **Atomic Operations**: Deploy should succeed or fail completely
4. **Rollback Capability**: Keep recent backups for quick rollback
5. **Verify After Deploy**: Check deployed site works correctly
6. **Deploy from Production Environment**: Always deploy from `publish/prod/`, never from `src/`

### Script Responsibilities

#### gzbuild.cmd|sh (Master Pipeline)

- Runs complete build pipeline from start to finish
- Executes all 8 stages in correct order
- Requires `-e <environment>` argument
- Handles errors at each stage
- See: `scripts/gzbuild.cmd` and `scripts/gzbuild.sh`

#### clean module

- Removes orphaned files from environment directory
- Compares publish/{env}/ against source files
- Source files (src/) are source of truth
- Cleans up empty directories
- See: `utils/clean/README.md`

#### generate module

- Converts markdown to HTML
- Outputs to publish/{env}/content/
- Uses gzconfig for file groups and converters
- Calls normalise internally for heading structure
- See: `utils/generate/README.md`

#### package module

- Syncs files within environment directory
- Minifies CSS and JavaScript
- Creates timestamped ZIP archives
- Keeps last 5 packages for rollback
- See: `utils/package/README.md`

#### deploy module

- Reads deployment configuration
- Uploads to FTP/SFTP server
- Shows progress feedback
- Handles connection errors gracefully

---

## 🔀 Version Control

### Git Workflow

1. **Commit Often**: Small, focused commits
2. **Descriptive Messages**: Explain what and why, not how
3. **Branch Strategy**: Use feature branches for major changes
4. **Ignore Generated Files**: Never commit `publish/` directory

### .gitignore Rules

```
# Build outputs
publish/staging/
publish/packages/
publish/backups/

# Configuration (sensitive)
deploy.config
*.secret
*.key

# Temporary files
*.tmp
*_temp.*
__pycache__/
*.pyc
```

### Commit Message Format

```
feat: Add sitemap generation to package pipeline
fix: Correct UTF-8 encoding in Python files
docs: Update SETUP_SITE.md with new workflow
refactor: Split setup_site.py into modules
style: Fix trailing whitespace in HTML files
test: Add validation tests for color input
```

---

## ✅ Testing and Validation

### Pre-Commit Checks

Before committing code, ensure:

1. ✅ **GZLint Passes**: Run `scripts\gzlint.cmd` or `./scripts/gzlint.sh`
2. ✅ **No console.log()**: Remove debug statements from JavaScript
3. ✅ **Proper Encoding**: All Python files are UTF-8 without BOM
4. ✅ **Headers Present**: All Python files have required headers
5. ✅ **Documentation Updated**: README and relevant docs reflect changes

### Manual Testing

1. **Setup Wizard**: Test both interactive and force-apply modes
2. **Local Server**: Test site works at http://localhost:7190
3. **Build Pipeline**: Ensure package.py completes without errors
4. **Cross-Platform**: Test scripts on both Windows and Unix if possible

### Automated Checks

#### GZLint Rules:
- H1_MISSING: Pages must have exactly one h1
- H1_MULTIPLE: No multiple h1 tags
- H1_ORDER: h1 must come before h2/h3/etc
- CONSOLE_LOG: No console.log() in JavaScript

### Exit Codes

#### All scripts must return proper exit codes:
- `0` - Success (warnings are OK)
- `1` - Failure (errors found)

---

## 🚫 Anti-Patterns to Avoid

### Don't Do This

❌ **Hardcode Configuration Values**
```python
site_name = "GAZ Tank"  # BAD
```

✅ **Load from Configuration**
```python
site_name = config['site']['name']  # GOOD
```

---

❌ **Use Relative Imports in Scripts**
```python
from .ui_helpers import print_header  # BAD - breaks direct execution
```

✅ **Use Absolute Imports**
```python
import ui_helpers  # GOOD - works when run directly
```

---

❌ **Modify Generated Files Manually**
```css
/* variables.css */
:root {
    --color-primary: #FF0000;  /* BAD - will be overwritten */
}
```

✅ **Update Configuration and Regenerate**
```toml
# config/site.toml
[theme]
primary_color = "#FF0000"  # GOOD - source of truth
```

---

❌ **Ignore Exit Codes**
```python
subprocess.run(['python', 'script.py'])  # BAD - ignores failures
```

✅ **Check Exit Codes**
```python
result = subprocess.run(['python', 'script.py'])
if result.returncode != 0:
    print("Script failed!")
    sys.exit(1)
```

---

❌ **Use console.log() in Production**
```javascript
console.log("Loading page...");  // BAD - GZLint will catch this
loadContent(key);
```

✅ **Remove Debug Logging**
```javascript
// Clean production code
loadContent(key);

// Or use console.error() for intentional logging
fetch(url).catch(err => console.error("Failed:", err));
```

---

❌ **Use Regex for Structured Data Parsing**
```python
import re

# BAD - Fragile, breaks on edge cases
html_content = file.read()
title = re.search(r'<title>(.*?)</title>', html_content)

# BAD - Doesn't handle nested tags, attributes, etc.
links = re.findall(r'<a href="(.*?)">', html_content)

# BAD - JavaScript is complex, regex can't parse it safely
js_content = file.read()
site_name = re.sub(r'siteName:\s*".*?"', f'siteName: "{new_name}"', js_content)
```

✅ **Use Proper Parsers for Structured Data**
```python
# GOOD - For HTML: Use BeautifulSoup
from bs4 import BeautifulSoup

soup = BeautifulSoup(html_content, 'html.parser')
title = soup.find('title').string
links = [a['href'] for a in soup.find_all('a', href=True)]

# GOOD - For JavaScript: Use Node.js with Babel AST parser
subprocess.run(['node', 'js_updater.mjs'], input=json.dumps(config))

# GOOD - For URLs: Use urllib.parse
from urllib.parse import urlparse, urlunparse

parsed = urlparse(url)
new_url = urlunparse((parsed.scheme, new_domain, parsed.path, '', '', ''))

# GOOD - For text files: Use line-by-line processing
lines = file.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith('# Title:'):
        lines[i] = f'# Title: {new_title}'
```

#### Why Avoid Regex for Structured Data?

1. **HTML/XML**: Not regular languages - regex can't handle nesting, attributes, entities
2. **JavaScript/Code**: Complex syntax with strings, comments, nested structures
3. **URLs**: Have specific structure (scheme, netloc, path, query) - use urllib.parse
4. **Maintainability**: Regex patterns are cryptic; proper parsers are self-documenting
5. **Edge Cases**: Parsers handle all valid inputs; regex breaks on unexpected formats

#### Project Standards:

| **Data Type** | **Use This** | **Not Regex** |
|---------------|--------------|---------------|
| HTML/XML | BeautifulSoup (`bs4`) | `re.sub()` on HTML |
| JavaScript | Node.js + Babel AST | `re.sub()` on JS code |
| JSON | `json` module | `re.findall()` on JSON |
| URLs | `urllib.parse` | `re.match()` URL patterns |
| Simple text | Line-by-line + `str` methods | `re.sub()` when simple works |
| CSV | `csv` module | `re.split()` |

#### When Regex IS Appropriate:

- ✅ Simple validation: Email format, phone numbers
- ✅ Simple string patterns: Finding dates in plain text
- ✅ Search/replace in unstructured text: Log files, prose
- ✅ Fallback method: When proper parser unavailable (document this!)

#### Example from This Project:

The setup wizard previously used 18+ regex patterns. These were refactored:
- **Phase 1**: HTML → BeautifulSoup (6 patterns eliminated)
- **Phase 2**: JavaScript → Node.js/Babel AST (4 patterns eliminated)
- **Phase 3**: Text files → Line-by-line processing (3 patterns eliminated)
- **Phase 4**: URLs → urllib.parse (2 patterns eliminated)

Only 4 regex patterns remain as a fallback when Node.js is unavailable.

**See Also:** `dev/00TODO/REMOVE_RE_MODULE_FROM_FILE_GENERATORS.md` for detailed refactoring plan

---

❌ **Create Launcher for Only One Platform**
```
# Project structure - BAD
scripts\setup_site.cmd     # Windows only
scripts\deploy.cmd         # Windows only
scripts\package.cmd        # Windows only
```

✅ **Provide Both Platform Launchers**
```
# Project structure - GOOD
scripts\setup_site.cmd + setup_site.sh
scripts\deploy.cmd + deploy.sh
scripts\package.cmd + package.sh
scripts\gzserve.cmd + gzserve.sh
```

---

## 🔄 Change Management

### Adding New Features

1. **Update Configuration**: Add new settings to `config/site.toml` if needed
2. **Update Setup Wizard**: Add prompts for new configuration options
3. **Update File Generators**: Generate files based on new configuration
4. **Update Documentation**: Document new features in relevant files
5. **Update GZLint**: Add new validation rules if applicable
6. **Test End-to-End**: Verify entire workflow works

### Refactoring Existing Code

1. **Maintain Compatibility**: Old configs should still work
2. **Update Tests**: Ensure validation still passes
3. **Update Documentation**: Reflect structural changes
4. **Incremental Changes**: Small, focused refactorings

### Breaking Changes

1. **Document Migration Path**: Explain how to upgrade
2. **Version Bump**: Increment version numbers
3. **Update Changelog**: List breaking changes
4. **Notify Users**: Clear communication about changes

---

## 📐 Architecture Patterns

### Setup Wizard Pattern

```
Main Orchestrator (setup_site.py)
├── UI Helpers (ui_helpers.py)
├── Validators (validators.py)
├── User Interaction (user_interaction.py)
├── Configuration I/O (config_io.py)
├── File Generators (file_generators.py)
└── Backup Manager (backup_manager.py)
```

#### Principles:
- Main script orchestrates, doesn't implement
- Each module has single responsibility
- Absolute imports for direct execution
- No circular dependencies

### Build Pipeline Pattern

```
Validation → Sitemap Generation → Staging → Archiving
    ↓              ↓                 ↓         ↓
  Abort         Abort            Success    Success
```

#### Principles:
- Fail-fast: Stop on first error
- Clear feedback: Show progress at each stage
- Exit codes: Return proper status
- Rollback-safe: Don't modify originals until verified

---

## 🎓 Learning Resources

### Project-Specific

- `README.md` - Project overview
- `docs/SETUP_SITE.md` - Complete setup guide
- `utils/gzlint/GZ_LINT_RULES.md` - Linting rules
- `dev/00TODO/` - Development roadmap

### External Resources

- [Python PEP 8](https://pep8.org/) - Python style guide
- [TOML Spec](https://toml.io/) - TOML format specification
- [Semantic HTML](https://developer.mozilla.org/en-US/docs/Glossary/Semantics#semantics_in_html) - HTML best practices
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) - Accessibility standards

---

## 📝 Final Notes

### When in Doubt

1. **Check Existing Code**: Follow established patterns
2. **Read Documentation**: Comprehensive guides exist
3. **Test Thoroughly**: Run validation before committing
4. **Ask Questions**: Document unclear decisions

### Contributing

When contributing to this project:

1. ✅ Follow these design rules
2. ✅ Write clear commit messages
3. ✅ Update documentation
4. ✅ Test on multiple platforms if possible
5. ✅ Run GZLint before committing

---

## 🔄 Version History

**Version 2.0** (October 23, 2025)
- Added comprehensive Module Architecture Standards section
- Documented environment-aware design (v2.0 architecture)
- Added gzconfig and gzlogging usage patterns
- Documented module maturity checklist (12 criteria)
- Updated build pipeline order (8-stage gzbuild process)
- Documented command line argument standards
- Added dry-run mode implementation guidelines
- Clarified logging vs console output separation
- Updated build and deployment section for v2.0 architecture

**Version 1.0** (October 19, 2025)
- Initial design rules document
- Established core principles and standards
- Documented architecture patterns
- Defined validation requirements
- Python file headers and UTF-8 handling
- Shell script standards (setlocal/endlocal)
- Subprocess Unicode handling patterns

---

### Questions or Suggestions?
Open an issue or submit a pull request with proposed changes to these rules.

---

*"Good design is as little design as possible."* — Dieter Rams

---

### End of Design Rules
