# GAZTank Project Structure

This document provides a comprehensive overview of the GAZTank project directory structure and file organization.

## Full Directory Tree

```
GAZTank/
├── src/                          # Source files
│   ├── index.html               # Main HTML file with navigation structure
│   ├── .htaccess                # Apache server configuration
│   ├── css/
│   │   ├── styles.css           # All styles (Grid, Flexbox, components)
│   │   └── variables.css        # CSS custom properties and theme variables
│   ├── js/
│   │   └── app.js               # Navigation, routing, content loading, SEO
│   ├── images/
│   │   ├── gaztank_favicon_16x16.webp
│   │   ├── gaztank_favicon_32x32.webp
│   │   ├── gaztank_favicon_RAW.pdn
│   │   ├── gaztank_logo_256x256.webp
│   │   └── gaztank_logo_75x75.webp
│   ├── robots.txt               # Search engine directives
│   ├── sitemap.xml              # Site map for search engines (auto-generated)
│   ├── humans.txt               # Team attribution
│   └── content/                 # Content HTML files
│       ├── about.html
│       ├── contact.html
│       ├── future.html
│       ├── home.html
│       ├── setup_guide.html
│       ├── test_lazy_loading.html
│       ├── nesting/             # Nested content example
│       │   ├── nesting.html
│       │   ├── sister_node.html
│       │   └── brother_node.html
│       └── setup/               # Setup documentation (converted from docs/)
│           ├── DEVELOPER_SETUP.html
│           ├── DESIGN_RULES.html
│           ├── README.html
│           ├── RESPONSIVE_IMAGES.html
│           ├── SEO_IMPLEMENTATION.html
│           └── SETUP_SITE.html
│
├── utils/                        # Utility modules
│   ├── 00MODULE_MATURITY.md     # Module maturity tracking document
│   ├── FLOW_PIPELINE.md         # Pipeline flow documentation
│   ├── clean/                   # Orphaned file cleanup module
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── cleaner.py           # Core cleanup logic
│   │   └── README.md
│   ├── deploy/                  # FTP/FTPS deployment module
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── deployer.py          # Core deployment logic
│   │   └── README.md
│   ├── generate/                # Content generation module
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── generate.py          # Core generation logic
│   │   └── README.md
│   ├── gzconfig/                # Configuration management library
│   │   ├── __init__.py
│   │   ├── deploy.py            # Deploy configuration
│   │   ├── generate.py          # Generate configuration
│   │   ├── pipeline.py          # Pipeline configuration
│   │   ├── site.py              # Site configuration
│   │   └── tools.py             # Tools configuration
│   ├── gzlint/                  # HTML/JS linting module
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── gzlinter.py          # Core linting logic
│   │   └── README.md
│   ├── gzlogging/               # Centralized logging library
│   │   ├── __init__.py
│   │   ├── logger.py            # Core logging infrastructure
│   │   └── README.md
│   ├── normalise/               # Markdown normalization module
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── normaliser.py        # Core normalization logic
│   │   ├── example_usage.py
│   │   └── README.md
│   ├── package/                 # Build/package module
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── packager.py          # Core packaging logic
│   │   └── README.md
│   ├── gzserve/                 # Development server module
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── server.py            # HTTP server implementation
│   │   └── README.md
│   ├── setup/                   # Interactive site configuration
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── setup_site.py        # Main setup wizard entry point
│   │   ├── user_interaction.py  # User input and prompts
│   │   ├── config_io.py         # Configuration file I/O
│   │   ├── validators.py        # Input validation
│   │   ├── file_generators.py   # CSS, HTML generation
│   │   ├── backup_manager.py    # Backup management
│   │   ├── ui_helpers.py        # UI formatting and messages
│   │   ├── js_updater.mjs       # JavaScript configuration updater
│   │   ├── package.json         # Node.js dependencies for js_updater
│   │   └── README.md
│   ├── sitemap/                 # Sitemap generation module
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── generator.py         # Core sitemap generation logic
│   │   └── README.md
│   └── toc/                     # Table of Contents generation module
│       ├── __init__.py
│       ├── __main__.py
│       ├── generator.py         # Core TOC generation logic
│       └── README.md
│
├── config/                       # Configuration files (TOML format)
│   ├── site.toml                # Site configuration (colors, branding, SEO)
│   ├── deploy.toml              # FTP deployment credentials (gitignored)
│   ├── deploy.example.toml      # Deployment config template
│   ├── generate.toml            # Content generation configuration
│   ├── gzlogrotate.toml         # Log rotation configuration
│   ├── pipeline.toml            # Environment-specific pipeline configuration
│   └── tools.toml               # Tools configuration
│
├── docs/                         # Documentation (Markdown sources)
│   ├── SETUP_SITE.md            # Comprehensive setup guide
│   ├── DESIGN_RULES.md          # Project design principles
│   ├── DEVELOPER_SETUP.md       # Developer environment setup
│   ├── RESPONSIVE_IMAGES.md     # Image optimization guide
│   └── SEO_IMPLEMENTATION.md    # SEO best practices and analytics
│
├── publish/                      # Build outputs (gitignored)
│   ├── dev/                     # Development environment build
│   ├── staging/                 # Staging environment build
│   ├── prod/                    # Production environment build
│   ├── packages/                # Timestamped deployment packages
│   └── backups/                 # Configuration backups with timestamps
│
├── scripts/                      # Cross-platform launcher scripts
│   ├── gzclean.cmd              # Windows cleanup launcher
│   ├── gzclean.sh               # Linux/Unix cleanup launcher
│   ├── deploy.cmd               # Windows deployment launcher
│   ├── deploy.sh                # Linux/Unix deployment launcher
│   ├── generate.cmd             # Windows content generator launcher
│   ├── generate.sh              # Linux/Unix content generator launcher
│   ├── generate_sitemap.cmd     # Windows sitemap generator launcher
│   ├── generate_sitemap.sh      # Linux/Unix sitemap generator launcher
│   ├── generate_toc.cmd         # Windows TOC generator launcher
│   ├── generate_toc.sh          # Linux/Unix TOC generator launcher
│   ├── gzbuild.cmd              # Windows complete pipeline build
│   ├── gzbuild.sh               # Linux/Unix complete pipeline build
│   ├── gzlint.cmd               # Windows linter launcher
│   ├── gzlint.sh                # Linux/Unix linter launcher
│   ├── normalise.cmd            # Windows markdown normalizer launcher
│   ├── normalise.sh             # Linux/Unix markdown normalizer launcher
│   ├── package.cmd              # Windows package launcher
│   ├── package.sh               # Linux/Unix package launcher
│   ├── server.cmd               # Windows dev server launcher
│   ├── server.sh                # Linux/Unix dev server launcher
│   ├── setup_site.cmd           # Windows setup wizard launcher
│   └── setup_site.sh            # Linux/Unix setup wizard launcher
│
├── dev/                          # Development utilities
│   ├── gzlint.cmd               # Windows linter launcher
│   ├── gzlint.sh                # Linux/Unix linter launcher
│   ├── create_responsive_images.cmd    # Image processing (Windows)
│   ├── create_responsive_images.py     # Image processing script
│   ├── create_responsive_images.sh     # Image processing (Linux/Unix)
│   ├── prompts.txt              # Development prompts and notes
│   ├── 00TODO/                  # Active tasks and planning
│   │   ├── 00LIST.md            # Main task list
│   │   └── CONFIG_DRIVEN_INDEX.md      # Config-driven documentation
│   ├── 00TODO_DONE/             # Completed tasks archive
│   │   ├── convert_md_to_utf8.ps1
│   │   ├── CSS_Variable_Analysis.md
│   │   ├── GENERICIZATION.md
│   │   ├── REMOVE_RE_MODULE_FROM_FILE_GENERATORS.md
│   │   ├── TOC_MODULE_IMPLEMENTATION.md
│   │   └── TODO_Hardcoded_Colors.md
│   ├── gzlint/                  # GZLint linter (old development version)
│   │   ├── gzlint.py            # Old linter (deprecated, see utils/gzlint/)
│   │   └── GZ_LINT_RULES.md     # Linter rules documentation
│   └── images/                  # Image processing workspace
│       ├── create_responsive_images_temp.cmd
│       └── RAW_gaztank_logo_and_favicon.pdn
│
├── .github/                      # GitHub-specific files
│   ├── pull_request_template.md
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── .gitignore                   # Git ignore rules
├── CHANGELOG.md                 # Project changelog
├── CONTRIBUTING.md              # Contribution guidelines
├── LICENSE                      # MIT License
├── PROJECT_STRUCTURE.md         # This file
├── PROFESSIONAL_REPO_CHECKLIST.md  # Repository quality checklist
├── README.md                    # Main project documentation
├── SECURITY.md                  # Security policy
├── gzlint-issues.txt            # Linter output (auto-generated)
└── requirements.txt             # Python dependencies
```

## Directory Purposes

### `/src/` - Source Files
The main source directory containing all files that will be deployed to the web server:
- **index.html**: Single-page application shell with navigation structure
- **css/**: Stylesheets with CSS custom properties for theming
- **js/**: Client-side JavaScript for SPA functionality
- **content/**: HTML content files loaded dynamically by the SPA
- **images/**: Optimized images (WebP format with responsive sizes)

### `/utils/` - Utility Modules
Python modules following a consistent structure:
- Each module has: `__init__.py`, `__main__.py`, core logic file, and `README.md`
- **Foundational modules**: gzconfig (configuration), gzlogging (logging)
- **Pipeline modules**: clean, deploy, generate, gzlint, normalise, package, gzserve, setup, sitemap, toc
- All modules are environment-aware (require `-e` argument)
- All modules use gzconfig for configuration management
- All modules use gzlogging for centralized logging

### `/config/` - Configuration Files
TOML configuration files accessed via gzconfig library:
- **site.toml**: Site settings (colors, branding, SEO metadata)
- **deploy.toml**: FTP/FTPS credentials (gitignored, use deploy.example.toml as template)
- **generate.toml**: Content generation file groups and mappings
- **gzlogrotate.toml**: Log rotation settings
- **pipeline.toml**: Environment-specific directory paths (dev/staging/prod)
- **tools.toml**: Tools and utilities configuration

### `/docs/` - Documentation Sources
Markdown documentation files:
- Source files that are converted to HTML and placed in `src/content/setup/`
- Provides both Markdown (for GitHub) and HTML (for website) versions

### `/publish/` - Build Outputs
Environment-specific build directories (all gitignored):
- **dev/**: Development environment build output
- **staging/**: Staging environment build output
- **prod/**: Production environment build output
- **packages/**: Timestamped ZIP archives for deployment
- **backups/**: Configuration backups with timestamps

### `/scripts/` - Launcher Scripts
Cross-platform shell scripts for running utilities:
- `.cmd` files for Windows (PowerShell)
- `.sh` files for Linux/Unix/Mac (Bash)
- Set up PYTHONPATH and execute Python modules

### `/dev/` - Development Tools
Development-only utilities and documentation:
- **00PROMPTS_MAIN.md**: Main development prompts
- **01PROMPTS_MODULE_MATURITY.md**: Module maturity prompts
- **CHECK_TYPES_README.md**: Type checking documentation
- **MODULE_README_STRUCTURE.md**: Module README template
- **PROJECT_STRUCTURE.md**: This file
- **check_types.cmd/ps1/sh**: Type checking scripts
- **create_responsive_images**: Image optimization scripts
- **00TODO/**: Active task tracking
- **00TODO_DONE/**: Completed task archive
- **images/**: Image processing workspace

## Module Architecture

All utility modules follow this consistent pattern:

```
utils/{module}/
├── __init__.py          # Exports and version info
├── __main__.py          # Entry point for `python -m {module}`
├── {module}.py          # Core implementation logic
└── README.md            # Comprehensive module documentation
```

### Available Modules

#### Foundational:
1. **gzconfig** - Configuration management library
2. **gzlogging** - Centralized logging infrastructure

#### Pipeline:
3. **clean** - Remove orphaned files from environment directories
4. **deploy** - FTP/FTPS deployment to web server
5. **generate** - Environment-aware content generation
6. **gzlint** - HTML/JS linting and validation
7. **normalise** - Markdown file normalization
8. **package** - Build system with minification and archiving
9. **gzserve** - Development HTTP server
10. **setup** - Interactive site configuration wizard
11. **sitemap** - XML sitemap generation
12. **toc** - Table of contents generation for HTML files

## Build Pipeline

The complete build process (`gzbuild.cmd/sh`) runs:
1. **clean** - Remove orphaned files from target environment
2. **setup --force** - Apply site configuration and regenerate config-driven files
3. **gzlint** - Run linting checks on all content
4. **generate** - Generate fresh content files
5. **sitemap** - Generate sitemap.xml
6. **toc** - Add table of contents to HTML files
7. **package** - Sync, minify, and archive site files
8. **deploy** - Deploy to target environment

## Key Features

### Configuration-Driven Design
- Site colors, branding, and SEO in `config/site.toml`
- No hardcoded values in code
- Easy customization and rebranding

### Single-Page Application (SPA)
- Client-side routing without page reloads
- Dynamic content loading
- Navigation state persistence
- SEO-friendly with proper meta tags

### Developer Experience
- Cross-platform scripts (Windows/Linux/Mac)
- Comprehensive documentation
- Automated build pipeline
- Linting and validation tools
- Local development server

### Production Ready
- Minified CSS/JS in production builds
- Optimized WebP images
- Timestamped deployment packages
- Configuration backups
- Security best practices

## Related Documentation

- [README.md](README.md) - Main project overview and quick start
- [DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md) - Development environment setup
- [DESIGN_RULES.md](docs/DESIGN_RULES.md) - Project design principles
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [SETUP_SITE.md](docs/SETUP_SITE.md) - Site configuration guide

## Navigation Structure

The site navigation is defined in `src/index.html` and follows a hierarchical structure:
- **Level 1**: Main navigation items (Home, About, etc.)
- **Level 2**: Sub-pages under main items
- **Level 3**: Nested sub-pages (if needed)
- **Level 4**: Deep nested pages (if needed)

The navigation structure is parsed by:
- `utils/sitemap/generator.py` - For sitemap.xml generation
- `src/js/app.js` - For dynamic content loading and TOC generation
