#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Environment Cleaner
===================
Identifies and removes orphaned files from environment directories.

Orphaned files are files that exist in the environment directory
but no longer exist in the source directory. This ensures the
environment stays synchronized with src/ as the source of truth.

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
import argparse
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.gzlogging import get_logging_context
from utils.gzconfig import get_pipeline_config, PipelineEnvironment

# Global logging context
log = None


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent


def get_orphaned_files(src_dir: Path, env_dir: Path) -> List[Path]:
    """
    Identify files in env_dir that no longer exist in src_dir (orphaned files).
    
    Args:
        src_dir: Source directory (src/)
        env_dir: Environment directory (publish/environment/)
        
    Returns:
        List of orphaned file paths
    """
    # Build set of all files in source (excluding src/components - composition source files)
    src_files = set()
    for item in src_dir.rglob('*'):
        if item.is_file():
            relative_path = item.relative_to(src_dir)
            # Skip files in components directory
            if not str(relative_path).startswith('components' + str(Path('/')) ) and not str(relative_path).startswith('components\\'):
                src_files.add(relative_path)
    
    # Find files in environment that don't exist in source
    orphaned_files = []
    for item in env_dir.rglob('*'):
        if item.is_file():
            relative_path = item.relative_to(env_dir)
            if relative_path not in src_files:
                orphaned_files.append(item)
    
    return orphaned_files


def remove_all_files(env_dir: Path, dry_run: bool = False, force: bool = False) -> tuple[int, int]:
    """
    Remove all files and directories from environment directory.
    
    Args:
        env_dir: Environment directory to clean
        dry_run: If True, don't actually remove files
        force: If True, skip confirmation prompt
        
    Returns:
        Tuple of (files_removed, directories_removed)
    """
    # Count files and directories
    all_files = list(env_dir.rglob('*'))
    file_count = sum(1 for item in all_files if item.is_file())
    dir_count = sum(1 for item in all_files if item.is_dir())
    
    if file_count == 0:
        print("  ✓ Environment directory is already empty")
        if log:
            log.inf("Environment directory is already empty")
        return (0, 0)
    
    if dry_run:
        print(f"  🗑️  [DRY RUN] Would remove ALL {file_count} file(s) and {dir_count} directory(ies)")
        if log:
            log.inf(f"[DRY RUN] Would remove ALL {file_count} files and {dir_count} directories")
        
        # Show sample of files
        files = [item for item in all_files if item.is_file()]
        sample_size = min(5, len(files))
        for file_path in files[:sample_size]:
            print(f"    • {file_path.relative_to(env_dir)}")
        if len(files) > sample_size:
            print(f"    ... and {len(files) - sample_size} more")
        
        return (file_count, dir_count)
    
    # Confirmation prompt unless force is enabled
    if not force:
        print(f"\n⚠️  WARNING: This will DELETE ALL {file_count} file(s) and {dir_count} directory(ies)")
        print(f"  from: {env_dir}")
        response = input("\n  Type 'yes' to confirm deletion: ")
        if response.lower() != 'yes':
            print("  ❌ Operation cancelled")
            if log:
                log.inf("Clean-all operation cancelled by user")
            return (0, 0)
        print()
    
    print(f"  🗑️  Removing ALL {file_count} file(s) and {dir_count} directory(ies)...")
    if log:
        log.inf(f"Removing ALL {file_count} files and {dir_count} directories")
    
    # Remove all files
    removed_files = 0
    for item in all_files:
        if item.is_file():
            try:
                item.unlink()
                removed_files += 1
                if log:
                    log.dbg(f"Removed: {item.relative_to(env_dir)}")
            except Exception as e:
                print(f"    ⚠️  Warning: Could not remove {item.name}: {e}")
                if log:
                    log.wrn(f"Could not remove {item.name}: {e}")
    
    # Remove all directories (bottom-up)
    removed_dirs = 0
    for item in sorted(all_files, reverse=True):
        if item.is_dir() and item.exists():
            try:
                item.rmdir()
                removed_dirs += 1
                if log:
                    log.dbg(f"Removed directory: {item.relative_to(env_dir)}")
            except Exception as e:
                if log:
                    log.wrn(f"Could not remove directory {item.name}: {e}")
    
    print(f"  ✓ Removed {removed_files} file(s) and {removed_dirs} directory(ies)")
    if log:
        log.inf(f"Removed {removed_files} files and {removed_dirs} directories")
    
    return (removed_files, removed_dirs)


def remove_orphaned_files(env_dir: Path, orphaned_files: List[Path], dry_run: bool = False, force: bool = False) -> int:
    """
    Remove orphaned files and empty directories from environment directory.
    
    Args:
        env_dir: Environment directory
        orphaned_files: List of orphaned file paths
        dry_run: If True, don't actually remove files
        force: If True, skip confirmation prompt
        
    Returns:
        Number of directories removed (0 if dry_run)
    """
    if not orphaned_files:
        print("  ✓ No orphaned files found")
        if log:
            log.inf("No orphaned files found")
        return 0
    
    if dry_run:
        print(f"  🗑️  [DRY RUN] Would remove {len(orphaned_files)} orphaned file(s)")
        if log:
            log.inf(f"[DRY RUN] Would remove {len(orphaned_files)} orphaned files")
        
        # Show sample of files that would be removed
        sample_size = min(5, len(orphaned_files))
        for file_path in orphaned_files[:sample_size]:
            print(f"    • {file_path.relative_to(env_dir)}")
        if len(orphaned_files) > sample_size:
            print(f"    ... and {len(orphaned_files) - sample_size} more")
        
        return 0
    
    # Confirmation prompt unless force is enabled
    if not force:
        print(f"\n⚠️  WARNING: This will DELETE {len(orphaned_files)} orphaned file(s)")
        print(f"  from: {env_dir}")
        
        # Show sample of files that will be removed
        sample_size = min(5, len(orphaned_files))
        for file_path in orphaned_files[:sample_size]:
            print(f"    • {file_path.relative_to(env_dir)}")
        if len(orphaned_files) > sample_size:
            print(f"    ... and {len(orphaned_files) - sample_size} more")
        
        response = input("\n  Type 'yes' to confirm deletion: ")
        if response.lower() != 'yes':
            print("  ❌ Operation cancelled")
            if log:
                log.inf("Clean-orphaned operation cancelled by user")
            return 0
        print()
    
    print(f"  🗑️  Removing {len(orphaned_files)} orphaned file(s)...")
    if log:
        log.inf(f"Removing {len(orphaned_files)} orphaned files")
    
    # Remove files
    removed_count = 0
    for file_path in orphaned_files:
        try:
            file_path.unlink()
            removed_count += 1
            if log:
                log.dbg(f"Removed: {file_path.relative_to(env_dir)}")
        except Exception as e:
            print(f"    ⚠️  Warning: Could not remove {file_path.name}: {e}")
            if log:
                log.wrn(f"Could not remove {file_path.name}: {e}")
    
    # Remove empty directories
    dir_count = 0
    for item in sorted(env_dir.rglob('*'), reverse=True):
        if item.is_dir() and not any(item.iterdir()):
            try:
                item.rmdir()
                dir_count += 1
                if log:
                    log.dbg(f"Removed empty directory: {item.relative_to(env_dir)}")
            except Exception:
                pass
    
    if dir_count > 0:
        print(f"  ✓ Removed {removed_count} file(s) and {dir_count} empty directory(ies)")
        if log:
            log.inf(f"Removed {removed_count} files and {dir_count} empty directories")
    else:
        print(f"  ✓ Removed {removed_count} file(s)")
        if log:
            log.inf(f"Removed {removed_count} files")
    
    return dir_count


def clean_site(environment: str, force: bool = False, dry_run: bool = False, clean_all: bool = False, clean_orphaned: bool = False) -> bool:
    """
    Clean orphaned files or all files from environment directory.
    
    Args:
        environment: Environment name (dev/staging/prod)
        force: If True, skip confirmation prompts
        dry_run: If True, show what would be done without doing it
        clean_all: If True, remove all files (not just orphaned ones)
        clean_orphaned: If True, remove orphaned files (with confirmation unless force is set)
        
    Returns:
        True if cleaning succeeded, False otherwise
    """
    global log
    
    # Initialize logging
    try:
        log = get_logging_context(environment, 'clean', console=False)
        log.inf("Environment Cleaner started")
        log.inf(f"Environment: {environment}")
        if clean_all:
            log.inf("CLEAN ALL MODE enabled")
        if clean_orphaned:
            log.inf("CLEAN ORPHANED MODE enabled")
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
    
    print("=" * 60)
    print("  GAZ Tank - Environment Cleaner")
    print("=" * 60)
    if clean_all:
        print("⚠️  CLEAN ALL MODE - Will remove ALL files in environment")
    elif clean_orphaned:
        print("ℹ️  CLEAN ORPHANED MODE - Will remove orphaned files")
    if dry_run:
        print("⚠️  DRY RUN MODE enabled - No files will be modified")
    if force:
        print("🔄 FORCE MODE enabled")
    print()
    
    if log:
        log.inf(f"Project root: {project_root}")
        log.inf(f"Source directory: {src_dir}")
        log.inf(f"Environment directory: {env_dir}")
    
    # Verify source directory exists
    if not src_dir.exists():
        print(f"\n❌ ERROR: Source directory not found: {src_dir}")
        if log:
            log.err(f"Source directory not found: {src_dir}")
        print("=" * 60)
        return False
    
    # Verify environment directory exists
    if not env_dir.exists():
        print(f"\n✓ Environment directory does not exist: {env_dir}")
        print("  Nothing to clean")
        if log:
            log.inf(f"Environment directory does not exist: {env_dir}")
            log.inf("Nothing to clean")
        print("\n" + "=" * 60)
        print("✅ CLEANING COMPLETED")
        print("=" * 60)
        if log:
            log.inf("Environment Cleaner completed successfully")
        return True
    
    # Handle clean-all mode
    if clean_all:
        print("\nRemoving ALL files from environment directory...")
        if log:
            log.inf("Clean-all mode: Removing all files")
        
        files_removed, dir_count = remove_all_files(env_dir, dry_run, force)
        orphaned_files = []  # For summary
        file_count = files_removed
    elif clean_orphaned:
        # Identify orphaned files
        print("\nIdentifying orphaned files...")
        if log:
            log.inf("Identifying orphaned files")
        
        orphaned_files = get_orphaned_files(src_dir, env_dir)
        
        # Remove orphaned files
        dir_count = remove_orphaned_files(env_dir, orphaned_files, dry_run, force)
        file_count = len(orphaned_files)
    else:
        # Just identify orphaned files but don't remove them
        print("\nIdentifying orphaned files...")
        if log:
            log.inf("Identifying orphaned files (no deletion)")
        
        orphaned_files = get_orphaned_files(src_dir, env_dir)
        
        if orphaned_files:
            print(f"  ℹ️  Found {len(orphaned_files)} orphaned file(s)")
            
            # Show sample of files
            sample_size = min(5, len(orphaned_files))
            for file_path in orphaned_files[:sample_size]:
                print(f"    • {file_path.relative_to(env_dir)}")
            if len(orphaned_files) > sample_size:
                print(f"    ... and {len(orphaned_files) - sample_size} more")
            
            print(f"\n  ℹ️  Use --clean-orphaned to remove these files")
            if log:
                log.inf(f"Found {len(orphaned_files)} orphaned files (not removed)")
        else:
            print("  ✓ No orphaned files found")
            if log:
                log.inf("No orphaned files found")
        
        file_count = 0
        dir_count = 0
    
    # Summary
    print("\n" + "=" * 60)
    if dry_run:
        print("ℹ️  DRY RUN COMPLETED")
        print("=" * 60)
        print("  No files were modified")
        if clean_all:
            print(f"  Would remove: ALL {file_count} file(s)")
        elif clean_orphaned:
            print(f"  Would remove: {file_count} orphaned file(s)")
        else:
            print(f"  Found: {len(orphaned_files)} orphaned file(s)")
        if log:
            log.inf("Dry-run completed: No files were modified")
            if clean_all or clean_orphaned:
                log.inf(f"Would remove: {file_count} files")
    else:
        print("✅ CLEANING COMPLETED")
        print("=" * 60)
        print(f"  Environment directory: {env_dir.resolve()}")
        if clean_all:
            print(f"  Removed: ALL {file_count} file(s)")
        elif clean_orphaned:
            print(f"  Removed: {file_count} orphaned file(s)")
        else:
            print(f"  Found: {len(orphaned_files)} orphaned file(s)")
        if dir_count > 0:
            print(f"  Removed: {dir_count} directory(ies)")
        if log:
            log.inf("Environment Cleaner completed successfully")
            if clean_all or clean_orphaned:
                log.inf(f"Removed: {file_count} files")
                if dir_count > 0:
                    log.inf(f"Removed: {dir_count} directories")
            else:
                log.inf(f"Found: {len(orphaned_files)} orphaned files (not removed)")
    
    return True


def main():
    """Main entry point for the cleaner"""
    parser = argparse.ArgumentParser(
        description='Environment Cleaner - Remove orphaned files from environment directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m clean -e dev                         # Identify orphaned files (no deletion)
  python -m clean -e dev --clean-orphaned        # Remove orphaned files (prompts for confirmation)
  python -m clean -e dev --clean-orphaned --force  # Remove orphaned files (no confirmation)
  python -m clean -e dev --dry-run               # Preview without modifying files
  python -m clean -e dev --clean-all             # Remove ALL files (prompts for confirmation)
  python -m clean -e dev --clean-all --force     # Remove ALL files (no confirmation)

Orphaned files are files that exist in publish/{environment}/ but not in src/.
This ensures the environment directory stays synchronized with the source.

By default (no flags), the tool only identifies orphaned files without removing them.
Use --clean-orphaned to actually remove the orphaned files (with confirmation prompt).
Use --clean-all to remove ALL files from the environment (not just orphaned ones).

The --force flag skips confirmation prompts for both --clean-orphaned and --clean-all.

Environments are configured in config/pipeline.toml
        """
    )
    
    parser.add_argument(
        '-e', '--environment',
        required=True,
        choices=['dev', 'staging', 'prod'],
        help='Environment to clean (dev/staging/prod)'
    )
    
    parser.add_argument(
        '--clean-orphaned',
        action='store_true',
        help='Remove orphaned files from environment. Requires confirmation unless --force is also specified'
    )
    
    parser.add_argument(
        '--clean-all',
        action='store_true',
        help='Remove ALL files from environment (not just orphaned). Requires confirmation unless --force is also specified'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompts when using --clean-orphaned or --clean-all'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    
    # Use parse_known_args to ignore unknown arguments from pipeline
    args, unknown = parser.parse_known_args()
    
    # Run cleaning
    success = clean_site(
        args.environment, 
        force=args.force, 
        dry_run=args.dry_run,
        clean_all=args.clean_all,
        clean_orphaned=args.clean_orphaned
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
