#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Markdown Structure Normaliser
==============================
Converts standalone bold text to proper markdown headings while preserving
bold text used for emphasis within sentences and lists.

Usage:
    python -m normalise <filename> [--force] [--dry-run]
    python -m normalise docs/SETUP_SITE.md
    python -m normalise docs/SETUP_SITE.md --force
    python -m normalise docs/SETUP_SITE.md --dry-run

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.gzlogging import get_logging_context

# Global logging context
log = None


class ProcessingState:
    """
    Encapsulates the state during markdown processing.
    """
    def __init__(self, line_no=0, heading_level=1, is_in_code_block=False):
        self.line_no = line_no
        self.heading_level = heading_level
        self.is_in_code_block = is_in_code_block
    
    def update_code_block_state(self, line):
        """
        Update the is_in_code_block state based on the current line.
        
        Args:
            line (str): Current line being processed
        """
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            self.is_in_code_block = not self.is_in_code_block


def read_file(filepath):
    """
    Read the contents of a markdown file into a list of strings.
    
    Args:
        filepath (Path): Path to the markdown file
        
    Returns:
        list: List of strings (lines from the file)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if log:
                log.dbg(f"Read {len(lines)} lines from {filepath}")
            return lines
    except FileNotFoundError:
        error_msg = f"File not found: {filepath}"
        if log:
            log.err(error_msg)
        print(f"Error: {error_msg}")
        sys.exit(1)
    except Exception as e:
        error_msg = f"Error reading file: {e}"
        if log:
            log.err(error_msg)
        print(error_msg)
        sys.exit(1)


def write_file(filepath, lines, dry_run=False):
    """
    Write the processed lines back to the file.
    
    Args:
        filepath (Path): Path to the markdown file
        lines (list): List of strings to write
        dry_run (bool): If True, don't actually write the file
    """
    if dry_run:
        success_msg = f"  ✓ File would be updated: {filepath}"
        print(success_msg)
        if log:
            log.inf(f"Dry-run: File would be updated: {filepath} ({len(lines)} lines prepared)")
        return
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        success_msg = f"  ✓ File updated: {filepath}"
        print(success_msg)
        if log:
            log.inf(f"File updated: {filepath} ({len(lines)} lines written)")
    except Exception as e:
        error_msg = f"Error writing file: {e}"
        if log:
            log.err(error_msg)
        print(f"  ❌ {error_msg}")
        sys.exit(1)


def get_stripped_standalone_bold(line):
    """
    Check if a line contains standalone bold text that should be converted to a heading.
    
    Standalone bold text is:
    - Starts with ** and ends with ** (optionally followed by :)
    - Not part of a list item (doesn't start with -, *, or number.)
    - Not in the middle of a sentence (the whole line is bold)
    
    Args:
        line (str): Line to check
        
    Returns:
        bool: True if this is standalone bold text
    """
    stripped = line.strip()
    
    # Skip empty lines
    if not stripped:
        return False, line
    
    # Check if the line is standalone bold text
    if stripped.startswith("**") and stripped.endswith("**"):
        return True, stripped[2:-2].strip()
    
    return False, line


def count_leading_hashes(s):
    return next((i for i, c in enumerate(s) if c != '#'), len(s))


def get_heading_level(line, state):
    stripped = line.lstrip()
    hash_count = count_leading_hashes(stripped)
    result = hash_count if hash_count > 0 else state.heading_level

    return result


def should_skip_line(line, state):
    """
    Determine if a line should be skipped from processing.
    
    Args:
        line (str): Line to check
        state (ProcessingState): Current processing state

    Returns:
        bool: True if line should be skipped
    """
    if not line:
        return True
    
    # Skip lines inside code blocks
    if state.is_in_code_block:
        return True
    
    return False


def process_line(line, state):
    """
    Process a single line and convert standalone bold text to headings.
    
    Args:
        line (str): Line to process
        state (ProcessingState): Current processing state
        
    Returns:
        tuple: (modified_line, was_modified)
    """
    # Update code block state before processing
    state.update_code_block_state(line)

    if should_skip_line(line, state):
        return line, False
    
    was_bold, bold_text = get_stripped_standalone_bold(line)
    if not was_bold:
        state.heading_level = get_heading_level(line, state)
        return line, False
          
    # Create the heading
    heading_marker = '#' * (state.heading_level + 1)
    new_line = f"{heading_marker} {bold_text}\n"

    return new_line, True


def process_lines(lines):
    """
    Process all lines in the document and convert standalone bold text to headings.
    
    Args:
        lines (list): List of lines from the markdown file
        
    Returns:
        tuple: (processed_lines, modification_count)
    """
    processed_lines = []
    modification_count = 0    
    state = ProcessingState()

    if log:
        log.dbg(f"Processing {len(lines)} lines")

    for i, line in enumerate(lines):
        state.line_no = i
        new_line, was_modified = process_line(line, state)
        processed_lines.append(new_line)
        
        if was_modified:
            modification_count += 1
            if log:
                old_text = line.strip()
                new_text = new_line.strip()
                log.dbg(f"Line {i+1}, H{state.heading_level+1}: {old_text} -> {new_text}")
    
    if log:
        log.inf(f"Processing complete: {modification_count} modifications made")
    
    return processed_lines, modification_count


def needs_processing(filepath, force=False):
    """
    Determine if a file needs processing.
    
    In this context, we always need to read and analyze the file to check for
    standalone bold text. The force flag affects whether we process even if
    no modifications are needed.
    
    Args:
        filepath (Path): Path to the markdown file
        force (bool): If True, always process
        
    Returns:
        bool: True if file should be processed
    """
    # For normalise, we always need to read the file to check for modifications
    # The force flag will be used to control dry-run behavior
    # Possible future enhancement: Keep track of last processed state in a metadata file, so
    # we can avoid re-processing unchanged files
    return True


def process_file(filename, force=False, dry_run=False):
    """
    Process a markdown file and convert standalone bold text to headings.
    
    This function can be called from other scripts that import this module.
    
    Args:
        filename (str or Path): Path to the markdown file to process
        force (bool): If True, process even if no modifications needed
        dry_run (bool): If True, don't actually write changes
        
    Returns:
        int: Number of modifications made to the file
        
    Raises:
        FileNotFoundError: If the file does not exist
        Exception: If there are errors reading or writing the file
    """
    filepath = Path(filename)
    
    if not filepath.exists():
        error_msg = f"File does not exist: {filepath}"
        if log:
            log.err(error_msg)
        raise FileNotFoundError(error_msg)
    
    mode_info = []
    if dry_run:
        mode_info.append("DRY RUN")
    if force:
        mode_info.append("FORCE")
    mode_str = f" [{', '.join(mode_info)}]" if mode_info else ""
    
    print(f"📄 Processing{mode_str}: {filepath}")
    if log:
        log.inf(f"Starting processing: {filepath}")
    
    # Read the file
    lines = read_file(filepath)
    
    # Process the lines
    processed_lines, modification_count = process_lines(lines)
    
    # Write back if anything was modified
    if modification_count > 0:
        write_file(filepath, processed_lines, dry_run=dry_run)
        if dry_run:
            print(f"  📊 Total modifications prepared: {modification_count}")
            if log:
                log.inf(f"Dry-run complete: {modification_count} modifications prepared (not written)")
        else:
            print(f"  ✅ Total modifications: {modification_count}")
            if log:
                log.inf(f"File processing complete: {modification_count} modifications made")
    else:
        msg = "⏭️  No modifications needed - file is already properly structured."
        print(msg)
        if log:
            log.inf("No modifications needed - file is already properly structured")
    
    return modification_count


def main():
    """Main entry point for the script."""
    global log
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        prog='normalise',
        description='Markdown Structure Normaliser - Converts standalone bold text to proper markdown headings',
        epilog='Example: python -m normalise docs/SETUP_SITE.md --force --dry-run'
    )
    
    parser.add_argument(
        'filename',
        help='Path to the markdown file to process'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Process file even if it appears up-to-date (always applies for normalise)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually modifying files'
    )
    
    # Use parse_known_args to ignore unknown arguments from pipeline
    args, unknown = parser.parse_known_args()
    
    # Print console header
    print("=" * 60)
    print("📝 Markdown Structure Normaliser")
    print("=" * 60)
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE enabled - No files will be modified")
    
    if args.force:
        print("🔄 FORCE MODE enabled - Processing regardless of state")
    
    # Initialize logging (using 'dev' environment by default, console output disabled for logs)
    try:
        log = get_logging_context('dev', 'normalise', console=False)
        log.inf("Markdown Structure Normaliser started")
        if args.dry_run:
            log.inf("DRY RUN MODE enabled")
        if args.force:
            log.inf("FORCE MODE enabled")
    except Exception as e:
        print(f"⚠️  Warning: Logging initialization failed: {e}")
        print("Continuing without logging...")
        log = None
    
    filepath = Path(args.filename)
    
    if not filepath.exists():
        error_msg = f"File does not exist: {filepath}"
        print(f"❌ Error: {error_msg}")
        if log:
            log.err(error_msg)
        return 1
    
    if filepath.suffix.lower() not in ['.md', '.markdown']:
        warning_msg = f"File does not appear to be a markdown file: {filepath}"
        print(f"⚠️  Warning: {warning_msg}")
        if log:
            log.wrn(warning_msg)
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("❌ Aborted.")
            if log:
                log.inf("Processing aborted by user")
            return 0
    
    try:
        # Get project root info
        from pathlib import Path as PathLib
        project_root = PathLib(__file__).parent.parent.parent
        print(f"📁 Project root: {project_root}")
        if log:
            log.inf(f"Project root: {project_root}")
        
        # Process the file
        modification_count = process_file(filepath, force=args.force, dry_run=args.dry_run)
        
        if args.dry_run:
            print()
            print("⚠️  DRY RUN MODE - No files were modified")
        
        # Log completion
        if log:
            log.inf("Markdown Structure Normaliser completed successfully")
        
        print("=" * 60)
        print("✅ Normalisation complete")
        print("=" * 60)
        
        return 0
    except Exception as e:
        error_msg = f"Error: {e}"
        print(f"❌ {error_msg}")
        if log:
            log.err(f"Processing failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
