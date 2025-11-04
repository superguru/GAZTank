#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Setup Package
=============
Site setup wizard modular package.

Authors: superguru, gazorper
License: GPL v3.0
"""

from .ui_helpers import (
    Colors,
    print_header,
    print_section,
    print_success,
    print_error,
    print_warning,
    print_info,
    format_setup_date,
    print_setup_completion
)

from .validators import get_color, hex_to_rgba

from .backup_manager import create_backup, cleanup_old_backups

from .config_io import (
    load_existing_config,
    is_first_time_setup,
    update_config_file,
    backup_all_config_files
)

from .user_interaction import get_input, get_yes_no, interactive_setup

from .file_generators import (
    generate_css_variables,
    update_domain_references,
    update_image_references,
    update_stylesheet_integration,
    update_site_branding
)

from .file_tracker import (
    track_modified_file,
    get_modified_files,
    clear_tracked_files,
    copy_modified_files_to_environment
)

__all__ = [
    # UI Helpers
    'Colors',
    'print_header',
    'print_section',
    'print_success',
    'print_error',
    'print_warning',
    'print_info',
    'format_setup_date',
    'print_setup_completion',
    # Validators
    'get_color',
    'hex_to_rgba',
    # Backup Manager
    'create_backup',
    'cleanup_old_backups',
    # Config I/O
    'load_existing_config',
    'is_first_time_setup',
    'update_config_file',
    'backup_all_config_files',
    # User Interaction
    'get_input',
    'get_yes_no',
    'interactive_setup',
    # File Generators
    'generate_css_variables',
    'update_domain_references',
    'update_image_references',
    'update_stylesheet_integration',
    'update_site_branding',
    # File Tracker
    'track_modified_file',
    'get_modified_files',
    'clear_tracked_files',
    'copy_modified_files_to_environment',
]
