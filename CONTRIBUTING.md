# Contributing to GAZ Tank

Thank you for your interest in contributing to GAZ Tank! This document provides guidelines and instructions for contributing to the project.

## 🎯 Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

### Our Standards

- **Be respectful** and considerate in your communication
- **Be collaborative** and open to feedback
- **Focus on what is best** for the community and the project
- **Show empathy** towards other community members
- **Accept constructive criticism** gracefully

## 🚀 How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**When submitting a bug report, include:**

- **Clear descriptive title** for the issue
- **Detailed description** of the problem
- **Steps to reproduce** the behavior
- **Expected behavior** vs. actual behavior
- **Screenshots** if applicable
- **Environment details:**
  - OS: [e.g., Windows 10, Ubuntu 22.04]
  - Browser: [e.g., Chrome 120, Firefox 121]
  - Python version: [e.g., 3.11.5]
- **Additional context** or logs

**Template:**
```markdown
## Bug Description
A clear description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: Windows 11
- Browser: Chrome 120
- Python: 3.11.5

## Screenshots
If applicable, add screenshots.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues.

**When suggesting an enhancement, include:**

- **Clear descriptive title**
- **Detailed description** of the proposed functionality
- **Use cases** and examples
- **Mockups or diagrams** if applicable
- **Alternatives considered**
- **Impact assessment** (breaking changes, backward compatibility)

### Pull Requests

We actively welcome your pull requests!

#### Process

1. **Fork the repository** and create your branch from `main`
2. **Set up your development environment** (see `docs/DEVELOPER_SETUP.md`)
3. **Make your changes** following our coding standards
4. **Test thoroughly** - ensure all existing tests pass and add new tests if needed
5. **Run validation tools:**
   ```bash
   python utils/gzlint/
   ```
6. **Update documentation** if you changed functionality
7. **Commit your changes** with clear, descriptive messages
8. **Push to your fork** and submit a pull request
9. **Respond to review feedback** promptly

#### Pull Request Guidelines

**Title Format:**
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit to 50 characters
- Reference issues: "Fix #123: Description"

**Description:**
- Describe what changes you made and why
- Reference related issues
- Include screenshots/GIFs for UI changes
- List breaking changes if any
- Note any deployment considerations

**Example:**
```markdown
## Description
Adds support for h2 headings in the TOC, allowing three-level heading hierarchy.

## Related Issues
Fixes #45

## Changes
- Updated app.js to query for h2, h3, h4 headings
- Added CSS styling for .toc-h2 class
- Updated documentation

## Testing
- [x] Tested in Chrome, Firefox, Edge
- [x] Verified responsive design
- [x] Ran GZLint validation
- [x] Updated unit tests

## Screenshots
[Attach screenshots if UI changed]

## Breaking Changes
None

## Checklist
- [x] My code follows the project's style guidelines
- [x] I have performed a self-review
- [x] I have commented my code where necessary
- [x] I have updated the documentation
- [x] My changes generate no new warnings
- [x] I have added tests that prove my fix is effective
- [x] New and existing unit tests pass locally
```

## 💻 Development Setup

See `docs/DEVELOPER_SETUP.md` for detailed instructions on setting up your development environment.

**Quick Start:**
```bash
# Clone your fork
git clone https://github.com/your-username/GAZTank.git
cd GAZTank

# Set up Python environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install beautifulsoup4 tomlkit mistune rcssmin rjsmin

# Start development server
python -m utils.server
```

## 📝 Coding Standards

### Python

- **Style Guide:** Follow [PEP 8](https://pep8.org/)
- **Line Length:** 100 characters maximum
- **Docstrings:** Use for all public modules, functions, classes, methods
- **Type Hints:** Use where appropriate
- **Imports:** Group standard library, third-party, local imports

**Example:**
```python
"""
Module description.
"""

import os
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup


def process_file(file_path: Path, output_dir: Optional[Path] = None) -> bool:
    """
    Process a file and generate output.
    
    Args:
        file_path: Path to the input file
        output_dir: Optional output directory (defaults to current directory)
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        FileNotFoundError: If input file doesn't exist
    """
    pass
```

### JavaScript

- **Style Guide:** Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- **ES6+:** Use modern JavaScript features
- **No console.log:** Remove debug statements before committing
- **Comments:** Use JSDoc for functions
- **Formatting:** 2-space indentation, semicolons required

**Example:**
```javascript
/**
 * Load content from HTML file and display it
 * @param {string} contentKey - The key identifying the content file
 * @param {boolean} updateHistory - Whether to update browser history
 * @returns {Promise<void>}
 */
async function loadContent(contentKey, updateHistory = true) {
  // Implementation
}
```

### HTML/CSS

- **HTML5:** Use semantic HTML elements
- **CSS:** Use CSS custom properties (variables)
- **Indentation:** 2 spaces
- **Class Names:** Use kebab-case
- **Accessibility:** Include ARIA labels and alt text

### Git Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(toc): add h2 heading support to table of contents

Added support for h2 headings in TOC generation with proper
CSS styling and three-level hierarchy (h2 > h3 > h4).

Fixes #45

---

fix(css): correct ordered list numbering in content area

Lists were displaying without numbers due to global CSS reset.
Added specific styling for #page-content ol/ul elements.

Fixes #67

---

docs: add developer setup guide

Created comprehensive DEVELOPER_SETUP.md with Python environment
setup, VS Code configuration, and development workflow.
```

## 🧪 Testing

### Before Submitting

1. **Run GZLint:**
   ```bash
   python utils/gzlint/
   ```

2. **Test in Multiple Browsers:**
   - Chrome/Edge (Chromium)
   - Firefox
   - Safari (if available)

3. **Check Responsive Design:**
   - Use browser DevTools device mode
   - Test on actual mobile devices if possible

4. **Validate HTML:**
   - Use [W3C Validator](https://validator.w3.org/nu/)

5. **Check Accessibility:**
   - Use browser DevTools Lighthouse
   - Target: 90+ accessibility score

6. **Manual Testing Checklist:**
   - [ ] Navigation works correctly
   - [ ] Sidebar toggle functions
   - [ ] TOC generates and collapses properly
   - [ ] Deep linking works (`#page:heading`)
   - [ ] Images load lazily
   - [ ] No console errors
   - [ ] Mobile responsive

## 📚 Documentation

### When to Update Documentation

Update documentation when you:
- Add new features
- Change existing functionality
- Modify configuration options
- Add new build scripts or tools
- Change development setup requirements

### Documentation Files

- `README.md` - Project overview and quick start
- `docs/SETUP_SITE.md` - End-user setup guide
- `docs/DEVELOPER_SETUP.md` - Developer environment setup
- `docs/SEO_IMPLEMENTATION.md` - SEO and analytics guide
- `docs/DESIGN_RULES.md` - Design principles
- `dev/00TODO/CONFIG_DRIVEN_INDEX.md` - Configuration reference
- `utils/gzlint/GZ_LINT_RULES.md` - Linter rules

### Markdown Conversion

After updating markdown documentation:
```bash
python utils/generate/md_to_html.py
```

This converts markdown to HTML for web viewing in `src/content/setup/`.

## 🏗️ Project Structure

For a comprehensive directory structure with detailed descriptions, see [PROJECT_STRUCTURE.md](#setup/PROJECT_STRUCTURE).

**Quick Overview:**
- **`src/`** - Source files (HTML, CSS, JS, images, content)
- **`utils/`** - Python utility modules (deploy, package, sitemap, etc.)
- **`config/`** - TOML configuration files
- **`docs/`** - Markdown documentation
- **`publish/`** - Build outputs (gitignored)
- **`scripts/`** - Cross-platform launcher scripts
- **`dev/`** - Development tools (linter, tasks)

## 🔍 Code Review Process

### For Reviewers

When reviewing pull requests:

1. **Check functionality** - Does it work as described?
2. **Review code quality** - Is it clean, readable, maintainable?
3. **Verify tests** - Are there tests? Do they pass?
4. **Check documentation** - Is it updated?
5. **Assess impact** - Are there breaking changes?
6. **Test locally** - Pull the branch and test it yourself
7. **Provide constructive feedback** - Be specific and helpful

### Review Checklist

- [ ] Code follows project style guidelines
- [ ] Changes are focused and coherent
- [ ] Documentation is updated
- [ ] Tests are included and pass
- [ ] No console errors or warnings
- [ ] Backward compatible (or breaking changes documented)
- [ ] Performance impact considered
- [ ] Accessibility maintained/improved

## 🚫 What NOT to Contribute

- **Personal configuration** (credentials, local paths)
- **Generated files** (build output, compiled files)
- **IDE-specific files** (.vscode/, .idea/ unless specifically needed)
- **Large binary files** without prior discussion
- **Breaking changes** without RFC (Request for Comments)
- **Code without tests** for significant features
- **Undocumented features**

## 📞 Questions?

- Check existing documentation in `docs/`
- Search existing issues on GitHub
- Open a new issue with the "question" label
- Be specific about what you need help with

## 📜 License

By contributing to GAZ Tank, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🙏

Your contributions help make GAZ Tank better for everyone.
