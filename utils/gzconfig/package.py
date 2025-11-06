#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Package Configuration Module
=============================
Provides access to package.toml configuration.

Authors: superguru, gazorper
License: GPL v3.0
"""

import tomllib
from pathlib import Path
from typing import List
from dataclasses import dataclass


@dataclass
class PackageExclusions:
    """Package exclusions configuration"""
    directories: List[str]
    files: List[str]


@dataclass
class PackageConfig:
    """Package configuration"""
    max_backups: int
    exclusions: PackageExclusions
    
    def __post_init__(self):
        """Validate configuration values"""
        if self.max_backups < 1:
            raise ValueError(f"max_backups must be a positive integer, got {self.max_backups}")


def get_package_config() -> PackageConfig:
    """
    Load and parse package.toml configuration.
    
    Returns:
        PackageConfig object with package settings
        
    Raises:
        FileNotFoundError: If package.toml doesn't exist
        ValueError: If configuration is invalid
    """
    config_path = Path(__file__).parent.parent.parent / 'config' / 'package.toml'
    
    if not config_path.exists():
        raise FileNotFoundError(f"Package configuration not found: {config_path}")
    
    # Load and parse TOML
    with open(config_path, 'rb') as f:
        data = tomllib.load(f)
    
    # Parse package section
    if 'package' not in data:
        raise ValueError("Missing [package] section in package.toml")
    
    package_section = data['package']
    max_backups = package_section.get('max_backups', 4)
    
    # Parse exclusions section
    if 'exclusions' not in data:
        raise ValueError("Missing [exclusions] section in package.toml")
    
    exclusions_section = data['exclusions']
    directories = exclusions_section.get('directories', [])
    files = exclusions_section.get('files', [])
    
    # Create exclusions object
    exclusions = PackageExclusions(
        directories=directories,
        files=files
    )
    
    # Create and return config object
    return PackageConfig(
        max_backups=max_backups,
        exclusions=exclusions
    )
