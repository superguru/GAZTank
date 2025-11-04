#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Responsive Image Script Generator
=================================
Generates a command-line script to create responsive images using ImageMagick.

Prompts the user to select an image and configure output settings, then
creates and executes a script to generate multiple sizes for logos and favicons.

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
import os
import subprocess
import re
from datetime import datetime
from InquirerPy import inquirer
from InquirerPy.validator import PathValidator

# Configuration constants
DEFAULT_PREFIX = "sitename"
DEFAULT_QUALITY = 85
LOGO_SIZES = [512, 256, 128, 75, 50]
FAVICON_SIZES = [32, 16]

def natural_sort_key(text):
    """
    Generate a key for natural sorting that handles numbers and special characters.
    Prioritizes files without copy/variant suffixes.
    """
    def atoi(text):
        return int(text) if text.isdigit() else text.lower()
    
    # Check if filename contains copy indicators and penalize them
    basename = os.path.splitext(text)[0].lower()
    has_copy_suffix = ' - copy' in basename or ' copy' in basename or '- copy' in basename
    
    # Return tuple: (has_copy_suffix, natural_sort_parts)
    # False sorts before True, so originals come first
    return (has_copy_suffix, [atoi(c) for c in re.split(r'(\d+)', text)])

def get_file_info(filename):
    """Get file information including size and modification date."""
    stats = os.stat(filename)
    size = stats.st_size
    mod_time = stats.st_mtime
    
    # Format size (directories will show as <DIR> in the calling function)
    if os.path.isdir(filename):
        size_str = "<DIR>"
    elif size < 1024:
        size_str = f"{size} B"
    elif size < 1024 * 1024:
        size_str = f"{size / 1024:.1f} KB"
    else:
        size_str = f"{size / (1024 * 1024):.1f} MB"
    
    # Format date
    date_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
    
    return size_str, date_str, mod_time

def get_image_files_and_dirs():
    """Get list of image files and subdirectories in current directory."""
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.svg')
    items = []
    
    # Add parent directory option if not in root
    current_path = os.getcwd()
    parent_path = os.path.dirname(current_path)
    if parent_path != current_path:  # Not in root directory
        items.append({
            'name': '..',
            'type': 'directory',
            'size': '',
            'date': '',
            'mod_time': 0,
            'display_name': '../ (Parent Directory)'
        })
    
    # Get all items in current directory
    for filename in os.listdir('.'):
        if os.path.isdir(filename):
            # Add subdirectory
            try:
                size_str, date_str, mod_time = get_file_info(filename)
                items.append({
                    'name': filename,
                    'type': 'directory',
                    'size': '<DIR>',
                    'date': date_str,
                    'mod_time': mod_time,
                    'display_name': f"{filename}/"
                })
            except (OSError, PermissionError):
                # Skip directories we can't access
                continue
        elif os.path.isfile(filename) and filename.lower().endswith(image_extensions):
            # Add image file
            try:
                size_str, date_str, mod_time = get_file_info(filename)
                items.append({
                    'name': filename,
                    'type': 'file',
                    'size': size_str,
                    'date': date_str,
                    'mod_time': mod_time,
                    'display_name': filename
                })
            except (OSError, PermissionError):
                # Skip files we can't access
                continue
    
    # Sort directories first, then files
    # Within each group, sort by modification time DESC (newest first), then filename using natural sort ASC
    items.sort(key=lambda x: (
        x['type'] == 'file',  # directories first (False < True)
        -x['mod_time'], 
        natural_sort_key(x['name'])
    ))
    
    return items

def display_generated_filenames(prefix):
    """Display the filenames that will be generated for the given prefix."""
    print(f"\nFiles that will be generated with prefix '{prefix}':")
    print("\nLogos:")
    for size in LOGO_SIZES:
        print(f"  - {prefix}_logo_{size}x{size}.webp")
    
    print("\nFavicons:")
    for size in FAVICON_SIZES:
        print(f"  - {prefix}_favicon_{size}x{size}.webp")
    print()

def validate_quality(value):
    """Validate quality input. Returns True if valid, False otherwise."""
    # Empty string is valid (will use default)
    if not value or value.strip() == "":
        return True
    
    # Try to convert to integer
    try:
        quality_int = int(value)
        if 1 <= quality_int <= 100:
            return True
        return False
    except ValueError:
        return False

def generate_cmd_script(input_file, prefix, quality):
    """Generate a CMD script that creates responsive images using ImageMagick."""
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        return None
    
    # Generate CMD script content
    cmd_lines = [
        "@echo off",
        "REM ========================================================================",
        "REM This script was auto-generated by create_responsive_images.py",
        "REM Manual editing is not recommended - regenerate using the Python script",
        "REM ========================================================================",
        "",
        "echo Generating responsive images...",
        ""
    ]
    
    # Generate logo commands
    for size in LOGO_SIZES:
        output_file = f"{prefix}_logo_{size}x{size}.webp"
        cmd_lines.append(f'magick "{input_file}" -resize {size}x{size} -quality {quality} "{output_file}"')
        cmd_lines.append(f'echo Created {output_file}')
    
    cmd_lines.append("")
    
    # Generate favicon commands
    for size in FAVICON_SIZES:
        output_file = f"{prefix}_favicon_{size}x{size}.webp"
        cmd_lines.append(f'magick "{input_file}" -resize {size}x{size} -quality {quality} "{output_file}"')
        cmd_lines.append(f'echo Created {output_file}')
    
    cmd_lines.append("")
    cmd_lines.append("echo All images generated successfully!")
    cmd_lines.append("pause")
    
    return "\n".join(cmd_lines)

def select_image_file():
    """Navigate through directories and select an image file."""
    while True:
        # Get current directory items
        items = get_image_files_and_dirs()
        
        # Check if there are any image files in current directory
        image_files = [item for item in items if item['type'] == 'file']
        
        if not items:
            print(f"Error: No accessible files or directories found in {os.getcwd()}")
            sys.exit(1)
        
        # Create choices with formatted display
        choices = []
        for item in items:
            if item['type'] == 'directory':
                display = f"📁 {item['display_name']:<38} {item['size']:>10} {item['date']}"
            else:
                display = f"🖼️  {item['display_name']:<38} {item['size']:>10} {item['date']}"
            choices.append({'name': display, 'value': item})
        
        # Show current directory
        current_dir = os.getcwd()
        
        # Prompt user to select an item
        selected_item = inquirer.select(
            message=f"Current directory: {current_dir}\nSelect an image file or directory:",
            choices=choices,
            pointer="→",
        ).execute()
        
        if selected_item['type'] == 'directory':
            # Navigate to selected directory
            if selected_item['name'] == '..':
                os.chdir('..')
            else:
                try:
                    os.chdir(selected_item['name'])
                except (OSError, PermissionError) as e:
                    print(f"Error: Cannot access directory '{selected_item['name']}': {e}")
                    continue
        else:
            # File selected, return it
            return os.path.join(os.getcwd(), selected_item['name'])

def main():
    # Check if filename argument is provided
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        # Navigate and select image file
        input_file = select_image_file()
    
    # Verify file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    # Display generated filenames with default prefix
    display_generated_filenames(DEFAULT_PREFIX)
    
    # Prompt for prefix
    prefix = inquirer.text(
        message="Enter the prefix for generated images:",
        default=DEFAULT_PREFIX,
        validate=lambda result: len(result) > 0,
        invalid_message="Prefix cannot be empty.",
    ).execute()
    
    # Display updated filenames if prefix was changed
    if prefix != DEFAULT_PREFIX:
        display_generated_filenames(prefix)
    
    # Prompt for quality using text input with validation
    quality_input = inquirer.text(
        message=f"Enter quality level (1-100, default {DEFAULT_QUALITY}):",
        default=f"{DEFAULT_QUALITY}",
        validate=validate_quality,
        invalid_message="Quality must be a number between 1 and 100.",
    ).execute()
    
    # Convert quality input to integer, use default if empty
    if not quality_input or quality_input.strip() == "":
        quality = DEFAULT_QUALITY
    else:
        quality = int(quality_input)
    
    print(f"\nUsing quality level: {quality}")
    
    # Generate CMD script
    cmd_content = generate_cmd_script(input_file, prefix, quality)
    
    if cmd_content is None:
        sys.exit(1)
    
    # Write CMD script to file
    cmd_filename = "create_responsive_images_temp.cmd"
    with open(cmd_filename, 'w') as f:
        f.write(cmd_content)
    
    print(f"\nGenerated CMD script: {cmd_filename}")
    print("Executing script...\n")
    
    # Execute the CMD script
    try:
        subprocess.run([cmd_filename], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError executing CMD script: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\nError: Could not execute CMD script. Make sure you have proper permissions.")
        sys.exit(1)
    
    print("\nDone!")

if __name__ == "__main__":
    main()
