# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **10-Step Pipeline Architecture** (November 4, 2025)
  - **Compose Module**: Source content generation from templates (step 2)
  - **Normalise Module**: Markdown file formatting normalization (step 5)
  - Pipeline now: clean → compose → setup → gzlint → normalise → generate → sitemap → toc → package → deploy
  - Separation of concerns: normalise handles formatting, generate handles conversion
  - Batch normaliser (`utils/normalise/batch.py`) for pipeline integration
  
- **Clean Module Safety Features v1.2** (November 4, 2025)
  - **Identify-Only Default**: Clean step no longer deletes files by default
  - `--clean-orphaned` flag: Targeted cleanup of orphaned files (requires confirmation)
  - `--clean-all` flag: Complete environment cleanup (requires confirmation)
  - `--force` flag: Skip confirmation prompts for automation
  - Three operating modes: identify-only (default), clean-orphaned, clean-all
  - Confirmation prompts require typing "yes" to proceed
  - Safe defaults prevent accidental data loss
  
- Developer setup documentation (`docs/DEVELOPER_SETUP.md`)
- Professional repository structure (LICENSE, CONTRIBUTING, CHANGELOG)
- Python requirements.txt for dependency management
- **Generate Module Documentation**: Comprehensive README for `utils/generate/` module
  - Detailed usage instructions for command-line and programmatic use
  - Configuration guide for `generate.toml`
  - Troubleshooting section with common issues
  - Future enhancements roadmap
  - Integration points documentation
- **Generate Module Command-Line Arguments** (October 22, 2025)
  - `--force` flag to regenerate all files regardless of timestamps
  - `--dry-run` flag to preview what would be done without making changes
  - Flags can be combined (e.g., `--force --dry-run`)
  - Help text with usage examples (`--help`)
  - Arguments logged for audit trail
- **Generate Module UTF-8 Support** (October 22, 2025)
  - Added `__main__.py` to support `python -m generate` invocation
  - Updated launcher scripts to set `PYTHONIOENCODING=utf-8`
  - Updated launcher scripts to set PYTHONPATH correctly
  - Ensures proper display of Unicode characters (emojis) in output
  - Follows design rules for Python subprocess Unicode handling
- **Environment Parameter**: Setup script now requires `-e/--environment` parameter
- **File Tracking System**: Setup now tracks modified files and copies them to environment directories
  - Automatically copies modified src/ files to publish/<environment>/ directory
  - Preserves directory structure when copying
  - Only copies files that were actually modified during setup
- **Environment-Tagged Request Logging**: Server now includes environment name in every HTTP request log
  - Format: `[env] [timestamp] request details`
  - Improves debugging when running multiple environments simultaneously
  - Clear visual identification of which environment is handling each request
- **Setup Manifest Files**: Setup now generates markdown manifest of all copied files
  - Lists all files (src/ files AND image files) in detailed tables
  - Includes skipped files (up-to-date files) in separate table
  - Column order: Source Path, Filename, Destination Path, Size, Modified
  - Paths shown relative to common root with leading path separator (e.g., `\css\styles.css`)
  - Smart sorting: files in parent directory appear before subdirectories
  - Modified timestamps include timezone offset (e.g., `2025-10-21 14:30:45 +0000`)
  - Size column is right-aligned for better readability
  - Named `setup_manifest.md` (not timestamped)
  - Only included in backup zip, not saved separately in backups directory
  - Automatically included in backup zip for audit trail
- **Image File Management**: Setup now copies favicon and logo files to environment directories
  - Automatically copies favicon_32, favicon_16, and all logo files (512, 256, 128, 75, 50)
  - Only copies if source file is newer than destination (respects timestamps)
  - Ensures environment directories have all required branding assets
- **Environment Clean Command**: New `--clean` parameter to delete environment directories
  - Usage: `python utils/setup/setup_site.py -e dev --clean`
  - Prompts for confirmation with file/directory counts
  - Use `--clean --force` to skip confirmation prompt
  - Can only be used with `-e` and optionally `--force` (no other parameters allowed)

### Changed
- **Pipeline Architecture** (November 4, 2025)
  - Expanded from 8 to 10 steps for better separation of concerns
  - Generate module no longer handles markdown normalization
  - Normalise step runs before generate to ensure consistent formatting
  - All documentation updated to reflect 10-step pipeline
  
- **Module Documentation Updates** (November 4, 2025)
  - `utils/clean/README.md` → v1.2: Documents three operating modes, confirmation prompts
  - `utils/gzbuild/README.md` → v1.1: Updated to 10-step pipeline, safe clean defaults
  - `README.md`: Updated with current 10-step pipeline and clean safety notes
  - `dev/00TODO/PROFESSIONAL_REPO_SETUP.md`: Reflects current architecture
  
- **Parameter Rename**: `--force-apply` renamed to `--force` for brevity
  - Usage: `python utils/setup/setup_site.py -e dev --force`
  - Skips all prompts and applies current site.toml configuration
- **MD to HTML Module Refactoring** (October 22, 2025)
  - Removed standalone script functionality (main(), argparse, config loading)
  - Module now provides only the `MarkdownConverter` class for use by generate.py
  - Removed duplicate utility functions (get_project_root, load_config, get_output_path)
  - Removed global logging context (generate.py handles all logging)
  - Cleaner separation of concerns: generate.py orchestrates, md_to_html.py converts
  - No breaking changes to generate.py functionality
- **Generate Module Logging Improvements** (October 22, 2025)
  - Separated console UI output from log file content
  - Log files now contain only operational information (no decorative lines, emojis, or blank lines)
  - Console output retains user-friendly formatting with emojis and visual elements
  - Logging mode set to file-only (console has independent formatting)
  - Clean, parseable log entries suitable for audit trails
- **Generate Module Statistics Enhancement** (October 22, 2025)
  - Improved reporting to distinguish between converted, skipped, and failed files
  - Timestamp-based regeneration: only converts when input is newer than output
  - Status messages now show: "X converted, Y skipped (up-to-date)" for mixed results
  - More informative group completion messages based on actual operations performed
  - Log file tracks individual file conversion and skip status
- **Force Mode Behavior**: `--force` now skips timestamp checks when copying files
  - Without `--force`: Only copies files where source is newer than destination
  - With `--force`: Copies all files regardless of timestamps
  - Applies to both src/ files and image files (favicon/logos)
- **Backup System Optimization**
  - Setup script now backs up all config files from config/ directory automatically
  - Backups created as zip files instead of directory structures
  - Backup location: `publish/backups/config_<environment>_YYYYMMDDHHMM.zip`
  - Environment parameter now **required** for setup script (`-e dev`, `-e production`, etc.)
  - Backup files named by environment for separate backup history per environment
  - Cleanup process maintains separate backup history per environment
  - Excludes backup files (.backup.*) and example files (.example.*)
  - New config files automatically included without code changes
  - Manifest files now included in backup zips
- **Setup Workflow Enhancement**
  - Setup modifies files in src/ directory based on site.toml configuration
  - Modified files are automatically copied to specified environment directory (publish/dev, publish/prod, etc.)
  - Ensures environment directories stay synchronized with latest configuration

## [0.0.1] - 2025-11-04

### Added
- **10-Step Build Pipeline**
  - Added compose module for source content generation
  - Added normalise module for markdown formatting
  - Complete pipeline: clean → compose → setup → gzlint → normalise → generate → sitemap → toc → package → deploy
  - Better separation of concerns between modules

- **Enhanced Clean Module (v1.2)**
  - Safe defaults: identify-only mode (no deletion)
  - `--clean-orphaned` flag with confirmation prompt
  - `--clean-all` flag with confirmation prompt
  - `--force` flag to skip confirmations
  - Three operating modes documented

### Changed
- Generate module no longer handles markdown normalization
- All documentation updated to reflect 10-step pipeline
- Clean module now requires explicit flags for deletion
- Improved safety with confirmation prompts

### Documentation
- Updated `utils/clean/README.md` to v1.2
- Updated `utils/gzbuild/README.md` to v1.1
- Updated main `README.md` with 10-step pipeline
- Updated `dev/00TODO/PROFESSIONAL_REPO_SETUP.md`

## [1.0.0] - 2025-10-20

### Added
- **Table of Contents Enhancements**
  - H2 heading support in TOC (previously only h3, h4)
  - Smart filtering: headings ending with colon (:) excluded from TOC
  - Auto-generated IDs for all h2, h3, h4 headings for deep linking
  - Three-level hierarchy: h2 > h3 > h4 with proper nesting
  - CSS styling for .toc-h2 class

- **SEO & Configuration**
  - Configurable `keywords` field in [seo] section
  - Configurable `robots_directive` field (e.g., "index, follow")
  - Automatic meta tag updates from configuration
  - JSON-LD description field pulls from config
  - CONFIG_DRIVEN_INDEX.md documentation tracking config-driven items

- **GZLint Improvements**
  - HTML structure validation (detects malformed tags)
  - Mismatched closing tag detection
  - Recursive subdirectory processing
  - H1 validation (missing h1, duplicate h1 detection)
  - GZ_LINT_RULES.md documentation

- **Documentation**
  - SEO_IMPLEMENTATION.md with comprehensive analytics configuration
  - Analytics examples for Plausible, Google Analytics 4, Matomo
  - Privacy considerations and implementation status
  - SETUP_SITE.md updated with recent changes

- **CSS Improvements**
  - Proper list styling for ordered/unordered lists in content
  - TOC list style overrides to maintain custom appearance
  - Nested list styling (disc > circle > square for ul, decimal > alpha > roman for ol)

### Changed
- Updated README.md with October 2025 improvements section
- Improved markdown to HTML conversion pipeline
- Enhanced package.py pre-flight validation
- Configuration now uses TOML format (site.toml) instead of INI

### Fixed
- Ordered lists not displaying numbers due to CSS reset
- TOC lists showing numbers/bullets instead of custom arrows
- Subdirectory files not processed by gzlint
- Malformed HTML not detected during validation

## [0.9.0] - 2025-10-15

### Added
- **Setup Wizard Enhancements**
  - Force-apply mode (--force-apply) for non-interactive config application
  - Comment preservation in TOML configuration files using tomlkit
  - Automatic backup management (keeps last 5 backups)
  - Modular architecture with separate concerns
  - Cross-platform support (.cmd for Windows, .sh for Linux/Mac)

- **Build Pipeline**
  - Pre-flight validation with GZLint
  - Automatic markdown to HTML conversion
  - Sitemap generation integration
  - Orphaned file cleanup
  - CSS/JS minification (optional with rcssmin/rjsmin)
  - Timestamped package archives
  - Exit codes for CI/CD integration

- **Documentation**
  - DESIGN_RULES.md project design principles
  - RESPONSIVE_IMAGES.md image optimization guide
  - MODULE_STRUCTURE.md for setup wizard architecture

### Changed
- Setup wizard refactored into modular components:
  - ui_helpers.py (terminal formatting)
  - validators.py (input validation)
  - config_io.py (TOML I/O)
  - user_interaction.py (interactive prompts)
  - file_generators.py (CSS/HTML generation)
  - backup_manager.py (backup operations)

- Package script enhanced with validation and automation
- Deploy script with FTP/FTPS support and progress bars

## [0.8.0] - 2025-10-10

### Added
- **Navigation System**
  - Multi-level nested navigation (up to 4 levels)
  - Collapsible sidebar with state persistence
  - Expandable/collapsible tree menu
  - Smart auto-expansion for parent items
  - Active page indicators with color coding

- **Content Management**
  - Dynamic content loading from separate HTML files
  - Hashtag system for content categorization
  - Advanced Table of Contents with multi-level collapsibility
  - Two-column TOC layout (Contents and Navigation sections)
  - Deep linking support (#page:heading-id)
  - No duplicate loading with smart caching

- **SEO Features**
  - Dynamic page-specific meta tags
  - Open Graph tags for social media
  - Twitter Card tags
  - JSON-LD structured data (WebSite schema)
  - Canonical URLs
  - sitemap.xml generation
  - robots.txt and humans.txt

- **Layout & Design**
  - CSS Grid layout for main structure
  - Flexbox components
  - Responsive design with mobile breakpoints
  - Custom color scheme with CSS variables
  - Dark sidebar with professional styling
  - Fixed header and footer

### Changed
- Switched to hash-based routing for SPA functionality
- Improved breadcrumb navigation with Schema.org markup
- Enhanced TOC with ellipsis indicator when collapsed

## [0.7.0] - 2025-10-05

### Added
- **Development Tools**
  - Local development server (server.py) with no-cache headers
  - Interactive admin commands (stop, quit, help)
  - Sitemap generator (sitemap module)
  - Image responsive sizing tools
  - GZLint code quality checker

- **Configuration System**
  - TOML-based configuration (config/site.toml)
  - Descriptive color naming system
  - Automatic CSS variable generation
  - Layout dimensions and typography settings

### Changed
- Improved file structure organization
- Enhanced cross-platform script support

## [0.6.0] - 2025-09-30

### Added
- Initial public release
- Single-page application architecture
- Basic navigation and routing
- Content loading system
- CSS Grid and Flexbox layout
- Configuration-driven theming

---

## Version History Summary

- **0.0.1** (2025-11-04) - Pipeline expansion to 10 steps, clean module safety enhancements, comprehensive documentation updates
- **0.0.0** (2025-10-20) - Major feature release with TOC enhancements, SEO improvements, GZLint validation
- **0.0.0** (2025-10-15) - Setup wizard modularization and build pipeline automation
- **0.0.0** (2025-10-10) - Navigation system, SEO features, and content management
- **0.0.0** (2025-10-05) - Development tools and configuration system
- **0.0.0** (2025-09-30) - Initial public release

---

## Legend

- `Added` - New features
- `Changed` - Changes in existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security fixes

---

[Unreleased]: https://github.com/yourusername/GAZTank/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/yourusername/GAZTank/compare/v1.0.0...v0.0.1
