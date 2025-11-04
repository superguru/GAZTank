#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
UI Helper Functions
===================
ANSI color codes and printing utilities for terminal output.

Authors: superguru, gazorper
License: GPL v3.0
"""

from datetime import datetime


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_section(text):
    """Print a section header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-' * len(text)}{Colors.ENDC}")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")


def format_setup_date(timestamp_str):
    """Format timestamp string to human-readable date"""
    try:
        # Parse the timestamp format yyyyMMddhhmm
        dt = datetime.strptime(timestamp_str, '%Y%m%d%H%M')
        # Format as dd-MMM-yyyy hh:mm am/pm
        return dt.strftime('%d-%b-%Y %I:%M %p').replace(' 0', ' ')
    except:
        return None


def print_setup_completion(is_force_apply=False):
    """Print setup completion message with file list and next steps"""
    print_success("✓")
    print_success("Setup completed successfully!")
    print()
    
    # List updated files
    mode_desc = "All files updated" if is_force_apply else "Updated files based on timestamps"
    print_info(f"{mode_desc}:")
    files_list = [
        "✓ src/css/variables.css - CSS theme variables",
        "✓ src/css/styles.css - CSS variables integration",
        "✓ src/index.html - Meta tags, titles, logo/favicon references",
        "✓ src/js/app.js - Dynamic URL generation",
        "✓ src/robots.txt - Domain references",
        "✓ src/humans.txt - Site credits",
        "✓ Documentation files - Branding updates"
    ]
    
    for file_info in files_list:
        print(f"  {file_info}")
    
    print()
    print_info("Next steps:")
    print("  1. Add your logo images to src/images/")
    print("  2. Test locally: run scripts\\server.cmd or scripts/server.sh to start a local server for the site")
    print("  3. Generate sitemap: run scripts\\generate_sitemap.cmd or scripts/generate_sitemap.sh")
    print("  4. Deploy when ready!")
