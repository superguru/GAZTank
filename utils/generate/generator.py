#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Static Content Generator
========================
General-purpose static content generation module that reads generate.toml
and delegates to appropriate converters based on input_type.

Currently supported input types:
- markdown: Converts .md files to HTML using md_to_html module

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.gzlogging import get_logging_context
from utils.gzconfig import get_generate_config, GenerateGroup

# Global logging context
log = None


def process_markdown_group(group: GenerateGroup, project_root: Path, environment: str, force: bool = False, dry_run: bool = False) -> bool:
    """
    Process a markdown group by converting files to HTML.
    
    Args:
        group: GenerateGroup configuration object
        project_root: Project root directory path
        environment: Target environment (dev/staging/prod)
        force: If True, convert even if output is up-to-date
        dry_run: If True, show what would be done without doing it
        
    Returns:
        bool: True if all files processed successfully, False otherwise
    """
    from utils.generate.md_to_html import MarkdownConverter
    
    if not group.files:
        print(f"⚠️  Group '{group.name}' has no files to process")
        if log:
            log.wrn(f"Group '{group.name}' has no files to process")
        return True
    
    print(f"📝 Processing markdown group: {group.name}")
    print(f"   Output directory: {group.output_path.relative_to(project_root)}")
    print(f"   Files to process: {len(group.files)}")
    if log:
        log.inf(f"Processing markdown group '{group.name}' with {len(group.files)} files to {group.output_path.relative_to(project_root)}")
    
    # Create output directory
    output_path = group.output_path
    if not dry_run:
        output_path.mkdir(parents=True, exist_ok=True)
    elif not output_path.exists():
        print(f"   [DRY RUN] Would create directory: {output_path}")
    
    # Process each file
    converter = MarkdownConverter(dry_run=dry_run, force=force)
    converted_count = 0
    skipped_count = 0
    failure_count = 0
    
    for file_path_str in group.files:
        # Convert to Path and resolve relative to project root
        input_file = project_root / file_path_str.replace('\\', '/')
        
        if not input_file.exists():
            print(f"❌ Input file not found: {input_file}")
            if log:
                log.err(f"Input file not found: {input_file}")
            failure_count += 1
            continue
        
        # Generate output filename based on path_transform setting
        input_path = Path(file_path_str)
        
        if group.path_transform == 'flatten':
            # Use only the filename: utils/clean/README.md -> README.html
            output_file = output_path / f"{input_file.stem}.html"
        elif group.path_transform == 'preserve_parent':
            # Keep immediate parent directory: utils/clean/README.md -> clean/README.html
            if len(input_path.parts) > 1:
                parent_dir = input_path.parts[-2]
                output_file = output_path / parent_dir / f"{input_file.stem}.html"
            else:
                # No parent directory, just use filename
                output_file = output_path / f"{input_file.stem}.html"
        elif group.path_transform == 'preserve_all':
            # Keep full relative path: utils/clean/README.md -> utils/clean/README.html
            relative_dir = input_path.parent
            output_file = output_path / relative_dir / f"{input_file.stem}.html"
        elif group.path_transform == 'strip_prefix':
            # Strip prefix then use remaining path: utils/clean/README.md -> clean/README.html (with strip_path_prefix="utils/")
            prefix = group.strip_path_prefix
            path_str = file_path_str.replace('\\', '/')
            
            if prefix and path_str.startswith(prefix):
                # Remove the prefix
                remaining_path = path_str[len(prefix):]
                remaining_path_obj = Path(remaining_path)
                
                # Use remaining path structure
                if remaining_path_obj.parent and str(remaining_path_obj.parent) != '.':
                    output_file = output_path / remaining_path_obj.parent / f"{input_file.stem}.html"
                else:
                    # No remaining path, just filename
                    output_file = output_path / f"{input_file.stem}.html"
            else:
                # No prefix match or no prefix specified, just use filename
                output_file = output_path / f"{input_file.stem}.html"
        else:
            # Default to flatten
            output_file = output_path / f"{input_file.stem}.html"
        
        # Create subdirectories if needed
        if not dry_run:
            output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"   Processing: {input_file.name} -> {output_file.relative_to(project_root)}")
        
        try:
            result = converter.convert(input_file, output_file)
            if result == 'success':
                converted_count += 1
                if log:
                    if dry_run:
                        log.inf(f"[DRY RUN] Would convert {input_file.name} to {output_file.relative_to(project_root)}")
                    else:
                        log.inf(f"Converted {input_file.name} to {output_file.relative_to(project_root)}")
            elif result == 'skipped':
                skipped_count += 1
                if log:
                    log.inf(f"Skipped {input_file.name} (up-to-date)")
            else:  # 'failed'
                failure_count += 1
        except Exception as e:
            print(f"❌ Failed to convert {input_file.name}: {e}")
            if log:
                log.err(f"Failed to convert {input_file.name}: {e}")
            failure_count += 1
    
    # Report results
    total_processed = converted_count + skipped_count
    if failure_count == 0:
        if dry_run:
            # Dry-run reporting
            if converted_count > 0 and skipped_count > 0:
                print(f"ℹ️  [DRY RUN] Group '{group.name}': {converted_count} would be converted, {skipped_count} already up-to-date")
            elif converted_count > 0:
                print(f"ℹ️  [DRY RUN] Group '{group.name}': All {converted_count} file(s) would be converted")
            else:
                print(f"✅ [DRY RUN] Group '{group.name}': All {skipped_count} file(s) already up-to-date")
            if log:
                log.inf(f"[DRY RUN] Group '{group.name}': {converted_count} would be converted, {skipped_count} skipped")
        else:
            # Actual operation reporting
            if converted_count > 0 and skipped_count > 0:
                print(f"✅ Group '{group.name}': {converted_count} converted, {skipped_count} skipped (up-to-date)")
            elif converted_count > 0:
                print(f"✅ Group '{group.name}': All {converted_count} file(s) converted successfully")
            else:
                print(f"✅ Group '{group.name}': All {skipped_count} file(s) already up-to-date")
            if log:
                log.inf(f"Group '{group.name}' completed: {converted_count} converted, {skipped_count} skipped")
        return True
    else:
        if dry_run:
            print(f"⚠️  [DRY RUN] Group '{group.name}': {converted_count} would be converted, {skipped_count} skipped, {failure_count} would fail")
            if log:
                log.err(f"[DRY RUN] Group '{group.name}': {converted_count} would be converted, {skipped_count} skipped, {failure_count} would fail")
        else:
            print(f"❌ Group '{group.name}': {converted_count} converted, {skipped_count} skipped, {failure_count} failed")
            if log:
                log.err(f"Group '{group.name}' completed with failures: {converted_count} converted, {skipped_count} skipped, {failure_count} failed")
        return False


def process_groups(environment: str, force: bool = False, dry_run: bool = False) -> int:
    """
    Process all groups in the configuration.
    
    Args:
        environment: Target environment (dev/staging/prod)
        force: If True, convert even if output is up-to-date
        dry_run: If True, show what would be done without doing it
        
    Returns:
        int: Exit code (0 for success, 1 for failures)
    """
    # Get configuration from gzconfig with environment
    config = get_generate_config(environment)
    
    # Get project root - need to navigate up from output path correctly
    if config.groups:
        # output_path is publish/{env}/content/{subdir}
        # Go up through: subdir -> content -> {env} -> publish -> root
        first_output = config.groups[0].output_path
        project_root = first_output.parent.parent.parent.parent
    else:
        print("⚠️  No groups found in configuration")
        if log:
            log.wrn("No groups found in configuration")
        return 0
    
    print(f"📋 Found {config.group_count} group(s) in configuration")
    print()
    if log:
        log.inf(f"Found {config.group_count} groups in configuration")
    
    total_groups = 0
    successful_groups = 0
    skipped_groups = 0
    disabled_groups = 0
    
    for group in config.groups:
        # Check if group is enabled
        if not group.enabled:
            print(f"⏸️  Group '{group.name}' is disabled - skipping")
            if log:
                log.inf(f"Group '{group.name}' is disabled (enabled=false)")
            disabled_groups += 1
            continue
        
        # Check for required input_type attribute
        if not group.input_type:
            print(f"❌ Group '{group.name}' is missing required 'input_type' attribute - skipping")
            if log:
                log.err(f"Group '{group.name}' is missing required 'input_type' attribute - skipping")
            skipped_groups += 1
            continue
        
        total_groups += 1
        
        # Process based on input type
        if group.input_type == 'markdown':
            success = process_markdown_group(group, project_root, environment, force=force, dry_run=dry_run)
            if success:
                successful_groups += 1
        else:
            print(f"ℹ️  Group '{group.name}' has unsupported input_type '{group.input_type}' - skipping")
            if log:
                log.inf(f"Group '{group.name}' has unsupported input_type '{group.input_type}' - skipping")
            skipped_groups += 1
        
        print()
    
    # Final summary
    print("=" * 60)
    if dry_run:
        print("DRY RUN SUMMARY")
    else:
        print("GENERATION SUMMARY")
    print("=" * 60)
    print(f"Total groups: {total_groups + skipped_groups + disabled_groups}")
    if disabled_groups > 0:
        print(f"⏸️  Disabled: {disabled_groups}")
    if dry_run:
        print(f"ℹ️  Would process: {successful_groups}")
    else:
        print(f"✅ Processed successfully: {successful_groups}")
    if skipped_groups > 0:
        print(f"⏭️  Skipped: {skipped_groups}")
    if total_groups > successful_groups:
        if dry_run:
            print(f"⚠️  Would fail: {total_groups - successful_groups}")
        else:
            print(f"❌ Failed: {total_groups - successful_groups}")
    
    # Log summary
    if log:
        if dry_run:
            log.inf(f"[DRY RUN] Summary: {successful_groups}/{total_groups} groups would be processed, {disabled_groups} disabled, {skipped_groups} skipped")
        else:
            log.inf(f"Generation summary: {successful_groups}/{total_groups} groups processed successfully, {disabled_groups} disabled, {skipped_groups} skipped")
    
    # Return exit code
    if total_groups > 0 and successful_groups == total_groups:
        if dry_run:
            print("ℹ️  [DRY RUN] All groups would be processed successfully!")
        else:
            print("✅ All groups processed successfully!")
        return 0
    elif successful_groups > 0:
        if dry_run:
            print("⚠️  [DRY RUN] Some groups would have failures")
        else:
            print("⚠️  Some groups processed with failures")
        if log:
            if dry_run:
                log.wrn("[DRY RUN] Some groups would have failures")
            else:
                log.wrn("Some groups processed with failures")
        return 1
    else:
        if dry_run:
            print("❌ [DRY RUN] No groups would be processed successfully")
        else:
            print("❌ No groups were processed successfully")
        if log:
            if dry_run:
                log.err("[DRY RUN] No groups would be processed successfully")
            else:
                log.err("No groups were processed successfully")
        return 1


def main() -> int:
    """
    Main entry point for the static content generator.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    global log
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Static content generator - converts source files to HTML based on generate.toml',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scripts\\generate.cmd -e dev             # Generate to dev environment
  scripts\\generate.cmd -e staging         # Generate to staging environment
  scripts\\generate.cmd -e prod            # Generate to production environment
  scripts\\generate.cmd -e dev --force     # Force regeneration
  scripts\\generate.cmd -e dev --dry-run   # Preview without changes
        """
    )
    parser.add_argument(
        '-e', '--environment',
        required=True,
        choices=['dev', 'staging', 'prod'],
        help='Environment to generate content for (dev/staging/prod)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force regeneration of all files (ignore timestamps)'
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
    print("Static Content Generator")
    print("=" * 60)
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE enabled - No files will be modified")
    
    if args.force:
        print("🔄 FORCE MODE enabled - Regenerating all files")
    
    print(f"📁 Target environment: {args.environment}")
    
    # Initialize logging using specified environment
    try:
        log = get_logging_context(args.environment, 'generate', console=False)
        log.inf("Static Content Generator started")
        log.inf(f"Environment: {args.environment}")
        if args.dry_run:
            log.inf("DRY RUN MODE enabled")
        if args.force:
            log.inf("FORCE MODE enabled")
    except Exception as e:
        print(f"Warning: Logging initialization failed: {e}")
        print("Continuing without logging...")
        log = None
    
    try:
        # Load configuration from gzconfig with environment
        config = get_generate_config(environment=args.environment)
        print(f"📋 Loaded configuration with {config.group_count} group(s)")
        if log:
            log.inf(f"Loaded configuration with {config.group_count} groups")
        
        # Process all groups
        exit_code = process_groups(environment=args.environment, force=args.force, dry_run=args.dry_run)
        
        if args.dry_run:
            print()
            print("⚠️  DRY RUN MODE - No files were modified")
        
        # Log completion
        if log:
            log.inf("Static Content Generator completed successfully")
        
        return exit_code
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        if log:
            log.err(str(e))
        return 1
    except ImportError as e:
        print(f"❌ {e}")
        if log:
            log.err(str(e))
        return 1
    except ValueError as e:
        print(f"❌ {e}")
        if log:
            log.err(str(e))
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if log:
            log.err(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
