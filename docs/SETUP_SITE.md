# 🚀 GAZ Website System: Generic Content Site - Quick Start Guide

## Setup your own!

This is a generic, configuration-driven website template that can be easily customized for various content types: gaming sites, blogs, documentation, portfolios, knowledge bases, and more!

---

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Initial Setup](#initial-setup)
- [Configuration](#configuration)
- [Customization Guide](#customization-guide)
- [File Structure](#file-structure)
- [Development Tools](#development-tools)
- [Deployment](#deployment)
- [License](#license)

---

## ✨ Features

### Core Features
- ✅ **Single-Page Application (SPA)** - Fast, seamless navigation
- ✅ **Fully Responsive** - Mobile-first design
- ✅ **Configuration-Driven** - Easy customization without code changes
- ✅ **SEO Optimized** - Structured data, meta tags, sitemap generation
- ✅ **Performance Optimized** - Compression, minification, lazy loading
- ✅ **Accessibility (a11y)** - WCAG 2.1 AA compliant
- ✅ **Security Headers** - CSP, HSTS, XSS protection
- ✅ **Theme Support** - CSS variables for easy styling

### Built-in Tools
- 🛠️ **Setup Wizard** - Interactive configuration (modular architecture)
- 🔍 **GZLint** - HTML/JS linter for code quality (automatic pre-build validation)
- 🗺️ **Sitemap Generator** - Automatic SEO sitemap (integrated into build pipeline)
- 📦 **Build System** - Minification and packaging with validation
- 🚀 **Deployment Tools** - Automated deployment scripts (Windows CMD & Linux Bash)

### Advanced Features
- Dynamic table of contents (h2, h3, h4 headings with auto-generated IDs)
- Smart TOC filtering (excludes headings ending with colon)
- Breadcrumb navigation
- Collapsible sidebar
- Keyboard navigation support
- Image lazy loading
- Responsive images with srcset
- Session state persistence

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (for build tools and setup wizard)
- **Web server** (Apache, Nginx, or Python's built-in server)
- **Git** (optional, for cloning)

### 1. Clone or Download

```bash
git clone https://github.com/yourusername/your-site.git
cd your-site
```

Or download and extract the ZIP file.

### 2. Run Setup Wizard

#### Windows
```cmd
scripts\setup_site.cmd
```

#### Linux/Mac
```bash
./scripts/setup_site.sh
```

#### Force Configuration (skip prompts, use config file only):
```cmd
# Windows
scripts\setup_site.cmd --force-apply
```

```bash
# Linux/Mac
./scripts/setup_site.sh --force
```

The wizard will ask you for:
- Site name and tagline
- **Domain name** (e.g., `mydomain.com` - without https://)
- Brand colors
- Logo filenames
- Feature preferences
- SEO and analytics settings

**Important:** The domain you enter here will be used throughout the site for:
- Canonical URLs for SEO
- Sitemap generation  
- Social media meta tags
- All internal URL references

**The setup wizard automatically updates ALL files** including:
- `src/index.html` (meta tags, canonical URLs, site titles)
- `src/js/app.js` (dynamic URL generation)
- `src/sitemap.xml` (all sitemap URLs)
- `src/robots.txt` (sitemap URL reference)  
- `src/humans.txt` (site URL)
- `utils/sitemap/` (base URL configuration)
- `config/site.toml` (domain configuration)
- `src/css/variables.css` (CSS theme variables)
- Documentation files (branding references)

### 3. Add Your Content

1. **Add your logo images** to `src/images/`:
   - `site_logo_256x256.webp` (desktop)
   - `site_logo_75x75.webp` (mobile)
   - `site_favicon_32x32.webp`
   - `site_favicon_16x16.webp`

2. **Create content files** in `src/content/`:
   - Create HTML files (e.g., `about.html`, `blog_post1.html`)
   - Use the template provided below

3. **Update navigation** in `src/index.html`:
   - Edit the sidebar navigation structure
   - Add links to your content pages

### 4. Test Locally

#### Windows
```cmd
scripts\server.cmd
```

#### Linux/Mac
```bash
./scripts/server.sh
```

Visit `http://localhost:7190` in your browser (default port).

### 5. Build and Deploy

#### Windows
```cmd
# Package for production (includes validation & sitemap generation)
scripts\package.cmd

# Deploy to your server (includes sitemap generation & packaging)
scripts\deploy.cmd
```

#### Linux/Mac
```bash
# Package for production
./scripts/package.sh

# Deploy to your server
./scripts/deploy.sh
```

The packaging workflow automatically:
1. ✅ Runs code validation (GZLint)
2. ✅ Generates sitemap (if validation passes)
3. ✅ Cleans orphaned files from staging
4. ✅ Copies modified files
5. ✅ Minifies CSS and JavaScript
6. ✅ Creates timestamped archive

---

## 🔧 Initial Setup

### Step-by-Step Configuration

#### 1. Run Setup Wizard

The setup wizard (`scripts\setup_site.cmd`) will guide you through configuration:

```
============================================
  SITE SETUP WIZARD
============================================

1. Basic Site Information
   - Site name: My Awesome Site
   - Tagline: Your Content Hub
   - Domain: example.com

2. Theme Colors
   - Primary color: #E58822
   - Hover color: #d47a1a

3. Images & Branding
   - Logo files
   - Favicon files

4. Features
   - Enable/disable features

5. SEO & Analytics
   - Google verification
   - Analytics integration
```

##### Setup Wizard Modes:
- **Interactive mode** (default): Prompts for all settings with current values as defaults
- **Force mode** (`--force` or `--force-apply`): Applies config file settings without prompts
- **Help** (`--help`): Shows usage information and available options

The setup wizard uses a **modular architecture** with separate components for:
- UI output formatting
- Input validation
- Configuration file I/O
- User interaction prompts
- File generation (CSS, HTML updates)
- Backup management

#### 2. Review Generated Files

After setup, check these files:

**`config/site.toml`** - Main configuration
```ini
[site]
name = My Awesome Site
domain = example.com
primary_color = #E58822
...
```

**`src/css/variables.css`** - CSS variables
```css
:root {
    --color-primary: #E58822;
    --bg-main: #0A3A3A;
    --text-primary: #E0E0E0;
    ...
}
```

#### 3. Customize Styling

Edit `src/css/styles.css` to use CSS variables:

```css
/* Before (hardcoded) */
body {
    background-color: #0A3A3A;
    color: #E0E0E0;
}

/* After (using variables) */
body {
    background-color: var(--bg-main);
    color: var(--text-primary);
}
```

#### 4. Add Your Logo

Place your logo files in `src/images/`:

- **256x256** - Desktop version
- **75x75** - Mobile version  
- **32x32** - Favicon
- **16x16** - Small favicon

**Tip:** Use the `create_responsive_images` script to generate sizes:

```cmd
# Windows
dev\create_responsive_images.cmd
```

```bash
# Linux/Mac
./dev/create_responsive_images.sh
```

#### 5. Create Content Pages

Create HTML files in `src/content/`:

##### Example: `src/content/about.html`

```html
<div data-hashtags="about, info">
    <h2>About Us</h2>
    <p>Welcome to our site! This is the about page.</p>
    
    <h3>Our Mission</h3>
    <p>We strive to provide great content...</p>
</div>
```

#### 6. Update Navigation

Edit the sidebar in `src/index.html`:

```html
<nav id="sidebar">
    <ul class="nav-level-1">
        <li>
            <a href="#" data-content="home">Home</a>
        </li>
        <li>
            <a href="#" data-content="about">About</a>
        </li>
        <li class="has-children">
            <div class="nav-item-wrapper">
                <a href="#" data-content="blog">Blog</a>
                <button class="nav-toggle">▼</button>
            </div>
            <ul class="nav-level-2">
                <li><a href="#" data-content="blog_post1">First Post</a></li>
                <li><a href="#" data-content="blog_post2">Second Post</a></li>
            </ul>
        </li>
    </ul>
</nav>
```

---

## ⚙️ Configuration

### Configuration File: `config/site.toml`

All site settings are centralized in this file.

#### Site Section

```ini
[site]
name = My Site Name
tagline = My Site Tagline
short_name = MySite
domain = example.com
description = Site description for SEO
author = Your Name
```

#### Theme Section

```ini
[theme]
primary_color = #E58822
primary_color_hover = #d47a1a
background_main = #0A3A3A
text_primary = #E0E0E0
text_link = #80D0D0
```

#### Features Section

```ini
[features]
enable_breadcrumbs = true
enable_toc = true
enable_lazy_loading = true
enable_sidebar_toggle = true
```

#### SEO Section

```ini
[seo]
google_site_verification = your-code-here
canonical_base = https://example.com/
keywords = "gaming, mods, tutorials, your keywords"
robots_directive = "index, follow"
```

**Note:** SEO keywords and robots directive are automatically applied to meta tags in `index.html`.

#### Analytics Section

```ini
[analytics]
plausible_domain = example.com
google_analytics_id = GA-XXXXXXX
matomo_url = ""
matomo_site_id = ""
```

**Note:** Analytics configuration is documented in `docs/SEO_IMPLEMENTATION.md`.

### Re-running Setup

To reconfigure your site (including changing the domain):

```cmd
# Windows
scripts\setup_site.cmd
```

```bash
# Linux/Mac
./scripts/setup_site.sh
```

The wizard will detect existing configuration and ask if you want to reconfigure.

#### Common scenarios:
- **Changing domain:** Run the wizard and enter your new domain when prompted
- **Moving from development to production:** Run wizard with your live domain
- **Updating branding:** Change colors, site name, or other settings

**Note:** The setup wizard is **fully automated** and updates all domain and branding references:
- `config/site.toml` (main configuration)
- `src/css/variables.css` (CSS theme variables)
- `src/index.html` (meta tags, titles, canonical URLs)
- `src/js/app.js` (dynamic URL generation)  
- `src/sitemap.xml` (SEO sitemap URLs)
- `src/robots.txt` and `src/humans.txt` (domain references)
- `utils/sitemap/` (base URL configuration)
- Documentation files (branding updates)

**The setup wizard is idempotent** - you can run it multiple times safely to:
- Change your domain from development to production
- Update site branding (name, colors, description)
- Modify feature settings
- Switch between different configurations

**No manual updates needed!** The wizard handles everything automatically.

---

## 🎨 Customization Guide

### Theme Customization

#### Using CSS Variables

The setup wizard generates `src/css/variables.css` with all your theme colors and settings.

##### Example: Change button color

```css
/* In styles.css */
button {
    background-color: var(--color-primary);
    color: white;
}

button:hover {
    background-color: var(--color-primary-hover);
}
```

#### Color Scheme

Edit `config/site.toml` and re-run setup:

```ini
[theme]
primary_color = #3498db       # Change to blue
background_main = #1a1a2e     # Dark blue background
text_link = #74b9ff           # Light blue links
```

Then run:
```cmd
# Windows
scripts\setup_site.cmd --force-apply
```

```bash
# Linux/Mac
./scripts/setup_site.sh --force
```

### Content Templates

#### Basic Content Page

```html
<div data-hashtags="tutorial, guide">
    <h2>Page Title</h2>
    <p>Introduction paragraph...</p>
    
    <h3>Section 1</h3>
    <p>Section content...</p>
    
    <h3>Section 2</h3>
    <p>More content...</p>
</div>
```

#### Content with Images

```html
<div>
    <h2>Gallery Page</h2>
    
    <img src="../images/photo1.webp" 
         alt="Description"
         width="800" 
         height="600"
         loading="lazy">
    
    <p>Image caption or description...</p>
</div>
```

#### Content with Code Blocks

```html
<div>
    <h2>Tutorial</h2>
    
    <h3>Installation</h3>
    <pre><code>npm install package-name</code></pre>
    
    <h3>Usage</h3>
    <pre><code>const example = require('package-name');
example.doSomething();</code></pre>
</div>
```

### Navigation Structure

#### Flat Navigation

```html
<ul class="nav-level-1">
    <li><a href="#" data-content="welcome">Welcome</a></li>
    <li><a href="#" data-content="about">About</a></li>
    <li><a href="#" data-content="contact">Contact</a></li>
</ul>
```

#### Hierarchical Navigation

```html
<ul class="nav-level-1">
    <li class="has-children">
        <div class="nav-item-wrapper">
            <a href="#" data-content="docs">Documentation</a>
            <button class="nav-toggle">▼</button>
        </div>
        <ul class="nav-level-2">
            <li><a href="#" data-content="docs_getting_started">Getting Started</a></li>
            <li class="has-children">
                <div class="nav-item-wrapper">
                    <a href="#" data-content="docs_api">API Reference</a>
                    <button class="nav-toggle">▼</button>
                </div>
                <ul class="nav-level-3">
                    <li><a href="#" data-content="docs_api_functions">Functions</a></li>
                    <li><a href="#" data-content="docs_api_classes">Classes</a></li>
                </ul>
            </li>
        </ul>
    </li>
</ul>
```

#### 🎯 Default Page Configuration

The site automatically loads the **first navigation item** when visitors arrive. To change what loads initially:

1. **Reorder navigation items** in `src/index.html`
2. **Move your desired default page** to the first `<li>` position
3. **No code changes needed** - the app detects the first item automatically

**Example:** To make "About" the default page:
```html
<ul class="nav-level-1">
    <li><a href="#" data-content="about">About</a></li>  <!-- Now loads first -->
    <li><a href="#" data-content="home">Home</a></li>
    <li><a href="#" data-content="contact">Contact</a></li>
</ul>
```

---

## 📁 File Structure

```
your-site/
├── config/
│   └── site.toml                # Main configuration
├── docs/
│   ├── SETUP_SITE.md            # This file
│   ├── RESPONSIVE_IMAGES.md     # Image guide
│   ├── SEO_IMPLEMENTATION.md    # SEO & analytics documentation
│   └── DESIGN_RULES.md          # Design principles
├── src/
│   ├── css/
│   │   ├── styles.css           # Main stylesheet
│   │   └── variables.css        # CSS variables (auto-generated)
│   ├── js/
│   │   └── app.js               # Main JavaScript
│   ├── images/
│   │   ├── site_logo_256x256.webp
│   │   ├── site_logo_75x75.webp
│   │   └── *.webp               # Your images
│   ├── content/
│   │   ├── home.html            # Home page content
│   │   └── *.html               # Your content pages
│   ├── index.html               # Main HTML file
│   ├── robots.txt               # SEO robots file
│   ├── sitemap.xml              # Auto-generated sitemap
│   ├── humans.txt               # Credits
│   └── .htaccess                # Apache configuration
├── utils/
│   ├── setup/
│   │   ├── __init__.py          # Setup package init
│   │   ├── setup_site.py        # Setup wizard (main)
│   │   ├── ui_helpers.py        # ANSI colors & printing
│   │   ├── validators.py        # Input validation
│   │   ├── backup_manager.py    # File backup & cleanup
│   │   ├── config_io.py         # TOML config I/O
│   │   ├── user_interaction.py  # Interactive prompts
│   │   └── file_generators.py   # CSS/HTML generation
│   ├── sitemap module      # Sitemap generator
│   ├── package.py               # Build system with validation
│   ├── deploy module                # Deployment script
│   ├── gzserve module               # Local dev server
│   └── create_responsive_images.py
├── dev/
│   ├── 00TODO/
│   │   └── CONFIG_DRIVEN_INDEX.md  # Config-driven items documentation
│   ├── gzlint/
│   │   ├── gzlint.py            # Old linter (deprecated, kept for reference)
│   │   └── GZ_LINT_RULES.md     # Linter rules documentation
│   ├── create_responsive_images.cmd  # Windows launcher
│   ├── create_responsive_images.sh   # Linux/Mac launcher
│   └── create_responsive_images.py   # Image generator
├── publish/
│   ├── staging/                 # Staging directory (build output)
│   ├── packages/                # Timestamped ZIP archives
│   └── backups/                 # Configuration backups
├── setup_site.cmd               # Setup wizard launcher (Windows)
├── package.cmd                  # Build launcher (Windows)
├── deploy.cmd                   # Deploy launcher (Windows)
├── deploy.sh                    # Deploy script (Linux/Mac)
├── gzlint.cmd                   # Linter launcher (Windows)
├── server.cmd                   # Dev server launcher (Windows)
├── generate_sitemap.cmd         # Sitemap generator (Windows)
└── README.md                    # Project README
```

---

## 🛠️ Development Tools

### 1. Setup Wizard

Interactive configuration tool:

```cmd
# Windows
scripts\setup_site.cmd
```

```bash
# Linux/Mac
./scripts/setup_site.sh
```

### 2. Code Linter (GZLint)

Check HTML and JavaScript quality:

```cmd
# Windows
scripts\gzlint.cmd
```

```bash
# Linux/Mac
./scripts/gzlint.sh
```

Checks for:
- HTML structure validation (malformed tags, mismatched closing tags)
- Heading hierarchy (h1, h2, h3, h4) - missing h1, duplicate h1
- Console.log statements in JavaScript
- Processes all files recursively including subdirectories
- Code quality issues

### 3. Sitemap Generator

Generate SEO sitemap:

```cmd
# Windows
scripts\generate_sitemap.cmd
```

```bash
# Linux/Mac
./scripts/generate_sitemap.sh
```

Auto-generates `src/sitemap.xml` from your content.

### 4. Build System

Package for production:

#### Windows
```cmd
scripts\package.cmd
```

#### Linux/Mac
```bash
./scripts/package.sh
```

#### Build Pipeline Features:
- ✅ **Pre-flight validation** - Runs GZLint before packaging
- ✅ **Automatic sitemap** - Generates sitemap.xml if validation passes
- ✅ **Orphan cleanup** - Removes deleted files from staging
- ✅ **Smart copying** - Only copies modified files
- ✅ **Minification** - Minifies CSS (rcssmin) and JavaScript (rjsmin)
- ✅ **Size reporting** - Shows compression savings
- ✅ **Archiving** - Creates timestamped ZIP in `publish/packages/`
- ✅ **Backup management** - Keeps 4 most recent packages
- ✅ **Exit codes** - Returns proper codes for CI/CD integration

#### Build Process:
```
[Pre-flight] Running validation checks...
  ✓ All validation checks passed

[Pre-flight] Generating sitemap...
  ✓ Sitemap generated successfully

[1/3] Cleaning orphaned files from staging...
  ✓ No orphaned files found

[2/3] Copying files from src to staging...
  ✓ Copied X modified/new files
  ✓ Skipped Y unchanged files
  Minifying CSS and JavaScript...
  ✓ Total: X → Y bytes (Z% reduction)

[3/3] Creating package archive...
  ✓ Backup created with N files

✓ PACKAGING COMPLETED SUCCESSFULLY
```

#### Error Handling:
- If validation fails → packaging aborts
- If sitemap generation fails → packaging aborts
- If validation scripts not found → continues with warning

### 5. Deployment

Deploy to your server:

#### Windows
```cmd
scripts\deploy.cmd
```

#### Linux/Mac
```bash
./scripts/deploy.sh
```

#### Deployment Workflow:
1. Generates sitemap (`sitemap module`)
2. Validates and packages files (`package.py`)
   - Includes validation and sitemap generation
3. Deploys to configured server (`deploy module`)
   - Reads configuration from `deploy.config`
   - Creates backups before deployment
   - Uploads to FTP/SFTP server

#### Configuration:
Create `deploy.config` (not tracked in git):
```ini
[server]
host = ftp.yourserver.com
username = your-username
password = your-password
remote_path = /public_html/
```

### 6. Image Tools

Create responsive image sizes:

```cmd
# Windows
dev\create_responsive_images.cmd
```

```bash
# Linux/Mac
./dev/create_responsive_images.sh
```

Requires [ImageMagick](https://imagemagick.org/) or [Pillow](https://pillow.readthedocs.io/).

---

## 🏗️ Architecture Overview

### Setup Wizard - Modular Design

The setup wizard has been refactored into a modular architecture for better maintainability:

#### Module Structure:
```
utils/setup/
├── __init__.py              # Package exports
├── setup_site.py            # Main orchestrator (~200 lines)
├── ui_helpers.py            # Terminal output formatting (~120 lines)
├── validators.py            # Input validation (~65 lines)
├── backup_manager.py        # Backup & cleanup (~110 lines)
├── config_io.py             # TOML configuration I/O (~400 lines)
├── user_interaction.py      # Interactive prompts (~400 lines)
└── file_generators.py       # CSS/HTML generation (~550 lines)
```

#### Key Features:
- **Separation of concerns** - Each module has a single responsibility
- **Absolute imports** - Supports direct script execution
- **Comment preservation** - Uses `tomlkit` to maintain config file comments
- **Backup system** - Automatic backups before major changes
- **Error handling** - Graceful degradation and clear error messages

#### Running the Setup Wizard:
```cmd
# Windows - Interactive mode (prompts for all settings)
scripts\setup_site.cmd

# Windows - Force mode (uses config file only)
scripts\setup_site.cmd --force-apply

# Windows - Show help
scripts\setup_site.cmd --help
```

```bash
# Linux/Mac - Interactive mode
./scripts/setup_site.sh

# Linux/Mac - Force mode
./scripts/setup_site.sh --force

# Linux/Mac - Show help
./scripts/setup_site.sh --help
```

### Build Pipeline - Validation First

The packaging system now includes **automatic validation and sitemap generation**:

#### Pipeline Stages:
1. **Pre-flight: Validation** (`run_validation()`)
   - Runs `utils/gzlint/`
   - Checks HTML structure and JavaScript quality
   - Aborts packaging if validation fails

2. **Pre-flight: Sitemap** (`generate_sitemap()`)
   - Runs `utils/sitemap/`
   - Generates fresh sitemap.xml
   - Aborts packaging if generation fails

3. **Stage 1: Clean** (`clean_orphaned_files()`)
   - Identifies files in staging not in source
   - Removes orphaned files
   - Cleans empty directories

4. **Stage 2: Copy & Minify** (`package_site()`)
   - Copies only modified files (timestamp comparison)
   - Minifies CSS with rcssmin (optional)
   - Minifies JavaScript with rjsmin (optional)
   - Reports compression savings

5. **Stage 3: Archive** (`backup_previous_package()`)
   - Creates timestamped ZIP in `publish/packages/`
   - Keeps 4 most recent packages
   - Cleans up old archives

#### Exit Codes:
- `0` - Success (all stages passed)
- `1` - Failure (validation, sitemap, or packaging failed)

#### Error Handling:
- Missing validation scripts → Warning + continue
- Validation failure → Abort with error message
- Sitemap failure → Abort with error message
- Missing minification libraries → Skip minification with warning

### Cross-Platform Support

#### Windows
- `setup_site.cmd` → Calls `python utils/setup/setup_site.py`
- `package.cmd` → Calls `python -m package`
- `deploy.cmd` → Calls `python utils/deploy/`
- `gzlint.cmd` → Calls `python utils/gzlint/`

#### Linux/Mac
- `deploy.sh` → Bash script with error checking
- Proper exit code propagation for CI/CD

### Development Workflow

#### Recommended workflow:

#### Windows
```cmd
# 1. Configure site (first time or when changing settings)
scripts\setup_site.cmd

# 2. Create/modify content files in src/content/

# 3. Test locally
scripts\server.cmd

# 4. Check code quality (optional - runs automatically during build)
scripts\gzlint.cmd

# 5. Build for production (includes validation & sitemap)
scripts\package.cmd

# 6. Deploy to server (includes full build pipeline)
scripts\deploy.cmd
```

#### Linux/Mac
```bash
# 1. Configure site (first time or when changing settings)
./scripts/setup_site.sh

# 2. Create/modify content files in src/content/

# 3. Test locally
./scripts/server.sh

# 4. Check code quality (optional - runs automatically during build)
./scripts/gzlint.sh

# 5. Build for production (includes validation & sitemap)
./scripts/package.sh

# 6. Deploy to server (includes full build pipeline)
./scripts/deploy.sh
```

#### CI/CD Integration:
```bash
# In your CI/CD pipeline
./scripts/package.sh
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "Build successful, deploying..."
    ./scripts/deploy.sh
else
    echo "Build failed, aborting deployment"
    exit 1
fi
```

---

## 🚀 Deployment

### Local Testing

#### Windows
```cmd
scripts\server.cmd
```

#### Linux/Mac
```bash
./scripts/server.sh
```

Visit `http://localhost:7190` (default port)

### Production Deployment

#### Option 1: Using Deploy Script

1. Configure deployment in `deploy.config` (not in git):
   ```ini
   [server]
   host = ftp.yourserver.com
   username = your-username
   password = your-password
   remote_path = /public_html/
   ```

2. Run deploy:
   ```bash
   scripts\deploy.cmd
   ```

#### Option 2: Manual Deployment

1. Build production files:
   ```cmd
   # Windows
   scripts\package.cmd
   ```
   
   ```bash
   # Linux/Mac
   ./scripts/package.sh
   ```

2. Upload `publish/staging/` contents to your server via FTP/SFTP

3. Ensure `.htaccess` is uploaded (may be hidden)

**Note:** The build system creates archives in `publish/packages/` for backup purposes. The `publish/staging/` directory contains the actual files to deploy.

### Apache Configuration

The included `.htaccess` provides:
- Gzip/Deflate compression
- Security headers (CSP, HSTS)
- Cache headers for performance
- Browser compatibility fixes

### HTTPS Setup

1. Enable SSL on your server (Let's Encrypt recommended)
2. Update `config/site.toml`:
   ```ini
   [security]
   hsts_enabled = true
   ```
3. Uncomment HSTS in `src/.htaccess`:
   ```apache
   Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
   ```

---

## 📜 License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📞 Support

For issues, questions, or suggestions:

1. Check the documentation in `docs/`
   - `SETUP_SITE.md` - This comprehensive guide
   - `SEO_IMPLEMENTATION.md` - SEO best practices and analytics
   - `RESPONSIVE_IMAGES.md` - Image optimization
   - `DESIGN_RULES.md` - Design principles
2. Review configuration in `config/site.toml`
3. Check config-driven items: `dev/00TODO/CONFIG_DRIVEN_INDEX.md`
4. Run the setup wizard again: `scripts\setup_site.cmd`
5. Create an issue on GitHub

---

## 🎯 Use Cases

This template works great for:

- **Gaming Content Sites** - Mods, guides, campaign runs
- **Documentation Sites** - API docs, user guides, wikis
- **Portfolio Sites** - Projects, case studies, galleries
- **Blog Sites** - Articles, tutorials, news
- **Knowledge Bases** - FAQs, how-tos, resources
- **Community Sites** - Forums, groups, resources

---

## 📝 Recent Updates (October 2025)

### Table of Contents Enhancements
- **H2 heading support** - TOC now includes h2, h3, and h4 headings (was h3, h4 only)
- **Smart filtering** - Headings ending with colon (:) automatically excluded from TOC
- **Auto-generated IDs** - All h2, h3, h4 headings get IDs for deep linking
- **Three-level hierarchy** - Proper h2 > h3 > h4 nesting with collapsible sections

### SEO & Configuration
- **Keywords configuration** - Added `keywords` field to `[seo]` section
- **Robots directive** - Added `robots_directive` field (e.g., "index, follow")
- **Config documentation** - New `dev/00TODO/CONFIG_DRIVEN_INDEX.md` tracks config-driven items
- **SEO documentation** - Expanded `docs/SEO_IMPLEMENTATION.md` with analytics examples

### GZLint Improvements
- **HTML validation** - Detects malformed tags and mismatched closing tags
- **Subdirectory support** - Recursively processes all files including nested folders
- **H1 validation** - Checks for missing h1 tags and duplicate h1 tags

### Documentation
- **Analytics guide** - Comprehensive Plausible, GA4, and Matomo configuration
- **Config reference** - Complete tracking of what's config-driven vs hardcoded

---

## ⚡ Quick Tips

1. **Start with the wizard** - Run `scripts\setup_site.cmd` first for automatic configuration
2. **Run wizard multiple times** - It's safe and updates everything automatically
3. **Use force mode** - Run `scripts\setup_site.cmd --force-apply` to apply config without prompts
4. **Reorder navigation** - The first sidebar item loads automatically, no code changes needed
5. **Use CSS variables** - Makes theme changes easy
6. **Test locally** - Always test before deploying
7. **Validation is automatic** - GZLint runs before every build
8. **Sitemap is automatic** - Generated during build and deploy
9. **Backup regularly** - Build and deploy scripts create automatic backups
10. **Check exit codes** - Build system returns proper codes for CI/CD integration
11. **Cross-platform** - Use `.cmd` files on Windows, `.sh` on Linux/Mac
12. **Check Lighthouse** - Monitor performance scores

---

### Happy building! 🚀
