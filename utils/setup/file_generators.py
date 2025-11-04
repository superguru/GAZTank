#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
File Generators
===============
Functions for generating and updating site files (CSS, HTML, etc).

Authors: superguru, gazorper
License: GPL v3.0
"""

import re
import json
import subprocess
import shutil
import os
from pathlib import Path
from datetime import datetime

from . import ui_helpers
from . import validators
from . import backup_manager
from . import file_tracker

# Re-export for convenience
print_info = ui_helpers.print_info
print_warning = ui_helpers.print_warning
print_success = ui_helpers.print_success
print_error = ui_helpers.print_error
hex_to_rgba = validators.hex_to_rgba
create_backup = backup_manager.create_backup
track_modified_file = file_tracker.track_modified_file


def check_nodejs_available():
    """Check if Node.js is available in the system PATH
    
    Returns:
        bool: True if Node.js is available, False otherwise
    """
    return shutil.which('node') is not None


def update_js_with_nodejs(js_path, site_name, description):
    """Update JavaScript file using Node.js and Babel AST parsing
    
    This is the most robust way to update JavaScript files as it uses proper
    AST parsing instead of regex, ensuring syntax safety and handling edge cases.
    
    Args:
        js_path: Path to JavaScript file
        site_name: New site name
        description: New site description
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        Exception: If Node.js execution fails
    """
    # Prepare configuration for Node.js script
    config = {
        'filePath': str(js_path.absolute()),
        'siteName': site_name,
        'description': description
    }
    
    # Path to Node.js updater script
    node_script = Path(__file__).parent / 'js_updater.mjs'
    
    if not node_script.exists():
        raise FileNotFoundError(f"Node.js updater script not found: {node_script}")
    
    # Check if node_modules exists, if not provide helpful error
    node_modules = Path(__file__).parent / 'node_modules'
    if not node_modules.exists():
        raise FileNotFoundError(
            "Node.js dependencies not installed. Please run:\n"
            f"  cd {Path(__file__).parent}\n"
            "  npm install"
        )
    
    try:
        # Call Node.js script with config via stdin
        # Set environment to handle Unicode output on Windows
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'  # For any Python subprocess spawned by Node
        
        result = subprocess.run(
            ['node', str(node_script)],
            input=json.dumps(config),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30,  # 30 second timeout
            env=env
        )
        
        # Check if successful
        if result.returncode == 0 and 'SUCCESS' in result.stdout:
            # Track modified file
            track_modified_file(js_path)
            # Log any informational messages from stderr (node script uses it for logging)
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        print_info(f"  Node.js: {line}")
            return True
        else:
            # Node.js execution failed
            error_msg = result.stderr if result.stderr else "Unknown error"
            raise Exception(f"Node.js updater failed with code {result.returncode}: {error_msg}")
            
    except subprocess.TimeoutExpired:
        raise Exception("Node.js updater timed out after 30 seconds")
    except FileNotFoundError:
        raise Exception("Node.js (node) not found in PATH")


def update_js_with_string_replacement(js_path, site_name, description):
    """Fallback method: Update JavaScript using simple string replacement
    
    This is less robust than AST parsing but works without Node.js.
    Used as a fallback when Node.js is not available.
    
    Args:
        js_path: Path to JavaScript file
        site_name: New site name
        description: New site description
        
    Returns:
        bool: True if successful
    """
    content = js_path.read_text(encoding='utf-8')
    
    # Update hardcoded site name references in JavaScript
    # Pattern 1: Document title updates: ${pageTitle} - My Awesome Site
    content = re.sub(r'(\${pageTitle}\s*-\s*)[^`}]*', f'\\1{site_name}', content)
    
    # Pattern 2: Fallback description references
    content = re.sub(r'Welcome to My Awesome Site\. Explore our content and resources\.', description, content)
    
    # Pattern 3: Meta tag updates with site name
    content = re.sub(r'(\${pageTitle}\s*-\s*)[^`}]*(?=`)', f'\\1{site_name}', content)
    
    # Pattern 4: Any remaining "My Awesome Site" references
    content = re.sub(r'My Awesome Site', site_name, content)
    
    js_path.write_text(content, encoding='utf-8')
    # Track modified file
    track_modified_file(js_path)
    return True


def update_text_file_line_based(file_path, site_name, updates):
    """Update text files using line-by-line processing instead of regex
    
    This is more maintainable than regex for simple text file updates.
    Processes files line by line and applies string replacements.
    
    Args:
        file_path: Path to text file
        site_name: New site name
        updates: List of update rules, each can be:
            - {'starts_with': str, 'replace_with': str} - Replace entire line if it starts with pattern
            - {'contains': str, 'old': str, 'new': str} - Replace substring in lines containing pattern
            - {'line_number': int, 'new_line': str} - Replace specific line number (1-indexed)
            
    Returns:
        bool: True if successful
        
    Example:
        updates = [
            {'starts_with': '# robots.txt for', 'replace_with': f'# robots.txt for {site_name}'},
            {'contains': 'Thanks for visiting', 'old': 'My Awesome Site', 'new': site_name}
        ]
    """
    lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)
    modified = False
    
    for i, line in enumerate(lines):
        for update in updates:
            # Rule 1: Replace entire line if it starts with pattern
            if 'starts_with' in update:
                if line.strip().startswith(update['starts_with']):
                    lines[i] = update['replace_with'] + '\n'
                    modified = True
                    break
            
            # Rule 2: Replace substring in lines containing pattern
            elif 'contains' in update:
                if update['contains'] in line:
                    lines[i] = line.replace(update['old'], update['new'])
                    modified = True
                    # Don't break - might have multiple updates for same line
            
            # Rule 3: Replace specific line number (1-indexed)
            elif 'line_number' in update:
                if i + 1 == update['line_number']:
                    lines[i] = update['new_line'] + '\n'
                    modified = True
                    break
    
    if modified:
        file_path.write_text(''.join(lines), encoding='utf-8')
        # Track modified file
        track_modified_file(file_path)
    
    return modified


def generate_css_variables(config_data):
    """Generate CSS custom properties file from config
    
    Args:
        config_data: Dictionary containing configuration values
    """
    css_path = Path("src/css/variables.css")
    
    # Create backup
    if css_path.exists():
        create_backup(css_path)
    
    css_content = f"""/* ============================================
   CSS Custom Properties (Variables)
   ============================================
   Auto-generated by setup.py
   Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
   
   DO NOT EDIT THIS FILE MANUALLY
   Run 'python utils/setup/setup.py' to regenerate
   ============================================ */

:root {{
    /* Header Colors */
    --header-text: {config_data.get('header_text_color', '#212529')};
    --header-bg: {config_data.get('header_background_color', '#f8f9fa')};
    
    /* Footer Colors */
    --footer-text: {config_data.get('footer_text_color', '#6c757d')};
    --footer-bg: {config_data.get('footer_background_color', '#e9ecef')};
    --footer-link: {config_data.get('footer_link_text_color', '#0066cc')};
    --footer-link-hover: {config_data.get('footer_link_hover_text_color', '#0052a3')};
    
    /* Sidebar Colors */
    --sidebar-bg: {config_data.get('sidebar_background_color', '#f1f3f4')};
    --sidebar-highlight-bg: {config_data.get('sidebar_highlight_background_color', '#0066cc')};
    --sidebar-hover-bg: {config_data.get('sidebar_hover_background_color', '#e9ecef')};
    --sidebar-toggle-button-bg: {config_data.get('sidebar_toggle_button_background_color', '#0066cc')};
    --sidebar-left-accent: {config_data.get('sidebar_left_accent_color', '#ff0000')};
    --sidebar-submenu-overlay: {hex_to_rgba(config_data.get('sidebar_submenu_overlay_color', '#000000'), '0.15')};
    
    /* Content Colors */
    --content-text: {config_data.get('content_text_color', '#212529')};
    --content-bg: {config_data.get('content_background_color', '#ffffff')};
    --image-loading-bg: {hex_to_rgba(config_data.get('image_loading_background_color', '#E58822'), '0.1')};
    
    /* Breadcrumb Colors */
    --breadcrumb-text: {config_data.get('breadcrumb_text_color', '#6c757d')};
    
    /* TOC Colors */
    --toc-bg: {config_data.get('toc_background_color', '#f1f3f4')};
    --toc-heading: {config_data.get('toc_heading_text_color', '#ffffff')};
    --toc-link: {config_data.get('toc_link_text_color', '#0066cc')};
    --toc-link-hover: {config_data.get('toc_link_hover_text_color', '#0052a3')};
    
    /* Hashtag Colors */
    --hashtag-text: {config_data.get('hashtag_text_color', '#0066cc')};
    --hashtag-bg: {config_data.get('hashtag_background_color', '#f8f9fa')};
    
    /* Link Colors */
    --link-text: {config_data.get('link_text_color', '#0066cc')};
    --link-visited: {config_data.get('link_visited_text_color', '#6f42c1')};
    --link-hover: {config_data.get('link_hover_text_color', '#0052a3')};
    
    /* Text Colors (General) */
    --text-body: {config_data.get('body_text_color', '#212529')};
    --text-muted: {config_data.get('muted_text_color', '#6c757d')};
    
    /* Keyboard Navigation Colors */
    --keyboard-focus-outline: {config_data.get('keyboard_focus_outline_color', '#FFD700')};
    --keyboard-focus-bg: {config_data.get('keyboard_focus_background_color', '#FFD700')};
    --keyboard-hover-bg: {config_data.get('keyboard_hover_background_color', '#D47A1A')};
    --keyboard-focus-bg-15: {hex_to_rgba(config_data.get('keyboard_focus_background_color', '#FFD700'), '0.15')};
    --keyboard-focus-bg-20: {hex_to_rgba(config_data.get('keyboard_focus_background_color', '#FFD700'), '0.2')};
    --keyboard-focus-bg-25: {hex_to_rgba(config_data.get('keyboard_focus_background_color', '#FFD700'), '0.25')};
    --keyboard-focus-bg-30: {hex_to_rgba(config_data.get('keyboard_focus_background_color', '#FFD700'), '0.3')};
    --keyboard-focus-bg-40: {hex_to_rgba(config_data.get('keyboard_focus_background_color', '#FFD700'), '0.4')};
    
    /* Layout */
    --header-height: {config_data.get('header_height', '70px')};
    --header-logo-size: {config_data.get('header_logo_size', '50px')};
    --sidebar-width: {config_data.get('sidebar_width', '240px')};
    --sidebar-collapsed-width: {config_data.get('sidebar_collapsed_width', '30px')};
    --toc-max-width: {config_data.get('toc_max_width', '640px')};
    
    /* Typography */
    --font-family: {config_data.get('font_family', '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, sans-serif')};
    --font-size-base: {config_data.get('font_size_base', '16px')};
    --font-size-small: {config_data.get('font_size_small', '0.9rem')};
    --font-size-large: {config_data.get('font_size_large', '1.2rem')};
}}

/* Usage Examples:
   
   body {{
       color: var(--text-body);
       font-family: var(--font-family);
   }}
   
   header {{
       background-color: var(--header-bg);
       color: var(--header-text);
   }}
   
   footer {{
       background-color: var(--footer-bg);
       color: var(--footer-text);
   }}
   
   .sidebar {{
       background-color: var(--sidebar-bg);
   }}
   
   .sidebar .item:hover {{
       background-color: var(--sidebar-hover-bg);
   }}
   
   .sidebar .item.active {{
       background-color: var(--sidebar-highlight-bg);
   }}
   
   .sidebar-toggle {{
       background-color: var(--sidebar-toggle-button-bg);
   }}
   
   .sidebar::before {{
       background-color: var(--sidebar-left-accent);
   }}
   
   .content {{
       background-color: var(--content-bg);
       color: var(--content-text);
   }}
   
   .breadcrumb {{
       color: var(--breadcrumb-text);
   }}
   
   .toc {{
       background-color: var(--toc-bg);
   }}
   
   .toc-heading {{
       color: var(--toc-heading);
   }}
   
   .toc a {{
       color: var(--toc-link);
   }}
   
   .toc a:hover {{
       color: var(--toc-link-hover);
   }}
   
   .hashtag {{
       background-color: var(--hashtag-bg);
       color: var(--hashtag-text);
   }}
   
   a {{
       color: var(--link-text);
   }}
   
   a:visited {{
       color: var(--link-visited);
   }}
   
   a:hover {{
       color: var(--link-hover);
   }}
*/
"""
    
    css_path.parent.mkdir(parents=True, exist_ok=True)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    # Track modified file
    track_modified_file(css_path)
    
    print_success(f"CSS variables generated: {css_path}")


def update_file_domain_references(file_path, updates):
    """Update domain references in a specific file using simple string replacement
    
    Args:
        file_path: Path object for the file to update
        updates: List of (old_pattern, new_pattern) tuples
    """
    try:
        # Create backup
        create_backup(file_path)
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Track if any changes were made
        original_content = content
        
        # Apply all updates using simple string replacement
        # Sort updates by length of old_pattern (descending) to handle longer matches first
        sorted_updates = sorted(updates, key=lambda x: len(x[0]), reverse=True)
        
        for old_pattern, new_pattern in sorted_updates:
            # Only replace if the old pattern is actually different from new pattern
            if old_pattern != new_pattern:
                # Simple string replacement - no regex needed
                content = content.replace(old_pattern, new_pattern)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print_success(f"Updated domain references: {file_path}")
        else:
            print_info(f"No domain updates needed: {file_path}")
            
    except Exception as e:
        print_error(f"Error updating {file_path}: {e}")


def update_html_domain_references(file_path, target_domain):
    """Update domain references in HTML file using proper HTML parsing
    
    This intelligently finds and replaces ANY domain in HTML URLs without
    needing to maintain a hardcoded list of historical domains.
    
    Args:
        file_path: Path to HTML file
        target_domain: Target domain (e.g., 'greatsite.com')
    """
    from bs4 import BeautifulSoup
    import json
    
    try:
        # Create backup
        create_backup(file_path)
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        target_base_url = f"https://{target_domain}/"
        changes_made = []
        
        # Update canonical link
        canonical = soup.find('link', {'rel': 'canonical'})
        if canonical and canonical.get('href'):
            old_url = canonical['href']
            # Type check: href should be a string, not a list
            if isinstance(old_url, str):
                # Extract path if any
                if old_url.startswith('https://') or old_url.startswith('http://'):
                    parsed = old_url.split('/', 3)
                    path = '/' + parsed[3] if len(parsed) > 3 else '/'
                    new_url = target_base_url.rstrip('/') + path
                else:
                    new_url = target_base_url
                
                if old_url != new_url:
                    canonical['href'] = new_url
                    changes_made.append(f"canonical: {old_url} -> {new_url}")
        
        # Update Open Graph meta tags
        og_url = soup.find('meta', {'property': 'og:url'})
        if og_url and og_url.get('content'):
            old_url = og_url['content']
            # Type check: content should be a string, not a list
            if isinstance(old_url, str):
                if old_url.startswith('https://') or old_url.startswith('http://'):
                    parsed = old_url.split('/', 3)
                    path = '/' + parsed[3] if len(parsed) > 3 else '/'
                    new_url = target_base_url.rstrip('/') + path
                    
                    if old_url != new_url:
                        og_url['content'] = new_url
                        changes_made.append(f"og:url: {old_url} -> {new_url}")
        
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image and og_image.get('content'):
            content_val = og_image['content']
            # Type check: content should be a string, not a list
            if isinstance(content_val, str):
                if content_val.startswith('https://') or content_val.startswith('http://'):
                    parsed = content_val.split('/', 3)
                    path = parsed[3] if len(parsed) > 3 else 'images/site_logo_256x256.webp'
                    new_url = f"{target_base_url}{path}"
                    
                    if content_val != new_url:
                        og_image['content'] = new_url
                        changes_made.append(f"og:image: {content_val} -> {new_url}")
        
        # Update Twitter meta tags
        twitter_url = soup.find('meta', {'name': 'twitter:url'})
        if twitter_url and twitter_url.get('content'):
            old_url = twitter_url['content']
            # Type check: content should be a string, not a list
            if isinstance(old_url, str):
                if old_url.startswith('https://') or old_url.startswith('http://'):
                    parsed = old_url.split('/', 3)
                    path = '/' + parsed[3] if len(parsed) > 3 else '/'
                    new_url = target_base_url.rstrip('/') + path
                    
                    if old_url != new_url:
                        twitter_url['content'] = new_url
                        changes_made.append(f"twitter:url: {old_url} -> {new_url}")
        
        twitter_image = soup.find('meta', {'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            content_val = twitter_image['content']
            # Type check: content should be a string, not a list
            if isinstance(content_val, str):
                if content_val.startswith('https://') or content_val.startswith('http://'):
                    parsed = content_val.split('/', 3)
                    path = parsed[3] if len(parsed) > 3 else 'images/site_logo_256x256.webp'
                    new_url = f"{target_base_url}{path}"
                    
                    if content_val != new_url:
                        twitter_image['content'] = new_url
                        changes_made.append(f"twitter:image: {content_val} -> {new_url}")
        
        # Update JSON-LD structured data
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in json_ld_scripts:
            if script.string:
                try:
                    data = json.loads(script.string)
                    modified = False
                    
                    # Update url field
                    if 'url' in data:
                        old_url = data['url']
                        if isinstance(old_url, str) and (old_url.startswith('https://') or old_url.startswith('http://')):
                            parsed = old_url.split('/', 3)
                            path = '/' + parsed[3] if len(parsed) > 3 else '/'
                            new_url = target_base_url.rstrip('/') + path
                            
                            if old_url != new_url:
                                data['url'] = new_url
                                changes_made.append(f"JSON-LD url: {old_url} -> {new_url}")
                                modified = True
                    
                    # Update potentialAction urlTemplate
                    if 'potentialAction' in data:
                        action = data['potentialAction']
                        if isinstance(action, dict) and 'target' in action:
                            target = action['target']
                            if isinstance(target, dict) and 'urlTemplate' in target:
                                old_template = target['urlTemplate']
                                if isinstance(old_template, str) and (old_template.startswith('https://') or old_template.startswith('http://')):
                                    # Keep the fragment/hash part
                                    if '#' in old_template:
                                        hash_part = old_template.split('#', 1)[1]
                                        new_template = f"{target_base_url}#{hash_part}"
                                    else:
                                        parsed = old_template.split('/', 3)
                                        path = '/' + parsed[3] if len(parsed) > 3 else '/'
                                        new_template = target_base_url.rstrip('/') + path
                                    
                                    if old_template != new_template:
                                        target['urlTemplate'] = new_template
                                        changes_made.append(f"JSON-LD urlTemplate: {old_template} -> {new_template}")
                                        modified = True
                    
                    if modified:
                        # Pretty print JSON with proper indentation
                        json_str = json.dumps(data, indent=4, ensure_ascii=False)
                        # Add proper indentation for HTML context
                        script.string = '\n    ' + json_str.replace('\n', '\n    ') + '\n    '
                
                except (json.JSONDecodeError, TypeError, KeyError) as e:
                    print_warning(f"  Could not parse JSON-LD in {file_path}: {e}")
        
        # Write back if changed
        if changes_made:
            new_content = str(soup)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            # Track modified file
            track_modified_file(file_path)
            print_success(f"Updated HTML domain references: {file_path}")
            for change in changes_made:
                print_info(f"  • {change}")
        else:
            print_info(f"No HTML domain updates needed: {file_path}")
            
    except Exception as e:
        print_error(f"Error updating HTML domain references in {file_path}: {e}")
        import traceback
        traceback.print_exc()


def update_text_file_domains(file_path, target_domain):
    """Update domain references in text files using urllib.parse for URL handling
    
    Args:
        file_path: Path to text file
        target_domain: Target domain (e.g., 'greatsite.com')
    """
    from urllib.parse import urlparse, urlunparse
    
    try:
        create_backup(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        changes_made = []
        
        # List of known external domains that should never be replaced
        external_domains = [
            'cdnjs.cloudflare.com',
            'schema.org',
            'developers.facebook.com',
            'facebook.com',
            'twitter.com',
            'cards-dev.twitter.com',
            'search.google.com',
            'google.com',
            'pagespeed.web.dev',
            'web.dev',
            'gtmetrix.com',
            'github.com',
            'gitlab.com',
            'bitbucket.org',
            'stackoverflow.com',
            'w3.org',
            'mozilla.org',
            'microsoft.com',
            'npmjs.com',
            'pypi.org',
            'linkedin.com',
        ]
        
        # Process content line by line to find and replace URLs
        lines = content.split('\n')
        modified = False
        
        for i, line in enumerate(lines):
            # Find all https:// URLs in the line
            words = line.split()
            new_words = []
            
            for word in words:
                if 'https://' in word:
                    # Extract URL from word (might have punctuation)
                    url_start = word.find('https://')
                    prefix = word[:url_start]
                    url_and_suffix = word[url_start:]
                    
                    # Find end of URL (stop at whitespace, quotes, or common punctuation)
                    url_end = len(url_and_suffix)
                    for end_char in [' ', '"', "'", ')', ']', ',', ';']:
                        pos = url_and_suffix.find(end_char)
                        if pos > 0 and pos < url_end:
                            url_end = pos
                    
                    url = url_and_suffix[:url_end]
                    suffix = url_and_suffix[url_end:]
                    
                    # Parse URL to extract domain and path
                    try:
                        parsed = urlparse(url)
                        domain = parsed.netloc
                        
                        # Skip external domains
                        if any(ext_domain in domain for ext_domain in external_domains):
                            new_words.append(word)
                            continue
                        
                        # Replace with target domain
                        new_url = urlunparse((
                            parsed.scheme,
                            target_domain,
                            parsed.path,
                            parsed.params,
                            parsed.query,
                            parsed.fragment
                        ))
                        
                        if url != new_url:
                            change_str = f"{url} -> {new_url}"
                            if change_str not in changes_made:
                                changes_made.append(change_str)
                            new_words.append(prefix + new_url + suffix)
                            modified = True
                        else:
                            new_words.append(word)
                    except Exception:
                        # If URL parsing fails, keep original
                        new_words.append(word)
                else:
                    new_words.append(word)
            
            if modified:
                lines[i] = ' '.join(new_words)
        
        if modified:
            content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            # Track modified file
            track_modified_file(file_path)
            print_success(f"Updated domain references: {file_path}")
            for change in changes_made[:5]:  # Show first 5 changes
                print_info(f"  • {change}")
            if len(changes_made) > 5:
                print_info(f"  • ... and {len(changes_made) - 5} more")
        else:
            print_info(f"No domain updates needed: {file_path}")
            
    except Exception as e:
        print_error(f"Error updating {file_path}: {e}")


def update_domain_references(config_data):
    """Update domain references throughout the project using intelligent parsing
    
    This new approach uses proper HTML parsing and intelligent regex to detect
    and replace ANY domain, eliminating the need for hardcoded placeholder lists.
    
    Args:
        config_data: Dictionary containing configuration values
    """
    domain = config_data['domain']
    
    print_info("Updating domain references in all files...")
    
    # Update HTML files using proper HTML parsing (handles meta tags, JSON-LD, etc.)
    html_files = [
        Path('src/index.html'),
    ]
    
    for html_file in html_files:
        if html_file.exists():
            update_html_domain_references(html_file, domain)
        else:
            print_warning(f"File not found: {html_file}")
    
    # Update other text files using intelligent regex
    text_files = [
        Path('src/js/app.js'),
        Path('src/robots.txt'),
        Path('src/humans.txt'),
    ]
    
    for text_file in text_files:
        if text_file.exists():
            update_text_file_domains(text_file, domain)
        else:
            print_warning(f"File not found: {text_file}")



def update_image_references(config_data):
    """Update logo and favicon references in index.html using BeautifulSoup
    
    Args:
        config_data: Dictionary containing configuration values
    """
    from bs4 import BeautifulSoup
    
    print_info("Updating image references in index.html...")
    
    index_path = Path("src/index.html")
    if not index_path.exists():
        print_warning(f"File not found: {index_path}")
        return
    
    # Create backup
    create_backup(index_path)
    
    try:
        # Read and parse HTML
        content = index_path.read_text(encoding='utf-8')
        original_content = content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Get config values
        favicon_32 = config_data.get('favicon_32', 'site_favicon_32x32.webp')
        favicon_16 = config_data.get('favicon_16', 'site_favicon_16x16.webp')
        logo_256 = config_data.get('logo_256', 'site_logo_256x256.webp')
        logo_75 = config_data.get('logo_75', 'site_logo_75x75.webp')
        og_image = config_data.get('og_image', 'site_logo_256x256.webp')
        logo_alt_text = config_data.get('logo_alt_text', 'Site Logo')
        domain = config_data.get('domain', 'example.com')
        
        # Update favicon links
        favicon_links = soup.find_all('link', rel='icon')
        for link in favicon_links:
            href = link.get('href', '')
            # Type check: href should be a string, not a list or None
            if isinstance(href, str):
                if '32x32' in href:
                    link['href'] = f'images/{favicon_32}'
                elif '16x16' in href:
                    link['href'] = f'images/{favicon_16}'
        
        # Update main logo image src and alt text
        logo_img = soup.find('img', class_='header-logo')
        if logo_img:
            logo_img['src'] = f'images/{logo_256}'
            logo_img['alt'] = logo_alt_text
            
            # Update srcset attribute if it exists
            if logo_img.get('srcset'):
                logo_img['srcset'] = f"images/{logo_75} 75w, images/{logo_256} 256w"
        
        # Update Open Graph image
        og_image_tag = soup.find('meta', property='og:image')
        if og_image_tag:
            og_image_tag['content'] = f'https://{domain}/images/{og_image}'
        
        # Update Twitter image
        twitter_image_tag = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image_tag:
            twitter_image_tag['content'] = f'https://{domain}/images/{og_image}'
        
        # Write back if changed
        new_content = str(soup)
        if new_content != original_content:
            index_path.write_text(new_content, encoding='utf-8')
            # Track modified file
            track_modified_file(index_path)
            print_success(f"Updated image references: {index_path}")
        else:
            print_info(f"No image updates needed: {index_path}")
            
    except Exception as e:
        print_error(f"Error updating {index_path}: {e}")


def update_syntax_highlighting(config_data):
    """Update Prism.js syntax highlighting inclusion in index.html using BeautifulSoup
    
    Args:
        config_data: Dictionary containing configuration values
    """
    from bs4 import BeautifulSoup, Comment
    from bs4.element import NavigableString
    
    print_info("Updating syntax highlighting settings in index.html...")
    
    index_path = Path("src/index.html")
    if not index_path.exists():
        print_warning(f"File not found: {index_path}")
        return
    
    # Create backup
    create_backup(index_path)
    
    try:
        # Read and parse HTML
        content = index_path.read_text(encoding='utf-8')
        original_content = content
        soup = BeautifulSoup(content, 'html.parser')
        
        enable_syntax_highlighting = config_data.get('enable_syntax_highlighting', True)
        
        # Define Prism.js URLs
        prism_css_url = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css'
        prism_components = [
            'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-powershell.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-css.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markup.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-ini.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js',
        ]
        
        # Find existing Prism.js elements
        prism_css_link = soup.find('link', href=lambda x: isinstance(x, str) and 'prism' in x and '.css' in x)
        prism_scripts = soup.find_all('script', src=lambda x: isinstance(x, str) and 'prism' in x)
        
        if enable_syntax_highlighting:
            # Add Prism.js CSS if not present
            if not prism_css_link:
                # Find the head tag
                head = soup.find('head')
                if head:
                    # Create comment
                    comment = Comment(' Prism.js for syntax highlighting ')
                    # Create CSS link tag
                    link_tag = soup.new_tag('link', href=prism_css_url, rel='stylesheet')
                    
                    # Insert before </head> (append to head)
                    head.append(NavigableString('\n'))
                    head.append(comment)
                    head.append(NavigableString('\n    '))
                    head.append(link_tag)
            
            # Add Prism.js scripts if not present
            if not prism_scripts:
                # Find app.js script as insertion point
                app_js_script = soup.find('script', src='js/app.js')
                if app_js_script:
                    # Create comment
                    comment = Comment(' Prism.js core and language components ')
                    app_js_script.insert_before(NavigableString('\n    '))
                    app_js_script.insert_before(comment)
                    app_js_script.insert_before(NavigableString('\n    '))
                    
                    # Add all Prism.js script tags
                    for src_url in prism_components:
                        script_tag = soup.new_tag('script', src=src_url)
                        app_js_script.insert_before(script_tag)
                        app_js_script.insert_before(NavigableString('\n    '))
        else:
            # Remove Prism.js CSS and its comment
            if prism_css_link:
                # Check if previous sibling is a comment about Prism
                prev = prism_css_link.previous_sibling
                if isinstance(prev, Comment) and 'Prism' in prev:
                    prev.extract()
                prism_css_link.extract()
            
            # Remove all Prism.js scripts and their comment
            if prism_scripts:
                # Find and remove the Prism comment
                for script in prism_scripts:
                    prev = script.previous_sibling
                    if isinstance(prev, Comment) and 'Prism' in prev:
                        prev.extract()
                        break  # Only remove the first comment
                
                # Remove all Prism script tags
                for script in prism_scripts:
                    script.extract()
        
        # Write back if changed
        new_content = str(soup)
        if new_content != original_content:
            index_path.write_text(new_content, encoding='utf-8')
            # Track modified file
            track_modified_file(index_path)
            print_success(f"Updated syntax highlighting: {index_path}")
        else:
            print_info(f"No syntax highlighting updates needed: {index_path}")
            
    except Exception as e:
        print_error(f"Error updating {index_path}: {e}")


def update_stylesheet_integration(config_data):
    """Update styles.css to import variables.css and use CSS variables
    
    Args:
        config_data: Dictionary containing configuration values
    """
    print_info("Updating stylesheet to use CSS variables...")
    
    styles_path = Path("src/css/styles.css")
    if not styles_path.exists():
        print_warning(f"File not found: {styles_path}")
        return
    
    # Create backup
    create_backup(styles_path)
    
    try:
        # Read file content
        with open(styles_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Add import at the top if not present
        if '@import "variables.css";' not in content:
            content = '@import "variables.css";\n\n' + content
        
        # Replace common hardcoded values with CSS variables and update old variable names
        replacements = {
            # Update old variable names to new descriptive names
            'var(--text-primary)': 'var(--text-body)',
            'var(--text-secondary)': 'var(--text-muted)',
            'var(--text-link)': 'var(--link-text)',
            'var(--text-link-hover)': 'var(--link-hover)',
            'var(--text-link-visited)': 'var(--link-visited)',
            'var(--bg-content)': 'var(--content-bg)',
            'var(--bg-sidebar)': 'var(--sidebar-bg)',
            'var(--bg-toc)': 'var(--toc-bg)',
            # Legacy hardcoded values replacement
            'background-color: #212529': 'background-color: var(--sidebar-bg)',
            'color: #E0E0E0': 'color: var(--text-body)',
            'color: #B0B0B0': 'color: var(--text-muted)',
            'color: #80D0D0': 'color: var(--link-text)',
            'color: #A0F0F0': 'color: var(--link-hover)',
            'rgba(0, 0, 0, 0.3)': 'var(--content-bg)',
            'rgba(0, 0, 0, 0.4)': 'var(--sidebar-bg)',
            'rgba(0, 0, 0, 0.5)': 'var(--toc-bg)'
        }
        
        for old_value, new_value in replacements.items():
            content = content.replace(old_value, new_value)
        
        # Write back if changed
        if content != original_content:
            with open(styles_path, 'w', encoding='utf-8') as f:
                f.write(content)
            # Track modified file
            track_modified_file(styles_path)
            print_success(f"Updated stylesheet integration: {styles_path}")
        else:
            print_info(f"Stylesheet already uses CSS variables: {styles_path}")
            
    except Exception as e:
        print_error(f"Error updating {styles_path}: {e}")


def update_site_branding(config_data):
    """Update site name and branding throughout the project using BeautifulSoup
    
    Args:
        config_data: Dictionary containing configuration values
    """
    from bs4 import BeautifulSoup
    
    site_name = config_data['site_name']
    short_name = config_data['short_name']
    description = config_data['description']
    tagline = config_data['tagline']
    author = config_data['author']
    
    print_info("Updating site branding in all files...")
    
    # Update index.html using BeautifulSoup for proper HTML parsing
    index_path = Path('src/index.html')
    if index_path.exists():
        create_backup(index_path)
        
        content = index_path.read_text(encoding='utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        
        # Update title tags
        title_text = f"{site_name} - {tagline}" if tagline and tagline != site_name else f"{site_name} - Gaming Content, Mods & Campaign Runs"
        
        title_tag = soup.find('title')
        if title_tag:
            title_tag.string = title_text
        
        meta_title = soup.find('meta', {'name': 'title'})
        if meta_title:
            meta_title['content'] = title_text
        
        # Update description
        meta_description = soup.find('meta', {'name': 'description'})
        if meta_description:
            meta_description['content'] = description
        
        # Update keywords from SEO config
        keywords = config_data.get('keywords', '')
        if keywords:
            meta_keywords = soup.find('meta', {'name': 'keywords'})
            if meta_keywords:
                meta_keywords['content'] = keywords
        
        # Update robots directive from SEO config
        robots_directive = config_data.get('robots_directive', 'index, follow')
        meta_robots = soup.find('meta', {'name': 'robots'})
        if meta_robots:
            meta_robots['content'] = robots_directive
        
        # Update Open Graph tags
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title:
            og_title['content'] = title_text
        
        og_description = soup.find('meta', {'property': 'og:description'})
        if og_description:
            og_description['content'] = description
        
        og_site_name = soup.find('meta', {'property': 'og:site_name'})
        if og_site_name:
            og_site_name['content'] = site_name
        
        # Update Twitter tags
        twitter_title = soup.find('meta', {'name': 'twitter:title'})
        if twitter_title:
            twitter_title['content'] = title_text
        
        twitter_description = soup.find('meta', {'name': 'twitter:description'})
        if twitter_description:
            twitter_description['content'] = description
        
        # Update author meta tag
        author_secondary = config_data.get('author_secondary', '')
        authors_list = [author] if author else []
        if author_secondary:
            authors_list.append(author_secondary)
        authors_text = ', '.join(authors_list) if authors_list else 'Site Author'
        
        meta_author = soup.find('meta', {'name': 'author'})
        if meta_author:
            meta_author['content'] = authors_text
        
        # Update JSON-LD structured data author field
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in json_ld_scripts:
            if script.string:
                import json
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        # Update alternateName with short_name
                        if 'alternateName' in data:
                            data['alternateName'] = short_name
                        
                        # Update description field if present
                        if 'description' in data:
                            data['description'] = description
                        
                        # Update author array from config
                        if 'author' in data:
                            # Build author array from config
                            author_objects = []
                            for author_name in authors_list:
                                author_objects.append({
                                    "@type": "Person",
                                    "name": author_name
                                })
                            if author_objects:
                                data['author'] = author_objects
                        
                        script.string = json.dumps(data, indent=4)
                except (json.JSONDecodeError, KeyError):
                    pass  # Skip if JSON is invalid or doesn't have expected structure
        
        # Update header h1 text
        h1_tag = soup.find('h1')
        if h1_tag:
            h1_tag.string = site_name
        
        # Update footer copyright text
        footer = soup.find('footer', id='footer')
        if footer:
            footer_p = footer.find('p')
            if footer_p:
                # Preserve the copyright year span structure
                # Find or create the span
                year_span = footer_p.find('span', id='copyright-year')
                if year_span:
                    # Clear the paragraph and rebuild it
                    footer_p.clear()
                    footer_p.append('© 2025')
                    footer_p.append(year_span)
                    footer_p.append(f' {site_name}. All rights reserved.')
                else:
                    # If no span exists, parse and update the text
                    text = footer_p.get_text()
                    # Extract year if present, default to 2025
                    parts = text.split()
                    year = '2025'
                    if len(parts) > 0 and parts[0] == '©' and len(parts) > 1:
                        # Check if next part is a year
                        potential_year = parts[1].strip('.')
                        if potential_year.isdigit() and len(potential_year) == 4:
                            year = potential_year
                    footer_p.string = f'© {year} {site_name}. All rights reserved.'
        
        index_path.write_text(str(soup), encoding='utf-8')
        # Track modified file
        track_modified_file(index_path)
        print_success(f"Updated branding: {index_path}")
    
    # Update app.js
    app_js_path = Path('src/js/app.js')
    if app_js_path.exists():
        create_backup(app_js_path)
        
        # Try to use Node.js with Babel AST parsing (most robust)
        # Falls back to regex if Node.js is unavailable
        if check_nodejs_available():
            try:
                update_js_with_nodejs(app_js_path, site_name, description)
                print_success(f"Updated branding (Node.js AST): {app_js_path}")
            except Exception as e:
                print_warning(f"  Node.js AST parser failed: {e}")
                print_info("  Falling back to regex-based updates...")
                update_js_with_string_replacement(app_js_path, site_name, description)
                print_success(f"Updated branding (regex fallback): {app_js_path}")
        else:
            print_info("  Node.js not available, using regex fallback")
            update_js_with_string_replacement(app_js_path, site_name, description)
            print_success(f"Updated branding (regex fallback): {app_js_path}")
    
    # Update robots.txt
    robots_path = Path('src/robots.txt')
    if robots_path.exists():
        create_backup(robots_path)
        updates = [
            {'starts_with': '# robots.txt for', 'replace_with': f'# robots.txt for {site_name}'}
        ]
        if update_text_file_line_based(robots_path, site_name, updates):
            print_success(f"Updated branding: {robots_path}")
    else:
        print_warning(f"File not found: {robots_path}")
    
    # Update humans.txt
    humans_path = Path('src/humans.txt')
    if humans_path.exists():
        create_backup(humans_path)
        updates = [
            {'contains': 'Thanks for visiting', 'old': 'GAZ Tank', 'new': site_name}
        ]
        if update_text_file_line_based(humans_path, site_name, updates):
            print_success(f"Updated branding: {humans_path}")
    else:
        print_warning(f"File not found: {humans_path}")
    
    # Update README.md
    readme_path = Path('README.md')
    if readme_path.exists():
        create_backup(readme_path)
        updates = [
            # Update title (line 1: "# GAZ Tank" -> "# {site_name}")
            {'line_number': 1, 'new_line': f'# {site_name}'},
            # Update copyright line
            {'contains': '© 2025', 'old': 'GAZ Tank', 'new': site_name}
        ]
        if update_text_file_line_based(readme_path, site_name, updates):
            print_success(f"Updated branding: {readme_path}")
    else:
        print_warning(f"File not found: {readme_path}")
