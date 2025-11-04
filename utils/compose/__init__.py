"""
Compose Module
==============

Assembles HTML files from source components based on configuration.

This module reads compose.toml to determine which files to compose,
then processes composition markers in base HTML files to conditionally
include components based on site.toml feature flags.

Author: superguru
Version: 1.0
Last Updated: November 4, 2025
"""

from .composer import main

__version__ = "1.0"
__all__ = ["main"]
