#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Website Packager
================
Core packaging logic for preparing website files for deployment.

Packages the specified environment directory by:
- Removing orphaned files not present in source
- Minifying CSS and JavaScript assets
- Creating timestamped backup archives
- Managing backup retention

This module does NOT perform generation, validation, or sitemap creation.
Those are separate pipeline steps that must run before packaging.

Authors: superguru, gazorper
License: GPL v3.0
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional
import zipfile

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.gzlogging import get_logging_context
from utils.gzconfig import get_pipeline_config, PipelineEnvironment

# Try to import minification libraries
try:
    import rcssmin
    CSSMIN_AVAILABLE = True
except ImportError:
    CSSMIN_AVAILABLE = False

try:
    import rjsmin
    JSMIN_AVAILABLE = True
except ImportError:
    JSMIN_AVAILABLE = False

# Global logging context
log = None


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent


def backup_previous_package(
    env_dir: Path,
    packages_dir: Path,
    environment: str,
    max_backups: int = 3,
    dry_run: bool = False
) -> Optional[Path]:
    """
    Create a timestamped zip backup of the current environment directory.
    
    Args:
        env_dir: Environment directory to backup
        packages_dir: Directory to store backup packages
        environment: Environment name (dev/staging/prod)
        max_backups: Maximum number of backups to keep
        dry_run: If True, don't actually create backup
        
    Returns:
        Path to created backup file, or None if no backup created
    """
    # Check if environment directory exists and has content
    if not env_dir.exists() or not any(env_dir.iterdir()):
        print("  No content to backup")
        if log:
            log.inf("No content to backup")
        return None
    
    # Create packages directory if it doesn't exist
    if not dry_run:
        packages_dir.mkdir(exist_ok=True)
    
    # Create timestamp for backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"package_{environment}_{timestamp}.zip"
    backup_path = packages_dir / backup_filename
    
    if dry_run:
        print(f"  📦 [DRY RUN] Would create backup: {backup_filename}")
        if log:
            log.inf(f"[DRY RUN] Would create backup: {backup_filename}")
        return backup_path
    
    print(f"  📦 Creating backup: {backup_filename}")
    if log:
        log.inf(f"Creating backup: {backup_filename}")
    
    # Create zip file of current environment directory
    file_count = 0
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in env_dir.rglob('*'):
            if item.is_file():
                arcname = item.relative_to(env_dir)
                zipf.write(item, arcname)
                file_count += 1
    
    print(f"  ✓ Backup created with {file_count} files")
    if log:
        log.inf(f"Backup created with {file_count} files: {backup_filename}")
    
    # Clean up old backups, keeping only the most recent ones
    cleanup_old_backups(packages_dir, environment, max_backups, dry_run)
    
    return backup_path


def cleanup_old_backups(
    packages_dir: Path,
    environment: str,
    max_backups: int = 3,
    dry_run: bool = False
) -> None:
    """
    Keep only the most recent N backup files for a specific environment.
    
    Args:
        packages_dir: Directory containing backup packages
        environment: Environment name (dev/staging/prod)
        max_backups: Maximum number of backups to keep
        dry_run: If True, don't actually delete files
    """
    # Get all backup zip files for this environment sorted by modification time (newest first)
    backup_files = sorted(
        [f for f in packages_dir.glob(f"package_{environment}_*.zip")],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    # Remove old backups beyond max_backups
    if len(backup_files) > max_backups:
        removed_count = len(backup_files) - max_backups
        if dry_run:
            print(f"  🗑️  [DRY RUN] Would clean up {removed_count} old backup(s) (keeping {max_backups} most recent)")
            if log:
                log.inf(f"[DRY RUN] Would clean up {removed_count} old backups (keeping {max_backups} most recent)")
        else:
            print(f"  🗑️  Cleaning up {removed_count} old backup(s) (keeping {max_backups} most recent)")
            if log:
                log.inf(f"Cleaning up {removed_count} old backups (keeping {max_backups} most recent)")
            for old_backup in backup_files[max_backups:]:
                old_backup.unlink()
                if log:
                    log.dbg(f"Deleted old backup: {old_backup.name}")


def minify_css(src_file: Path, dest_file: Path, dry_run: bool = False) -> Tuple[int, int, float]:
    """
    Minify a CSS file using rcssmin.
    
    Args:
        src_file: Source CSS file path
        dest_file: Destination CSS file path
        dry_run: If True, don't actually write file
        
    Returns:
        Tuple of (original_size, minified_size, savings_percent)
    """
    if not CSSMIN_AVAILABLE:
        # Copy original file if minification library not available
        if not dry_run:
            shutil.copy2(src_file, dest_file)
        return 0, 0, 0
    
    try:
        with open(src_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Minify
        import rcssmin as css_minifier
        minified = css_minifier.cssmin(css_content)
        
        # Ensure minified is a string
        if isinstance(minified, bytes):
            minified_str = minified.decode('utf-8')
        else:
            minified_str = str(minified)
        
        # Write minified version (unless dry-run)
        if not dry_run:
            with open(dest_file, 'w', encoding='utf-8') as f:
                f.write(minified_str)
        
        # Calculate savings
        original_size = len(css_content)
        minified_size = len(minified_str)
        savings = ((original_size - minified_size) / original_size) * 100 if original_size > 0 else 0
        
        return original_size, minified_size, savings
    except Exception as e:
        print(f"    ⚠️  Warning: Could not minify {src_file.name}: {e}")
        if log:
            log.wrn(f"Could not minify {src_file.name}: {e}")
        # Copy original file if minification fails
        if not dry_run:
            shutil.copy2(src_file, dest_file)
        return 0, 0, 0


def minify_js(src_file: Path, dest_file: Path, dry_run: bool = False) -> Tuple[int, int, float]:
    """
    Minify a JavaScript file using rjsmin.
    
    Args:
        src_file: Source JS file path
        dest_file: Destination JS file path
        dry_run: If True, don't actually write file
        
    Returns:
        Tuple of (original_size, minified_size, savings_percent)
    """
    if not JSMIN_AVAILABLE:
        # Copy original file if minification library not available
        if not dry_run:
            shutil.copy2(src_file, dest_file)
        return 0, 0, 0
    
    try:
        with open(src_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Minify
        import rjsmin as js_minifier
        minified = js_minifier.jsmin(js_content)
        
        # Ensure minified is a string
        if isinstance(minified, bytes):
            minified_str = minified.decode('utf-8')
        else:
            minified_str = str(minified)
        
        # Write minified version (unless dry-run)
        if not dry_run:
            with open(dest_file, 'w', encoding='utf-8') as f:
                f.write(minified_str)
        
        # Calculate savings
        original_size = len(js_content)
        minified_size = len(minified_str)
        savings = ((original_size - minified_size) / original_size) * 100 if original_size > 0 else 0
        
        return original_size, minified_size, savings
    except Exception as e:
        print(f"    ⚠️  Warning: Could not minify {src_file.name}: {e}")
        if log:
            log.wrn(f"Could not minify {src_file.name}: {e}")
        # Copy original file if minification fails
        if not dry_run:
            shutil.copy2(src_file, dest_file)
        return 0, 0, 0


def minify_assets(env_dir: Path, dry_run: bool = False) -> None:
    """
    Minify CSS and JavaScript files in environment directory.
    
    Args:
        env_dir: Environment directory to process
        dry_run: If True, don't actually write files
    """
    print("\n[2.5/3] Minifying CSS and JavaScript files...")
    if log:
        log.inf("Minifying CSS and JavaScript files")
    
    if not CSSMIN_AVAILABLE and not JSMIN_AVAILABLE:
        print("  ⚠️  Minification libraries not installed")
        print("  Install with: pip install rcssmin rjsmin")
        print("  Skipping minification...")
        if log:
            log.wrn("Minification libraries not installed, skipping")
        return
    
    css_files = list(env_dir.rglob('*.css'))
    js_files = list(env_dir.rglob('*.js'))
    
    total_original = 0
    total_minified = 0
    
    # Minify CSS files
    if CSSMIN_AVAILABLE and css_files:
        action = "[DRY RUN] Would minify" if dry_run else "Minifying"
        print(f"  {action} {len(css_files)} CSS file(s)...")
        if log:
            log.inf(f"{action} {len(css_files)} CSS files")
        for css_file in css_files:
            original, minified, savings = minify_css(css_file, css_file, dry_run)
            if original > 0:
                total_original += original
                total_minified += minified
                print(f"    {css_file.name}: {original:,} → {minified:,} bytes ({savings:.1f}% smaller)")
    elif not CSSMIN_AVAILABLE and css_files:
        print(f"  ⚠️  rcssmin not available, skipping {len(css_files)} CSS file(s)")
        if log:
            log.wrn(f"rcssmin not available, skipping {len(css_files)} CSS files")
    
    # Minify JS files
    if JSMIN_AVAILABLE and js_files:
        action = "[DRY RUN] Would minify" if dry_run else "Minifying"
        print(f"  {action} {len(js_files)} JavaScript file(s)...")
        if log:
            log.inf(f"{action} {len(js_files)} JavaScript files")
        for js_file in js_files:
            original, minified, savings = minify_js(js_file, js_file, dry_run)
            if original > 0:
                total_original += original
                total_minified += minified
                print(f"    {js_file.name}: {original:,} → {minified:,} bytes ({savings:.1f}% smaller)")
    elif not JSMIN_AVAILABLE and js_files:
        print(f"  ⚠️  rjsmin not available, skipping {len(js_files)} JS file(s)")
        if log:
            log.wrn(f"rjsmin not available, skipping {len(js_files)} JS files")
    
    # Show total savings
    if total_original > 0:
        total_savings = ((total_original - total_minified) / total_original) * 100
        if dry_run:
            print(f"  ℹ️  [DRY RUN] Would achieve: {total_original:,} → {total_minified:,} bytes ({total_savings:.1f}% reduction)")
            if log:
                log.inf(f"[DRY RUN] Would achieve: {total_original:,} → {total_minified:,} bytes ({total_savings:.1f}% reduction)")
        else:
            print(f"  ✓ Total: {total_original:,} → {total_minified:,} bytes ({total_savings:.1f}% reduction)")
            if log:
                log.inf(f"Total minification: {total_original:,} → {total_minified:,} bytes ({total_savings:.1f}% reduction)")
    else:
        print("  ✓ No files minified")
        if log:
            log.inf("No files minified")


def update_package_metadata(env_dir: Path, environment: str, dry_run: bool = False) -> None:
    """
    Create/update package metadata timestamp file.
    
    Creates a '.metainfo' directory in the environment and writes the environment
    name to a file named '<environment>.txt' to track when packaging last occurred.
    
    Args:
        env_dir: Environment directory path
        environment: Environment name (dev/staging/prod)
        dry_run: If True, don't actually create/update files
    """
    if dry_run:
        print("  ℹ️  [DRY RUN] Would update package metadata")
        if log:
            log.inf("[DRY RUN] Would update package metadata timestamp")
        return
    
    # Create .metainfo directory if it doesn't exist
    meta_dir = env_dir / '.metainfo'
    meta_dir.mkdir(exist_ok=True)
    
    # Write environment name to the timestamp file
    timestamp_file = meta_dir / f"{environment}.txt"
    timestamp_file.write_text(environment, encoding='utf-8')
    
    if log:
        log.dbg(f"Updated package metadata: {timestamp_file.relative_to(env_dir.parent)}")


def package_site(environment: str, force: bool = False, dry_run: bool = False) -> bool:
    """
    Package the website from src to environment directory.
    
    Args:
        environment: Environment name (dev/staging/prod)
        force: If True, copy all files regardless of timestamps
        dry_run: If True, show what would be done without doing it
        
    Returns:
        True if packaging succeeded, False otherwise
    """
    global log
    
    # Initialize logging
    try:
        log = get_logging_context(environment, 'package', console=False)
        log.inf("Website Packager started")
        log.inf(f"Environment: {environment}")
        if dry_run:
            log.inf("DRY RUN MODE enabled")
        if force:
            log.inf("FORCE MODE enabled")
    except Exception as e:
        print(f"⚠️  Warning: Logging initialization failed: {e}")
        print("   Continuing without logging...")
        log = None
    
    # Define paths
    project_root = get_project_root()
    
    # Load environment configuration
    try:
        env_config: PipelineEnvironment = get_pipeline_config(environment)  # type: ignore
        env_dir = env_config.directory_path
        if log:
            log.dbg("Pipeline configuration loaded successfully")
            log.inf(f"Target directory: {env_dir}")
    except (FileNotFoundError, ValueError, ImportError) as e:
        error_msg = f"Configuration Error: {e}"
        print(f"❌ {error_msg}")
        if log:
            log.err(error_msg)
        return False
    
    src_dir = project_root / 'src'
    publish_dir = project_root / 'publish'
    packages_dir = publish_dir / 'packages'
    
    print("=" * 60)
    print("  GAZ Tank - Website Packager")
    print("=" * 60)
    if dry_run:
        print("⚠️  DRY RUN MODE enabled - No files will be modified")
    if force:
        print("🔄 FORCE MODE enabled - Processing all files")
    print()
    
    if log:
        log.inf(f"Project root: {project_root}")
        log.inf(f"Source directory: {src_dir}")
        log.inf(f"Environment directory: {env_dir}")
    
    # Step 1: Identify and remove orphaned files
    print("\n[1/3] Checking for orphaned files...")
    if log:
        log.inf("Checking for orphaned files")
    
    if not src_dir.exists():
        print(f"\n✗ ERROR: Source directory not found: {src_dir}")
        if log:
            log.err(f"Source directory not found: {src_dir}")
        print("=" * 60)
        return False
    
    # Create environment directory if it doesn't exist
    if not env_dir.exists():
        if dry_run:
            print(f"  📁 [DRY RUN] Would create environment directory: {env_dir}")
            if log:
                log.inf(f"[DRY RUN] Would create environment directory: {env_dir}")
        else:
            print(f"  📁 Creating environment directory: {env_dir}")
            env_dir.mkdir(parents=True, exist_ok=True)
            if log:
                log.inf(f"Created environment directory: {env_dir}")
    
    # Step 2: Copy modified or new files from src to environment
    print("\n[2/3] Copying modified and new files...")
    if log:
        log.inf("Copying modified and new files")
    
    copied_count = 0
    skipped_count = 0
    
    for item in src_dir.rglob('*'):
        if item.is_file():
            relative_path = item.relative_to(src_dir)
            
            # Skip files in components directory (composition source files)
            if str(relative_path).startswith('components' + str(Path('/')) ) or str(relative_path).startswith('components\\'):
                continue
            
            target_path = env_dir / relative_path
            
            # Check if we need to copy this file
            should_copy = False
            
            if force:
                # Force mode: always copy
                should_copy = True
            elif not target_path.exists():
                # Target doesn't exist: copy
                should_copy = True
            else:
                # Compare modification times
                src_mtime = item.stat().st_mtime
                target_mtime = target_path.stat().st_mtime
                
                if src_mtime > target_mtime:
                    # Source is newer: copy
                    should_copy = True
            
            if should_copy:
                if not dry_run:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target_path)
                copied_count += 1
            else:
                skipped_count += 1
    
    if dry_run:
        print(f"  ℹ️  [DRY RUN] Would copy {copied_count} modified/new files")
        print(f"  ℹ️  [DRY RUN] Would skip {skipped_count} unchanged files")
        if log:
            log.inf(f"[DRY RUN] Would copy {copied_count} modified/new files, skip {skipped_count} unchanged files")
    else:
        print(f"  ✓ Copied {copied_count} modified/new files")
        print(f"  ✓ Skipped {skipped_count} unchanged files")
        if log:
            log.inf(f"Copied {copied_count} modified/new files, skipped {skipped_count} unchanged files")
    
    # Step 2.5: Minify CSS and JavaScript files
    minify_assets(env_dir, dry_run)
    
    # Step 2.6: Update package metadata timestamp
    update_package_metadata(env_dir, environment, dry_run)
    
    # Step 3: Create backup of this package
    print("\n[3/3] Creating package archive...")
    if log:
        log.inf("Creating package archive")
    
    backup_path = backup_previous_package(env_dir, packages_dir, environment, max_backups=4, dry_run=dry_run)
    
    print("\n" + "=" * 60)
    if dry_run:
        print("ℹ️  DRY RUN COMPLETED")
        print("=" * 60)
        print("  No files were modified")
        if log:
            log.inf("Dry-run completed: No files were modified")
    else:
        print("✅ PACKAGING COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"  Environment directory: {env_dir.resolve()}")
        if backup_path:
            print(f"  Package file: {backup_path.resolve()}")
        if log:
            log.inf("Website Packager completed successfully")
            log.inf(f"Environment directory: {env_dir.resolve()}")
            if backup_path:
                log.inf(f"Package file: {backup_path.resolve()}")
    
    return True


def main():
    """Main entry point for the packager"""
    parser = argparse.ArgumentParser(
        description='Website Packager - Build, validate, and package website for deployment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m package -e dev                # Package for dev environment
  python -m package -e staging            # Package for staging environment
  python -m package -e prod               # Package for production environment
  python -m package -e dev --force        # Force package all files
  python -m package -e dev --dry-run      # Preview changes without modifying files

Environments are configured in config/pipeline.toml
        """
    )
    
    parser.add_argument(
        '-e', '--environment',
        required=True,
        choices=['dev', 'staging', 'prod'],
        help='Environment to package (dev/staging/prod)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force packaging of all files (ignore timestamps)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing to files'
    )
    
    # Use parse_known_args to ignore unknown arguments from pipeline
    args, unknown = parser.parse_known_args()
    
    # Run packaging
    success = package_site(args.environment, force=args.force, dry_run=args.dry_run)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
