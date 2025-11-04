#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Table of Contents Generator
============================
Adds IDs to headings and injects TOC HTML into content files at build time.

Authors: superguru, gazorper
License: GPL v3.0
"""

from .toc import (
    slugify,
    add_ids_to_headings,
    remove_ids_from_headings,
    build_toc_structure,
    inject_toc,
    remove_existing_toc,
    process_html_file,
    strip_toc_from_file,
    scan_html_files,
    main
)

__version__ = "1.0.0"
__all__ = [
    "slugify",
    "add_ids_to_headings",
    "remove_ids_from_headings",
    "build_toc_structure",
    "inject_toc",
    "remove_existing_toc",
    "process_html_file",
    "strip_toc_from_file",
    "scan_html_files",
    "main"
]
