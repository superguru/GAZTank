# GAZ Tank

![GitHub release](https://img.shields.io/github/v/release/superguru/GAZTank)
![License](https://img.shields.io/github/license/superguru/GAZTank)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Issues](https://img.shields.io/github/issues/superguru/GAZTank)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

<div class="image-text-row">
<img src="src/images/gaztank_logo_75x75.webp" alt="GAZ Tank Logo" class="no-lazy"/>
<p>
A modern, single-page web application built with native CSS Grid, Flexbox, and vanilla JavaScript - no frameworks or libraries required.
<br><em>Some JS libraries are used for optional features, which will not be loaded at all in the site if turned off, for example Prism and Mermaid<em>
</p>
</div> 

```textfile
Note:
------
Have a look a the README.md file to see how you can add images and the CSS class used to achieve the text alignment with the image as shown here.
```

## Features

### Navigation & Routing
- **Multi-level Nested Navigation** (up to 4 levels deep)
- **Collapsible Sidebar** with toggle button (◀/▶)
  - State persists in sessionStorage
  - Smooth transitions with content area expansion
- **Expandable/Collapsible Tree Menu** with smart auto-expansion
  - Click parent items with children to expand automatically
  - Already-expanded items load content without collapsing
  - Top-level parent remains highlighted when sub-page is active
- **URL Hash Routing** for direct linking and shareable URLs
- **Browser History Support** (back/forward buttons work)
- **Active Page Indicators**:
  - Top-level parent pages: Orange background (#E58822), no hand icon
  - Active pages: Orange text (#E58822) OR orange background with white hand icon (☞)
  - Hand icon only appears on the actual active page, not parent nodes
  - Hover: Light grey background overlay
- **Persistent Menu State** across page refreshes
- **Fixed Header & Footer** for app-like layout
  - Header and footer stay frozen while content scrolls
  - Main content area positioned between header and footer

### Content Management
- **Dynamic Content Loading** from separate HTML files
- **Hashtag System** for content categorization:
  - Add `<div data-hashtags="tag1, tag2, tag3"></div>` to any content file
  - Hashtags display in compact area at bottom of content
  - Right-aligned with golden yellow color (#FFC845)
  - Minimal height with subtle divider line
  - Ready for future click functionality (filtering, search)
- **Advanced Table of Contents** with multi-level collapsibility:
  - Two-column layout (content on left, collapse button on right)
  - Separate "Contents" and "Navigation" sections with independent collapse
  - Contents: Extracts h2, h3, and h4 headings from current page
  - Navigation: Shows child pages from navigation hierarchy (excludes current page)
  - Collapsible h2 sections with h3/h4 children, h3 sections with h4 children (▾/▸ arrows)
  - Entire TOC collapsible with visual ellipsis indicator when collapsed
  - Smart default states: Contents expanded if present, Navigation collapsed unless no Contents
  - Deep linking support: Share links to specific headings (#page:heading-id)
  - Automatically generates IDs for all h2, h3, and h4 headings
  - Skips headings ending with colon (:) to avoid category header clutter
  - Clickable ellipsis to expand collapsed TOC
  - Per-page state persistence using sessionStorage
  - Excludes current page from its own TOC
- **SEO-Friendly Breadcrumbs** with Schema.org markup
  - Compact design with reduced spacing
- **No Duplicate Loading** - smart caching prevents unnecessary reloads
- **Comprehensive SEO Implementation**:
  - Dynamic page-specific meta tags (title, description, keywords, robots)
  - Open Graph tags for social media sharing
  - Twitter Card tags for tweet previews
  - JSON-LD structured data (WebSite schema)
  - Canonical URLs for each page
  - Configurable SEO keywords and robots directive
  - sitemap.xml with all pages and priorities
  - robots.txt with search engine directives
  - humans.txt with team attribution
  - Resource preloading for performance
  - Comprehensive documentation in docs/SEO_IMPLEMENTATION.md

### Layout & Design
- **CSS Grid Layout** for main page structure
- **Flexbox Components** for flexible layouts
- **Responsive Design** with mobile breakpoints
- **Clean Sidebar Navigation**:
  - Simple design with orange left border (3px)
  - White text with orange highlighting for active items
  - No tree lines for easier maintenance
  - Arrow indicators (▾/▸) for expandable sections
- **Custom Color Scheme**:
  - Teal background (#286C76)
  - Orange accent (#E58822)
  - Gold links (#FFD700) / Silver visited links (#C0C0C0)
  - Grey TOC collapse indicator (rgba(128, 128, 128, 0.2))
  - Golden yellow hashtags (#FFC845)
  - Subtle dividers (rgba(255, 255, 255, 0.1))
- **Dark Sidebar** with professional styling and smooth transitions
  - Orange left border extends full height
  - Sidebar height extended to eliminate visual gaps

### Deployment & Development
- **Smart Package Script** with file modification checking:
  - Pre-flight validation with GZLint checks (HTML validation, heading checks, JS linting)
  - Markdown to HTML conversion for documentation
  - Automatic sitemap generation
  - Creates timestamped packages in publish/packages/
  - Automatic backup system (keeps last 5 packages as zips)
  - Orphaned file cleanup ensures no stale content
  - Copies from src/ to publish/staging/
  - GZLint validates HTML structure (malformed tags, duplicate h1s, missing h1s)
  - Processes all files including subdirectories recursively
- **Automated FTP/FTPS Deploy Script**:
  - TOML configuration (config/deploy.toml) with sensitive data gitignored
  - Timestamped upload subdirectories with random postfix for organization
  - Configurable date format for upload directories
  - Supports both FTPS (secure) and regular FTP
  - Custom port configuration
  - Uploads latest package from publish/packages/
  - [Y/n] confirmation prompts before deployment
  - Checks if package is older than source files
  - Offers to run package script if sources are newer
  - Real-time upload progress bar with percentage and MB transferred
  - Shows final upload location path
- **Enhanced Development Server** with:
  - No-cache headers for fresh reloads during development
  - Interactive admin commands (type `stop` or `quit` to shutdown)
  - Graceful shutdown handling
  - Auto-detection of src/ directory
  - Default port 7190 with custom port support
- **Comprehensive Site Setup System**:
  - Interactive setup wizard for complete site configuration
  - Smart configuration management with config/site.toml as source of truth
  - Force-apply mode preserves existing configuration values (--force-apply)
  - Comment preservation in configuration files
  - Descriptive color naming (brand_button_color, body_text_color, etc.)
  - Automatic CSS variable generation from configuration
  - Updates meta tags (keywords, robots directive) from configuration
  - Updates JSON-LD structured data from configuration
  - Backup management with automatic cleanup (keeps last 5 backups)
  - Cross-platform support with both .cmd and .sh scripts
  - Documentation of config-driven vs hardcoded items in dev/00TODO/CONFIG_DRIVEN_INDEX.md
- **Markdown to HTML Converter**:
  - Converts documentation markdown files to HTML for web viewing
  - TOML-based configuration (config/md_to_html.toml)
  - Multiple file groups with separate output directories
  - Automatic integration into package pipeline
  - Supports markdown extensions (tables, code highlighting, TOC)
- **Update All Script** for complete site refresh:
  - Runs setup with force-apply to regenerate all config-driven files
  - Converts all markdown documentation to HTML
  - Generates fresh sitemap
  - Single command updates entire site

## Project Structure

For a comprehensive directory structure with detailed descriptions, see [PROJECT_STRUCTURE.md](#setup/PROJECT_STRUCTURE).

### Quick Overview:
- **`src/`** - Source files (HTML, CSS, JS, images, content)
- **`utils/`** - Python utility modules (deploy, package, sitemap, toc, etc.)
- **`config/`** - TOML configuration files (site settings, deployment)
- **`docs/`** - Markdown documentation (converted to HTML for the site)
- **`publish/`** - Build outputs (staging, packages, backups) - gitignored
- **`scripts/`** - Cross-platform launcher scripts (.cmd for Windows, .sh for Linux/Mac)
- **`dev/`** - Development tools (linter, image processing, TODO tracking)

## Getting Started

### Site Configuration

Before running the site, configure your branding and theme:

```bash
# Interactive setup for development environment
python utils/setup/setup_site.py -e dev

# Force mode - skip prompts and apply current configuration
python utils/setup/setup_site.py -e dev --force

# Clean environment - delete all files in environment directory
python utils/setup/setup_site.py -e dev --clean

# Clean with force - skip confirmation prompt
python utils/setup/setup_site.py -e dev --clean --force
```

The setup wizard will help you configure:
- Site name, tagline, description, and author
- Color theme with descriptive names (brand_button_color, body_text_color, etc.)
- Layout dimensions and typography
- SEO settings and analytics
- Image references and branding

#### Setup Features:
- Automatically copies modified files to the specified environment directory
- Copies favicon and logo files to environment when configured
- Generates manifest file listing all copied files with timestamps
- Creates backup of configuration with manifest included
- Respects file timestamps (only copies newer files unless `--force` is used)

Configuration is stored in `config/site.toml` which serves as the source of truth.

### Running the Development Server

The development server supports multiple environments (dev/staging/prod) configured in `config/pipeline.toml`.

#### Windows:
```bash
scripts\gzserve.cmd -e dev                # Development environment
scripts\gzserve.cmd -e staging -p 8080    # Staging with custom port
scripts\gzserve.cmd -e prod               # Production environment
```

#### Linux/Unix/Mac:
```bash
./scripts/gzserve.sh -e dev               # Development environment
./scripts/gzserve.sh -e staging -p 8080   # Staging with custom port
./scripts/gzserve.sh -e prod              # Production environment
```

#### Direct Python Module:
```bash
python -m utils.gzserve -e dev             # Development (port from config)
python -m utils.gzserve -e staging -p 8080 # Staging with custom port
```

##### Default Ports (configured in `config/pipeline.toml`):
- Development: http://localhost:7190
- Staging: http://localhost:7191
- Production: http://localhost:7192

#### Server Commands
- Type `stop`, `quit`, or `exit` to gracefully shutdown the server
- Type `help` to see available commands
- Press Ctrl+C as a fallback to stop the server

### Generating Sitemap

#### Windows:
```bash
scripts\generate_sitemap.cmd
```

#### Linux/Unix/Mac:
```bash
./scripts/generate_sitemap.sh
```

#### Direct Python:
```bash
python utils/sitemap/
```

### Packaging the Site

The package script runs a complete build pipeline with validation:

```bash
# GAZ Tank
scripts\package.cmd

# Windows
scripts\package.cmd

# Linux/Mac
./scripts/package.sh

# Or directly as a module
python -m package
```

The package script pipeline:
1. **Pre-flight Validation**: Run GZLint checks on HTML/CSS/JS files
2. **Markdown Conversion**: Convert documentation to HTML for web viewing
3. **Sitemap Generation**: Create fresh sitemap.xml
4. **Orphan Cleanup**: Remove outdated files from previous packages
5. **File Copying**: Copy only modified/new files from src to publish/staging
6. **Archive Creation**: Create timestamped zip in publish/packages
7. **Backup Management**: Keep the last 5 package backups

### Complete Site Build

Run the complete pipeline from start to finish with a single command:

```bash
# Windows
scripts\gzbuild.cmd -e dev

# Linux/Mac
./scripts/gzbuild.sh -e dev
```

This executes the full pipeline in order:
1. **clean** - Identify orphaned files in target environment (no deletion by default)
2. **compose** - Generate source content from templates
3. **setup --force** - Apply site configuration and regenerate config-driven files
4. **gzlint** - Run linting checks on all content
5. **normalise** - Normalize markdown file formatting
6. **generate** - Generate fresh content files
7. **sitemap** - Generate sitemap.xml
8. **toc** - Generate table of contents
9. **package** - Sync, minify, and archive site files
10. **deploy** - Deploy to target environment

Perfect for a complete site rebuild and deployment.

**Note:** The clean step identifies orphaned files but doesn't delete them by default. Use `scripts\gzbuild.cmd -e dev --clean-orphaned` or `--clean-all` separately if you need to remove files (requires confirmation prompt).

### Deploying to FTP Server

#### First-time setup

1. Copy the configuration template:
   ```bash
   copy config\deploy.example.toml config\deploy.toml
   ```

2. Edit `config/deploy.toml` with your FTP details:
   ```toml
   [ftp]
   server = "ftp.example.com"
   port = 21
   use_ftps = true
   username = "your-username"
   password = "your-password"
   target_dir = "/public_html"
   
   # Optional: Upload subdirectory configuration
   upload_subdir_fmt = "%Y%m%d_%H%M%S_%j"  # Timestamp format
   upload_subdir_postfix_len = 5            # Random postfix length (1-10)
   ```

#### Deploy

```bash
# GAZ Tank
scripts\deploy.cmd

# GAZ Tank
./scripts/deploy.sh

# GAZ Tank
python utils/deploy/
```

The deployment script will:
1. Load FTP configuration from config/deploy.toml
2. Find the latest package in publish/packages/
3. Check if package is older than source files
4. Offer to run package script first if sources are newer
5. Show confirmation prompt with package details
6. Create timestamped upload subdirectory on server (with random postfix)
7. Upload via FTPS (or FTP) with real-time progress bar
8. Display final upload location with full path

#### Configuration Options
- `port`: FTP server port (default: 21)
- `use_ftps`: Set to `true` for secure FTPS, `false` for regular FTP
- `upload_subdir_fmt`: Python strftime format for subdirectories (default: "%Y%m%d_%H%M%S_%j")
  - Examples: "%Y%m%d" → 20251019, "%Y-%m-%d_%H%M" → 2025-10-19_1430
  - Set to "" to disable subdirectory creation
- `upload_subdir_postfix_len`: Length of random alphanumeric postfix (1-10, default: 5)
- Common ports: 21 (FTP/FTPS), 990 (implicit FTPS)

#### Upload Organization
Files are uploaded to timestamped subdirectories for better organization:
```
/public_html/20251019_143025_292_a7k3x/package_20251019_143012.zip
             └─ timestamp ──┘ └postfix┘
```

## Adding Content

### Creating a New Page

1. Create a new HTML file in `src/content/`:
   ```html
   <!-- src/content/my_new_page.html -->
   
   <!-- Optional: Add hashtags for categorization -->
   <div data-hashtags="category, topic, keyword"></div>
   
   <h2>My New Page</h2>
   <p>Content goes here...</p>
   
   <!-- Add h2, h3, and h4 headings for automatic TOC generation -->
   <h2>Major Section</h2>
   <p>Major section content...</p>
   
   <h3>Section 1</h3>
   <p>Section content...</p>
   
   <h4>Subsection 1.1</h4>
   <p>Subsection content...</p>
   
   <h3>Section 2</h3>
   <p>More content...</p>
   
   <!-- Category headers ending with colon will be excluded from TOC -->
   <h3>Category:</h3>
   <p>This heading won't appear in the TOC because it ends with ":"</p>
   ```

2. Add a link in `src/index.html` sidebar:
   ```html
   <li>
       <a href="#" data-content="my_new_page">My New Page</a>
   </li>
   ```

**Note:** h2, h3, and h4 headings are automatically extracted and added to the page's Table of Contents. H2 sections with h3/h4 children and h3 sections with h4 children are collapsible in the TOC. Headings ending with colon (:) are excluded from TOC to avoid category header clutter. The TOC has two separate sections: "Contents" (for headings) and "Navigation" (for child pages), each independently collapsible.

### Creating Nested Pages

For multi-level navigation, wrap items with `has-children` class:

```html
<li class="has-children">
    <div class="nav-item-wrapper">
        <a href="#" data-content="parent_page">Parent Page</a>
        <button class="nav-toggle" aria-label="Toggle submenu">▼</button>
    </div>
    <ul class="nav-level-2">
        <li>
            <a href="#" data-content="child_page">Child Page</a>
        </li>
    </ul>
</li>
```

## Direct Linking

Share direct links to any page or specific heading using URL hashes:

### Page Links
```
http://yoursite.com/#home
http://yoursite.com/#runs_campaign1
http://yoursite.com/#runs_campaign1_mission2_part1
```

### Heading Links (Deep Linking)
```
http://yoursite.com/#runs_campaign1_mission3:introduction
http://yoursite.com/#runs_campaign1_mission3:game-settings
```

Format: `#page-name:heading-id` where heading-id is auto-generated from heading text (lowercase, hyphens, special chars removed).

## Technical Details

### Technologies Used
- **HTML5** - Semantic markup
- **CSS3** - Grid, Flexbox, custom properties
- **Vanilla JavaScript** - No frameworks
- **Python** - Deployment automation and dev server

### Browser Support
- Modern browsers (Chrome, Firefox, Edge, Safari)
- CSS Grid and Flexbox required
- ES6+ JavaScript (async/await, arrow functions)

### Key Features Implementation

#### CSS Grid Layout
```css
body {
    display: grid;
    grid-template-rows: auto 1fr auto;  /* header, main, footer */
}

.main-container {
    display: grid;
    grid-template-columns: 250px 1fr;  /* sidebar, content */
}
```

#### Hash Routing
```javascript
window.addEventListener('hashchange', function() {
    const contentKey = window.location.hash.slice(1);
    loadContent(contentKey);
});
```

#### Table of Contents Generation
The TOC is automatically generated with a two-column layout:
- Left column: Contains "Contents" and "Navigation" sections
- Right column: Contains the master collapse button

Content Sources:
- **Contents Section**: h2, h3, and h4 headings from current page content
- **Navigation Section**: Child pages from navigation hierarchy (excludes current page)

Features:
- Three levels of collapsibility:
  1. Master TOC collapse (button in right column)
  2. Contents section collapse (independent)
  3. Navigation section collapse (independent)
- H2 sections with h3/h4 children and h3 sections with h4 children are collapsible (▾/▸ arrows)
- Visual ellipsis indicator (···) when TOC is collapsed
- Clickable ellipsis to re-expand TOC
- Smart defaults: Contents expanded by default, Navigation collapsed unless no Contents
- State persists per page per section using sessionStorage
- Smooth scroll to heading anchors with deep linking support
- Automatically generates IDs for all h2, h3, and h4 headings
- Excludes headings ending with colon (:) from TOC (useful for category headers)
- Sub-page links trigger navigation

#### Schema.org Breadcrumbs
```html
<nav aria-label="Breadcrumb">
    <ol itemscope itemtype="https://schema.org/BreadcrumbList">
        <li itemprop="itemListElement" itemscope 
            itemtype="https://schema.org/ListItem">
            <a href="#" itemprop="item">
                <span itemprop="name">Home</span>
            </a>
            <meta itemprop="position" content="1">
        </li>
    </ol>
</nav>
```

## File Naming Conventions

Content files use descriptive names with underscores for hierarchy:
- `mods.html` - Top-level page
- `mods_7_days_to_die.html` - Child page
- `runs_campaign1_mission2_part1.html` - Deeply nested page

**Note:** The `Z0*_` prefix convention was removed for cleaner, more descriptive filenames.

## Customization

### Colors and Theming

The site uses a configuration-driven color system. Edit `config/site.toml` to customize colors:

```toml
[theme]
# Sidebar Colors - Navigation sidebar
sidebar_background_color = "#062323"
sidebar_highlight_background_color = "#0066CC"
sidebar_hover_background_color = "#35A2A2"

# Content Colors - Main content area
content_text_color = "#FFFFFF"
content_background_color = "#0A3A3A"

# Global Link Colors - All link elements
link_text_color = "#0066CC"
link_visited_text_color = "#6F42C1"
link_hover_text_color = "#0052A3"

# Text Colors - General typography
body_text_color = "#212529"
muted_text_color = "#6C757D"

[seo]
keywords = "gaming, mods, campaigns, 7 days to die, game walkthroughs"
robots_directive = "index, follow"
canonical_base = "https://mygaztank.com/"
```

After updating colors, run the setup script to apply changes:
```bash
python utils/setup/setup_site.py -e dev --force
```

This automatically generates CSS variables and updates all relevant files.

### Sidebar Width

```css
.main-container {
    grid-template-columns: 250px 1fr;  /* Change 250px */
}
```

### Package Backup Count

Edit `utils/package/packager.py`:
```python
cleanup_old_backups(packages_dir, max_backups=5)  # Change 5
```

### Configuration Management

The site uses `config/site.toml` (TOML format) as the single source of truth for all configuration. Key features:

- **Descriptive color names**: `brand_button_color` instead of ambiguous `primary_color`
- **Comment preservation**: Setup script preserves user comments in configuration
- **Force-apply mode**: `--force-apply` applies current config without prompts
- **Automatic backup**: Configuration changes are automatically backed up
- **SEO configuration**: Keywords, robots directive, canonical URLs all configurable
- **Cross-platform**: Works on Windows (.cmd) and Linux/Unix (.sh) systems
- **Configuration tracking**: `dev/00TODO/CONFIG_DRIVEN_INDEX.md` documents what's config-driven vs hardcoded

### Adding Hashtags to Content

Add an empty div with `data-hashtags` attribute anywhere in your content file:
```html
<div data-hashtags="gaming, mods, 7DaysToDie"></div>
```

Hashtags will automatically:
- Display at the bottom of the content area
- Render with `#` prefix (e.g., #gaming, #mods)
- Appear right-aligned in golden yellow (#FFC845)
- Show in a compact, minimal-height area with subtle divider

## Recent Updates

### October 2025

#### TOC Enhancements
- **H2 Support**: Table of Contents now includes h2 headings as top-level items
- **Smart Filtering**: Headings ending with colon (:) are automatically excluded from TOC
- **Three-Level Hierarchy**: Supports h2 > h3 > h4 nesting with proper indentation

#### Configuration System
- **SEO Meta Tags**: Added configurable `keywords` and `robots_directive` fields
- **JSON-LD Updates**: Description field now pulls from configuration
- **Config Documentation**: New `dev/00TODO/CONFIG_DRIVEN_INDEX.md` tracks what's config-driven

#### GZLint Improvements
- **HTML Validation**: Detects malformed tags (mismatched open/close tags)
- **Subdirectory Support**: Recursively processes all HTML files including nested folders
- **H1 Validation**: Checks for missing h1 tags and duplicate h1 tags per file

#### Documentation
- **SEO Guide**: Expanded `docs/SEO_IMPLEMENTATION.md` with analytics configuration examples
- **Analytics Placeholders**: Documented Plausible, Google Analytics 4, and Matomo integration

## License

© 2025 GAZ Tank. All rights reserved.

## Contributing

This is a personal project. Feel free to fork and adapt for your own use.
