#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Table of Contents Generator
============================
Adds IDs to headings and injects TOC HTML into content files at build time.

This module processes HTML files to:
1. Add unique IDs to all h2, h3, h4 headings
2. Generate hierarchical TOC structure
3. Inject TOC HTML at the top of content
4. Ensure headings are SEO-friendly and linkable

Authors: superguru, gazorper
License: GPL v3.0
"""

import warnings
from pathlib import Path
from typing import List, Dict, Tuple, Any
from bs4 import BeautifulSoup, Tag, MarkupResemblesLocatorWarning

from utils.gzconfig import get_pipeline_config
from utils.gzlogging import get_logging_context

# Suppress BeautifulSoup warning when text looks like a filename
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def slugify(text: str) -> str:
    """
    Convert heading text to URL-friendly ID.
    
    Uses BeautifulSoup for HTML removal and string methods for the rest.
    No regex required.
    
    Args:
        text: Heading text to convert
        
    Returns:
        Slugified text suitable for use as an HTML ID
        
    Example:
        >>> slugify("1. Meta Tags (index.html)")
        'meta-tags-index-html'
    """
    # Remove HTML tags robustly (headings might contain <code>, <em>, etc.)
    text = BeautifulSoup(text, 'lxml').get_text()
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove leading numbers/punctuation
    text = text.lstrip('0123456789.)]}\t\n\r ')
    
    # Keep only alphanumeric, spaces, hyphens, and underscores (will convert _ later)
    allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789 -_')
    text = ''.join(c if c in allowed_chars else '' for c in text)
    
    # Replace underscores and spaces with hyphens
    text = text.replace('_', '-')
    text = text.replace(' ', '-')
    
    # Collapse multiple hyphens to single hyphen
    while '--' in text:
        text = text.replace('--', '-')
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text


def add_ids_to_headings(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Add unique IDs to all h2, h3, h4 headings.
    
    Args:
        soup: BeautifulSoup object of HTML content
        
    Returns:
        List of heading data dictionaries with level, text, and id
    """
    headings = []
    used_ids = set()
    
    for tag_name in ['h2', 'h3', 'h4']:
        for heading in soup.find_all(tag_name):
            text = heading.get_text().strip()
            
            # Generate base ID
            base_id = slugify(text)
            
            # Ensure uniqueness
            heading_id = base_id
            counter = 1
            while heading_id in used_ids:
                heading_id = f"{base_id}-{counter}"
                counter += 1
            
            used_ids.add(heading_id)
            
            # Add ID to heading
            heading['id'] = heading_id
            
            # Store heading data
            headings.append({
                'level': tag_name,
                'text': text,
                'id': heading_id,
                'element': heading
            })
    
    return headings


def build_toc_structure(headings: List[Dict[str, Any]]) -> str:
    """
    Build hierarchical TOC HTML from heading list.
    
    Args:
        headings: List of heading dictionaries
        
    Returns:
        HTML string for the table of contents
    """
    if not headings:
        return ""
    
    # Filter to only include h2, h3, h4
    toc_headings = [h for h in headings if h['level'] in ['h2', 'h3', 'h4']]
    
    if not toc_headings:
        return ""
    
    html_parts = []
    html_parts.append('<nav class="table-of-contents">')
    html_parts.append('  <div class="toc-header">')
    html_parts.append('    <div class="toc-header-left">')
    html_parts.append('      <ul>')
    
    # CONTENTS section (page headings)
    html_parts.append('        <li class="toc-section">')
    html_parts.append('          <div class="toc-section-header">')
    html_parts.append('            <button class="toc-section-toggle" data-section="headings">▼</button>')
    html_parts.append('            <span class="toc-section-title">Contents</span>')
    html_parts.append('          </div>')
    html_parts.append('          <ul class="toc-section-content" data-section="headings">')
    
    # Track current depth for proper nesting
    current_depth = 2  # Start at h2
    open_lists = 1  # One <ul> already open
    
    for heading in toc_headings:
        level_num = int(heading['level'][1])  # Extract number from 'h2', 'h3', etc.
        
        # Handle depth changes
        if level_num > current_depth:
            # Going deeper - open nested lists
            for _ in range(level_num - current_depth):
                html_parts.append('            <ul>')
                open_lists += 1
        elif level_num < current_depth:
            # Going shallower - close nested lists
            for _ in range(current_depth - level_num):
                html_parts.append('            </ul>')
                html_parts.append('          </li>')
                open_lists -= 1
        else:
            # Same level - close previous item
            if not html_parts[-1].endswith('<ul class="toc-section-content" data-section="headings">'):
                html_parts.append('          </li>')
        
        current_depth = level_num
        
        # Add the TOC entry
        indent = '  ' * (open_lists + 5)
        html_parts.append(f'{indent}<li>')
        html_parts.append(f'{indent}  <a href="#{heading["id"]}">{heading["text"]}</a>')
    
    # Close all open lists
    while open_lists > 0:
        html_parts.append('          </li>')
        html_parts.append('          </ul>')
        open_lists -= 1
    
    html_parts.append('        </li>')  # Close toc-section
    
    # Note: Navigation section (sub-pages) is added dynamically by JavaScript
    # since it depends on the navigation structure from site.toml
    
    html_parts.append('      </ul>')  # Close left column ul
    html_parts.append('    </div>')  # Close toc-header-left
    html_parts.append('    <div class="toc-header-right">')
    html_parts.append('      <button class="toc-toggle" aria-label="Toggle table of contents">▼</button>')
    html_parts.append('    </div>')  # Close toc-header-right
    html_parts.append('  </div>')  # Close toc-header
    html_parts.append('</nav>')
    
    return '\n'.join(html_parts)


def inject_toc(soup: BeautifulSoup, toc_html: str) -> bool:
    """
    Inject TOC HTML at the top of content, after h1.
    
    Args:
        soup: BeautifulSoup object of HTML content
        toc_html: HTML string of the table of contents
        
    Returns:
        True if TOC was injected, False otherwise
    """
    if not toc_html:
        return False
    
    # Find the h1 tag (main heading)
    h1 = soup.find('h1')
    
    if h1:
        # Create TOC element from HTML string
        toc_soup = BeautifulSoup(toc_html, 'lxml')
        toc_nav = toc_soup.find('nav', class_='table-of-contents')
        
        # Insert TOC after h1 (only if toc_nav was found)
        if toc_nav:
            h1.insert_after(toc_nav)
            return True
    else:
        # If no h1, insert at beginning of body content
        # Look for first element (skip data-hashtags div if present)
        first_element = None
        for child in soup.children:
            if isinstance(child, Tag) and child.name != 'div':
                first_element = child
                break
            elif isinstance(child, Tag) and 'data-hashtags' not in child.attrs:
                first_element = child
                break
        
        if first_element:
            toc_soup = BeautifulSoup(toc_html, 'lxml')
            toc_nav = toc_soup.find('nav', class_='table-of-contents')
            if toc_nav:
                first_element.insert_before(toc_nav)
                return True
    
    return False


def remove_existing_toc(soup: BeautifulSoup) -> None:
    """
    Remove any existing TOC from the document.
    
    Args:
        soup: BeautifulSoup object of HTML content
    """
    existing_toc = soup.find('nav', class_='table-of-contents')
    if existing_toc:
        existing_toc.decompose()


def remove_ids_from_headings(soup: BeautifulSoup) -> int:
    """
    Remove IDs from all h2, h3, h4 headings.
    
    Args:
        soup: BeautifulSoup object of HTML content
        
    Returns:
        Number of IDs removed
    """
    count = 0
    
    for tag_name in ['h2', 'h3', 'h4']:
        for heading in soup.find_all(tag_name):
            if heading.has_attr('id'):
                del heading['id']
                count += 1
    
    return count


def strip_toc_from_file(file_path: Path, dry_run: bool = False, force: bool = False) -> Tuple[bool, str]:
    """
    Strip TOC and heading IDs from an HTML file (inverse operation).
    
    Args:
        file_path: Path to HTML file to process
        dry_run: If True, don't write changes to disk
        force: If True, process file even if not needed
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Read file
        html_content = file_path.read_text(encoding='utf-8')
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Check if TOC exists
        has_toc = soup.find('nav', class_='table-of-contents') is not None
        
        # Count IDs on headings
        ids_count = 0
        for tag_name in ['h2', 'h3', 'h4']:
            for heading in soup.find_all(tag_name):
                if heading.has_attr('id'):
                    ids_count += 1
        
        # If nothing to strip and not forced, skip
        if not force and not has_toc and ids_count == 0:
            return True, "Skipped (no TOC or IDs found)"
        
        # Remove TOC
        remove_existing_toc(soup)
        
        # Remove IDs from headings
        ids_removed = remove_ids_from_headings(soup)
        
        # Check if anything was changed
        if not has_toc and ids_removed == 0:
            return True, "Skipped (no TOC or IDs found)"
        
        # Write back to file (unless dry run)
        if not dry_run:
            # Extract just the body content (without <html> and <body> wrappers from lxml)
            body = soup.find('body')
            if body:
                # Get inner HTML of body (without the body tag itself)
                html_output = ''.join(str(child) for child in body.children)
            else:
                # Fallback if no body tag (shouldn't happen with lxml)
                html_output = str(soup)
            
            file_path.write_text(html_output, encoding='utf-8')
        
        changes = []
        if has_toc:
            changes.append("TOC removed")
        if ids_removed > 0:
            changes.append(f"{ids_removed} IDs removed")
        
        summary = ", ".join(changes)
        return True, f"✓ {summary}"
        
    except Exception as e:
        return False, f"Error: {str(e)}"


def process_html_file(file_path: Path, dry_run: bool = False, force: bool = False) -> Tuple[bool, str]:
    """
    Process a single HTML file: add IDs to headings and inject TOC.
    
    Args:
        file_path: Path to HTML file to process
        dry_run: If True, don't write changes to disk
        force: If True, process file even if not needed based on timestamps
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Try to find the source markdown file to check timestamps
        # HTML files are in publish/{env}/content/... and source files are in docs/, utils/, dev/, etc.
        source_file = None
        
        # Check if there's a source note in the HTML to find the original file
        try:
            html_content = file_path.read_text(encoding='utf-8')
            soup_temp = BeautifulSoup(html_content, 'lxml')
            
            # Look for the source note: "This content was automatically generated from <code>filename</code>"
            # Find all <em> tags and check their text content
            for em_tag in soup_temp.find_all('em'):
                em_text = em_tag.get_text()
                if em_text and 'automatically generated from' in em_text:
                    code_tag = em_tag.find('code')
                    if code_tag:
                        source_filename = code_tag.get_text()
                        
                        # Try to find the source file based on the HTML file path
                        # publish/dev/content/setup/SETUP_SITE.html -> docs/SETUP_SITE.md
                        # publish/dev/content/pipeline-docs/deploy/README.html -> utils/deploy/README.md
                        
                        project_root = file_path.parents[4]  # Go up from publish/dev/content/...
                        
                        if 'pipeline-docs' in file_path.parts:
                            # Pipeline docs: publish/dev/content/pipeline-docs/module/README.html -> utils/module/README.md
                            parts = file_path.parts
                            pipeline_idx = parts.index('pipeline-docs')
                            if pipeline_idx + 1 < len(parts):
                                module_path = Path(*parts[pipeline_idx + 1:-1])  # Get module path
                                source_file = project_root / 'utils' / module_path / source_filename
                            else:
                                # Top-level pipeline-docs/README.html -> utils/README.md
                                source_file = project_root / 'utils' / source_filename
                        elif 'setup' in file_path.parts:
                            # Setup docs: publish/dev/content/setup/SETUP_SITE.html -> docs/SETUP_SITE.md
                            if source_filename == 'README.md':
                                source_file = project_root / source_filename
                            elif source_filename == 'PROJECT_STRUCTURE.md':
                                source_file = project_root / 'dev' / source_filename
                            else:
                                source_file = project_root / 'docs' / source_filename
                        
                        # Verify the source file exists
                        if source_file and not source_file.exists():
                            source_file = None
                        break  # Found the source note, exit loop
        except Exception:
            # If we can't determine the source file, continue without timestamp checking
            pass
        
        # Check timestamps if source file was found and not in force mode
        if not force and source_file and source_file.exists() and file_path.exists():
            source_mtime = source_file.stat().st_mtime
            output_mtime = file_path.stat().st_mtime
            
            if output_mtime >= source_mtime:
                return True, "Skipped (up-to-date)"
        
        # Read file
        html_content = file_path.read_text(encoding='utf-8')
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Check if TOC already exists and file hasn't been modified
        existing_toc = soup.find('nav', class_='table-of-contents')
        
        # If not forced and TOC exists, check if we need to regenerate
        if not force and existing_toc:
            # Check if headings already have IDs
            headings_with_ids = 0
            for tag_name in ['h2', 'h3', 'h4']:
                for heading in soup.find_all(tag_name):
                    if heading.has_attr('id'):
                        headings_with_ids += 1
            
            # If TOC exists and headings have IDs, skip processing
            if headings_with_ids > 0:
                return True, "Skipped (already processed, use --force to regenerate)"
        
        # Remove existing TOC if present
        remove_existing_toc(soup)
        
        # Add IDs to headings
        headings = add_ids_to_headings(soup)
        
        # Count headings by level
        h2_count = sum(1 for h in headings if h['level'] == 'h2')
        h3_count = sum(1 for h in headings if h['level'] == 'h3')
        h4_count = sum(1 for h in headings if h['level'] == 'h4')
        
        # Only generate TOC if there are h2/h3/h4 headings
        toc_headings = [h for h in headings if h['level'] in ['h2', 'h3', 'h4']]
        
        if not toc_headings:
            return True, "Skipped (no h2/h3/h4 headings)"
        
        # Build TOC HTML
        toc_html = build_toc_structure(headings)
        
        # Inject TOC
        injected = inject_toc(soup, toc_html)
        
        if not injected:
            return False, "Failed to inject TOC"
        
        # Write back to file (unless dry run)
        if not dry_run:
            # Extract just the body content (without <html> and <body> wrappers from lxml)
            body = soup.find('body')
            if body:
                # Get inner HTML of body (without the body tag itself)
                html_output = ''.join(str(child) for child in body.children)
            else:
                # Fallback if no body tag (shouldn't happen with lxml)
                html_output = str(soup)
            
            file_path.write_text(html_output, encoding='utf-8')
        
        heading_summary = []
        if h2_count:
            heading_summary.append(f"{h2_count} h2")
        if h3_count:
            heading_summary.append(f"{h3_count} h3")
        if h4_count:
            heading_summary.append(f"{h4_count} h4")
        
        summary = ", ".join(heading_summary)
        return True, f"✓ TOC added ({summary})"
        
    except Exception as e:
        return False, f"Error: {str(e)}"


def scan_html_files(src_dir: Path) -> List[Path]:
    """
    Recursively find all HTML files in src directory.
    
    Args:
        src_dir: Source directory to scan
        
    Returns:
        List of HTML file paths
    """
    html_files = []
    
    # Find all .html files recursively
    for html_file in src_dir.rglob('*.html'):
        # Skip index.html (it's the main SPA file, not content)
        if html_file.name == 'index.html':
            continue
        html_files.append(html_file)
    
    return sorted(html_files)


def main():
    """Main entry point for TOC generator."""
    import sys
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Table of Contents Generator - Adds IDs to headings and injects TOC HTML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m utils.toc -e dev                # Add TOC and IDs to dev environment
  python -m utils.toc -e staging            # Add TOC and IDs to staging environment
  python -m utils.toc -e prod               # Add TOC and IDs to production environment
  python -m utils.toc -e dev --strip        # Remove TOC and IDs from dev environment
  python -m utils.toc -e dev --dry-run      # Preview changes without writing
  python -m utils.toc -e dev --force        # Force regeneration of all TOCs

Environments are configured in config/environments.toml
        """
    )
    
    parser.add_argument(
        '-e', '--environment',
        required=True,
        choices=['dev', 'staging', 'prod'],
        help='Environment to process (dev/staging/prod)'
    )
    
    parser.add_argument(
        '--strip',
        action='store_true',
        help='Remove TOC and heading IDs (inverse operation)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force processing of all files (ignore timestamps)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing to files'
    )
    
    # Use parse_known_args to ignore unknown arguments from pipeline
    args, unknown = parser.parse_known_args()
    
    # Determine operation mode
    mode = "Strip" if args.strip else "Generate"
    
    # Print console header
    print("=" * 60)
    print(f"  GAZ Tank - Table of Contents {mode}")
    print("=" * 60)
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE enabled - No files will be modified")
    
    if args.force:
        print("🔄 FORCE MODE enabled - Processing all files")
    
    print()
    
    # Initialize logging
    try:
        log = get_logging_context(args.environment, 'toc', console=False)
        log.inf("Table of Contents Generator started")
        log.inf(f"Environment: {args.environment}")
        if args.strip:
            log.inf("Mode: Strip TOC and IDs")
        else:
            log.inf("Mode: Generate TOC and IDs")
        if args.dry_run:
            log.inf("DRY RUN MODE enabled")
        if args.force:
            log.inf("FORCE MODE enabled")
    except Exception as e:
        print(f"⚠️  Warning: Logging initialization failed: {e}")
        print("   Continuing without logging...")
        log = None
    
    # Load environment configuration
    try:
        from utils.gzconfig import PipelineEnvironment
        env_config: PipelineEnvironment = get_pipeline_config(args.environment)  # type: ignore
        env_dir = env_config.directory_path
        if log:
            log.dbg("Pipeline configuration loaded successfully")
            log.inf(f"Target directory: {env_dir}")
    except (FileNotFoundError, ValueError, ImportError) as e:
        error_msg = f"Configuration Error: {e}"
        print(f"❌ {error_msg}")
        if log:
            log.err(error_msg)
        return 1
    
    # Validate environment directory exists
    if not env_dir.exists():
        error_msg = f"Environment directory not found: {env_dir}"
        print(f"❌ {error_msg}")
        print(f"   Please create the directory or run a build for environment '{args.environment}'")
        if log:
            log.err(error_msg)
        return 1
    
    # Scan for HTML files in the environment directory
    print(f"📂 Scanning: {env_dir}")
    if log:
        log.inf(f"Scanning: {env_dir}")
    
    html_files = scan_html_files(env_dir)
    
    if not html_files:
        print("   No HTML files found to process")
        if log:
            log.inf("No HTML files found to process")
        return 0
    
    print(f"   Found {len(html_files)} HTML file(s)")
    print()
    if log:
        log.inf(f"Found {len(html_files)} HTML files")
    
    # Process each file
    operation = "Stripping" if args.strip else "Processing"
    print(f"{operation} HTML files...")
    if log:
        log.inf(f"{operation} HTML files...")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for html_file in html_files:
        rel_path = html_file.relative_to(env_dir)
        
        # Choose processing function based on mode
        if args.strip:
            success, message = strip_toc_from_file(html_file, dry_run=args.dry_run, force=args.force)
        else:
            success, message = process_html_file(html_file, dry_run=args.dry_run, force=args.force)
        
        if success:
            if "Skipped" in message:
                skip_count += 1
                # Choose emoji based on skip reason
                if "no h2/h3/h4 headings" in message:
                    emoji = "⚠️ "
                elif "up-to-date" in message:
                    emoji = "⏭️ "
                else:
                    emoji = "⏭️ "
                print(f"  {emoji}{rel_path}: {message}")
                if log:
                    log.dbg(f"{rel_path}: {message}")
            else:
                success_count += 1
                print(f"  ✅ {rel_path}: {message}")
                if log:
                    log.inf(f"{rel_path}: {message}")
        else:
            error_count += 1
            print(f"  ❌ {rel_path}: {message}")
            if log:
                log.err(f"{rel_path}: {message}")
    
    # Print summary
    print()
    print("=" * 60)
    print("  Summary")
    print("=" * 60)
    print(f"  Files processed:  {success_count}")
    print(f"  Files skipped:    {skip_count}")
    print(f"  Errors:           {error_count}")
    print("=" * 60)
    print()
    
    if log:
        log.inf(f"Summary: {success_count} processed, {skip_count} skipped, {error_count} errors")
    
    if error_count > 0:
        print(f"❌ TOC {mode.lower()} completed with errors")
        if log:
            log.err(f"TOC {mode.lower()} completed with errors")
        return 1
    else:
        print(f"✅ TOC {mode.lower()} completed successfully")
        if log:
            log.inf(f"TOC {mode.lower()} completed successfully")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
