#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Backup Manager
==============
File backup creation and cleanup utilities.

Authors: superguru, gazorper
License: GPL v3.0
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

from . import ui_helpers

print_info = ui_helpers.print_info
print_warning = ui_helpers.print_warning


def create_backup(file_path, environment='unknown'):
    """Create a backup of config files in a timestamped zip file in publish/backups
    
    Only config files from the config/ directory are backed up. Files in other directories,
    backup files (.backup.*), and example files (.example.*) are skipped.
    
    Args:
        file_path: Path to the file to backup
        environment: Environment name to include in zip filename (dev, staging, production, etc.)
        
    Returns:
        String path to the backup zip file, or None if file doesn't exist or is not a config file
    """
    if not os.path.exists(file_path):
        return None
    
    # Convert to Path object and resolve to absolute path
    source_path = Path(file_path).resolve()
    
    # Only backup files in the config directory
    try:
        relative_path = source_path.relative_to(Path.cwd().resolve())
        # Check if file is in config directory
        if relative_path.parts[0] != 'config':
            return None
    except (ValueError, IndexError):
        # Not in current working directory or no parts
        return None
    
    # Skip backup files and example files
    if '.backup.' in source_path.name or '.example.' in source_path.name:
        return None
    
    # Get the current timestamp for this backup session
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    
    # Create backup directory
    backup_base = Path("publish/backups")
    backup_base.mkdir(parents=True, exist_ok=True)
    
    # Create zip file path with environment name
    zip_path = backup_base / f"config_{environment}_{timestamp}.zip"
    
    # If zip already exists (multiple config files in same session), append to it
    mode = 'a' if zip_path.exists() else 'w'
    
    with zipfile.ZipFile(zip_path, mode, zipfile.ZIP_DEFLATED) as zipf:
        # Store the file with its relative path structure
        zipf.write(file_path, arcname=str(relative_path))
    
    print_info(f"Backed up config to: {zip_path}")
    return str(zip_path)


def add_manifest_to_backup(manifest_path, environment):
    """Add manifest file to the most recent backup zip for this environment
    
    Adds the manifest to the zip and then deletes the temporary manifest file.
    
    Args:
        manifest_path: Path to the manifest markdown file
        environment: Environment name to match backup zip
    
    Returns:
        True if successful, False otherwise
    """
    if not manifest_path or not Path(manifest_path).exists():
        return False
    
    try:
        # Find the most recent backup zip for this environment
        backup_base = Path("publish/backups")
        if not backup_base.exists():
            return False
        
        # Get current timestamp (YYYYMMDDHHMM format)
        current_time = datetime.now()
        timestamp = current_time.strftime('%Y%m%d%H%M')
        
        # Look for backup zip with this environment and timestamp
        pattern = f"config_{environment}_{timestamp}.zip"
        backup_zips = list(backup_base.glob(pattern))
        
        if not backup_zips:
            print_warning(f"No matching backup zip found: {pattern}")
            # Clean up temp file
            try:
                Path(manifest_path).unlink()
            except:
                pass
            return False
        
        # Should only be one match for current timestamp
        zip_path = backup_zips[0]
        
        # Add manifest to the zip with simple filename
        with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(manifest_path, arcname="setup_manifest.md")
        
        print_info(f"Added manifest to backup: {zip_path}")
        
        # Delete the temporary manifest file
        try:
            Path(manifest_path).unlink()
        except Exception as e:
            print_warning(f"Could not delete temporary manifest: {e}")
        
        return True
        
    except Exception as e:
        print_warning(f"Failed to add manifest to backup: {e}")
        # Clean up temp file on error
        try:
            Path(manifest_path).unlink()
        except:
            pass
        return False


def cleanup_old_backups(max_backups=5, environment=None):
    """Clean up old backup zip files, keeping only the most recent ones
    
    Args:
        max_backups: Maximum number of backup zip files to keep
        environment: If provided, only clean up backups for this environment
    """
    # Clean up zip backups in publish/backups
    backups_dir = Path("publish/backups")
    if backups_dir.exists():
        # Get all backup zip files (optionally filtered by environment)
        if environment:
            pattern = f"config_{environment}_*.zip"
        else:
            pattern = "config_*_*.zip"
        
        backup_zips = list(backups_dir.glob(pattern))
        
        if len(backup_zips) > max_backups:
            # Sort by filename (contains timestamp), newest first
            backup_zips.sort(key=lambda x: x.stem.split('_')[-1], reverse=True)
            
            # Keep only the most recent max_backups, remove the rest
            files_to_remove = backup_zips[max_backups:]
            
            for old_zip in files_to_remove:
                try:
                    old_zip.unlink()
                    print_info(f"Removed old backup: {old_zip}")
                except Exception as e:
                    print_warning(f"Could not remove old backup {old_zip}: {e}")
    
    # Clean up local site.toml backup files in config directory
    config_dir = Path("config")
    if config_dir.exists():
        # Get all site.toml backup files
        backup_files = list(config_dir.glob("site.toml.backup.*"))
        
        if len(backup_files) > max_backups:
            # Sort by timestamp in filename, newest first
            backup_files.sort(key=lambda x: x.name.split('.')[-1], reverse=True)
            
            # Keep only the most recent max_backups, remove the rest
            files_to_remove = backup_files[max_backups:]
            
            for old_file in files_to_remove:
                try:
                    old_file.unlink()
                    print_info(f"Removed old backup file: {old_file}")
                except Exception as e:
                    print_warning(f"Could not remove old backup file {old_file}: {e}")
