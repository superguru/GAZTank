#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Normalise Example Usage
========================
This demonstrates how to import and use the process_file() function
from the normalise module in other Python scripts.

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
from pathlib import Path

# Add utils to path so we can import normalise
sys.path.insert(0, str(Path(__file__).parent.parent))

from normalise import process_file


def batch_process_markdown_files(directory, pattern="*.md"):
    """
    Process all markdown files in a directory.
    
    Args:
        directory (str): Directory to search for markdown files
        pattern (str): Glob pattern for files to process
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"Error: Directory does not exist: {dir_path}")
        return
    
    md_files = list(dir_path.glob(pattern))
    
    if not md_files:
        print(f"No markdown files found matching '{pattern}' in {dir_path}")
        return
    
    print(f"Found {len(md_files)} markdown file(s)")
    print()
    
    total_modifications = 0
    
    for md_file in md_files:
        try:
            print(f"Processing: {md_file}")
            modifications = process_file(md_file)
            total_modifications += modifications
            print()
        except FileNotFoundError as e:
            print(f"Skipping: {e}")
            print()
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
            print()
    
    print("=" * 60)
    print("Batch processing complete!")
    print(f"Total modifications across all files: {total_modifications}")


def main():
    """Example usage of the batch processing function."""
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        # Default to docs directory
        directory = Path(__file__).parent.parent.parent / "docs"
    
    batch_process_markdown_files(directory)


if __name__ == "__main__":
    main()
