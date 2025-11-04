#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Batch Normaliser for Pipeline
==============================
Processes all markdown files in the content directory for pipeline execution.

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
import argparse
from pathlib import Path
from utils.normalise import process_file
from utils.gzlogging import get_logging_context

# Global logging context
log = None


def batch_normalize_content(environment: str, force: bool = False, dry_run: bool = False) -> tuple[int, int]:
    """
    Normalize all markdown files from the generate configuration.
    
    Args:
        environment: Target environment (dev/staging/prod) - used for logging
        force: If True, process even if files appear normalized
        dry_run: If True, show what would be done without making changes
        
    Returns:
        tuple: (total_files, total_modifications)
    """
    global log
    
    # Get project root (utils/normalise -> utils -> root)
    project_root = Path(__file__).parent.parent.parent
    
    # Import config module to get markdown files
    try:
        from utils.gzconfig import get_generate_config
        config = get_generate_config(environment=environment)
    except Exception as e:
        error_msg = f"Failed to load generate configuration: {e}"
        print(f"❌ {error_msg}")
        if log:
            log.err(error_msg)
        return 0, 0
    
    # Collect all markdown files from enabled groups
    md_files = []
    for group in config.groups:
        if group.enabled and group.input_type == 'markdown':
            for file_path in group.files:
                full_path = project_root / file_path.replace('\\', '/')
                if full_path.exists():
                    md_files.append(full_path)
                else:
                    print(f"⚠️  Warning: File not found: {file_path}")
                    if log:
                        log.wrn(f"File not found: {file_path}")
    
    # Sort for consistent ordering
    md_files = sorted(md_files)
    
    if not md_files:
        msg = "No markdown files found in generate configuration"
        print(f"ℹ️  {msg}")
        if log:
            log.inf(msg)
        return 0, 0
    
    print(f"📋 Found {len(md_files)} markdown file(s) to process")
    if log:
        log.inf(f"Found {len(md_files)} markdown files from generate configuration")
    print()
    
    total_modifications = 0
    processed_count = 0
    error_count = 0
    
    for md_file in md_files:
        relative_path = md_file.relative_to(project_root)
        
        try:
            modifications = process_file(md_file, force=force, dry_run=dry_run)
            total_modifications += modifications
            processed_count += 1
            
        except FileNotFoundError as e:
            print(f"❌ File not found: {relative_path}")
            if log:
                log.err(f"File not found: {relative_path}")
            error_count += 1
            
        except Exception as e:
            print(f"❌ Error processing {relative_path}: {e}")
            if log:
                log.err(f"Error processing {relative_path}: {e}")
            error_count += 1
    
    # Summary
    print()
    print("=" * 60)
    if dry_run:
        print("NORMALIZATION PREVIEW")
    else:
        print("NORMALIZATION SUMMARY")
    print("=" * 60)
    print(f"Files processed: {processed_count}")
    if error_count > 0:
        print(f"❌ Errors: {error_count}")
    if dry_run:
        print(f"ℹ️  Would make {total_modifications} total modification(s)")
    else:
        print(f"✅ Made {total_modifications} total modification(s)")
    
    if log:
        if dry_run:
            log.inf(f"[DRY RUN] Normalization complete: {processed_count} files, {total_modifications} modifications prepared, {error_count} errors")
        else:
            log.inf(f"Normalization complete: {processed_count} files, {total_modifications} modifications made, {error_count} errors")
    
    return processed_count, total_modifications


def main() -> int:
    """
    Main entry point for batch normalization.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    global log
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Batch Markdown Normaliser - Processes all content files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scripts\\normalise.cmd -e dev             # Normalize all content files
  scripts\\normalise.cmd -e dev --dry-run   # Preview changes
  scripts\\normalise.cmd -e dev --force     # Force processing
        """
    )
    parser.add_argument(
        '-e', '--environment',
        required=True,
        choices=['dev', 'staging', 'prod'],
        help='Environment for logging (dev/staging/prod)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Process all files regardless of state'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    # Use parse_known_args to ignore unknown arguments from pipeline
    args, unknown = parser.parse_known_args()
    
    # Print console header
    print("=" * 60)
    print("📝 Batch Markdown Normaliser")
    print("=" * 60)
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE enabled - No files will be modified")
    
    if args.force:
        print("🔄 FORCE MODE enabled - Processing all files")
    
    print(f"📁 Target environment: {args.environment}")
    print()
    
    # Initialize logging
    try:
        log = get_logging_context(args.environment, 'normalise', console=False)
        log.inf("Batch Markdown Normaliser started")
        log.inf(f"Environment: {args.environment}")
        if args.dry_run:
            log.inf("DRY RUN MODE enabled")
        if args.force:
            log.inf("FORCE MODE enabled")
    except Exception as e:
        print(f"⚠️  Warning: Logging initialization failed: {e}")
        print("Continuing without logging...")
        log = None
    
    try:
        # Process all content files
        processed, modifications = batch_normalize_content(
            environment=args.environment,
            force=args.force,
            dry_run=args.dry_run
        )
        
        # Determine exit code
        if processed > 0:
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print()
        print("⚠️  Operation cancelled by user")
        if log:
            log.wrn("Operation cancelled by user")
        return 1
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if log:
            log.err(f"Fatal error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
