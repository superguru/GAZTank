# 🛠️ GAZ Tank Developer Environment Setup

This guide covers setting up a complete development environment for working on the GAZ Tank Website System.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Required Software](#required-software)
- [Python Environment Setup](#python-environment-setup)
- [IDE Configuration (VS Code)](#ide-configuration-vs-code)
- [Project Structure for Development](#project-structure-for-development)
- [Development Workflow](#development-workflow)
- [Build Tools](#build-tools)
- [Testing and Validation](#testing-and-validation)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

### Operating System Support
- **Windows 10/11** (with PowerShell 5.1+ or PowerShell Core 7+)
- **Linux** (Ubuntu 20.04+, Debian 10+, or similar)
- **macOS** (10.15+)

### Required Knowledge
- Basic command line usage (PowerShell/Bash)
- HTML, CSS, and JavaScript fundamentals
- Python basics (for build scripts)
- Git version control

---

## 📦 Required Software

### 1. Python 3.11 or Later

**Why:** All build tools, setup wizards, and utilities are written in Python.

#### Windows:
Download from [python.org](https://www.python.org/downloads/)

During installation:
- ✅ Check "Add Python to PATH"
- ✅ Check "Install pip"

Verify installation:
```powershell
python --version
# Should show: Python 3.11.x or later

pip --version
# Should show: pip 23.x or later
```

#### Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-pip python3-venv

# macOS (using Homebrew)
brew install python@3.11

# Verify
python3 --version
pip3 --version
```

### 2. Git

**Why:** Version control for code management and collaboration.

#### Windows:
Download from [git-scm.com](https://git-scm.com/download/win)

#### Linux:
```bash
sudo apt install git  # Ubuntu/Debian
```

#### Mac:
```bash
brew install git
```

Verify:
```bash
git --version
```

### 3. Visual Studio Code (Recommended IDE)

**Why:** Best-in-class support for web development with excellent extensions.

Download from [code.visualstudio.com](https://code.visualstudio.com/)

#### Required VS Code Extensions
Install via Extensions panel (`Ctrl+Shift+X` / `Cmd+Shift+X`):

1. **Python** (`ms-python.python`)
   - Python language support, IntelliSense, debugging
   
2. **Pylance** (`ms-python.vscode-pylance`)
   - Fast Python language server with type checking

3. **HTML CSS Support** (`ecmel.vscode-html-css`)
   - CSS class/id completion in HTML

4. **JavaScript (ES6) code snippets** (`xabikos.JavaScriptSnippets`)
   - ES6 syntax snippets

5. **Path Intellisense** (`christian-kohler.path-intellisense`)
   - Autocomplete for file paths

#### Optional but Recommended Extensions

6. **Live Server** (`ritwickdey.LiveServer`)
   - Quick local development server with live reload
   - Alternative to the built-in Python server

7. **Prettier** (`esbenp.prettier-vscode`)
   - Code formatter for HTML/CSS/JS

8. **GitLens** (`eamodio.gitlens`)
   - Enhanced Git capabilities

9. **TODO Highlight** (`wayou.vscode-todo-highlight`)
   - Highlights TODO/FIXME comments

10. **Markdown All in One** (`yzhang.markdown-all-in-one`)
    - Markdown editing support for documentation

### 4. Web Browser with DevTools

**Required:** Modern browser for testing and debugging.

Recommended browsers:
- **Google Chrome** / **Microsoft Edge** (Chromium-based, best DevTools)
- **Firefox Developer Edition**

---

## 🐍 Python Environment Setup

### 1. Create a Virtual Environment (Optional but Recommended)

Virtual environments isolate project dependencies from system Python.

#### Windows (PowerShell):
```powershell
# Navigate to project root
cd D:\Projects\www\GAZTank

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Linux/Mac:
```bash
# Navigate to project root
cd ~/Projects/GAZTank

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**Note:** When virtual environment is active, you'll see `(venv)` in your prompt.

### 2. Install Required Python Packages

The project includes a `requirements.txt` file with all dependencies:

```bash
# Install all dependencies from requirements.txt
pip install -r requirements.txt
```

This installs:
- **beautifulsoup4** (>=4.12.0) - HTML parsing and manipulation
- **lxml** (>=5.0.0) - Fast XML/HTML parser for BeautifulSoup (performance)
- **tomlkit** (>=0.12.0) - TOML config with comment preservation
- **mistune** (>=3.0.0) - Markdown to HTML conversion
- **tomli** (>=2.0.0) - TOML parsing for Python < 3.11 (fallback)
- **rcssmin** (>=1.1.0) - CSS minification (optional)
- **rjsmin** (>=1.2.0) - JavaScript minification (optional)
- **pyftpdlib** (>=1.5.0) - FTP server for testing deployments (optional)

#### Manual Installation (Alternative)
If you prefer to install packages individually:

```bash
# Core dependencies
pip install beautifulsoup4    # HTML parsing and manipulation
pip install lxml             # Fast XML/HTML parser (performance)
pip install tomlkit          # TOML config with comment preservation
pip install mistune          # Markdown to HTML conversion

# Optional (for minification and testing)
pip install rcssmin          # CSS minification
pip install rjsmin           # JavaScript minification
pip install pyftpdlib        # FTP server for deployment testing
```

#### Quick Install (All at Once)
```bash
pip install beautifulsoup4 lxml tomlkit mistune rcssmin rjsmin pyftpdlib
```

### 3. Verify Python Environment

Run this command to check all dependencies:

```bash
python -c "import bs4, lxml, tomlkit, mistune; print('Core dependencies installed successfully!')"
```

To see installed package versions:
```bash
pip list | grep -E "beautifulsoup4|lxml|tomlkit|mistune|rcssmin|rjsmin|pyftpdlib"
# On Windows PowerShell:
pip list | Select-String "beautifulsoup4|lxml|tomlkit|mistune|rcssmin|rjsmin|pyftpdlib"
```

---

## 🎨 IDE Configuration (VS Code)

### 1. Open Project in VS Code

```bash
# From project root
code .
```

### 2. Configure Python Interpreter

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
2. Type "Python: Select Interpreter"
3. Choose the virtual environment: `./venv/bin/python` or `.\venv\Scripts\python.exe`

### 3. Recommended VS Code Settings

Create/update `.vscode/settings.json` in project root:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "files.encoding": "utf8",
    "files.eol": "\n",
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": true,
        "**/publish/staging": true,
        "**/publish/packages": true,
        "**/publish/backups": true
    },
    "[html]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },
    "[css]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },
    "[javascript]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },
    "[markdown]": {
        "editor.defaultFormatter": "yzhang.markdown-all-in-one",
        "editor.wordWrap": "on"
    },
    "liveServer.settings.root": "/src",
    "liveServer.settings.port": 7190,
    "liveServer.settings.CustomBrowser": "chrome"
}
```

### 4. Create Launch Configuration for Debugging

Create/update `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Development Server",
            "type": "python",
            "request": "launch",
            "module": "gzserve",
            "args": ["-e", "dev"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: Setup Wizard",
            "type": "python",
            "request": "launch",
            "module": "setup",
            "args": ["-e", "dev"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: GZLint",
            "type": "python",
            "request": "launch",
            "module": "gzlint",
            "args": ["-e", "dev"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: Package Site",
            "type": "python",
            "request": "launch",
            "module": "package",
            "args": ["-e", "dev"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: Deploy Site",
            "type": "python",
            "request": "launch",
            "module": "deploy",
            "args": ["-e", "prod"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### 5. Create Tasks Configuration

Create/update `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Dev Server",
            "type": "shell",
            "command": "python",
            "args": ["-m", "gzserve", "-e", "dev"],
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        },
        {
            "label": "Run GZLint",
            "type": "shell",
            "command": "python",
            "args": ["-m", "gzlint", "-e", "dev"],
            "problemMatcher": [],
            "group": {
                "kind": "test",
                "isDefault": true
            }
        },
        {
            "label": "Generate Sitemap",
            "type": "shell",
            "command": "python",
            "args": ["-m", "sitemap", "-e", "dev"],
            "problemMatcher": []
        },
        {
            "label": "Generate TOC",
            "type": "shell",
            "command": "python",
            "args": ["-m", "toc", "-e", "dev"],
            "problemMatcher": []
        },
        {
            "label": "Package Site",
            "type": "shell",
            "command": "python",
            "args": ["-m", "package", "-e", "dev"],
            "problemMatcher": []
        },
        {
            "label": "Build Complete Pipeline",
            "type": "shell",
            "command": "python",
            "args": ["-m", "gzbuild", "-e", "dev"],
            "problemMatcher": []
        }
    ]
}
```

---

## 📂 Project Structure for Development

For a comprehensive directory structure with detailed descriptions, see [PROJECT_STRUCTURE.md](#setup/PROJECT_STRUCTURE).

### Development-Focused Overview:
- **`src/`** - Your main work area (HTML, CSS, JS, content)
- **`utils/`** - Build tools and utilities (modular Python scripts)
- **`dev/`** - Development tools (linter, TODO tracking)
- **`docs/`** - Documentation sources (converted to HTML for site)
- **`config/`** - TOML configuration files
- **`scripts/`** - Cross-platform launcher scripts (.cmd/.sh)
- **`publish/`** - Build outputs (gitignored)
- **`.github/`** - GitHub templates and workflows
- **`venv/`** - Python virtual environment (gitignored)

---

## 🔄 Development Workflow

### Initial Setup

1. **Clone the repository** (if not done already):
   ```bash
   git clone <repository-url> GAZTank
   cd GAZTank
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   # Activate (see platform-specific commands above)
   pip install -r requirements.txt
   ```

3. **Run initial configuration**:
   ```bash
   # Windows
   .\scripts\setup_site.cmd
   
   # Linux/Mac
   ./scripts/setup_site.sh
   ```

4. **Read contribution guidelines** (for contributors):
   ```bash
   # Review these files before making changes
   - CONTRIBUTING.md    # Contribution guidelines
   - LICENSE            # MIT License terms
   - SECURITY.md        # Security policy
   - CHANGELOG.md       # Version history
   ```

### Daily Development Workflow

#### 1. Start Development Server

##### Using Python module directly:
```bash
python -m gzserve
```

##### Using VS Code task:
- Press `Ctrl+Shift+P` → "Tasks: Run Task" → "Start Dev Server"

##### Using launcher script:
```bash
# Windows
.\scripts\gzserve.cmd -e dev

# Linux/Mac
./scripts/gzserve.sh -e dev

# Staging environment with custom port
.\scripts\gzserve.cmd -e staging -p 8080
```

Visit: `http://localhost:7190` (dev) or `http://localhost:7191` (staging)

**Environment Configuration:** Ports and directories are configured in `config/environments.toml`

#### 2. Make Changes

Work on files in the `src/` directory:
- HTML: `src/index.html` and `src/content/*.html`
- CSS: `src/css/styles.css`
- JavaScript: `src/js/app.js`
- Images: `src/images/`

**Note:** In the new pipeline architecture, the server serves from `publish/{environment}/` directories. For development, copy `src/` contents to `publish/dev/` before starting the server.

**Hot Reload:** The server includes no-cache headers for development, so just refresh the browser to see changes.

#### 3. Validate Code

Run GZLint before committing:

```bash
# Using Python directly
python utils/gzlint/

# Using VS Code task
# Press Ctrl+Shift+B (default test task)

# Using launcher script
# Windows: .\scripts\gzlint.cmd
# Linux/Mac: ./scripts/gzlint.sh
```

GZLint checks for:
- HTML structure validation
- Heading hierarchy (h1-h4)
- Malformed/mismatched tags
- JavaScript console.log statements

#### 4. Update Documentation

When editing markdown documentation in `docs/`:

```bash
# Convert markdown to HTML using generate module
python -m utils.generate -e dev

# Or use launcher script
# Windows: .\scripts\generate.cmd -e dev
# Linux/Mac: ./scripts/generate.sh -e dev
```

This converts documentation to HTML in `src/content/setup/` for web viewing.

#### 5. Update Configuration

When changing site configuration in `config/site.toml`:

```bash
# Apply configuration changes (force mode - no prompts)
# Windows
.\scripts\setup_site.cmd -e dev --force

# Linux/Mac
./scripts/setup_site.sh -e dev --force
```

This updates:
- `src/css/variables.css` (CSS theme variables)
- `src/index.html` (meta tags, branding)
- `src/sitemap.xml` (if domain changed)
- Other config-driven files

### Pre-Commit Checklist

Before committing changes:

1. ✅ **Run GZLint**: `python utils/gzlint/`
2. ✅ **Test in browser**: Verify changes work correctly
3. ✅ **Check console**: No JavaScript errors in DevTools
4. ✅ **Validate HTML**: Use browser DevTools or W3C validator
5. ✅ **Update documentation**: If you changed functionality
6. ✅ **Generate sitemap**: If you added/removed pages

---

## 🤝 Contributing to GAZ Tank

### Before You Start

#### Required Reading:
- `CONTRIBUTING.md` - Comprehensive contribution guidelines
- `SECURITY.md` - Security policy and vulnerability reporting
- `LICENSE` - MIT License terms
- `CHANGELOG.md` - Version history and changelog format

### Contribution Process

#### 1. Report Issues
Use GitHub Issues with the appropriate template:
- **Bug Reports:** `.github/ISSUE_TEMPLATE/bug_report.md`
- **Feature Requests:** `.github/ISSUE_TEMPLATE/feature_request.md`

#### 2. Fork and Branch
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/GAZTank.git
cd GAZTank

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

#### 3. Make Changes
Follow our coding standards:
- **Python:** PEP 8 style guide
- **JavaScript:** Airbnb JavaScript Style Guide (adapted)
- **HTML/CSS:** See `docs/DESIGN_RULES.md`
- **Commits:** Conventional Commits format

#### 4. Test Your Changes
```bash
# Run all tests
python -m gzlint -e dev

# Test in browser
python -m gzserve -e dev
# Visit http://localhost:7190

# Build package to ensure no build errors
python -m package -e dev
```

#### 5. Submit Pull Request
Use the PR template (`.github/pull_request_template.md`):
- Clear description of changes
- Link to related issues
- Confirm testing checklist
- Note any breaking changes

### Coding Standards

#### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** feat, fix, docs, style, refactor, test, chore

##### Example:
```
feat(nav): add breadcrumb navigation component

Implements breadcrumb navigation for better UX on deep pages.
Uses CSS Grid for responsive layout.

Closes #123
```

#### Code Style
- **Python:** 4 spaces, max line 100 characters
- **JavaScript:** 2 spaces, semicolons required
- **HTML/CSS:** 2 spaces, attributes double-quoted
- See `.editorconfig` for full rules

### Security

#### Found a vulnerability?
- **DO NOT** open a public issue
- Email: [See SECURITY.md for contact details]
- Include: Description, steps to reproduce, impact assessment

---

## 🔨 Build Tools

### Package for Production

Creates a production-ready build with validation and minification:

```bash
# Using Python directly
python -m package

# Using launcher script
# Windows: .\scripts\package.cmd
# Linux/Mac: ./scripts/package.sh
```

#### Build pipeline:
1. Pre-flight validation (GZLint)
2. Markdown to HTML conversion
3. Sitemap generation
4. Orphaned file cleanup
5. File copying with modification checking
6. CSS/JS minification (if libraries installed)
7. ZIP archive creation
8. Backup management (keeps last 3 packages)

#### Output:
- Staging: `publish/staging/` (ready to deploy)
- Package: `publish/packages/package_YYYYMMDD_HHMMSS.zip`

### Generate Sitemap

```bash
python utils/sitemap/

# Or use launcher
# Windows: .\scripts\generate_sitemap.cmd
# Linux/Mac: ./scripts/generate_sitemap.sh
```

### Clean Environment

Remove orphaned files or completely clean an environment:

```bash
# Identify orphaned files (no deletion - default mode)
# Windows
.\scripts\gzclean.cmd -e dev

# Linux/Mac
./scripts/gzclean.sh -e dev

# Preview what would be removed (dry-run)
.\scripts\gzclean.cmd -e dev --dry-run

# Remove orphaned files only (requires confirmation)
.\scripts\gzclean.cmd -e dev --clean-orphaned

# Remove orphaned files without confirmation
.\scripts\gzclean.cmd -e dev --clean-orphaned --force

# Remove ALL files from environment (requires confirmation)
.\scripts\gzclean.cmd -e dev --clean-all

# Remove ALL files without confirmation (use with caution!)
.\scripts\gzclean.cmd -e dev --clean-all --force
```

#### Clean Module Features (v1.2 - November 2025):
- **Identify-Only Default**: Default mode identifies orphaned files but doesn't delete them
- **Clean Orphaned Mode**: `--clean-orphaned` removes only orphaned files (files in environment but not in source)
- **Clean-All Mode**: `--clean-all` removes ALL files from environment directory
- **Safety Confirmation**: Both clean modes prompt for 'yes' confirmation unless `--force` is used
- **Dry-Run Preview**: `--dry-run` shows what would be deleted without actually deleting
- **Automatic Backup Cleanup**: Removes old deploy backup directories (`.YYYYMMDD_*`) every run

#### Use Cases:
- **Planning**: Default mode identifies what needs cleaning without making changes
- **Regular cleaning**: Use `--clean-orphaned` to remove stale files after restructuring `src/`
- **Fresh rebuild**: Use `--clean-all` before regenerating entire environment
- **Automation**: Add `--force` flag for CI/CD pipelines (skips confirmation prompts)
- **Troubleshooting**: Preview changes with `--dry-run` before committing to cleanup

**⚠️ WARNING:** `--clean-all --force` is destructive and irreversible! Always preview with `--dry-run` first.

### Build Complete Pipeline

Runs the complete pipeline from start to finish:

```bash
# Windows
.\scripts\gzbuild.cmd -e dev

# Linux/Mac
./scripts/gzbuild.sh -e dev
```

This executes all pipeline stages in order:
1. `clean` (identify orphaned files - no deletion by default)
2. `compose` (generate source content from templates)
3. `setup --force` (apply configuration)
4. `gzlint` (run linting checks)
5. `normalise` (normalize markdown formatting)
6. `generate` (generate content)
7. `sitemap` (generate sitemap.xml)
8. `toc` (generate table of contents)
9. `package` (sync, minify, archive)
10. `deploy` (deploy to environment)

---

## ✅ Testing and Validation

### Manual Testing

1. **Browser Testing:**
   - Test in Chrome/Edge (Chromium)
   - Test in Firefox
   - Test in Safari (macOS)
   - Check mobile responsiveness (DevTools device mode)

2. **Functionality Testing:**
   - Navigation menu (expand/collapse)
   - Sidebar toggle
   - TOC generation and collapsing
   - Deep linking (`#page:heading`)
   - Breadcrumb navigation
   - Lazy image loading
   - Hash routing

3. **Performance Testing:**
   - Open DevTools → Lighthouse
   - Run audit for Performance, Accessibility, SEO
   - Target: 90+ scores in all categories

### Automated Validation

#### GZLint (HTML/JS)
```bash
python utils/gzlint/
```

Validates:
- HTML structure and tag matching
- Heading hierarchy
- JavaScript quality

#### W3C HTML Validator (Optional)
Use online: https://validator.w3.org/nu/
- Upload `src/index.html`
- Check for HTML5 compliance errors

### Browser DevTools Checks

**Console:** No errors or warnings
**Network:** All resources loading (200 status)
**Application:** sessionStorage working correctly

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Python Import Errors

**Problem:** `ModuleNotFoundError: No module named 'bs4'` (or similar)

##### Solution:
```bash
# Ensure virtual environment is activated
# Windows: .\venv\Scripts\Activate.ps1
# Linux/Mac: source venv/bin/activate

# Install missing package
pip install beautifulsoup4

# Or install all requirements
pip install -r requirements.txt
```

#### 2. Server Won't Start

**Problem:** `Address already in use` or port occupied

##### Solution:
```bash
# Use different port (override config)
python -m gzserve -e dev -p 8080

# Or find and kill process on the occupied port
# Windows (replace 7190 with your port)
netstat -ano | findstr :7190
taskkill /PID <process_id> /F

# Linux/Mac (replace 7190 with your port)
lsof -ti:7190 | xargs kill -9

# Or use a different environment (different default port)
.\scripts\gzserve.cmd -e staging  # Uses port 7191
```

#### 3. Permission Denied on Scripts

**Problem:** `./scripts/gzserve.sh: Permission denied`

##### Solution (Linux/Mac):
```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x dev/*.sh
```

#### 4. PowerShell Execution Policy

**Problem:** `cannot be loaded because running scripts is disabled`

##### Solution (Windows):
```powershell
# Set execution policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass
powershell -ExecutionPolicy Bypass -File .\scripts\gzserve.cmd
```

#### 5. CSS/JS Not Minifying

**Problem:** Build works but files not minified

##### Solution:
```bash
# Install optional minification libraries
pip install rcssmin rjsmin

# Verify installation
python -c "import rcssmin, rjsmin; print('Minification libraries installed')"
```

#### 6. Markdown Conversion Fails

**Problem:** `ModuleNotFoundError: No module named 'mistune'`

##### Solution:
```bash
pip install mistune
```

#### 7. TOML Config Errors

**Problem:** `Error: tomlkit library not found`

##### Solution:
```bash
pip install tomlkit
```

---

## 📚 Additional Resources

### Project Documentation
- **Setup Guide:** `docs/SETUP_SITE.md`
- **SEO Implementation:** `docs/SEO_IMPLEMENTATION.md`
- **Responsive Images:** `docs/RESPONSIVE_IMAGES.md`
- **Design Rules:** `docs/DESIGN_RULES.md`
- **Config Reference:** `dev/00TODO/CONFIG_DRIVEN_INDEX.md`
- **GZLint Rules:** `utils/gzlint/GZ_LINT_RULES.md`
- **Security Policy:** `SECURITY.md`
- **Version History:** `CHANGELOG.md`
- **Repo Setup Tracking:** `dev/00TODO/PROFESSIONAL_REPO_SETUP.md`

### Contributing & Community
- **Contribution Guidelines:** `CONTRIBUTING.md` - Read this before making changes
- **Code of Conduct:** See `CONTRIBUTING.md`
- **Bug Reports:** Use `.github/ISSUE_TEMPLATE/bug_report.md`
- **Feature Requests:** Use `.github/ISSUE_TEMPLATE/feature_request.md`
- **Pull Requests:** Follow `.github/pull_request_template.md`
- **License:** MIT License - See `LICENSE` file

### External Resources
- [Python Documentation](https://docs.python.org/3/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Mistune Documentation](https://mistune.lepture.com/)
- [TOML Specification](https://toml.io/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [VS Code Documentation](https://code.visualstudio.com/docs)

---

## 🎓 Learning Path for New Developers

### Week 1: Environment & Basics
1. Set up Python environment and VS Code
2. Install all dependencies
3. Run development server and explore the site
4. Read `SETUP_SITE.md` and `README.md`

### Week 2: Understanding the Codebase
1. Study `src/js/app.js` (routing and navigation)
2. Review `src/css/styles.css` (layout and styling)
3. Understand `config/site.toml` structure
4. Run setup wizard and see what it updates

### Week 3: Build Tools
1. Run GZLint and fix any issues
2. Use the package script and examine output
3. Try markdown to HTML conversion with generate module
4. Modify a config value and use `--force` to apply changes

### Week 4: Making Changes
1. Create a new content page
2. Add navigation menu item
3. Customize colors in configuration
4. Test responsive design

---

## ✨ Quick Command Reference

```bash
# Environment
python -m venv venv              # Create virtual environment
source venv/bin/activate         # Activate (Linux/Mac)
.\venv\Scripts\Activate.ps1      # Activate (Windows)
pip install -r requirements.txt  # Install all dependencies

# Development
python -m gzserve -e dev         # Start dev server
python -m gzlint -e dev          # Run linter
python -m sitemap -e dev         # Generate sitemap
python -m toc -e dev             # Generate table of contents

# Clean Environment
python -m clean -e dev                        # Identify orphaned files (no deletion)
python -m clean -e dev --dry-run              # Preview what would be cleaned
python -m clean -e dev --clean-orphaned       # Remove orphaned files (with confirmation)
python -m clean -e dev --clean-orphaned --force  # Remove orphaned files (no confirmation)
python -m clean -e dev --clean-all            # Remove ALL files (with confirmation)
python -m clean -e dev --clean-all --force    # Remove ALL files (no confirmation)

# Build & Deploy
python -m package -e dev         # Package for production
python -m deploy -e prod         # Deploy to server
python -m gzhost -e dev          # Start FTP test server

# Configuration
python -m setup -e dev           # Interactive setup
python -m setup -e dev --force   # Apply config only (skip prompts)

# Content Generation
python -m utils.generate -e dev  # Generate content from markdown
python -m utils.compose -e dev   # Generate source from templates
python -m normalise -e dev       # Normalize markdown formatting

# Complete Pipeline
.\scripts\gzbuild.cmd -e dev     # Windows: Run full 10-step pipeline
./scripts/gzbuild.sh -e dev      # Linux/Mac: Run full 10-step pipeline
```

---

### Happy coding! 🚀

If you encounter issues not covered in this guide, check existing documentation or open an issue on GitHub.
