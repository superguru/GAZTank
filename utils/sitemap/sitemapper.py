#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Sitemap Generator
=================
Automatically generates sitemap.xml from content files and navigation structure.

Authors: superguru, gazorper
License: GPL v3.0
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.gzlogging import get_logging_context
from utils.gzconfig import get_pipeline_config
from utils.setup.config_io import load_existing_config


def get_content_files(content_dir, log):
    """Get all HTML content files (including subdirectories)"""
    if not content_dir.exists():
        log.wrn(f"Content directory not found: {content_dir}")
        print(f"Warning: Content directory not found: {content_dir}")
        return []
    
    content_files = []
    for file in content_dir.rglob('*.html'):
        # Extract content key as relative path from content_dir (without .html extension)
        # Convert backslashes to forward slashes for URL compatibility
        relative_path = file.relative_to(content_dir)
        content_key = str(relative_path.with_suffix('')).replace('\\', '/')
        content_files.append(content_key)
    
    log.inf(f"Found {len(content_files)} content files in {content_dir}")
    return sorted(content_files)


def parse_navigation_structure(index_file, log):
    """
    Parse index.html to extract navigation hierarchy and determine priorities
    Returns dict with content_key -> {'level': int, 'priority': float}
    """
    if not index_file.exists():
        log.wrn(f"index.html not found: {index_file}")
        print(f"Warning: index.html not found: {index_file}")
        return {}
    
    with open(index_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    structure = {}
    
    # Parse line by line to find nav levels and data-content attributes
    lines = html.split('\n')
    current_level = 1
    
    for line in lines:
        # Detect nav level by looking for class="nav-level-N"
        if 'class="nav-level-' in line:
            # Extract the level number
            start = line.find('nav-level-') + 10  # length of 'nav-level-'
            end = start
            while end < len(line) and line[end].isdigit():
                end += 1
            if end > start:
                current_level = int(line[start:end])
        
        # Find data-content links
        # Look for data-content="CONTENT_KEY" in anchor tags
        if 'data-content="' in line and '<a ' in line:
            # Extract content key from data-content attribute
            start = line.find('data-content="') + 14  # length of 'data-content="'
            end = line.find('"', start)
            if end > start:
                content_key = line[start:end]
                structure[content_key] = {
                    'level': current_level,
                    'priority': calculate_priority(current_level, content_key)
                }
    
    log.inf(f"Parsed {len(structure)} navigation entries from {index_file.name}")
    return structure


def calculate_priority(level, content_key):
    """Calculate priority based on navigation level and content type"""
    # Home page always gets highest priority
    if content_key == 'home':
        return 1.0
    
    # Top-level pages (level 1)
    if level == 1:
        return 0.9
    
    # Second level pages
    if level == 2:
        # Schedule and main campaign pages get higher priority
        if 'schedule' in content_key or content_key.endswith('campaign1') or content_key.endswith('campaign2'):
            return 0.8
        return 0.7
    
    # Third level pages (missions)
    if level == 3:
        return 0.6
    
    # Fourth level pages (mission parts)
    if level == 4:
        return 0.5
    
    # Default
    return 0.5


def determine_changefreq(content_key, level):
    """Determine how often the page likely changes"""
    # Home page changes most frequently
    if content_key == 'home':
        return 'weekly'
    
    # Schedule changes frequently
    if 'schedule' in content_key:
        return 'weekly'
    
    # Active campaign pages
    if 'campaign1' in content_key or 'runs' == content_key:
        return 'weekly'
    
    # Older campaigns
    if 'campaign2' in content_key:
        return 'monthly'
    
    # Mods section
    if 'mods' in content_key:
        return 'monthly'
    
    # Static pages (about, contact)
    if content_key in ['about', 'contact', 'future']:
        return 'yearly'
    
    # Mission detail pages
    if 'mission' in content_key:
        return 'monthly'
    
    # Default
    return 'monthly'


def get_file_last_modified(content_file):
    """Get last modified date of content file"""
    if content_file.exists():
        mtime = content_file.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    return datetime.now().strftime('%Y-%m-%d')


def generate_sitemap(base_url, content_dir, index_file, output_file, log, dry_run=False):
    """Generate sitemap.xml file
    
    Args:
        base_url: Base URL for the site
        content_dir: Directory containing content files
        index_file: Path to index.html
        output_file: Path where sitemap.xml will be written
        log: Logging context
        dry_run: If True, perform all logic but don't write output file
    """
    
    log.inf("Starting sitemap generation")
    log.inf(f"Base URL: {base_url}")
    log.inf(f"Content directory: {content_dir}")
    log.inf(f"Output file: {output_file}")
    
    print("=" * 60)
    print("SITEMAP GENERATION" + (" (DRY RUN)" if dry_run else ""))
    print("=" * 60)
    if dry_run:
        print("⚠️  DRY RUN MODE enabled - No files will be modified")
    
    # Get content files
    print()
    print("\n[1/4] 📄 Scanning content files...")
    content_files = get_content_files(content_dir, log)
    print(f"       Found {len(content_files)} content files")
    
    # Parse navigation structure
    print("\n[2/4] 🗺️  Parsing navigation structure...")
    nav_structure = parse_navigation_structure(index_file, log)
    print(f"       Parsed {len(nav_structure)} navigation entries")
    
    # Create XML structure
    print("\n[3/4] 🔨 Building sitemap XML...")
    log.inf("Building sitemap XML structure")
    urlset = Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # Sort content files: home first, then by priority and name
    def sort_key(key):
        if key == 'home':
            return (0, key)
        nav_info = nav_structure.get(key, {'priority': 0.5})
        return (1 - nav_info['priority'], key)
    
    sorted_content = sorted(content_files, key=sort_key)
    
    # Generate URL entries
    for content_key in sorted_content:
        # Get navigation info
        nav_info = nav_structure.get(content_key, {'level': 1, 'priority': 0.5})
        
        # Create URL element
        url = SubElement(urlset, 'url')
        
        # Location
        loc = SubElement(url, 'loc')
        loc.text = f"{base_url}#{content_key}"
        
        # Last modified date
        lastmod = SubElement(url, 'lastmod')
        # content_key may include subdirectories (e.g., "setup/README")
        content_file = content_dir / (content_key + '.html')
        lastmod.text = get_file_last_modified(content_file)
        
        # Change frequency
        changefreq = SubElement(url, 'changefreq')
        changefreq.text = determine_changefreq(content_key, nav_info['level'])
        
        # Priority
        priority = SubElement(url, 'priority')
        priority.text = str(nav_info['priority'])
    
    # Pretty print XML
    print(f"\n[4/4] {'📝 Writing sitemap file...' if not dry_run else '👁️  Preparing sitemap (dry-run)...'}")
    
    xml_string = tostring(urlset, encoding='utf-8')
    dom = minidom.parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent='    ', encoding='utf-8')
    
    # Remove extra blank lines
    pretty_lines = [line for line in pretty_xml.decode('utf-8').split('\n') if line.strip()]
    pretty_xml = '\n'.join(pretty_lines) + '\n'
    
    # Write to file (or skip if dry-run)
    if not dry_run:
        log.inf(f"Writing sitemap to {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        print(f"       ✅ Sitemap written to: {output_file}")
        print(f"       ✅ Total URLs: {len(sorted_content)}")
        log.inf(f"Sitemap generation complete: {len(sorted_content)} URLs written to {output_file}")
    else:
        log.inf(f"Dry-run complete: {len(sorted_content)} URLs prepared (not written)")
        print(f"       ⚠️  Would write to: {output_file}")
        print(f"       ⚠️  Total URLs that would be included: {len(sorted_content)}")
    
    # Show summary
    print("\n" + "=" * 60)
    print("✅ SITEMAP GENERATION COMPLETE" + (" (DRY RUN)" if dry_run else ""))
    print("=" * 60)
    if dry_run:
        print("⚠️  DRY RUN: No files were written")
    print(f"📄 Output: {output_file}")
    print(f"🔗 URLs included: {len(sorted_content)}")
    print(f"🌐 Base URL: {base_url}")
    if not dry_run:
        print("\n✨ Next steps:")
        print("   1. Review the generated sitemap.xml")
        print(r"   2. Run scripts\package.cmd to include it in deployment")
        print("   3. After deploying, submit to:")
        print("      - Google Search Console")
        print("      - Bing Webmaster Tools")
    else:
        print("\n✨ Next steps:")
        print("   1. Run without --dry-run to generate the actual file")
        print(f"   2. Command: scripts\\generate_sitemap.cmd -e {log.environment}")
    print("=" * 60)


def get_project_root():
    """Get the project root directory"""
    current_file = Path(__file__).resolve()
    return current_file.parent.parent.parent


def is_sitemap_outdated(output_file: Path, content_dir: Path, index_file: Path, log=None) -> bool:
    """
    Check if sitemap needs to be regenerated.
    
    Args:
        output_file: Path to sitemap.xml output file
        content_dir: Path to content directory with HTML files
        index_file: Path to index.html file
        log: Optional logging context
        
    Returns:
        True if sitemap needs regeneration, False if up to date
    """
    # If output doesn't exist, needs generation
    if not output_file.exists():
        if log:
            log.inf("Sitemap does not exist, needs generation")
        return True
    
    # Get sitemap modification time
    sitemap_mtime = output_file.stat().st_mtime
    
    # Check if index.html is newer
    if index_file.exists():
        if index_file.stat().st_mtime > sitemap_mtime:
            if log:
                log.inf("index.html is newer than sitemap, needs regeneration")
            return True
    
    # Check if any HTML file in content/ is newer
    for html_file in content_dir.rglob('*.html'):
        if html_file.stat().st_mtime > sitemap_mtime:
            if log:
                log.inf(f"Content file {html_file.name} is newer than sitemap, needs regeneration")
            return True
    
    if log:
        log.inf("Sitemap is up to date, no regeneration needed")
    return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Sitemap generator - creates sitemap.xml for search engines',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m sitemap -e dev                 # Generate sitemap (skip if up to date)
  python -m sitemap -e dev --force         # Force regeneration
  python -m sitemap -e staging             # Generate sitemap for staging
  python -m sitemap -e prod                # Generate sitemap for production
  python -m sitemap -e dev --dry-run       # Preview without writing files

Environments are configured in config/environments.toml
        """
    )
    
    parser.add_argument(
        '-e', '--environment',
        required=True,
        choices=['dev', 'staging', 'prod'],
        help='Environment to generate sitemap for (dev/staging/prod)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without writing any files'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force regeneration even if sitemap is up to date'
    )
    
    # Use parse_known_args to ignore unknown arguments from pipeline
    args, unknown = parser.parse_known_args()
    
    # Initialize logging
    try:
        log = get_logging_context(args.environment, 'sitemapper', console=True)
        log.inf("Sitemap Generator started")
        log.inf(f"Environment: {args.environment}")
        if args.dry_run:
            log.inf("DRY RUN MODE enabled")
    except Exception as e:
        print(f"✗ Logging Error: {e}")
        print("  Continuing without logging...")
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
        if log:
            log.err(f"Configuration Error: {e}")
        else:
            print(f"✗ Configuration Error: {e}")
        return 1
    
    if not env_dir.exists():
        error_msg = f"Environment directory not found: {env_dir}\nPlease create the directory or run a build for environment '{args.environment}'"
        if log:
            log.err(error_msg)
        else:
            print(f"✗ Error: {error_msg}")
        return 1
    
    # Define paths
    project_root = get_project_root()
    content_dir = env_dir / 'content'
    index_file = env_dir / 'index.html'
    output_file = env_dir / 'sitemap.xml'
    
    # Load site configuration to get canonical base URL
    try:
        site_config = load_existing_config()
        base_url = site_config.get('canonical_base', 'https://gaztank.org/')
        if log:
            log.inf(f"Using base URL from site config: {base_url}")
    except Exception as e:
        base_url = 'https://gaztank.org/'
        if log:
            log.wrn(f"Could not load site config, using default base URL: {base_url}")
        print(f"⚠️  Warning: Could not load site config, using default base URL: {base_url}")
    
    # Validate directories exist
    if not content_dir.exists():
        error_msg = f"Content directory not found: {content_dir}"
        if log:
            log.err(error_msg)
        else:
            print(f"ERROR: {error_msg}")
        return 1
    
    if not index_file.exists():
        error_msg = f"index.html not found: {index_file}"
        if log:
            log.err(error_msg)
        else:
            print(f"ERROR: {error_msg}")
        return 1
    
    # Check if sitemap needs regeneration (unless --force or --dry-run)
    if not args.force and not args.dry_run:
        if not is_sitemap_outdated(output_file, content_dir, index_file, log):
            print("✓ Sitemap is up to date, no regeneration needed")
            print(f"  Use --force to regenerate anyway")
            if log:
                log.inf("Sitemap is up to date, skipping regeneration")
            return 0
    
    # Generate sitemap
    try:
        generate_sitemap(base_url, content_dir, index_file, output_file, log, dry_run=args.dry_run)
        if log:
            log.inf("Sitemap Generator completed successfully")
        return 0
    except Exception as e:
        if log:
            log.err(f"Sitemap generation failed: {e}")
        else:
            print(f"❌ ERROR: Sitemap generation failed: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
