# Sitemap Generator

Automatically generates XML sitemaps for search engine optimization (SEO). Scans content files and navigation structure to create properly formatted sitemap.xml with priorities and change frequencies.

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
- [How It Works](#how-it-works)
- [Priority Calculation](#priority-calculation)
- [Change Frequency](#change-frequency)
- [Invocation Points](#invocation-points)
- [Development](#development)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [XML Sitemap Specification](#xml-sitemap-specification)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)

## Purpose

The Sitemap Generator creates XML sitemaps that help search engines discover and index all pages on your website. It automatically:

1. **Scans content files** - Finds all HTML content in environment-specific directories
2. **Parses navigation** - Extracts hierarchy from index.html
3. **Assigns priorities** - Sets SEO priorities based on page importance (0.0-1.0)
4. **Determines change frequency** - Estimates how often pages are updated
5. **Generates sitemap.xml** - Creates properly formatted XML output

### Environment-Aware

The generator is fully integrated with the pipeline configuration system:
- Supports multiple environments: **dev**, **staging**, **prod**
- Reads from `config/pipeline.toml` for environment paths
- Generates sitemaps for specific deployment targets
- Ensures sitemaps match deployed content structure

## Build Pipeline

The sitemap generator integrates with the GAZTank build and deployment pipeline:

```
Sitemap Generation Pipeline:
  1. Read environment from -e argument (dev/staging/prod)
  2. Load pipeline.toml configuration
  3. Resolve environment directory: publish/{env}/
  4. Scan content files: publish/{env}/content/*.html
  5. Parse navigation: publish/{env}/index.html
  6. Build XML structure with priorities and frequencies
  7. Write sitemap: publish/{env}/sitemap.xml
  8. Log completion statistics
```

**Purpose:** Generates SEO-optimized sitemaps for deployed environments

**Location:** Called via `scripts/generate_sitemap.cmd` or as part of packaging pre-flight

### Workflow:
```
pipeline.toml → sitemapper.py → scans publish/{env}/ → writes sitemap.xml
```

### Benefits:
- Environment-specific sitemap generation
- Automatic priority calculation based on navigation hierarchy
- Intelligent change frequency estimation
- Search engine submission ready
- Dry-run mode for preview without writing

### Pre-flight Integration

The sitemap generator runs as part of the packaging pre-flight checks:

```
Package Pre-flight:
  1. Run validation (gzlint)
  2. Convert markdown to HTML (generate)
  3. Generate sitemap ← This module
  4. Continue with packaging...
```

This ensures the sitemap is always up-to-date before deployment.

## Logging

The generator uses the **gzlogging** infrastructure for operational logging.

### Log Configuration

- **Environment:** Matches `-e` argument (dev/staging/prod)
- **Tool Name:** `sitemapper`
- **Log Location:** `logs/{env}/sitemapper_YYYYMMDD.log`
- **Output Mode:** File + console (console shows progress with emojis)
- **Encoding:** UTF-8

### What Gets Logged

#### Logged to file (clean operational log):
- Sitemap Generator started
- Environment and mode settings (DRY RUN MODE enabled if applicable)
- Pipeline configuration loaded
- Target directory identified
- Starting sitemap generation
- Base URL, content directory, output file paths
- Number of content files found
- Number of navigation entries parsed
- Building sitemap XML structure
- Writing sitemap or dry-run completion
- URLs written/prepared count
- Sitemap Generator completed successfully

#### Console output (rich formatting with emojis):
- Progress indicators: [1/4] 📄 [2/4] 🗺️ [3/4] 🔨 [4/4] 📝/👁️
- Statistics: file counts, URLs included
- Mode warnings: ⚠️ DRY RUN MODE
- Success indicators: ✅ SITEMAP GENERATION COMPLETE
- Next steps guidance
- Error messages if failures occur

#### Not logged (kept clean):
- No blank lines in log files
- No separator lines (===) in logs
- No emoji or formatting characters in log files

### Log Example

```
[2025-10-22 14:15:30] [dev] [INF] Sitemap Generator started
[2025-10-22 14:15:30] [dev] [INF] Environment: dev
[2025-10-22 14:15:30] [dev] [INF] DRY RUN MODE enabled
[2025-10-22 14:15:30] [dev] [DBG] Pipeline configuration loaded successfully
[2025-10-22 14:15:30] [dev] [INF] Target directory: D:\Projects\www\GAZTank\publish\dev
[2025-10-22 14:15:30] [dev] [INF] Starting sitemap generation
[2025-10-22 14:15:30] [dev] [INF] Base URL: https://mygaztank.com/
[2025-10-22 14:15:30] [dev] [INF] Content directory: D:\Projects\www\GAZTank\publish\dev\content
[2025-10-22 14:15:30] [dev] [INF] Output file: D:\Projects\www\GAZTank\publish\dev\sitemap.xml
[2025-10-22 14:15:30] [dev] [INF] Found 6 content files in D:\Projects\www\GAZTank\publish\dev\content
[2025-10-22 14:15:30] [dev] [INF] Parsed 0 navigation entries from index.html
[2025-10-22 14:15:30] [dev] [INF] Building sitemap XML structure
[2025-10-22 14:15:30] [dev] [INF] Dry-run complete: 6 URLs prepared (not written)
[2025-10-22 14:15:30] [dev] [INF] Sitemap Generator completed successfully
```

## Usage

### Command Line

```bash
# Using the launcher script (recommended)
scripts\generate_sitemap.cmd -e dev              # Windows
./scripts/generate_sitemap.sh -e dev             # Linux/Mac

# Generate for different environments
scripts\generate_sitemap.cmd -e dev              # Development
scripts\generate_sitemap.cmd -e staging          # Staging
scripts\generate_sitemap.cmd -e prod             # Production

# Dry-run mode (preview without writing)
scripts\generate_sitemap.cmd -e dev --dry-run

# Or directly as a Python module
python -m sitemap -e dev
python -m sitemap -e staging --dry-run

# From utils directory with PYTHONPATH set
export PYTHONPATH="$PWD/utils:$PYTHONPATH"  # Linux/Mac
set PYTHONPATH=%CD%\utils;%PYTHONPATH%      # Windows
python -m sitemap -e dev
```

### As a Module

You can import and use the sitemap functions in your own Python scripts:

```python
from sitemap import generate_sitemap
from pathlib import Path
from utils.gzlogging import get_logging_context

# Initialize logging
log = get_logging_context('dev', 'sitemapper', console=True)

# Define paths
content_dir = Path('publish/dev/content')
index_file = Path('publish/dev/index.html')
output_file = Path('publish/dev/sitemap.xml')
base_url = 'https://mygaztank.com/'

# Generate sitemap
generate_sitemap(base_url, content_dir, index_file, output_file, log, dry_run=False)
```

For more granular control:

```python
from sitemap.sitemapper import (
    get_content_files,
    parse_navigation_structure,
    calculate_priority,
    determine_changefreq,
    get_environment_directory,
    load_pipeline_config
)

# Load configuration
config = load_pipeline_config()

# Get environment directory
env_dir = get_environment_directory('dev', config)
content_dir = env_dir / 'content'

# Get list of content files
content_files = get_content_files(content_dir, log)
print(f"Found {len(content_files)} content files")

# Parse navigation
index_file = env_dir / 'index.html'
nav_structure = parse_navigation_structure(index_file, log)
for key, info in nav_structure.items():
    print(f"{key}: level={info['level']}, priority={info['priority']}")
```

## Command Line Arguments

### Required Arguments

- **`-e, --environment`** - Environment to generate sitemap for
  - Choices: `dev`, `staging`, `prod`
  - Reads configuration from `config/pipeline.toml`
  - Determines input/output directories: `publish/{env}/`
  - Example: `-e dev` generates from `publish/dev/`

### Optional Arguments

- **`--dry-run`** - Show what would be done without writing files
  - Performs all scanning and analysis
  - Displays statistics and preview information
  - Does not modify sitemap.xml
  - Useful for testing and validation
  - Example: `--dry-run` shows "Would write to: publish/dev/sitemap.xml"

- **`--help`** - Show help message with usage examples

### Examples

```bash
# Generate sitemap for dev environment
python -m sitemap -e dev

# Preview what would be generated for staging
python -m sitemap -e staging --dry-run

# Generate for production deployment
python -m sitemap -e prod

# Show help and usage information
python -m sitemap --help
```

## Module Structure

```
sitemap/
├── __init__.py      # Package initialization and exports
├── __main__.py      # Entry point for python -m sitemap
├── sitemapper.py    # Core sitemap generation logic (renamed from generator.py)
└── README.md        # This file
```

### Key Files

- **`sitemapper.py`** - Main module containing all sitemap generation logic
- **`__init__.py`** - Exports public functions for module usage
- **`__main__.py`** - Entry point that calls `main()` from sitemapper.py

## Features

### ✅ Current Features

- **Environment-aware generation** - Supports dev/staging/prod from pipeline.toml
- **Automatic content scanning** - Finds all HTML files in content directory
- **Navigation hierarchy parsing** - Extracts structure from index.html
- **Intelligent priority assignment** - Based on navigation level and page type
- **Change frequency estimation** - Estimates update frequency per content type
- **Last modification tracking** - Uses file timestamps for `<lastmod>` dates
- **Pretty-printed XML** - Human-readable formatted output
- **Hash-based URLs** - Supports SPA navigation pattern (#content-key)
- **Dry-run mode** - Preview generation without writing files
- **Comprehensive logging** - Structured logs via gzlogging
- **Console progress indicators** - Visual feedback with emojis
- **Exit code support** - Proper error codes for automation
- **UTF-8 encoding** - Full Unicode support in console and files

### Key Functions

#### High-Level

- **`generate_sitemap(base_url, content_dir, index_file, output_file, log, dry_run=False)`**
  - Main function that generates complete sitemap.xml
  - Handles entire workflow from scanning to writing
  - Supports dry-run mode for preview

#### Configuration

- **`load_pipeline_config()`**
  - Loads pipeline configuration from config/pipeline.toml
  - Validates required [environments] section
  - Returns configuration dictionary

- **`get_environment_directory(environment, config=None)`**
  - Resolves environment name to directory path
  - Returns Path to publish/{env_dir}/
  - Validates directory exists

- **`get_project_root()`**
  - Returns Path to project root directory
  - Used for resolving relative paths

#### Content Discovery

- **`get_content_files(content_dir, log)`**
  - Scans content directory for HTML files
  - Returns sorted list of content keys (filenames without .html)
  - Logs count of files found

#### Navigation Parsing

- **`parse_navigation_structure(index_file, log)`**
  - Parses index.html to extract navigation hierarchy
  - Finds data-content attributes and nav-level classes
  - Returns dict mapping content keys to level and priority
  - Logs count of navigation entries

#### Priority & Frequency

- **`calculate_priority(level, content_key)`**
  - Calculates SEO priority (0.0-1.0) based on nav level
  - Special handling for home page (1.0) and important sections
  - Returns float priority value

- **`determine_changefreq(content_key, level)`**
  - Determines change frequency (weekly, monthly, yearly)
  - Based on content type and expected update patterns
  - Returns frequency string

#### Utilities

- **`get_file_last_modified(content_file)`**
  - Gets last modification date of content file
  - Returns formatted date string (YYYY-MM-DD)
  - Used for `<lastmod>` element in sitemap

## Configuration

### Pipeline Configuration

The module reads `config/pipeline.toml` for environment definitions:

```toml
[environments.dev]
dir = "dev"
port = 8000

[environments.staging]
dir = "staging"
port = 8080

[environments.prod]
dir = "prod"
port = 8888
```

#### How it's used:
- `-e dev` → reads `[environments.dev]` → uses `publish/dev/` directory
- `-e staging` → reads `[environments.staging]` → uses `publish/staging/` directory
- `-e prod` → reads `[environments.prod]` → uses `publish/prod/` directory

### Base URL Configuration

The base URL is hardcoded in `sitemapper.py`:

```python
# Base URL for the site
base_url = 'https://mygaztank.com/'
```

**To change:** Edit line ~448 in `utils/sitemap/sitemapper.py`

### Priority Customization

Priorities are calculated in `calculate_priority()` function:

```python
def calculate_priority(level, content_key):
    if content_key == 'home':
        return 1.0  # Home page always highest
    if level == 1:
        return 0.9  # Top-level pages
    if level == 2:
        return 0.8  # Important sub-pages (schedule, campaigns)
        return 0.7  # Regular sub-pages
    if level == 3:
        return 0.6  # Sub-sub-pages (missions)
    return 0.5  # Default for deep pages
```

**To customize:** Edit `calculate_priority()` in `sitemapper.py`

### Change Frequency Customization

Change frequencies are determined in `determine_changefreq()` function:

```python
def determine_changefreq(content_key, level):
    if content_key == 'home':
        return 'weekly'      # Landing page
    if 'schedule' in content_key:
        return 'weekly'      # Active schedule
    if 'campaign1' in content_key:
        return 'weekly'      # Current campaigns
    if 'campaign2' in content_key:
        return 'monthly'     # Older campaigns
    if 'mods' in content_key:
        return 'monthly'     # Mods section
    if content_key in ['about', 'contact', 'future']:
        return 'yearly'      # Static pages
    return 'monthly'         # Default
```

**To customize:** Edit `determine_changefreq()` in `sitemapper.py`

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                   SITEMAP GENERATION                        │
├─────────────────────────────────────────────────────────────┤
│  [1/4] 📄 Scan Content Files                                │
│     └─ Read all *.html files from publish/{env}/content/    │
│     └─ Extract content keys (filenames without .html)       │
│     └─ Sort alphabetically for consistent ordering          │
│                                                             │
│  [2/4] 🗺️  Parse Navigation Structure                       │
│     └─ Read publish/{env}/index.html                        │
│     └─ Find all data-content="key" attributes               │
│     └─ Detect nav-level-1, nav-level-2, etc. classes        │
│     └─ Build hierarchy map with levels and priorities       │
│                                                             │
│  [3/4] 🔨 Build Sitemap XML                                 │
│     └─ Create <urlset> root element with xmlns              │
│     └─ Sort content: home first, then by priority           │
│     └─ For each content file:                               │
│         ├─ <loc> Base URL + #content-key                    │
│         ├─ <lastmod> File modification timestamp            │
│         ├─ <changefreq> Estimated from content type         │
│         └─ <priority> Calculated from nav hierarchy         │
│     └─ Pretty-print XML with 4-space indentation            │
│                                                             │
│  [4/4] 📝/👁️  Write or Preview Sitemap                      │
│     └─ Normal: Write to publish/{env}/sitemap.xml           │
│     └─ Dry-run: Display preview, don't write file           │
│     └─ Report statistics: URLs written/prepared             │
└─────────────────────────────────────────────────────────────┘
```

## Priority Calculation

Pages are assigned priorities (0.0 to 1.0) based on their position in the navigation hierarchy:

| Page Type | Nav Level | Priority | Example |
|-----------|-----------|----------|---------|
| Home page | Special | 1.0 | `home` |
| Top-level pages | 1 | 0.9 | `about`, `runs`, `mods` |
| Important sub-pages | 2 | 0.8 | `runs_schedule`, `mods_campaign1` |
| Regular sub-pages | 2 | 0.7 | Other level 2 pages |
| Sub-sub-pages | 3 | 0.6 | `mods_campaign1_mission1` |
| Deep pages | 4+ | 0.5 | Mission parts |

### Higher priority = More important to search engines

### Priority Logic

1. **Home page** always gets 1.0 (highest priority)
2. **Top-level navigation** (level 1) gets 0.9
3. **Second level** gets 0.8 for important pages (schedule, campaigns), 0.7 otherwise
4. **Third level** (missions) gets 0.6
5. **Deeper levels** get 0.5 (default)

## Change Frequency

The module estimates how often pages are updated:

| Content Type | Change Frequency | Rationale |
|--------------|------------------|-----------|
| Home page | `weekly` | Landing page, updated frequently |
| Schedule | `weekly` | Active schedule, changes regularly |
| Active campaigns | `weekly` | Current content being updated |
| Older campaigns | `monthly` | Historical content, occasional updates |
| Mods section | `monthly` | Mods updated periodically |
| Static pages | `yearly` | About, Contact, Future - rarely change |
| Missions | `monthly` | Campaign missions, moderate updates |

### This helps search engines optimize crawl frequency

### Frequency Options

XML sitemaps support these frequency values:
- `always` - Changes with every access (not used)
- `hourly` - Changes every hour (not used)
- `daily` - Changes daily (not used)
- `weekly` - Changes weekly (used for active content)
- `monthly` - Changes monthly (used for stable content)
- `yearly` - Changes yearly (used for static pages)
- `never` - Archived content (not used)

## Invocation Points

### Direct Invocation

```bash
# Windows launcher
scripts\generate_sitemap.cmd -e dev

# Linux/Mac launcher
./scripts/generate_sitemap.sh -e dev

# Direct Python module
python -m sitemap -e dev
```

### Programmatic Invocation

```python
# From Python code
from sitemap.sitemapper import generate_sitemap, get_environment_directory, load_pipeline_config
from utils.gzlogging import get_logging_context
from pathlib import Path

# Initialize logging
log = get_logging_context('prod', 'sitemapper', console=True)

# Load configuration and resolve paths
config = load_pipeline_config()
env_dir = get_environment_directory('prod', config)

# Generate sitemap
generate_sitemap(
    base_url='https://mygaztank.com/',
    content_dir=env_dir / 'content',
    index_file=env_dir / 'index.html',
    output_file=env_dir / 'sitemap.xml',
    log=log,
    dry_run=False
)
```

### Build Pipeline Integration

Called by `utils/package/packager.py` during pre-flight checks:

```python
# Inside packager.py pre-flight checks
import subprocess

result = subprocess.run(
    [sys.executable, '-m', 'sitemap', '-e', environment],
    capture_output=True,
    text=True,
    encoding='utf-8'
)

if result.returncode != 0:
    log.err("Sitemap generation failed")
    return False
```

## Development

### Running Tests

```bash
# Test with different environments
python -m sitemap -e dev
python -m sitemap -e staging
python -m sitemap -e prod

# Test dry-run mode
python -m sitemap -e dev --dry-run

# Verify output
cat publish/dev/sitemap.xml       # Linux/Mac
type publish\dev\sitemap.xml      # Windows
```

### Adding New Features

1. **Add new priority rules:**
   - Edit `calculate_priority()` in `sitemapper.py`
   - Add conditions for new content types
   - Update this README's priority table

2. **Add new change frequencies:**
   - Edit `determine_changefreq()` in `sitemapper.py`
   - Add conditions for new update patterns
   - Update this README's frequency table

3. **Support new environments:**
   - Add environment to `config/pipeline.toml`
   - No code changes needed (automatically supported)

4. **Change base URL:**
   - Edit line ~448 in `sitemapper.py`: `base_url = 'https://newsite.com/'`
   - Consider making this configurable in future enhancement

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

### 1. Submit to Search Engines

After generating sitemap.xml, submit it to:

#### Google Search Console:
1. Go to https://search.google.com/search-console
2. Select your property
3. Navigate to Sitemaps
4. Enter: `https://mygaztank.com/sitemap.xml`
5. Click Submit

#### Bing Webmaster Tools:
1. Go to https://www.bing.com/webmasters
2. Select your site
3. Navigate to Sitemaps
4. Enter: `https://mygaztank.com/sitemap.xml`
5. Click Submit

### 2. Reference in robots.txt

Add to `publish/{env}/robots.txt`:

```
Sitemap: https://mygaztank.com/sitemap.xml
```

**Note:** This is already configured in the project templates.

### 3. Update Regularly

Regenerate sitemap when:
- Adding new content pages
- Restructuring navigation hierarchy
- Changing page priorities or frequencies
- Before deploying to production

**Automation:** The packaging pipeline automatically regenerates sitemaps.

### 4. Use Dry-Run for Validation

Before generating for production:

```bash
# Preview what will be generated
python -m sitemap -e prod --dry-run

# Review output and statistics
# If satisfied, generate actual file
python -m sitemap -e prod
```

### 5. Verify in Browser

After generation:
1. Open `publish/{env}/sitemap.xml` in a browser
2. Verify all expected pages are listed
3. Check URLs are correct (base URL + #content-key)
4. Confirm priorities make sense for your SEO strategy
5. Validate change frequencies match update patterns

### 6. Monitor Search Engine Indexing

After submission:
- Check Google Search Console for crawl errors
- Monitor Bing Webmaster Tools for indexing status
- Review search engine logs for sitemap access
- Adjust priorities/frequencies based on analytics

## Troubleshooting

### "Content directory not found"

**Problem:** Cannot find `publish/{env}/content/` directory

#### Solution:
- Ensure you specified correct environment: `-e dev`, `-e staging`, or `-e prod`
- Verify `publish/{env}/` directory exists
- Check that `config/pipeline.toml` has correct `dir` attribute
- Run generation pipeline first to create content: `scripts\generate.cmd`

### "index.html not found"

**Problem:** Cannot find `publish/{env}/index.html`

#### Solution:
- Verify `publish/{env}/index.html` exists
- Ensure navigation structure is present
- Run packaging to copy index.html to environment directory
- Check file permissions

### "No content files found"

**Problem:** No HTML files in content directory

#### Solution:
- Verify content files exist in `publish/{env}/content/`
- Run content generation: `scripts\generate.cmd`
- Check that files have `.html` extension
- Ensure files are not hidden or have permission issues

### "Unknown environment: 'xyz'"

**Problem:** Specified environment not in pipeline.toml

#### Solution:
- Check available environments: `dev`, `staging`, `prod`
- Verify `config/pipeline.toml` has `[environments.xyz]` section
- Use correct environment name with `-e` argument

### "Environment directory not found"

**Problem:** Directory specified in pipeline.toml doesn't exist

#### Solution:
- Check `config/pipeline.toml` for `dir` attribute
- Create directory: `mkdir publish/{env_dir}`
- Run packaging to create full environment structure

### Incorrect Priorities or Frequencies

**Problem:** Pages have unexpected priorities or change frequencies

#### Solution:
1. Check navigation structure in `publish/{env}/index.html`
2. Verify `data-content` attributes match filenames
3. Review `calculate_priority()` logic in `sitemapper.py`
4. Review `determine_changefreq()` logic in `sitemapper.py`
5. Customize functions if your site has different priorities

### Missing Pages in Sitemap

**Problem:** Some pages not included in generated sitemap

#### Solution:
1. Verify files exist in `publish/{env}/content/`
2. Check console output for file count: "Found X content files"
3. Ensure files have `.html` extension
4. Run with dry-run to see what would be included
5. Check log file for warnings: `logs/{env}/sitemapper_YYYYMMDD.log`

### Dry-Run Shows Different Count

**Problem:** Dry-run shows different URL count than expected

#### Solution:
1. Review console output for file listing
2. Check navigation structure parsing results
3. Compare content directory files with navigation links
4. Some files may not be in navigation (expected)
5. Use dry-run to validate before actual generation

## XML Sitemap Specification

The generated sitemap follows the official protocol defined at:
- https://www.sitemaps.org/protocol.html

### Required Elements

- `<urlset>` - Root element with xmlns attribute
- `<url>` - Container for each URL entry
- `<loc>` - URL of the page (required)

### Optional Elements (all used)

- `<lastmod>` - Last modification date (YYYY-MM-DD format)
- `<changefreq>` - Expected change frequency (weekly, monthly, yearly)
- `<priority>` - Relative priority (0.0-1.0 float)

### Output Format

```xml
<?xml version="1.0" ?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://mygaztank.com/#home</loc>
        <lastmod>2025-10-20</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://mygaztank.com/#runs_schedule</loc>
        <lastmod>2025-10-15</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <!-- ... more URLs ... -->
</urlset>
```

### Sitemap Limits

- **Maximum URLs:** 50,000 per sitemap
- **Maximum size:** 50MB uncompressed
- **Format:** UTF-8 encoding
- **Compression:** Can be gzipped (.xml.gz) for submission

**Our site:** ~18 content files, well under limits

### URL Format

The module uses **hash-based navigation** for Single Page Application (SPA) pattern:

```
https://mygaztank.com/#content-key
```

This allows:
- All content served from single domain
- Client-side navigation without page reloads
- Search engines can index individual content sections
- Back/forward browser buttons work correctly

## Future Enhancements

Potential improvements:

- [ ] **Configuration file for priorities and frequencies** - Move hardcoded values to TOML
- [ ] **Make base URL configurable** - Read from pipeline.toml or separate config
- [ ] **Support for multiple base URLs** - Multi-domain/subdomain sites
- [ ] **Image sitemap generation** - Separate sitemap for images
- [ ] **Video sitemap generation** - Separate sitemap for video content
- [ ] **News sitemap** - Time-sensitive news content format
- [ ] **Automatic submission via API** - Submit to Google/Bing programmatically
- [ ] **Sitemap index** - For very large sites with multiple sitemaps
- [ ] **XML schema validation** - Validate against sitemap.org XSD
- [ ] **Incremental updates** - Only regenerate changed pages
- [ ] **Alternative URL patterns** - Support for non-hash URLs
- [ ] **Sitemap styling** - XSLT stylesheet for browser viewing
- [ ] **Multi-language support** - hreflang annotations for i18n
- [x] **Environment support** - Generate for dev/staging/prod (v1.1)
- [x] **Dry-run mode** - Preview without writing files (v1.1)
- [x] **gzlogging integration** - Structured logging (v1.1)

## Related Documentation

### Internal Documentation
- **DESIGN_RULES.md** - GAZTank coding standards and patterns
- **generate module** - Content generation (runs before sitemap)
- **package module** - Calls sitemap during pre-flight checks
- **pipeline.toml** - Environment configuration

### External Resources
- **Sitemap Protocol:** https://www.sitemaps.org/
- **Google Sitemap Guidelines:** https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview
- **Bing Sitemap Guidelines:** https://www.bing.com/webmasters/help/sitemaps-3b5cf6ed
- **Google Search Console:** https://search.google.com/search-console
- **Bing Webmaster Tools:** https://www.bing.com/webmasters

## License

GPL-3.0-or-later

## Authors

superguru, gazorper

---

*Last updated: October 22, 2025*  
*Sitemap Generator version: 1.1*
