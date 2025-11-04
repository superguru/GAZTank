"""
Site Configuration Module
=========================

Provides access to site.toml configuration.

This module reads config/site.toml and provides it as a dictionary.
Unlike other gzconfig modules, site configuration is typically accessed
as a raw dict since it contains many dynamic sections (theme colors, etc.).

Author: superguru
Version: 1.0
Last Updated: November 4, 2025
"""

from pathlib import Path
import sys

# Use tomllib for Python 3.11+, tomli for older versions
if sys.version_info >= (3, 11):
    import tomllib as tomli
else:
    import tomli


def get_site_config() -> dict:
    """
    Load and return site configuration from config/site.toml
    
    Returns:
        Dictionary containing site configuration
        
    Raises:
        FileNotFoundError: If site.toml not found
        tomli.TOMLDecodeError: If TOML syntax error
    """
    config_path = Path(__file__).parent.parent.parent / 'config' / 'site.toml'
    
    if not config_path.exists():
        raise FileNotFoundError(f"Site configuration not found: {config_path}")
    
    with config_path.open('rb') as f:
        return tomli.load(f)
