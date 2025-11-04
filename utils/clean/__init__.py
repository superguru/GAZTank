#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Clean Module
============
Environment cleanup system for removing orphaned files.

This module identifies and removes files in environment directories
that no longer exist in the source directory, ensuring environments
stay synchronized with the source of truth.

Authors: superguru, gazorper
License: GPL v3.0
"""

from .cleaner import (
    clean_site,
    get_orphaned_files,
    remove_orphaned_files,
    remove_all_files,
)

__all__ = [
    'clean_site',
    'get_orphaned_files',
    'remove_orphaned_files',
    'remove_all_files',
]
