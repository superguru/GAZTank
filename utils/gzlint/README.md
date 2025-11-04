# GZLint Module

HTML, JavaScript, and configuration linter for the GAZTank project with automated validation.

**Version:** 0.03  
**Last Updated:** October 22, 2025

## Table of Contents

- [Purpose](#purpose)
- [Build Pipeline](#build-pipeline)
- [Logging](#logging)
- [Usage](#usage)
  - [Command Line (Recommended)](#command-line-recommended)
  - [Direct Module Execution](#direct-module-execution)
  - [As a Module](#as-a-module)
- [Command Line Arguments](#command-line-arguments)
  - [Help](#help)
  - [Exit Codes](#exit-codes)
- [Module Structure](#module-structure)
- [Features](#features)
  - [Validation Rules](#validation-rules)
  - [Severity Levels](#severity-levels)
- [Invocation Points](#invocation-points)
- [Output Examples](#output-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Customization](#customization)
- [Development](#development)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)
- [Authors](#authors)

## Purpose

This module scans HTML, JavaScript, and configuration files for common issues and best practice violations:

1. **HTML validation** - Detects malformed tags, unclosed elements
2. **Heading structure** - Ensures proper `<h1>` usage and hierarchy
3. **JavaScript quality** - Finds `console.log()` statements
4. **Configuration validation** - Validates `generate.toml` and `tools.toml` structure and consistency
5. **SEO compliance** - Validates heading structure for search engines
6. **Audit logging** - Logs all validation activities to `logs/dev/gzlint_YYYYMMDD.log`

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      GZLINT WORKFLOW                        │
├─────────────────────────────────────────────────────────────┤
│  [1/4] Initialize Logging                                   │
│     └─ Set up gzlogging with 'dev' environment              │
│     └─ Log to logs/dev/gzlint_YYYYMMDD.log                  │
│     └─ Enable dual output (console + file)                  │
│                                                             │
│  [2/4] Scan Files                                           │
│     └─ Recursively find *.html and *.js in src/             │
│     └─ Find config files: generate.toml, tools.toml         │
│     └─ Include all subdirectories                           │
│                                                             │
│  [3/4] Validate Each File                                   │
│     Config Files:                                           │
│     ├─ Validate generate.toml structure                     │
│     ├─ Validate tools.toml structure                        │
│     └─ Check consistency with pipeline.toml                 │
│                                                             │
│     HTML Files:                                             │
│     ├─ Parse HTML structure (check malformed tags)          │
│     ├─ Extract heading hierarchy (h1-h6)                    │
│     ├─ Count <h1> tags (should be exactly 1)                │
│     └─ Verify <h1> appears before other headings            │
│                                                             │
│     JavaScript Files:                                       │
│     ├─ Scan for console.log() statements                    │
│     └─ Ignore commented lines                               │
│                                                             │
│  [4/4] Generate Report                                      │
│     └─ Write gzlint-issues.txt with all findings            │
│     └─ Group by severity (errors, warnings, info)           │
│     └─ Include line numbers and suggestions                 │
│     └─ Log final status to log file                         │
└─────────────────────────────────────────────────────────────┘
```

### Architecture

```
GZLinter (Main)
├── ConfigLinter - Validates configuration files
│   ├── lint_generate_config() - Validates generate.toml structure
│   ├── lint_tools_config() - Validates tools.toml structure
│   └── lint_config_consistency() - Cross-checks pipeline.toml/tools.toml
├── HTMLValidator - Validates HTML structure (malformed/unclosed tags)
├── HTMLLinter - Checks HTML files
│   └── HeadingParser - Extracts heading hierarchy
└── JSLinter - Checks JavaScript files

Logging: gzlogging (logs/dev/gzlint_YYYYMMDD.log)
```

## Build Pipeline

GZLint runs as the first pre-flight check in the packaging pipeline:

```
Package Pre-flight:
  1. Run validation (gzlint)  ← This module
     ↓
     ✓ No errors → Continue
     ✗ Errors found → Abort packaging
     ↓
  2. Convert markdown to HTML
  3. Generate sitemap
  4. Continue with packaging...
```

### Benefits:
- Prevents deploying code with errors
- Enforces quality standards automatically
- Catches issues before production
- No manual linting step required

### Exit Codes:

| Exit Code | Meaning | Description |
|-----------|---------|-------------|
| `0` | Success | No errors found (warnings are OK) |
| `1` | Failure | Errors found - must fix before production |

### Usage in Scripts:

```bash
# Windows (CMD)
.\scripts\gzlint.cmd
if %errorlevel% neq 0 exit /b 1

# Linux/Mac (Bash)
./scripts/gzlint.sh
if [ $? -ne 0 ]; then exit 1; fi

# Python
import subprocess
result = subprocess.run(['python', '-m', 'gzlint'])
if result.returncode != 0:
    sys.exit(1)
```

## Logging

```
┌─────────────────────────────────────────────────────────────┐
│                      GZLINT WORKFLOW                        │
├─────────────────────────────────────────────────────────────┤
│  [1/4] Initialize Logging                                   │
│     └─ Set up gzlogging with 'dev' environment              │
│     └─ Log to logs/dev/gzlint_YYYYMMDD.log                  │
│     └─ Enable dual output (console + file)                  │
│                                                             │
│  [2/4] Scan Files                                           │
│     └─ Recursively find *.html and *.js in src/             │
│     └─ Find config files: generate.toml, tools.toml         │
│     └─ Include all subdirectories                           │
│                                                             │
│  [3/4] Validate Each File                                   │
│     Config Files:                                           │
│     ├─ Validate generate.toml structure                     │
│     ├─ Validate tools.toml structure                        │
│     └─ Check consistency with pipeline.toml                 │
│                                                             │
│     HTML Files:                                             │
│     ├─ Parse HTML structure (check malformed tags)          │
│     ├─ Extract heading hierarchy (h1-h6)                    │
│     ├─ Count <h1> tags (should be exactly 1)                │
│     └─ Verify <h1> appears before other headings            │
│                                                             │
│     JavaScript Files:                                       │
│     ├─ Scan for console.log() statements                    │
│     └─ Ignore commented lines                               │
│                                                             │
│  [4/4] Generate Report                                      │
│     └─ Write gzlint-issues.txt with all findings            │
│     └─ Group by severity (errors, warnings, info)           │
│     └─ Include line numbers and suggestions                 │
│     └─ Log final status to log file                         │
└─────────────────────────────────────────────────────────────┘
## Logging

GZLint uses the **gzlogging** infrastructure for comprehensive audit logging.

### HTML Rules

#### HTML_INVALID

**Severity:** ❌ Error

**Description:** Malformed HTML (mismatched/unclosed tags)

**Why This Matters:**
- Breaks page rendering
- Creates accessibility issues
- Prevents accurate content parsing
- Other checks cannot run until HTML is valid

**Example (Bad):**
```html
<h1>Title
<h2>Subtitle</h1>  <!-- ❌ Mismatched closing tag -->
<p>Text...         <!-- ❌ Unclosed tag -->
```

**Example (Good):**
```html
<h1>Title</h1>
<h2>Subtitle</h2>
<p>Text...</p>
```

**Suggestion:** Fix the malformed HTML tags before other checks can run.

---

#### H1_MISSING

**Severity:** ⚠️ Warning

**Description:** No `<h1>` tag found. Pages should have exactly one `<h1>` for SEO.

**Why This Matters:**
- Search engines use `<h1>` to understand page content
- Screen readers rely on proper heading hierarchy
- Users expect a clear page title
- Impacts SEO rankings

**Example (Bad):**
```html
<h2>Welcome to My Page</h2>
<p>This page has no h1 tag...</p>
```

**Example (Good):**
```html
<h1>Welcome to My Page</h1>
<h2>Introduction</h2>
<p>This page has proper heading structure...</p>
```

**Suggestion:** Add an `<h1>` tag as the main heading for this page.

---

#### H1_MULTIPLE

**Severity:** ❌ Error

**Description:** Found multiple `<h1>` tags. Pages should have exactly one `<h1>`.

**Why This Matters:**
- Multiple `<h1>` tags confuse search engines
- Dilutes SEO value across multiple headings
- Creates accessibility issues for screen reader users
- Violates HTML5 document outline best practices

**Example (Bad):**
```html
<h1>Main Title</h1>
<p>Some content...</p>
<h1>Another Main Title</h1>  <!-- ❌ Second h1 -->
<p>More content...</p>
```

**Example (Good):**
```html
<h1>Main Title</h1>
<p>Some content...</p>
<h2>Another Section</h2>  <!-- ✅ Use h2 instead -->
<p>More content...</p>
```

**Suggestion:** Keep only one `<h1>` tag and change others to `<h2>` or appropriate levels.

---

#### H1_ORDER

**Severity:** ❌ Error

**Description:** `<h1>` should appear before other heading tags.

**Why This Matters:**
- Logical heading order is crucial for SEO
- Screen readers expect headings in hierarchical order
- Users scan pages top-to-bottom expecting proper structure
- Search engines may misinterpret page hierarchy

**Example (Bad):**
```html
<h2>Introduction</h2>  <!-- ❌ h2 before h1 -->
<p>Welcome to our site...</p>
<h1>Main Page Title</h1>
<h3>Details</h3>
```

**Example (Good):**
```html
<h1>Main Page Title</h1>  <!-- ✅ h1 first -->
<h2>Introduction</h2>
<p>Welcome to our site...</p>
<h3>Details</h3>
```

**Suggestion:** Move the `<h1>` tag before all other heading tags.

---

### JavaScript Rules

#### CONSOLE_LOG

**Severity:** ❌ Error

**Description:** Found `console.log()` statement. Remove before production.

**Why This Matters:**
- Clutters browser console in production
- May expose sensitive information or implementation details
- Can cause performance issues with excessive logging
- Indicates code is not production-ready
- Professional sites should not have debug output

**Example (Bad):**
```javascript
function loadContent(key) {
    console.log("Loading content:", key);  // ❌ Remove this
    fetch(`content/${key}.html`)
        .then(response => response.text())
        .then(html => {
            console.log("Content loaded:", html);  // ❌ Remove this
            displayContent(html);
        });
}
```

**Example (Good):**
```javascript
function loadContent(key) {
    // Clean production code - no console.log
    fetch(`content/${key}.html`)
        .then(response => response.text())
        .then(html => {
            displayContent(html);
        });
}
```

**Alternative (If logging needed):**
```javascript
function loadContent(key) {
    fetch(`content/${key}.html`)
        .then(response => response.text())
        .then(html => displayContent(html))
        .catch(error => {
            console.error("Failed to load content:", error);  // ✅ OK for errors
        });
}
```

**Suggestion:** Remove the `console.log()` statement. For intentional production logging (errors, warnings), use `console.error()` or `console.warn()` instead.

**Note:** The linter skips `console.log()` in line comments (`//`).

---

### Configuration Rules

#### INPUT_TYPE_MISSING

**Severity:** ❌ Error

**Description:** Config group missing required `input_type` attribute in `generate.toml`.

**Why This Matters:**
- The generate system needs to know what converter to use
- Missing input_type prevents content generation
- Each group must specify its input format (e.g., "markdown")

**Example (Bad):**
```toml
[[group]]
name = "documentation"
output_dir = "src/content/setup"
files = ["docs/*.md"]
# ❌ Missing input_type attribute
```

**Example (Good):**
```toml
[[group]]
name = "documentation"
input_type = "markdown"  # ✅ Required
output_dir = "src/content/setup"
files = ["docs/*.md"]
```

**Suggestion:** Add `input_type = "markdown"` (or other supported type) to the config group.

---

#### OUTPUT_DIR_MISSING

**Severity:** ❌ Error

**Description:** Config group missing required `output_dir` attribute in `generate.toml`.

**Why This Matters:**
- The generate system needs to know where to write output files
- Missing output_dir prevents content generation
- Build process will fail without output location

**Example (Bad):**
```toml
[[group]]
name = "content"
input_type = "markdown"
files = ["content/*.md"]
# ❌ Missing output_dir attribute
```

**Example (Good):**
```toml
[[group]]
name = "content"
input_type = "markdown"
output_dir = "src/content"  # ✅ Required
files = ["content/*.md"]
```

**Suggestion:** Add `output_dir = "path/to/output"` to the config group.

---

#### FILES_MISSING

**Severity:** ❌ Error

**Description:** Config group missing required `files` attribute in `generate.toml`.

**Why This Matters:**
- The generate system needs to know which files to process
- Missing files list prevents any content generation
- Build process cannot proceed without file list

**Example (Bad):**
```toml
[[group]]
name = "content"
input_type = "markdown"
output_dir = "src/content"
# ❌ Missing files attribute
```

**Example (Good):**
```toml
[[group]]
name = "content"
input_type = "markdown"
output_dir = "src/content"
files = ["content/*.md"]  # ✅ Required
```

**Suggestion:** Add `files = ["glob/pattern/*.md"]` to the config group.

---

#### EMPTY_FILES_LIST

**Severity:** ⚠️ Warning

**Description:** Config group has empty `files` list in `generate.toml`.

**Why This Matters:**
- Empty files list means nothing will be processed
- Likely indicates incomplete configuration
- May be intentional (placeholder) but should be reviewed

**Example (Bad):**
```toml
[[group]]
name = "future_content"
input_type = "markdown"
output_dir = "src/content"
files = []  # ⚠️ Empty list
```

**Example (Good):**
```toml
[[group]]
name = "content"
input_type = "markdown"
output_dir = "src/content"
files = ["content/*.md"]  # ✅ Has files
```

**Suggestion:** Add file patterns to the `files` list or remove the empty group.

---

#### LOG_DIR_MISSING

**Severity:** ❌ Error

**Description:** Environment in `tools.toml` missing required `log_dir` attribute.

**Why This Matters:**
- All tools need a log directory for audit trails
- Missing log_dir prevents logging initialization
- Build and deployment tools will fail without logging

**Example (Bad):**
```toml
[dev]
# ❌ Missing log_dir attribute
description = "Development environment"
```

**Example (Good):**
```toml
[dev]
log_dir = "logs/dev"  # ✅ Required
description = "Development environment"
```

**Suggestion:** Add `log_dir = "logs/{env}"` to the environment configuration.

---

#### CONFIG_MISMATCH

**Severity:** ❌ Error

**Description:** Environment exists in `pipeline.toml` but not in `tools.toml` (or vice versa).

**Why This Matters:**
- All environments must be defined in both config files for consistency
- Missing environment definitions cause runtime errors
- Build pipeline cannot function with inconsistent configs

**Example (Bad):**
```toml
# pipeline.toml
[prod]  # Defined here
# ...

# tools.toml
[dev]   # ❌ 'prod' not defined in tools.toml
```

**Example (Good):**
```toml
# pipeline.toml
[prod]
# ...

# tools.toml
[prod]  # ✅ Matches pipeline.toml
log_dir = "logs/prod"
```

**Suggestion:** Ensure all environments in `pipeline.toml` are also defined in `tools.toml` with required attributes.

---

### Severity Levels

#### ❌ Error

**Impact:** High - Must be fixed before production

Errors indicate serious issues that:
- Break SEO best practices
- Violate web standards
- Create accessibility problems
- Leave debug code in production

**Build Impact:** Causes build/package script to fail (exit code 1)

### ⚠️ Warning

**Impact:** Medium - Should be fixed but not critical

Warnings indicate issues that:
- May impact SEO performance
- Could affect user experience
- Suggest improvements to code quality
- Are best practices violations

**Build Impact:** Build succeeds but issues are reported (exit code 0)

#### ℹ️ Info

**Impact:** Low - Informational only

Info messages provide:
- Best practice suggestions
- Optional improvements
- Code style recommendations

**Build Impact:** Build succeeds (exit code 0)

## Logging

GZLint uses the **gzlogging** infrastructure for comprehensive audit logging.

### Log Configuration

- **Environment:** `dev` (hardcoded, no parameter needed)
- **Log Location:** `logs/dev/gzlint_YYYYMMDD.log`
- **Output Mode:** Dual output (both console and log file)
- **Encoding:** UTF-8 with emoji support (❌ ⚠️ ℹ️ ✅)

### What Gets Logged

**Logged to file:**
- Startup banner and initialization
- Each file being validated (per-file actions)
- All errors, warnings, and info messages found during validation
- Final status (pass/fail with counts)

**Console-only (NOT logged):**
- Detailed summary reports
- File count statistics
- Formatted issue tables
- Progress indicators

This design ensures the log file provides a clean audit trail of what was checked and what issues were found, while keeping the console output readable with detailed formatting and summaries.

### Log File Example

```log
[2025-10-22 16:52:25] [dev] [INF] GZLint - HTML, JavaScript & Config Linter started
[2025-10-22 16:52:25] [dev] [INF] Linting config file: config\generate.toml
[2025-10-22 16:52:25] [dev] [INF] Linting HTML file: src\content\about.html
[2025-10-22 16:52:25] [dev] [INF] Linting HTML file: src\content\contact.html
[2025-10-22 16:52:25] [dev] [INF] Linting JavaScript file: src\js\app.js
[2025-10-22 16:52:25] [dev] [ERR] Multiple <h1> tags in src\content\about.html on lines: 12, 45
[2025-10-22 16:52:25] [dev] [WRN] console.log found in src\js\app.js line 87
[2025-10-22 16:52:25] [dev] [INF] Linting completed with 1 error(s) and 1 warning(s)
```

**Note:** Log files contain only timestamped operational messages. No separator lines (===), no blank lines, no visual formatting. This provides a clean audit trail.

### Viewing Logs

```bash
# View today's log
cat logs/dev/gzlint_$(date +%Y%m%d).log       # Linux/Mac
type logs\dev\gzlint_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log  # Windows

# View most recent log
ls -t logs/dev/gzlint_*.log | head -1 | xargs cat  # Linux/Mac
Get-ChildItem logs\dev\gzlint_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content  # PowerShell
```

### Log Retention

Logs are date-stamped and accumulate over time. Consider setting up log rotation:
- Keep logs for development troubleshooting
- Archive or delete old logs periodically
- Typical retention: 30-90 days for development logs

## Usage

### Command Line (Recommended)

```bash
# Windows
.\scripts\gzlint.cmd
.\scripts\gzlint.cmd --help

# Linux/Mac
./scripts/gzlint.sh
./scripts/gzlint.sh --help
```

### Direct Module Execution

```bash
# From project root
python -m gzlint
python -m gzlint --help

# With explicit PYTHONPATH
set PYTHONPATH=%CD%\utils;%PYTHONPATH%      # Windows
export PYTHONPATH="$PWD/utils:$PYTHONPATH"  # Linux/Mac
python -m gzlint
```

## Command Line Arguments

### Help

```bash
.\scripts\gzlint.cmd --help
```

**Output:**
```
usage: python.exe -m gzlint [-h]

GZLint - HTML, JavaScript & Config Linter

options:
  -h, --help            show this help message and exit

Examples:
  python -m gzlint              # Lint all files in src/
  python -m gzlint --help       # Show this help message

Exit codes:
  0 - No errors found (warnings are OK)
  1 - Errors found that must be fixed
```

### Exit Codes

| Exit Code | Meaning | Description |
|-----------|---------|-------------|
| `0` | Success | No errors found (warnings are OK) |
| `1` | Failure | Errors found - must fix before production |

**Console Output Example:**

```
[2025-10-22 16:57:43] [dev] [INF] GZLint - HTML, JavaScript & Config Linter started
============================================================
GZLINT - HTML, JAVASCRIPT & CONFIG LINTER
============================================================
Scanning: D:\Projects\www\GAZTank\src

Checking configuration files...
  config\generate.toml
[2025-10-22 16:57:43] [dev] [INF] Linting config file: config\generate.toml
  
Found 18 HTML file(s) (including subdirectories)
Found 1 JavaScript file(s) (including subdirectories)

...

✅ ALL CHECKS PASSED!

============================================================
✅ LINTING PASSED - No issues
============================================================
[2025-10-22 16:57:43] [dev] [INF] Linting passed - no issues found
```

```bash
# From project root
python -m gzlint

# With explicit PYTHONPATH
set PYTHONPATH=%CD%\utils;%PYTHONPATH%      # Windows
export PYTHONPATH="$PWD/utils:$PYTHONPATH"  # Linux/Mac
python -m gzlint
```

### As a Module

Import and use linting functions in your own Python scripts:

```python
from gzlint import GZLinter
from pathlib import Path

# Create linter instance
src_dir = Path('src')
output_file = 'gzlint-issues.txt'
linter = GZLinter(src_dir, output_file)

# Run scan
linter.scan()

# Check for issues
all_issues = linter.html_linter.issues + linter.js_linter.issues
if all_issues:
    print(f"Found {len(all_issues)} issues")
```

For individual file linting:

```python
from gzlint import HTMLLinter, JSLinter
from pathlib import Path

# Lint HTML file
html_linter = HTMLLinter()
html_linter.lint_file(Path('src/index.html'))
for issue in html_linter.issues:
    print(issue)

# Lint JavaScript file
js_linter = JSLinter()
js_linter.lint_file(Path('src/js/app.js'))
for issue in js_linter.issues:
    print(issue)
```

## Output Examples

### Console Output

```
[2025-10-22 16:57:43] [dev] [INF] GZLint - HTML, JavaScript & Config Linter started
============================================================
GZLINT - HTML, JAVASCRIPT & CONFIG LINTER
============================================================
Scanning: D:\Projects\www\GAZTank\src

Checking configuration files...
  config\generate.toml
[2025-10-22 16:57:43] [dev] [INF] Linting config file: config\generate.toml
  config\tools.toml

Found 18 HTML file(s) (including subdirectories)
Found 1 JavaScript file(s) (including subdirectories)

Checking HTML files (including subdirectories)...
  src\content\about.html
[2025-10-22 16:57:43] [dev] [INF] Linting HTML file: src\content\about.html
  src\content\contact.html
[2025-10-22 16:57:43] [dev] [INF] Linting HTML file: src\content\contact.html
  ...

Checking JavaScript files (including subdirectories)...
  src\js\app.js
[2025-10-22 16:57:43] [dev] [INF] Linting JavaScript file: src\js\app.js

============================================================
GENERATING REPORT
============================================================
✅ Report written to: gzlint-issues.txt

SUMMARY
  Files scanned: 21
  Files with issues: 0
  ❌ Errors: 0
  ⚠️  Warnings: 0
  ℹ️  Info: 0

✅ ALL CHECKS PASSED!

============================================================
✅ LINTING PASSED - No issues
============================================================
[2025-10-22 16:57:43] [dev] [INF] Linting passed - no issues found
```

**Note:** Lines starting with timestamps like `[2025-10-22 16:57:43] [dev] [INF]` appear in both console and log file. Lines without timestamps (like "Scanning:", "SUMMARY", separator lines etc.) appear only in console output. Log files contain clean operational data without visual formatting.

### Report File (`gzlint-issues.txt`)

```
================================================================================
GZLINT REPORT - GAZ TANK HTML LINTER
================================================================================
Generated: 2025-10-20 22:15:30
Scanned: 7 file(s)
Files with issues: 2

SUMMARY
--------------------------------------------------------------------------------
  ❌ Errors:   2
  ⚠️  Warnings: 1
  ℹ️  Info:     0

================================================================================
ERRORS
================================================================================

❌ [H1_MULTIPLE] src\content\about.html (line 12)
   Found 2 <h1> tags (lines: 12, 45). Pages should have exactly one <h1>.
   💡 Suggestion: Keep only one <h1> tag and change others to <h2> or appropriate levels.

❌ [CONSOLE_LOG] src\js\app.js (line 87)
   console.log() statement found. Remove console.log() before production.
   💡 Suggestion: Remove this console.log() or use console.error()/console.warn() for intentional logging.

================================================================================
WARNINGS
================================================================================

⚠️ [H1_MISSING] src\content\future.html
   No <h1> tag found. Pages should have exactly one <h1> for SEO.
   💡 Suggestion: Add an <h1> tag as the main heading for this page.

================================================================================
RULES CHECKED
================================================================================

HTML Rules:
  HTML_INVALID    - Malformed HTML (mismatched/unclosed tags)
  H1_MISSING      - Pages should have exactly one <h1> tag
  H1_MULTIPLE     - Pages should not have multiple <h1> tags
  H1_ORDER        - <h1> should appear before other heading tags

JavaScript Rules:
  CONSOLE_LOG     - No console.log() statements in production code

================================================================================
END OF REPORT
================================================================================
```

### Reading Issue Entries

Each issue shows:

```
[Severity Icon] [RULE_CODE] file/path (line X)
   Issue description
   💡 Suggestion: How to fix it
```

**Example:**
```
❌ [H1_ORDER] src/content/mods.html (line 5)
   <h2> appears before <h1> (line 5). The <h1> should be the first heading.
   💡 Suggestion: Move the <h1> tag before this <h2> tag.
```

## Module Structure

```
gzlint/
├── __init__.py        # Module initialization and exports
├── __main__.py        # Entry point for python -m gzlint
├── gzlinter.py        # Core linting logic (parsers, validators, reporters)
└── README.md          # This file (comprehensive documentation)
```

### Architecture

```
GZLinter (Main)
├── ConfigLinter - Validates configuration files
│   ├── lint_generate_config() - Validates generate.toml structure
│   ├── lint_tools_config() - Validates tools.toml structure
│   └── lint_config_consistency() - Cross-checks pipeline.toml/tools.toml
├── HTMLValidator - Validates HTML structure (malformed/unclosed tags)
├── HTMLLinter - Checks HTML files
│   └── HeadingParser - Extracts heading hierarchy
└── JSLinter - Checks JavaScript files

Logging: gzlogging (logs/dev/gzlint_YYYYMMDD.log)
```

### Key Classes

**High-Level:**

- **`GZLinter`**
  - Main linter class that orchestrates scanning
  - Manages HTML, JavaScript, and configuration linters
  - Generates reports
  - Initializes logging

**Configuration Validation:**

- **`ConfigLinter`**
  - Validates configuration file structure and consistency
  - `lint_generate_config()` - Checks generate.toml structure
  - `lint_tools_config()` - Checks tools.toml structure
  - `lint_config_consistency()` - Verifies pipeline.toml and tools.toml match

**HTML Validation:**

- **`HTMLLinter`**
  - Lints individual HTML files
  - Runs all HTML validation rules
  - Collects issues

- **`HTMLValidator`**
  - HTML parser for structure validation
  - Detects malformed and unclosed tags
  - Tracks line numbers

- **`HeadingParser`**
  - Extracts heading tags and content
  - Tracks heading hierarchy
  - Used for SEO validation

**JavaScript Validation:**

- **`JSLinter`**
  - Lints individual JavaScript files
  - Checks for console.log() statements
  - Handles comment detection

**Issue Reporting:**

- **`LintIssue`**
  - Represents a single linting issue
  - Contains severity, rule, message, line number
  - Provides formatted output

**Logging:**

- **`gzlogging`**
  - Centralized logging infrastructure (utils/gzlogging/)
  - `get_logging_context(env, tool, console)` - Initializes logging
  - Returns LoggingContext with `.inf()`, `.wrn()`, `.err()` methods
  - Logs to `logs/{env}/{tool}_YYYYMMDD.log`

## Features

- **Multi-file type validation**: HTML, JavaScript, and TOML configuration files
- **Comprehensive HTML checks**: Structure validation, heading hierarchy, SEO compliance
- **JavaScript quality checks**: Detects console.log() statements and other issues
- **Configuration validation**: Ensures config files are properly structured and consistent
- **Detailed error reporting**: Line numbers, descriptions, and suggestions for each issue
- **Severity levels**: Errors (block deployment), warnings (should fix), info (FYI)
- **Integrated logging**: Uses gzlogging for audit trails with dual output (console + file)
- **UTF-8 support**: Handles Unicode and emoji characters correctly
- **Cross-platform**: Works on Windows, Linux, and Mac
- **CI/CD integration**: Exit codes for automated build pipelines
- **Report generation**: Creates detailed `gzlint-issues.txt` report file

### Validation Rules

### High-Level

- **`GZLinter`**
  - Main linter class that orchestrates scanning
  - Manages HTML, JavaScript, and configuration linters
  - Generates reports
  - Initializes logging

### Configuration Validation

- **`ConfigLinter`**
  - Validates configuration file structure and consistency
  - `lint_generate_config()` - Checks generate.toml structure
  - `lint_tools_config()` - Checks tools.toml structure
  - `lint_config_consistency()` - Verifies pipeline.toml and tools.toml match

### HTML Validation

- **`HTMLLinter`**
  - Lints individual HTML files
  - Runs all HTML validation rules
  - Collects issues

- **`HTMLValidator`**
  - HTML parser for structure validation
  - Detects malformed and unclosed tags
  - Tracks line numbers

- **`HeadingParser`**
  - Extracts heading tags and content
  - Tracks heading hierarchy
  - Used for SEO validation

### JavaScript Validation

- **`JSLinter`**
  - Lints individual JavaScript files
  - Checks for console.log() statements
  - Handles comment detection

### Issue Reporting

- **`LintIssue`**
  - Represents a single linting issue
  - Contains severity, rule, message, line number
  - Provides formatted output

### Logging

- **`gzlogging`**
  - Centralized logging infrastructure (utils/gzlogging/)
  - `get_logging_context(env, tool, console)` - Initializes logging
  - Returns LoggingContext with `.inf()`, `.wrn()`, `.err()` methods
  - Logs to `logs/{env}/{tool}_YYYYMMDD.log`

## Invocation Points

### Called By

- `scripts/gzlint.cmd` - Windows launcher
- `scripts/gzlint.sh` - Linux/Mac launcher
- `utils/package/packager.py` - Pre-flight validation in build pipeline

### Integration with Build Pipeline

See [Build Pipeline](#build-pipeline) section for details on how gzlint integrates into the packaging workflow.

## Development

### File Locations

```
GAZTank/
├── gzlint-issues.txt           # Generated report (in project root)
│
├── logs/
│   └── dev/
│       └── gzlint_YYYYMMDD.log # Daily log files (audit trail)
│
├── config/
│   ├── generate.toml           # Validated by ConfigLinter
│   ├── tools.toml              # Validated by ConfigLinter
│   └── pipeline.toml           # Cross-checked with tools.toml
│
├── src/                        # Files scanned by linter
│   ├── index.html
│   ├── content/
│   │   ├── about.html
│   │   └── ...
│   └── js/
│       └── app.js
│
├── scripts/
│   ├── gzlint.cmd              # Windows launcher
│   └── gzlint.sh               # Linux/Mac launcher
│
└── utils/
    ├── gzlogging/              # Centralized logging system
    │   └── gzlogging.py        # Used by gzlint
    │
    └── gzlint/                 # This module
        ├── __init__.py
        ├── __main__.py
        ├── gzlinter.py
        └── README.md
```

## Customization

### Add New HTML Rules

Edit `utils/gzlint/gzlinter.py` in the `HTMLLinter` class:

```python
def lint_file(self, file_path, report_path=None):
    # ... existing code ...
    
    # Add your new check
    self.check_your_new_rule(report_path, parser.headings)

def check_your_new_rule(self, file_path, headings):
    """Your custom validation logic"""
    if condition_fails:
        self.issues.append(LintIssue(
            file_path,
            LintIssue.SEVERITY_ERROR,
            'YOUR_RULE_NAME',
            "Description of the issue",
            line=line_number,
            suggestion="How to fix it"
        ))
```

### Add New JavaScript Rules

Edit `utils/gzlint/gzlinter.py` in the `JSLinter` class:

```python
def lint_file(self, file_path, report_path=None):
    # ... existing code ...
    
    # Add your new check
    self.check_your_new_rule(report_path, lines)

def check_your_new_rule(self, file_path, lines):
    """Your custom JavaScript validation"""
    for i, line in enumerate(lines, start=1):
        if your_condition:
            self.issues.append(LintIssue(
                file_path,
                LintIssue.SEVERITY_WARNING,
                'YOUR_JS_RULE',
                "What's wrong",
                line=i,
                suggestion="How to fix it"
            ))
```

### Change Severity Levels

Modify the severity in rule checks:

```python
# Error (blocks deployment)
LintIssue.SEVERITY_ERROR    # '❌'

# Warning (allowed, but flagged)
LintIssue.SEVERITY_WARNING  # '⚠️'

# Info (FYI only)
LintIssue.SEVERITY_INFO     # 'ℹ️'
```

## Troubleshooting

### "No HTML or JavaScript files found"

**Problem:** Linter can't find files to scan

**Solution:**
1. Verify `src/` directory exists
2. Check that files have `.html` or `.js` extensions
3. Ensure you're running from project root

### "Failed to parse file"

**Problem:** File encoding or structure issues

**Solution:**
1. Ensure files are UTF-8 encoded
2. Check for binary files incorrectly named `.html/.js`
3. Verify file permissions

### False positives for `console.log()`

**Problem:** Commented console.log() flagged as error

**Solution:**
- The linter ignores lines starting with `//`
- Block comments `/* ... */` may not be detected correctly
- Consider removing console.log() entirely in production code

### Report not generated

**Problem:** `gzlint-issues.txt` not created

**Solution:**
1. Check write permissions in project root
2. Ensure disk space available
3. Check console for error messages

### Log files not created

**Problem:** No log files appearing in `logs/dev/`

**Solution:**
1. Verify `logs/dev/` directory exists (should be auto-created)
2. Check write permissions for logs directory
3. Ensure `utils/gzlogging/gzlogging.py` is present
4. Check console for logging initialization errors

### Unicode/Emoji not displaying

**Problem:** Emojis show as `?` or garbled characters

**Solution:**
1. Set encoding before running: `$env:PYTHONIOENCODING = 'utf-8'` (PowerShell)
2. Use modern terminal (Windows Terminal, VS Code terminal)
3. Check that log files are UTF-8 encoded

### Config validation errors

**Problem:** False positives for config file validation

**Solution:**
1. Verify TOML syntax is correct (no unquoted strings, proper arrays)
2. Check that all required attributes are present (input_type, output_dir, files, log_dir)
3. Ensure environment names match between pipeline.toml and tools.toml
4. Review detailed error messages in log file

## Performance

**Typical Scan Times:**

| Files | Time |
|-------|------|
| < 10 | < 1 second |
| 10-50 | 1-2 seconds |
| 50-100 | 2-5 seconds |

**Current project:** ~13 files, scans in < 1 second

## Best Practices

### 1. Run Before Every Commit

```bash
# Add to pre-commit hook
.\scripts\gzlint.cmd
if %errorlevel% neq 0 exit /b 1
```

### 2. Fix Errors Immediately

- ❌ Errors block deployment
- Fix before continuing development

### 3. Address Warnings

- ⚠️ Warnings don't block, but should be fixed
- Improve SEO and code quality

### 4. Review Report File

```bash
# Check detailed report
cat gzlint-issues.txt       # Linux/Mac
type gzlint-issues.txt      # Windows
```

### 5. Keep Rules Up to Date

- Review validation rules periodically
- Add rules for new best practices
- Update severity as needed

## Future Enhancements

Potential improvements:

### Build Pipeline
We currently lint the source code, but maybe in future we should also add the ability to lint a specified environment? Still considering if this would be useful or not.

### HTML
- [ ] `IMG_ALT_MISSING` - Images should have alt text
- [ ] `HEADING_SKIP` - Heading levels should not skip (e.g., h2 → h4)
- [ ] `EMPTY_HEADING` - Headings should have content
- [ ] `DUPLICATE_ID` - IDs should be unique within a page

### JavaScript
- [ ] `VAR_USAGE` - Use `const`/`let` instead of `var`
- [ ] `CONSOLE_ERROR` - Check for other console methods
- [ ] `EVAL_USAGE` - Avoid using `eval()`
- [ ] `ALERT_USAGE` - Remove `alert()` statements

### Infrastructure
- [ ] CSS validation (syntax, best practices)
- [ ] Accessibility checks (ARIA, alt text)
- [ ] Link validation (broken links)
- [ ] Image optimization checks
- [ ] Performance hints (inline scripts, large files)
- [ ] Configuration file support (`config/gzlint.toml`)
- [ ] Plugin system for custom rules
- [ ] HTML5 semantic tag validation
- [ ] JSON/TOML report output formats
- [ ] VS Code extension integration
- [ ] Incremental scanning (only changed files)
- [ ] Parallel file processing

## Related Documentation

- **HTML Validation:** https://validator.w3.org/
- **SEO Best Practices:** https://developers.google.com/search/docs
- **Python HTMLParser:** https://docs.python.org/3/library/html.parser.html
- **WCAG Accessibility:** https://www.w3.org/WAI/WCAG21/quickref/

## License

GPL-3.0-or-later

## Authors

superguru, gazorper

---

*Last updated: October 22, 2025*  
*GZLint version: 0.03*
