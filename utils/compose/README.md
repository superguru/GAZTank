# HTML Composition Module

Assembles HTML files from source components based on configuration. Enables conditional inclusion of HTML sections based on feature flags.

**Version:** 1.0  
**Last Updated:** November 4, 2025

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
- [Component Types](#component-types)
- [Invocation Points](#invocation-points)
- [Development](#development)
- [Customisation](#customisation)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)
- [Authors](#authors)

## Purpose

The Composition Module assembles HTML files from source components, enabling:

1. **Conditional HTML Sections** - Include/exclude components based on feature flags
2. **Markdown Navigation** - Define navigation in markdown, transform to HTML
3. **Component Reusability** - Separate reusable components from base templates
4. **Build-Time Assembly** - Compose HTML before configuration and deployment
5. **Clear Separation** - Source components tracked in git, output ignored

### Key Capabilities

- Reads composition definitions from `config/compose.toml`
- Processes `<!-- COMPOSE:KEY:config_flag -->` markers in base HTML
- Transforms markdown components to proper HTML structures
- Conditionally includes/excludes based on `site.toml` feature flags
- Adds CSS classes when components disabled (e.g., `no-sidebar`)
- Supports multiple compositions in configurable execution order

### Design Goals

- **Source vs Output**: Clear separation between source components and generated files
- **Configuration-Driven**: All compositions defined in compose.toml
- **Pipeline Integration**: Runs as step 0 before setup/generate
- **Extensible**: Easy to add new component types and transformers
- **Safe**: Validates paths and provides clear error messages

## Build Pipeline

The composition module is **Step 0** in the GAZTank build pipeline:

```
Build Pipeline:
  0. compose  → Assemble index.html from src/components/
  1. clean    → Clean orphaned files
  2. setup    → Apply config to composed index.html
  3. gzlint   → Lint checks
  4. generate → Markdown to HTML
  5. sitemap  → Generate sitemap
  6. toc      → Generate TOC
  7. package  → Package files
  8. deploy   → Deploy to environment
```

### Typical Workflow:
```powershell
# Windows
.\scripts\compose.cmd -e dev
.\scripts\setup.cmd -e dev
.\scripts\generate.cmd -e dev

# Linux/Mac
./scripts/compose.sh -e dev
./scripts/setup.sh -e dev
./scripts/generate.sh -e dev
```

## Logging

The module uses **gzlogging** infrastructure for environment-aware operational logging.

### Log Configuration

- **Environment:** Specified via `-e` argument (dev/staging/prod)
- **Tool Name:** `compose`
- **Log Location:** `logs/{environment}/compose_YYYYMMDD.log`
- **Output Mode:** File + Console
- **Encoding:** UTF-8

### What Gets Logged

#### Logged to file:
- HTML Composition started
- Environment and force flag
- Number of compositions to process
- Each composition: description and result
- Component injection/skipping events
- Composition markers processed
- Success/failure status
- Errors and warnings

#### Console output:
- Progress indicators: [1/N] through [N/N]
- Success checkmarks (✓) and crosses (❌)
- Composition summaries
- Warning symbols (⚠) for missing components

### Log File Example

```log
[2025-11-04 14:32:10] [dev] [INF] ============================================================
[2025-11-04 14:32:10] [dev] [INF] HTML Composition started
[2025-11-04 14:32:10] [dev] [INF] Environment: dev
[2025-11-04 14:32:10] [dev] [INF] Force: False
[2025-11-04 14:32:10] [dev] [INF] Processing 1 composition(s)
[2025-11-04 14:32:10] [dev] [INF] Composition 1/1: Main site HTML with conditional sidebar navigation
[2025-11-04 14:32:10] [dev] [INF] Marker SIDEBAR (flag: enable_sidebar_toggle = True)
[2025-11-04 14:32:10] [dev] [INF] Wrote composed HTML: src\index.html
[2025-11-04 14:32:10] [dev] [INF] Successfully composed 1/1 file(s)
[2025-11-04 14:32:10] [dev] [INF] HTML Composition completed successfully
[2025-11-04 14:32:10] [dev] [INF] ============================================================
```

## Usage

### Command Line

```powershell
# Windows
.\scripts\compose.cmd -e dev
.\scripts\compose.cmd -e staging --force
.\scripts\compose.cmd -e prod

# Linux/Mac
./scripts/compose.sh -e dev
./scripts/compose.sh -e staging --force
./scripts/compose.sh -e prod
```

### As a Module

```python
python -m utils.compose -e dev
python -m utils.compose -e staging --force
python -m utils.compose --help
```

### From Python Code

```python
from utils.compose.composer import HTMLComposer
from gzconfig import get_site_config, get_compose_config
from gzlogging import get_logger

# Initialize
logger = get_logger('compose', 'dev')
site_config = get_site_config()
compose_config = get_compose_config()

# Create composer
composer = HTMLComposer(
    site_config=site_config,
    compose_config=compose_config,
    environment='dev',
    logger=logger,
    force=False
)

# Execute all compositions
result = composer.compose_all()
```

## Command Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `-e`, `--environment` | Yes | Target environment: `dev`, `staging`, or `prod` |
| `--force` | No | Force recomposition even if files are up-to-date |
| `-h`, `--help` | No | Show help message and exit |

### Examples:

```bash
# Compose for development
python -m utils.compose -e dev

# Force recomposition for staging
python -m utils.compose -e staging --force

# Show help
python -m utils.compose --help
```

## Module Structure

```
utils/compose/
├── __init__.py           # Module exports
├── __main__.py           # CLI entry point (python -m utils.compose)
├── composer.py           # Main composition logic
├── README.md             # This file
└── tests/                # Unit tests (future)
    └── test_composer.py
```

### Key Classes

#### `ComponentTransformer`
- Transforms component sources to HTML
- Supports 'navigation' and 'raw' transform types
- Converts markdown lists to navigation HTML structures

#### `HTMLComposer`
- Main composition orchestrator
- Reads compose.toml and site.toml
- Processes composition markers
- Manages component injection/removal
- Writes composed output files

## Features

### Composition Markers

Insert markers in base HTML files:

```html
<div class="main-container">
  <!-- COMPOSE:SIDEBAR:enable_sidebar_toggle -->
  <main id="content">
    ...
  </main>
</div>
```

**Marker Format:** `<!-- COMPOSE:COMPONENT_KEY:config_flag -->`

- `COMPONENT_KEY`: Matches `key` field in compose.toml component
- `config_flag`: Feature flag name from `site.toml [features]` section

### Conditional Inclusion

If `site.toml` has:
```toml
[features]
enable_sidebar_toggle = true
```

Then marker `<!-- COMPOSE:SIDEBAR:enable_sidebar_toggle -->` will:
- ✅ **true**: Inject sidebar component at marker location
- ❌ **false**: Remove marker, add `no-sidebar` class to `.main-container`

### Component Transformations

#### Markdown to Navigation HTML:

Input (`src/components/sidebar.md`):
```markdown
- [Home](#home)
- [Guide](#guide)
  - [Setup](#guide/setup)
  - [Tutorial](#guide/tutorial)
```

Output (injected):
```html
<nav id="sidebar">
  <button aria-label="Toggle sidebar" class="sidebar-toggle" id="sidebar-toggle">◀</button>
  <ul class="nav-level-1">
    <li><a data-content="home" href="#">Home</a></li>
    <li class="has-children">
      <div class="nav-item-wrapper">
        <a data-content="guide" href="#">Guide</a>
        <button aria-label="Toggle submenu" class="nav-toggle">▼</button>
      </div>
      <ul class="nav-level-2">
        <li><a data-content="guide/setup" href="#">Setup</a></li>
        <li><a data-content="guide/tutorial" href="#">Tutorial</a></li>
      </ul>
    </li>
  </ul>
</nav>
```

## Configuration

### compose.toml

Location: `config/compose.toml`

```toml
[[compositions]]
output = "src/index.html"
base = "src/components/index-base.html"
description = "Main site HTML with conditional sidebar navigation"

[[compositions.components]]
key = "SIDEBAR"
source = "src/components/sidebar.md"
type = "markdown"
description = "Navigation sidebar (markdown source)"
transform = "navigation"  # Special transformer for nav lists
```

#### Composition Fields:
- `output`: Target file path (where to write composed HTML)
- `base`: Base HTML template with composition markers
- `description`: Human-readable description for logs
- `components`: Array of component definitions

#### Component Fields:
- `key`: Unique identifier (matches COMPOSE:KEY in markers)
- `source`: Path to component source file
- `type`: Component type (`markdown`, `html`, etc.)
- `description`: Human-readable description
- `transform`: Transformation type (`navigation`, `raw`)

### site.toml Integration

Composition module reads feature flags from `config/site.toml`:

```toml
[features]
enable_sidebar_toggle = true
enable_breadcrumbs = true
enable_toc = true
```

Each `<!-- COMPOSE:KEY:config_flag -->` marker checks the corresponding flag.

## How It Works

### Execution Flow

1. **Load Configurations**
   - Read `config/compose.toml` for composition definitions
   - Read `config/site.toml` for feature flags

2. **Process Each Composition** (in order)
   - Read base HTML file
   - Parse with BeautifulSoup

3. **Find Composition Markers**
   - Search for `<!-- COMPOSE:KEY:flag -->` comments
   - Extract component KEY and config flag

4. **Check Feature Flag**
   - Look up flag in `site.toml [features]`
   - Default to `true` if not specified

5. **Generate Component**
   - If enabled: Load component source
   - Transform based on type (e.g., markdown → HTML)
   - Inject at marker location

6. **Handle Disabled Components**
   - If disabled: Remove marker
   - Add `no-{KEY}` class to `.main-container`

7. **Write Output**
   - Save composed HTML to output path
   - Create directories if needed

### Example Execution

#### Input Files:

`src/components/index-base.html`:
```html
<!DOCTYPE html>
<html>
<body>
  <div class="main-container">
    <!-- COMPOSE:SIDEBAR:enable_sidebar_toggle -->
    <main id="content">...</main>
  </div>
</body>
</html>
```

`src/components/sidebar.md`:
```markdown
- [Home](#home)
- [About](#about)
```

`config/site.toml`:
```toml
[features]
enable_sidebar_toggle = true
```

#### Command:
```bash
python -m utils.compose -e dev
```

#### Output (`src/index.html`):
```html
<!DOCTYPE html>
<html>
<body>
  <div class="main-container">
    <nav id="sidebar">
      <button aria-label="Toggle sidebar" class="sidebar-toggle" id="sidebar-toggle">◀</button>
      <ul class="nav-level-1">
        <li><a data-content="home" href="#">Home</a></li>
        <li><a data-content="about" href="#">About</a></li>
      </ul>
    </nav>
    <main id="content">...</main>
  </div>
</body>
</html>
```

## Component Types

### Markdown Components

**Type:** `markdown`

**Transform:** `navigation`

Converts markdown lists to HTML navigation structures with proper classes, attributes, and toggle buttons.

**Use Case:** Sidebar navigation, menus, TOC

#### Example:
```toml
[[compositions.components]]
key = "SIDEBAR"
source = "src/components/sidebar.md"
type = "markdown"
transform = "navigation"
```

### Raw HTML Components

**Type:** `html` (or any non-markdown type)

**Transform:** `raw`

Injects HTML content as-is without transformation.

**Use Case:** Footer, header, custom sections

#### Example:
```toml
[[compositions.components]]
key = "FOOTER"
source = "src/components/footer.html"
type = "html"
transform = "raw"
```

## Invocation Points

### 1. Command Line Scripts

#### Windows:
```cmd
.\scripts\compose.cmd -e dev
```

#### Linux/Mac:
```bash
./scripts/compose.sh -e dev
```

### 2. Python Module

```bash
python -m utils.compose -e staging --force
```

### 3. Pipeline Orchestrator

Called by `gzbuild` as step 0:

```python
# In utils/gzbuild/builder.py
steps = [
    (0, "Composing HTML from components", "utils.compose"),
    (1, "Cleaning orphaned files", "utils.clean"),
    # ...
]
```

### 4. Python Import

```python
from utils.compose.composer import HTMLComposer
# Use directly in scripts
```

## Development

### Adding New Transform Types

1. **Add transformer method to `ComponentTransformer` class:**

```python
def _transform_custom(self, content: str, component_key: str) -> str:
    """Transform content for custom type"""
    # Your transformation logic
    return transformed_html
```

2. **Update `transform()` method:**

```python
def transform(self, content: str, transform_type: str, component_key: str) -> str:
    if transform_type == "navigation":
        return self._transform_navigation(content, component_key)
    elif transform_type == "custom":
        return self._transform_custom(content, component_key)
    # ...
```

3. **Use in compose.toml:**

```toml
[[compositions.components]]
key = "MYCONTENT"
source = "src/components/content.md"
type = "markdown"
transform = "custom"
```

### Adding New Compositions

Simply add to `config/compose.toml`:

```toml
[[compositions]]
output = "src/about.html"
base = "src/components/about-base.html"
description = "About page"

[[compositions.components]]
key = "TEAMLIST"
source = "src/components/team.md"
type = "markdown"
transform = "raw"
```

## Customisation

### Custom Component Directory

Modify paths in `compose.toml`:

```toml
[[compositions.components]]
key = "SIDEBAR"
source = "custom/components/nav.md"  # Custom location
type = "markdown"
transform = "navigation"
```

### Multiple Markers

Add multiple markers in base HTML:

```html
<div class="main-container">
  <!-- COMPOSE:SIDEBAR:enable_sidebar_toggle -->
  <main id="content">
    <!-- COMPOSE:TOC:enable_toc -->
    <div id="content-container"></div>
  </main>
  <!-- COMPOSE:FOOTER:show_footer -->
</div>
```

Define corresponding components:

```toml
[[compositions.components]]
key = "SIDEBAR"
# ...

[[compositions.components]]
key = "TOC"
# ...

[[compositions.components]]
key = "FOOTER"
# ...
```

### Conditional CSS Classes

When component disabled, `no-{key}` class added automatically:

```html
<!-- Component enabled -->
<div class="main-container">...</div>

<!-- Component disabled -->
<div class="main-container no-sidebar">...</div>
```

Handle in CSS:

```css
.main-container.no-sidebar {
  grid-template-columns: 1fr;  /* Remove sidebar column */
}
```

## Troubleshooting

### Issue: Component not injected

**Symptoms:** Marker remains in output, component missing

#### Causes:
- Component `key` doesn't match marker KEY
- Component source file not found
- Transform type not supported

#### Solutions:
1. Check `compose.toml` component `key` matches `<!-- COMPOSE:KEY:flag -->`
2. Verify source file exists at specified path
3. Check logs for specific error messages
4. Ensure feature flag exists in `site.toml [features]`

### Issue: Markdown not transformed correctly

**Symptoms:** Raw HTML instead of navigation structure

#### Causes:
- Wrong transform type specified
- Markdown formatting issues (indentation)

#### Solutions:
1. Set `transform = "navigation"` in compose.toml
2. Check markdown list indentation (use 2 spaces)
3. Validate markdown syntax

### Issue: "Component source not found"

**Symptoms:** Error message about missing source file

#### Causes:
- Incorrect path in `compose.toml`
- File not created yet
- Working directory incorrect

#### Solutions:
1. Verify path relative to project root
2. Create source file: `src/components/sidebar.md`
3. Run from project root directory

### Issue: Feature flag not working

**Symptoms:** Component always included/excluded

#### Causes:
- Flag name mismatch
- `site.toml` syntax error
- Feature flag missing

#### Solutions:
1. Check marker: `<!-- COMPOSE:KEY:exact_flag_name -->`
2. Verify `site.toml` has `[features]` section
3. Check flag name spelling: `enable_sidebar_toggle`
4. Reload configurations after changes

## Best Practices

### Component Organization

```
src/components/
├── README.md           # Document component structure
├── index-base.html     # Main HTML base
├── sidebar.md          # Navigation
├── footer.html         # Footer
└── ...
```

### Marker Comments

Add descriptive comments:

```html
<!-- Main container with optional sidebar -->
<div class="main-container">
  <!-- COMPOSE:SIDEBAR:enable_sidebar_toggle -->
  <!-- Sidebar injected here if enabled -->
  
  <main id="content">
    ...
  </main>
</div>
```

### Git Ignore Generated Files

Add to `.gitignore`:

```gitignore
# Generated HTML (composed from components)
src/index.html

# Track source components
!src/components/
```

### Composition Order

Order matters! Process foundations before details:

```toml
# Process layout structure first
[[compositions]]
output = "src/index.html"
# ...

# Then process specialized pages
[[compositions]]
output = "src/about.html"
# ...
```

### Testing

Test both enabled and disabled states:

```bash
# Test enabled
# Edit site.toml: enable_sidebar_toggle = true
python -m utils.compose -e dev
# Verify sidebar present in src/index.html

# Test disabled
# Edit site.toml: enable_sidebar_toggle = false
python -m utils.compose -e dev --force
# Verify no sidebar, no-sidebar class added
```

## Future Enhancements

### Planned Features

1. **Variable Substitution** - Replace `{{PLACEHOLDERS}}` during composition
2. **Conditional Nesting** - Support nested COMPOSE markers
3. **Component Validation** - Verify required components exist before composition
4. **Hot Reload** - Watch component files during development
5. **Component Library** - Reusable component templates
6. **YAML Front Matter** - Metadata in component files
7. **Template Inheritance** - Base templates with blocks
8. **Multi-Output** - One composition generates multiple files

### Extension Points

- Add custom transformers in `ComponentTransformer`
- Create component preprocessors
- Implement component validators
- Add composition post-processors

## Related Documentation

- **[Pipeline Overview](../gzbuild/README.md)** - Complete build pipeline
- **[Setup Module](../setup/README.md)** - Configuration application (step 2)
- **[Generate Module](../generate/README.md)** - Content generation (step 4)
- **[GZConfig Module](../gzconfig/README.md)** - Configuration access
- **[GZLogging Module](../gzlogging/README.md)** - Logging infrastructure
- **[Project Structure](../../dev/PROJECT_STRUCTURE.md)** - Overall project organization
- **[Design Rules](../../docs/DESIGN_RULES.md)** - Module design guidelines

## License

This project is licensed under the GNU General Public License v3.0 or later.
See the [LICENSE](../../LICENSE) file for details.

## Authors

- **superguru** - Initial implementation
- **gazorper** - Testing and feedback

---

**GAZTank Website System** - HTML Composition Module v1.0  
Last Updated: November 4, 2025
