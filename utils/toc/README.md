# Table of Contents (TOC) Generator Module

Environment-aware HTML table of contents generator that adds IDs to headings and injects navigable TOC markup at build time. Processes HTML files in environment-specific publish directories (dev/staging/prod).

**Version:** 1.1.0  
**Last Updated:** October 23, 2025

## Table of Contents

- [Purpose](#purpose)
- [Build Pipeline](#build-pipeline)
- [Logging](#logging)
- [Usage](#usage)
  - [Command Line](#command-line)
  - [Shell Scripts](#shell-scripts)
  - [Direct Module Execution](#direct-module-execution)
  - [As a Module](#as-a-module)
- [Command Line Arguments](#command-line-arguments)
- [Module Structure](#module-structure)
- [Features](#features)
- [Configuration](#configuration)
- [Invocation Points](#invocation-points)
- [How It Works](#how-it-works)
- [Development](#development)
- [Implementation Details](#implementation-details)
- [Customization](#customization)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Design Decisions](#design-decisions)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)

## Purpose

This module processes HTML content files at build time to:

1. **Add unique IDs** to all `<h2>`, `<h3>`, and `<h4>` headings for direct linking
2. **Generate hierarchical TOC structure** based on heading levels
3. **Inject TOC HTML** into content files (positioned after `<h1>`)
4. **Enable SEO-friendly heading anchors** for search engines and users
5. **Eliminate runtime JavaScript processing** for better performance

This module eliminates runtime TOC generation, improving page load performance and SEO. It processes environment-specific output directories (dev/staging/prod) and integrates with the build pipeline.

### Why Build-Time TOC?

#### Build-Time Advantages:
- ✅ Better SEO (IDs in static HTML visible to crawlers)
- ✅ Faster page loads (no runtime parsing required)
- ✅ Simpler JavaScript (only handles interactions)
- ✅ Consistent results across all pages
- ❌ Requires build step (acceptable trade-off)

#### Runtime TOC Disadvantages:
- ❌ Slower (must parse HTML on every page load)
- ❌ IDs not in static HTML (bad for SEO and direct links)
- ❌ Complex JavaScript code required
- ❌ Potential for inconsistent results

## Build Pipeline

The TOC generator is integrated into the GAZTank build pipeline:

```
Content Build Pipeline:
  1. setup       - Apply site configuration (site.toml)
  2. generate    - Convert markdown to HTML
  3. toc         - Add IDs and inject TOC ← This module
  4. sitemap     - Generate sitemap.xml with anchors
  5. package     - Create deployment packages
```

**Purpose:** Adds table of contents and heading anchors to HTML files

**Location:** Processes environment-specific directories: `publish/{environment}/`

### Workflow:
```
pipeline.toml → toc.py → reads HTML → adds IDs + TOC → writes HTML
```

### Benefits:
- Environment-aware processing (dev, staging, prod)
- Smart skip logic (only processes changed files)
- Force regeneration when needed
- Dry-run preview without modifying files
- Comprehensive logging and error handling
- Integrates with sitemap generator (anchors in sitemap)

## Logging

The TOC generator uses **gzlogging** infrastructure for operational logging with environment-aware configuration.

### Log Configuration

- **Environment:** Specified via `-e` argument (dev/staging/prod)
- **Tool Name:** `toc`
- **Log Location:** `logs/{environment}/toc_YYYYMMDD.log`
- **Output Mode:** File-only (console has separate rich formatting)
- **Encoding:** UTF-8

### What Gets Logged

#### Logged to file (clean operational log):
- Table of Contents Generator started
- Environment name (dev/staging/prod)
- Mode settings (Generate/Strip, DRY RUN MODE, FORCE MODE)
- Pipeline configuration loaded successfully
- Target directory path
- Scanning directory and file count
- Processing status for each file with relative paths
- Summary statistics (processed, skipped, errors)
- Completion status (success or errors)
- Error messages without emoji/formatting

#### Console output (rich formatting with emojis):
- Section headers with separators (============)
- Mode indicators: ⚠️ DRY RUN MODE, 🔄 FORCE MODE
- Progress indicators: 📂 for scanning
- Success/failure indicators: ✅ ❌ for completion
- File processing results with ✓ symbols
- Statistics summary in formatted box
- Blank lines for visual spacing
- User-facing messages with emoji

#### Not logged (kept clean):
- No blank lines in log files
- No separator lines (===) in logs
- No emoji or formatting characters in log files
- No decorative elements

### Log File Example

#### Normal mode (skipping already-processed files):
```log
[2025-10-23 09:44:38] [dev] [INF] Table of Contents Generator started
[2025-10-23 09:44:38] [dev] [INF] Environment: dev
[2025-10-23 09:44:38] [dev] [INF] Mode: Generate TOC and IDs
[2025-10-23 09:44:38] [dev] [DBG] Pipeline configuration loaded successfully
[2025-10-23 09:44:38] [dev] [INF] Target directory: D:\Projects\www\GAZTank\publish\dev
[2025-10-23 09:44:38] [dev] [INF] Scanning: D:\Projects\www\GAZTank\publish\dev
[2025-10-23 09:44:38] [dev] [INF] Found 17 HTML files
[2025-10-23 09:44:38] [dev] [INF] Processing HTML files...
[2025-10-23 09:44:38] [dev] [DBG] content\about.html: Skipped (no h2/h3/h4 headings)
[2025-10-23 09:44:38] [dev] [DBG] content\setup\README.html: Skipped (already processed, use --force to regenerate)
[2025-10-23 09:44:38] [dev] [INF] Summary: 0 processed, 17 skipped, 0 errors
[2025-10-23 09:44:38] [dev] [INF] TOC generate completed successfully
```

#### Force mode (regenerating all files):
```log
[2025-10-23 09:47:29] [staging] [INF] Table of Contents Generator started
[2025-10-23 09:47:29] [staging] [INF] Environment: staging
[2025-10-23 09:47:29] [staging] [INF] Mode: Generate TOC and IDs
[2025-10-23 09:47:29] [staging] [INF] DRY RUN MODE enabled
[2025-10-23 09:47:29] [staging] [INF] FORCE MODE enabled
[2025-10-23 09:47:29] [staging] [DBG] Pipeline configuration loaded successfully
[2025-10-23 09:47:29] [staging] [INF] Target directory: D:\Projects\www\GAZTank\publish\staging
[2025-10-23 09:47:29] [staging] [INF] Scanning: D:\Projects\www\GAZTank\publish\staging
[2025-10-23 09:47:29] [staging] [INF] Found 17 HTML files
[2025-10-23 09:47:29] [staging] [INF] Processing HTML files...
[2025-10-23 09:47:29] [staging] [INF] content\setup\DESIGN_RULES.html: ✓ TOC added (17 h2, 49 h3, 42 h4)
[2025-10-23 09:47:29] [staging] [INF] content\setup\DEVELOPER_SETUP.html: ✓ TOC added (14 h2, 37 h3, 36 h4)
[2025-10-23 09:47:29] [staging] [INF] Summary: 10 processed, 7 skipped, 0 errors
[2025-10-23 09:47:29] [staging] [INF] TOC generate completed successfully
```

#### Strip mode (removing TOCs):
```log
[2025-10-23 09:48:15] [dev] [INF] Table of Contents Generator started
[2025-10-23 09:48:15] [dev] [INF] Environment: dev
[2025-10-23 09:48:15] [dev] [INF] Mode: Strip TOC and IDs
[2025-10-23 09:48:15] [dev] [DBG] Pipeline configuration loaded successfully
[2025-10-23 09:48:15] [dev] [INF] Target directory: D:\Projects\www\GAZTank\publish\dev
[2025-10-23 09:48:15] [dev] [INF] Scanning: D:\Projects\www\GAZTank\publish\dev
[2025-10-23 09:48:15] [dev] [INF] Found 17 HTML files
[2025-10-23 09:48:15] [dev] [INF] Stripping HTML files...
[2025-10-23 09:48:15] [dev] [INF] content\setup\README.html: ✓ TOC removed, 54 IDs removed
[2025-10-23 09:48:15] [dev] [INF] Summary: 10 processed, 7 skipped, 0 errors
[2025-10-23 09:48:15] [dev] [INF] TOC strip completed successfully
```

## Usage

### Command Line

**Recommended: Use shell scripts** (automatically handles PYTHONPATH and encoding)

```bash
# Windows - Add TOC to dev environment
.\scripts\generate_toc.cmd -e dev

# Windows - Add TOC to staging environment
.\scripts\generate_toc.cmd -e staging

# Linux/Mac - Add TOC to dev environment
./scripts/generate_toc.sh -e dev

# Windows - Remove TOC (strip mode)
.\scripts\generate_toc.cmd -e dev --strip

# Linux/Mac - Remove TOC (strip mode)
./scripts/generate_toc.sh -e dev --strip

# Preview changes without writing files
.\scripts\generate_toc.cmd -e dev --dry-run
```

### Shell Scripts

#### Windows (generate_toc.cmd):
```batch
.\scripts\generate_toc.cmd -e dev
.\scripts\generate_toc.cmd -e staging --force
.\scripts\generate_toc.cmd -e prod --dry-run
.\scripts\generate_toc.cmd -e dev --strip
```

#### Linux/Mac (generate_toc.sh):
```bash
./scripts/generate_toc.sh -e dev
./scripts/generate_toc.sh -e staging --force
./scripts/generate_toc.sh -e prod --dry-run
./scripts/generate_toc.sh -e dev --strip
```

### Direct Module Execution

```bash
# From project root - Add TOC to dev environment
python -m utils.toc -e dev

# Add TOC to staging or prod
python -m utils.toc -e staging
python -m utils.toc -e prod

# Remove TOC and heading IDs (inverse operation)
python -m utils.toc -e dev --strip

# Preview changes without writing files
python -m utils.toc -e dev --dry-run
python -m utils.toc -e dev --strip --dry-run

# With explicit PYTHONPATH
set PYTHONPATH=%CD%;%PYTHONPATH%           # Windows
export PYTHONPATH="$PWD:$PYTHONPATH"       # Linux/Mac
python -m utils.toc -e dev
```

### As a Module

Import and use in your own Python scripts:

```python
from utils.toc.toc import process_html_file, strip_toc_from_file, scan_html_files
from pathlib import Path

# Note: When using as a module, you need to specify the environment directory
# The environment directory comes from config/pipeline.toml

# Process a single file - Add TOC
file_path = Path('publish/dev/content/about.html')
success, message = process_html_file(file_path)
print(f"{file_path}: {message}")

# Strip TOC from a single file
success, message = strip_toc_from_file(file_path)
print(f"{file_path}: {message}")
```

#### Process multiple files:

```python
# Process all HTML files in an environment directory
env_dir = Path('publish/dev')
html_files = scan_html_files(env_dir)

for html_file in html_files:
    success, message = process_html_file(html_file)
    print(f"{html_file}: {message}")
```

#### Utility functions:

```python
from utils.toc.toc import slugify, add_ids_to_headings, build_toc_structure
from bs4 import BeautifulSoup

# Generate slug from heading text
slug = slugify("1. Meta Tags (index.html)")
# Returns: "meta-tags-index-html"

# Add IDs to headings in HTML
html = '<h2>My Heading</h2><h3>Subheading</h3>'
soup = BeautifulSoup(html, 'html.parser')
headings = add_ids_to_headings(soup)
# headings = [
#   {'level': 'h2', 'text': 'My Heading', 'id': 'my-heading', 'element': <h2>},
#   {'level': 'h3', 'text': 'Subheading', 'id': 'subheading', 'element': <h3>}
# ]

# Build TOC HTML from headings
toc_html = build_toc_structure(headings)
# Returns: complete <nav> HTML with nested lists
```

## Command Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `-e, --environment` | **Yes** | - | Environment to process: `dev`, `staging`, or `prod` |
| `--strip` | No | False | Remove TOC and heading IDs (inverse operation) |
| `--force` | No | False | Force processing of all files (ignore existing TOCs) |
| `--dry-run` | No | False | Preview changes without writing to files |
| `-h, --help` | No | - | Show help message and exit |

### Argument Details

#### `-e, --environment {dev,staging,prod}` (Required)
- Specifies which environment directory to process
- Corresponds to sections in `config/pipeline.toml`
- Determines output directory: `publish/{environment}/`
- Examples: `-e dev`, `-e staging`, `-e prod`

#### `--strip` (Optional)
- Removes TOC navigation elements from HTML
- Removes `id` attributes from h2, h3, h4 headings
- Inverse operation of normal processing
- Useful for reverting changes or testing

#### `--force` (Optional)
- Processes all files regardless of existing content
- Without `--force`: Skips files that already have TOC and heading IDs
- With `--force`: Regenerates TOC for all files
- Useful after TOC template changes or heading updates
- Can be combined with `--dry-run` to preview forced regeneration

#### `--dry-run` (Optional)
- Shows what would be done without modifying files
- All logic executes normally (parsing, TOC generation)
- No files are written to disk
- Logging reflects dry-run mode
- Useful for testing and verification

### Usage Examples

```bash
# Standard processing (skip already-processed files)
python -m utils.toc -e dev

# Force regeneration of all TOCs
python -m utils.toc -e staging --force

# Preview what would be processed
python -m utils.toc -e prod --dry-run

# Preview forced regeneration
python -m utils.toc -e dev --force --dry-run

# Remove all TOCs and heading IDs
python -m utils.toc -e dev --strip

# Preview TOC removal
python -m utils.toc -e dev --strip --dry-run
```

## Module Structure

```
toc/
├── __init__.py        # Module initialization and exports
├── __main__.py        # Entry point for python -m toc
├── toc.py             # Core TOC generation logic
└── README.md          # This file (comprehensive documentation)
```

### Key Functions

#### High-Level Processing:
- **`main()`** - Entry point for command-line usage
- **`scan_html_files(src_dir)`** - Recursively find all .html files (skip index.html)
- **`process_html_file(file_path, dry_run=False, force=False)`** - Process single file (add TOC)
- **`strip_toc_from_file(file_path, dry_run=False, force=False)`** - Strip TOC from single file

#### ID Generation:
- **`slugify(text)`** - Convert heading text to URL-friendly slug
- **`add_ids_to_headings(soup)`** - Add unique IDs to h2, h3, h4 tags

#### TOC Building:
- **`build_toc_structure(headings)`** - Generate hierarchical TOC HTML
- **`inject_toc(soup, toc_html)`** - Inject TOC into HTML document
- **`remove_existing_toc(soup)`** - Remove existing TOC from document

#### Utilities:
- **`remove_ids_from_headings(soup)`** - Remove IDs from h2, h3, h4 tags

## Features

### ✅ Automatic ID Generation

- **Converts heading text to URL-friendly slugs**
  - Example: `"1. Meta Tags (index.html)"` → `"meta-tags-index-html"`
  - Removes HTML tags, leading numbers, special characters
  - Replaces spaces with hyphens
  - Converts to lowercase

- **Ensures uniqueness across document**
  - Tracks used IDs in a set
  - Appends `-1`, `-2`, etc. for duplicates
  - Example: Second "Introduction" becomes `"introduction-1"`

### ✅ Hierarchical TOC Structure

- **Properly nested lists based on heading levels**
  - h2 → Top-level items
  - h3 → Nested under parent h2
  - h4 → Nested under parent h3

- **Semantic HTML structure**
  - Uses `<nav>` element with `table-of-contents` class
  - Nested `<ul>` lists for hierarchy
  - Anchor links to heading IDs

### ✅ Smart Injection

- **Positions TOC after h1 (main heading)**
  - Fallback: Insert before first content element
  - Skips files with no h2/h3/h4 headings
  - Removes existing TOC before generating new one

### ✅ Environment-Aware Processing

- **Processes environment-specific directories**
  - Uses `config/pipeline.toml` for configuration
  - Targets `publish/{environment}/` directories
  - Supports dev, staging, prod environments

### ✅ Intelligent Skip Logic

- **Without --force:** Skips already-processed files
  - Checks for existing TOC navigation
  - Checks for heading IDs
  - Displays helpful message: "already processed, use --force"

- **With --force:** Regenerates all TOCs
  - Useful after template changes
  - Useful after heading content updates
  - Ensures consistency across all files

### ✅ Inverse Operation (Strip Mode)

- **Remove TOC:** Strips `<nav class="table-of-contents">` from HTML
- **Remove IDs:** Removes `id` attributes from h2, h3, h4 headings
- **Clean source:** Returns HTML to pre-processed state
- **Dry-run support:** Preview removal without writing

### ✅ SEO Benefits

- **All heading IDs in static HTML** (visible to search crawlers)
- **Direct linking to sections** works immediately on page load
- **Better content structure** signals for search engines
- **No JavaScript required** for basic TOC functionality
- **Faster indexing** (no need to execute JavaScript)

### ✅ Performance Benefits

- **No runtime HTML parsing** (all done at build time)
- **Faster page loads** (no JavaScript processing overhead)
- **Better caching** (static HTML changes less frequently)
- **Reduced JavaScript complexity** (only handles interactions)

## Configuration

The TOC generator uses `config/pipeline.toml` for environment configuration.

### Pipeline Configuration

**File:** `config/pipeline.toml`

```toml
# Build Pipeline Configuration
# Each environment has:
# - dir: Directory name under publish/ where build artifacts are stored
# - httpd_port: Default port for the development server
# - description: Human-readable description of the environment

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
description = "Production-ready build for deployment"
```

### How Configuration is Used

1. **Environment argument** (`-e dev`) selects configuration section
2. **gzconfig module** reads `pipeline.toml` and provides typed access
3. **Directory path** (`publish/dev/`) is derived from `dir` setting
4. **Module processes** all HTML files in environment directory

### Configuration Access

The module uses **gzconfig** for configuration access:

```python
from utils.gzconfig import get_pipeline_config

# Get environment configuration
env_config = get_pipeline_config('dev')

# Access environment directory
env_dir = env_config.directory_path  # Returns Path('publish/dev')

# Environment description (for logging)
description = env_config.description
```

## Invocation Points

### Direct Invocation

```bash
# Windows shell scripts
.\scripts\generate_toc.cmd -e dev
.\scripts\generate_toc.cmd -e staging --force

# Linux/Mac shell scripts
./scripts/generate_toc.sh -e dev
./scripts/generate_toc.sh -e staging --force

# Direct Python module
python -m utils.toc -e dev
python -m utils.toc -e staging --force
```

### Build Pipeline Integration

Called automatically as part of the content generation pipeline:

```bash
# Windows pipeline script
.\scripts\gzbuild.cmd -e dev

# Linux/Mac pipeline script
./scripts/gzbuild.sh -e dev
```

#### Pipeline execution order:
```
1. clean      - Remove orphaned files
2. generate   - Generate content files
3. compose    - Assemble HTML from components
4. setup      - Apply site configuration
5. gzlint     - Run linting checks
6. normalise  - Normalize markdown structure
7. sitemap    - Generate sitemap.xml
8. toc        - Add TOC and heading IDs (this module)
9. package    - Sync, minify, and archive
10. deploy    - Deploy to environment
```

### Called By

- `scripts/generate_toc.cmd` - Windows launcher
- `scripts/generate_toc.sh` - Linux/Mac launcher
- `scripts/gzbuild.cmd` - Windows build pipeline
- `scripts/gzbuild.sh` - Linux/Mac build pipeline
- Build automation scripts
- Developer workflows

## How It Works

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    TOC GENERATOR WORKFLOW                   │
├─────────────────────────────────────────────────────────────┤
│  [1/5] Parse Arguments & Initialize                         │
│     ├─ Parse -e environment argument (required)             │
│     ├─ Parse --strip, --force, --dry-run flags              │
│     ├─ Initialize gzlogging (console=False)                 │
│     └─ Print console header with mode indicators            │
│                                                             │
│  [2/5] Load Configuration                                   │
│     ├─ Use gzconfig to read pipeline.toml                   │
│     ├─ Get environment directory (publish/{env}/)           │
│     └─ Validate directory exists                            │
│                                                             │
│  [3/5] Scan Files                                           │
│     ├─ Recursively find *.html in environment dir           │
│     ├─ Skip index.html (main SPA file)                      │
│     └─ Report file count to console and log                 │
│                                                             │
│  [4/5] Process Each File                                    │
│     ├─ Read and parse HTML with BeautifulSoup               │
│     ├─ Check if processing needed (skip if not forced)      │
│     ├─ Remove existing TOC (if present)                     │
│     ├─ Add unique IDs to h2, h3, h4 headings                │
│     ├─ Build hierarchical TOC HTML structure                │
│     ├─ Inject TOC after <h1> (or at top of content)         │
│     ├─ Write modified HTML (unless dry-run)                 │
│     └─ Log result (processed/skipped/error)                 │
│                                                             │
│  [5/5] Report Results                                       │
│     ├─ Print statistics to console (formatted box)          │
│     ├─ Log summary (processed, skipped, errors)             │
│     └─ Return exit code (0=success, 1=errors)               │
└─────────────────────────────────────────────────────────────┘
```

### Example Transformation

#### Input HTML (before processing):
```html
<h1>SEO Implementation Summary</h1>
<h2>Meta Tags (index.html)</h2>
<p>Content about meta tags...</p>
<h3>Primary Meta Tags</h3>
<p>More details...</p>
<h3>Social Media Tags</h3>
<p>Open Graph and Twitter Cards...</p>
<h2>Structured Data</h2>
<p>JSON-LD implementation...</p>
```

#### Output HTML (after processing):
```html
<h1>SEO Implementation Summary</h1>
<nav class="table-of-contents">
  <div class="toc-header">
    <div class="toc-header-left">
      <ul>
        <li class="toc-section">
          <div class="toc-section-header">
            <button class="toc-section-toggle" data-section="headings">▼</button>
            <span class="toc-section-title">Contents</span>
          </div>
          <ul class="toc-section-content" data-section="headings">
            <li>
              <a href="#meta-tags-index-html">Meta Tags (index.html)</a>
              <ul>
                <li>
                  <a href="#primary-meta-tags">Primary Meta Tags</a>
                </li>
                <li>
                  <a href="#social-media-tags">Social Media Tags</a>
                </li>
              </ul>
            </li>
            <li>
              <a href="#structured-data">Structured Data</a>
            </li>
          </ul>
        </li>
      </ul>
    </div>
    <div class="toc-header-right">
      <button class="toc-toggle" aria-label="Toggle table of contents">▼</button>
    </div>
  </div>
</nav>
<h2 id="meta-tags-index-html">Meta Tags (index.html)</h2>
<p>Content about meta tags...</p>
<h3 id="primary-meta-tags">Primary Meta Tags</h3>
<p>More details...</p>
<h3 id="social-media-tags">Social Media Tags</h3>
<p>Open Graph and Twitter Cards...</p>
<h2 id="structured-data">Structured Data</h2>
<p>JSON-LD implementation...</p>
```

### Processing Logic

#### Skip logic (without --force):
1. Check if file has `<nav class="table-of-contents">`
2. Check if h2/h3/h4 headings have `id` attributes
3. If both exist → Skip with message "already processed"
4. Otherwise → Process the file

#### Force logic (with --force):
1. Process all files regardless of existing content
2. Remove existing TOC if present
3. Remove existing heading IDs
4. Regenerate everything from scratch

#### Strip logic (with --strip):
1. Find `<nav class="table-of-contents">` and remove
2. Remove `id` attributes from h2, h3, h4 headings
3. Report what was removed (TOC, ID count)

## Development

### Dependencies

#### Core:
- **Python 3.8+** - Required for type hints and pathlib
- **BeautifulSoup4** - HTML parsing and manipulation
- **gzconfig** - Configuration management (pipeline.toml)
- **gzlogging** - Environment-aware logging

#### Development:
- Type hints for IDE support
- Pathlib for cross-platform paths
- UTF-8 encoding throughout

### Adding New Features

#### To add support for h5/h6 headings:

```python
# In toc.py
def add_ids_to_headings(soup):
    """Update to include h5, h6"""
    for tag_name in ['h2', 'h3', 'h4', 'h5', 'h6']:  # Add h5, h6
        # ... rest of function
```

#### To customize TOC HTML structure:

```python
# In toc.py
def build_toc_structure(headings):
    """Modify HTML output structure"""
    html_parts = []
    html_parts.append('<div class="my-custom-toc">')  # Custom wrapper
    html_parts.append('  <h3>Page Contents</h3>')     # Custom heading
    # ... build nested list structure ...
    html_parts.append('</div>')
    return '\n'.join(html_parts)
```

#### To change slug generation:

```python
# In toc.py
def slugify(text: str) -> str:
    """Customize slug generation"""
    # Keep numbers in slugs:
    # Comment out: text = re.sub(r'^[\d\.\)\]\}\s]+', '', text)
    
    # Use underscores instead of hyphens:
    text = re.sub(r'[\s-]+', '_', text)
    
    # ... rest of function
```

### Testing

```bash
# Test with dry-run to preview changes
python -m utils.toc -e dev --dry-run

# Test force regeneration
python -m utils.toc -e dev --force --dry-run

# Test strip operation
python -m utils.toc -e dev --strip --dry-run

# Verify logging
Get-Content logs/dev/toc_YYYYMMDD.log

# Test on specific environment
python -m utils.toc -e staging --dry-run
```

### Code Quality

- Type hints on all function signatures
- Comprehensive docstrings with Args/Returns
- Consistent error handling with try/except
- Separation of concerns (parse, process, inject)
- Clean logging (file vs console separation)

## Implementation Details

### ID Slugification Algorithm

```python
def slugify(text: str) -> str:
    """
    Conversion steps:
    1. Remove HTML tags:     "<strong>Text</strong>" → "Text"
    2. Convert to lowercase: "Text" → "text"
    3. Remove leading nums:  "1. Text" → "Text"
    4. Remove special chars: "Text (v2)" → "Text v2"
    5. Replace spaces:       "Text v2" → "text-v2"
    6. Strip hyphens:        "-text-v2-" → "text-v2"
    """
```

#### Examples:
- `"1. Meta Tags (index.html)"` → `"meta-tags-index-html"`
- `"Getting Started"` → `"getting-started"`
- `"FAQ: Common Questions"` → `"faq-common-questions"`

### Duplicate ID Handling

IDs are tracked in a set to ensure uniqueness:

```python
# First "Introduction" → id="introduction"
# Second "Introduction" → id="introduction-1"
# Third "Introduction" → id="introduction-2"
```

### Heading Hierarchy

The TOC respects semantic heading levels:

```
h2                ← Level 1 (top-level items)
  h3              ← Level 2 (nested under h2)
    h4            ← Level 3 (nested under h3)
  h3              ← Level 2 (sibling of previous h3)
h2                ← Level 1 (sibling of first h2)
```

### File Skipping Logic

Files are skipped if:
- They are `index.html` (main SPA file)
- They have no h2, h3, or h4 headings
- They only have h1 (insufficient structure for TOC)
- They already have TOC and IDs (unless `--force` is used)

### BeautifulSoup Usage

- **Parser:** `'html.parser'` (built-in, no external dependencies)
- **Encoding:** UTF-8 for reading and writing
- **Manipulation:** Clean DOM API for adding IDs and injecting elements
- **Robustness:** Handles malformed HTML gracefully

## Customization

### Change Heading Levels

To include h5 and h6 in TOC:

```python
# In toc.py
def add_ids_to_headings(soup):
    for tag_name in ['h2', 'h3', 'h4', 'h5', 'h6']:  # Add h5, h6
        # ... rest of function
```

### Modify Slug Generation

To keep numbers in IDs:

```python
def slugify(text: str) -> str:
    # ... existing code ...
    
    # Comment out this line:
    # text = re.sub(r'^[\d\.\)\]\}\s]+', '', text)
    
    # ... rest of function
```

### Change TOC HTML Structure

Modify `build_toc_structure()` to change HTML output:

```python
def build_toc_structure(headings):
    html_parts = []
    html_parts.append('<div class="my-custom-toc">')  # Custom wrapper
    html_parts.append('  <h3>Contents</h3>')           # Custom heading
    # ... build list structure ...
    html_parts.append('</div>')
    return '\n'.join(html_parts)
```

### Add CSS Classes

Modify HTML generation to add custom classes:

```python
# Add class to individual TOC links
html_parts.append(f'  <a href="#{id}" class="toc-link">{text}</a>')

# Add level-based classes
html_parts.append(f'  <li class="toc-level-{level_num}">')
```

## Best Practices

### When to Use --force

Use `--force` when:
- TOC template HTML structure has changed
- Heading content has been significantly updated
- Testing TOC generation on all files
- Debugging TOC issues across the site
- After modifying TOC CSS classes

Don't use `--force` for:
- Normal incremental builds (wastes time)
- Files that haven't changed (no benefit)

### When to Use --dry-run

Use `--dry-run` to:
- Preview what would be processed before committing changes
- Verify skip logic is working correctly
- Test new features without modifying files
- Debug issues without affecting production files
- Check statistics before bulk processing

### When to Use --strip

Use `--strip` to:
- Remove TOC for testing purposes
- Revert to pre-processed HTML state
- Prepare files for manual editing
- Debug TOC-related issues
- Clean up before regenerating with new structure

### Environment Workflow

#### Development cycle:
```bash
# 1. Work in dev environment
python -m utils.toc -e dev

# 2. Test changes
python -m utils.toc -e dev --force --dry-run

# 3. Stage for testing
python -m utils.toc -e staging

# 4. Deploy to production
python -m utils.toc -e prod
```

### Integration with Build Pipeline

#### Typical workflow:
```bash
# 1. Generate HTML from markdown
python -m utils.generate

# 2. Add TOC to generated HTML (this module)
python -m utils.toc -e dev

# 3. Generate sitemap with anchors
python -m utils.sitemap -e dev

# 4. Package for deployment
python -m utils.package -e dev
```

Or use the all-in-one pipeline:
```bash
.\scripts\gzbuild.cmd -e dev
```

## Troubleshooting

### No HTML files found to process

**Problem:** Module can't find HTML files

#### Causes:
- Environment directory doesn't exist
- No build has been run for the environment
- Wrong environment argument

#### Solutions:
1. Verify environment directory exists: `publish/{environment}/`
2. Run a build first: `python -m utils.generate` then setup/file copy
3. Check environment argument: `-e dev`, `-e staging`, or `-e prod`
4. Ensure HTML files have `.html` extension

### Failed to inject TOC

**Problem:** TOC generation succeeds but injection fails

#### Causes:
- Malformed HTML structure
- Missing or multiple h1 tags
- Empty or invalid file

#### Solutions:
1. Verify HTML file has valid structure
2. Check if there's an `<h1>` tag in the file
3. Ensure file is not empty or corrupted
4. Use `--dry-run` to see error details without modifying

### Duplicate IDs in output

**Problem:** Multiple headings get the same ID

#### Expected behavior:
- This should NOT happen due to uniqueness checking
- Module automatically appends `-1`, `-2`, etc. for duplicates

#### If it occurs:
1. File a bug report with sample HTML
2. Check for special characters in heading text
3. Verify BeautifulSoup version is up to date

### TOC appears twice

**Problem:** Running generator multiple times creates duplicate TOCs

#### Expected behavior:
- This should NOT happen due to `remove_existing_toc()`
- Module removes old TOC before generating new one

#### If it occurs:
1. Check for TOCs with different class names
2. Verify only one `<nav class="table-of-contents">` exists
3. Use `--strip` to remove all TOCs, then regenerate

### Encoding errors (UnicodeEncodeError)

**Problem:** Non-ASCII characters cause errors

#### Context:
- Only occurs when redirecting output (e.g., `2>&1 |`)
- Normal console output works fine with emojis
- Windows console encoding issue

#### Solutions:
1. **Normal usage:** Run commands directly (no redirection)
2. **If you must redirect:** Error is expected on Windows
3. **Log files:** Always work correctly (UTF-8)
4. **Emojis in console:** Work correctly in normal usage

### Already processed, use --force

**Problem:** Files are skipped even though they should be processed

#### Causes:
- Files have existing TOC and heading IDs
- Skip logic is working as designed

#### Solutions:
1. Use `--force` to regenerate: `python -m utils.toc -e dev --force`
2. This is normal behavior (saves time on unchanged files)
3. Force regeneration when headings change significantly

### Environment directory not found

**Problem:** Error message about missing environment directory

#### Causes:
- Build hasn't been run for the environment
- Typo in environment argument
- Wrong project directory

#### Solutions:
1. Run build first: `python -m utils.generate`
2. Copy files to publish directory (via setup module)
3. Verify environment argument is correct: `dev`, `staging`, or `prod`
4. Check you're in the project root directory

## Design Decisions

### Why Build-Time vs Runtime?

#### Build-Time TOC (this approach):
- ✅ Better SEO (IDs in static HTML)
- ✅ Faster page loads (no parsing overhead)
- ✅ Simpler JavaScript (just interactions)
- ✅ Consistent results across pages
- ❌ Requires build step (acceptable)

#### Runtime TOC (JavaScript):
- ✅ No build step required
- ❌ Slower (must parse on every load)
- ❌ IDs not in static HTML (bad SEO)
- ❌ Complex JavaScript required
- ❌ Potential for inconsistent results

### Why Environment-Specific Processing?

- Different environments have different content
- Allows testing in dev before deploying
- Staging can be used for pre-production validation
- Production gets only verified, tested content

### Why Skip Already-Processed Files?

- Improves performance for large documentation sets
- Prevents unnecessary file writes (reduces disk I/O)
- Preserves file timestamps for cache invalidation
- Use `--force` when you need to regenerate all files

### Why h2/h3/h4 Only?

- h1 is the page title (not part of content TOC)
- h2-h4 provides sufficient depth for most content
- Deeper nesting (h5/h6) rarely needed
- Can be extended if needed (see Customization)

### Why BeautifulSoup?

- Well-maintained, stable library
- Clean API for HTML manipulation
- Handles malformed HTML gracefully
- No heavy dependencies
- Works with built-in `html.parser`

## Future Enhancements

- [ ] Support for h5/h6 headings (configurable depth)
- [ ] Wildcard file patterns in configuration
- [ ] Automatic detection of heading changes (timestamp comparison)
- [ ] Custom TOC templates (configurable HTML structure)
- [ ] TOC position customization (before/after h1, custom selector)
- [ ] Multi-language slug generation (transliteration support)
- [ ] TOC caching to improve regeneration performance
- [ ] Parallel processing for large file sets
- [ ] Custom ID prefix/suffix options
- [ ] TOC fragment links validation (check all IDs exist)
- [ ] Integration with linting tools (validate heading structure)
- [ ] Markdown TOC generation (for source files)

## Related Documentation

- **Pipeline Configuration:** `config/pipeline.toml` - Environment settings
- **Build Pipeline:** `utils/generate/README.md` - Overall content generation
- **Sitemap Generator:** `utils/sitemap/README.md` - Integrates with TOC anchors
- **Setup Module:** `utils/setup/README.md` - Site configuration
- **Logging System:** `utils/gzlogging/README.md` - Logging infrastructure
- **Configuration Module:** `utils/gzconfig/README.md` - Configuration management
- **Project Structure:** `dev/PROJECT_STRUCTURE.md` - Overall project organization
- **Module Structure:** `dev/MODULE_README_STRUCTURE.md` - README template

## License

This module is part of the GAZTank project.

**License:** GPL v3.0 or later  
**SPDX-License-Identifier:** GPL-3.0-or-later

See `LICENSE` file in project root for full license text.

## Authors

superguru, gazorper

---

*Last updated: October 23, 2025*  
*TOC Generator version: 1.1.0*
