#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Site Setup Tool
===============
Configuration tool for applying site.toml settings to project files.

This script reads configuration from config/site.toml and applies it to
CSS, HTML, and JavaScript files. It does not modify site.toml itself.

Usage:
    python utils/setup/setup.py -e dev
    python utils/setup/setup.py --environment production
    python utils/setup/setup.py -e dev --force

Options:
    -e, --environment    Environment name (required: dev, staging, production, etc.)
    --force              Update all files regardless of timestamps
    --dry-run            Preview operations without making changes (not yet fully implemented)

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
import argparse
import traceback

# Import all modules from the setup package
# Use relative imports to work when run as module
from . import ui_helpers
from . import config_io
from . import user_interaction
from . import file_generators
from . import backup_manager
from . import file_tracker

# Re-export for convenience
Colors = ui_helpers.Colors
print_header = ui_helpers.print_header
print_section = ui_helpers.print_section
print_info = ui_helpers.print_info
print_warning = ui_helpers.print_warning
print_error = ui_helpers.print_error
print_setup_completion = ui_helpers.print_setup_completion

load_existing_config = config_io.load_existing_config
backup_all_config_files = config_io.backup_all_config_files
update_canonical_base = config_io.update_canonical_base

generate_css_variables = file_generators.generate_css_variables
update_domain_references = file_generators.update_domain_references
update_image_references = file_generators.update_image_references
update_syntax_highlighting = file_generators.update_syntax_highlighting
update_stylesheet_integration = file_generators.update_stylesheet_integration
update_site_branding = file_generators.update_site_branding

cleanup_old_backups = backup_manager.cleanup_old_backups
add_manifest_to_backup = backup_manager.add_manifest_to_backup

clear_tracked_files = file_tracker.clear_tracked_files
copy_modified_files_to_environment = file_tracker.copy_modified_files_to_environment
copy_image_files_to_environment = file_tracker.copy_image_files_to_environment


def apply_configuration_files(config_data, environment, update_domain=True, force=False):
    """Generate all configuration files from config data
    
    Args:
        config_data: Dictionary containing all configuration values
        environment: Environment name (dev, staging, production, etc.)
        update_domain: If True, update domain references across project files
        force: If True, copy all files regardless of timestamp
    """
    # Clear any previously tracked files
    clear_tracked_files()
    
    # Backup all config files before making changes
    backup_all_config_files(environment)
    
    # Generate CSS variables
    generate_css_variables(config_data)
    
    # Update domain references (optional, skipped in force mode)
    if update_domain:
        update_domain_references(config_data)
    
    # Update site branding
    update_site_branding(config_data)
    
    # Update image references
    update_image_references(config_data)
    
    # Syntax highlighting (Prism.js) is now handled by the compose module
    # update_syntax_highlighting(config_data)
    
    # Update stylesheet integration
    update_stylesheet_integration(config_data)
    
    # Clean up old backups (keep only 5 most recent for this environment)
    cleanup_old_backups(5, environment)
    
    # Copy image files (favicon and logos) to environment directory first
    # This returns (copied_files, skipped_files, errors) tuples for manifest tracking
    image_copied, image_skipped, image_errors = copy_image_files_to_environment(environment, config_data, force=force)
    
    # Copy modified src/ files to environment directory
    # Pass image file tracking and errors so they're included in the manifest
    manifest_path = copy_modified_files_to_environment(
        environment, 
        force=force,
        additional_copied=image_copied,
        additional_skipped=image_skipped,
        additional_errors=image_errors
    )
    
    # Add manifest to backup zip if manifest was created
    if manifest_path:
        add_manifest_to_backup(manifest_path, environment)


def apply_configuration(config_data, environment, force):
    """Apply configuration data to all project files
    
    Args:
        config_data: Dictionary containing all configuration values
        environment: Environment name (dev, staging, production, etc.)
        force: If True, copy all files regardless of timestamp
    """
    print_section("Applying Configuration to Project Files")
    
    try:
        # Use shared logic, include domain updates
        apply_configuration_files(config_data, environment, update_domain=True, force=force)
        
        # Print completion message
        print_setup_completion(is_force_apply=force)
        
        return 0
        
    except Exception as e:
        print_error(f"Error during setup: {e}")
        traceback.print_exc()
        return 1


def main():
    """Main setup function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Site Setup Tool - Apply site.toml configuration to project files.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-e', '--environment',
        required=True,
        help='Environment name (dev, staging, production, etc.)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Update all files regardless of timestamps'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Ignored (accepted for compatibility with other modules)'
    )
    
    # Use parse_known_args to ignore unknown arguments from pipeline
    args, unknown = parser.parse_known_args()
    
    print_header("SITE SETUP TOOL")
    print_info(f"Environment: {args.environment}")
    print()
    
    if args.force:
        print(f"{Colors.BOLD}Force Mode - Updating all files regardless of timestamps...{Colors.ENDC}")
        print()
    else:
        print(f"{Colors.BOLD}Reading configuration from config/site.toml...{Colors.ENDC}")
        print()
    
    # Load existing configuration
    try:
        config_data = load_existing_config()
    except Exception as e:
        print_error(f"Failed to load config/site.toml: {e}")
        print_info("Please ensure config/site.toml exists and is valid.")
        return 1
    
    # Ensure canonical_base is updated based on domain
    if 'domain' in config_data and config_data['domain']:
        config_data['canonical_base'] = f"https://{config_data['domain']}/"
        # Write canonical_base back to site.toml
        update_canonical_base(config_data['domain'])
    
    # Apply the configuration
    return apply_configuration(config_data, args.environment, force=args.force)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled by user.{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)
