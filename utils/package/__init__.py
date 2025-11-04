#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Package Module
==============
Website packaging system for deployment preparation.

This module handles packaging the specified environment directory:
- Orphaned file cleanup (removes files not in source)
- Asset minification (CSS and JavaScript)
- Archive creation with timestamped backups
- Backup retention management

Does NOT perform generation, validation, or sitemap creation.
Those are separate pipeline steps that run before packaging.

Authors: superguru, gazorper
License: GPL v3.0
"""

from .packager import (
    package_site,
    minify_assets,
    backup_previous_package,
    cleanup_old_backups,
    minify_css,
    minify_js,
    update_package_metadata,
)

__all__ = [
    'package_site',
    'minify_assets',
    'backup_previous_package',
    'cleanup_old_backups',
    'minify_css',
    'minify_js',
    'update_package_metadata',
]
