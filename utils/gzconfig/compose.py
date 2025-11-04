"""
Compose Configuration Module
============================

Provides access to compose.toml configuration for HTML composition.

This module reads config/compose.toml which defines how HTML files
are assembled from source components.

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


def get_compose_config() -> dict:
    """
    Load and return composition configuration from config/compose.toml
    
    Returns:
        Dictionary containing composition definitions
        
    Raises:
        FileNotFoundError: If compose.toml not found
        tomli.TOMLDecodeError: If TOML syntax error
    """
    config_path = Path(__file__).parent.parent.parent / 'config' / 'compose.toml'
    
    if not config_path.exists():
        raise FileNotFoundError(f"Compose configuration not found: {config_path}")
    
    with config_path.open('rb') as f:
        return tomli.load(f)
