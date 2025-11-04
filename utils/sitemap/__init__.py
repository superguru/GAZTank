#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Sitemap Module
==============
XML sitemap generation for search engine optimization.

This module automatically generates sitemap.xml files by scanning HTML content
files and parsing the navigation structure from index.html. It assigns priorities
and change frequencies based on content hierarchy and type.

Authors: superguru, gazorper
License: GPL v3.0
"""

from .sitemapper import (
    generate_sitemap,
    get_content_files,
    parse_navigation_structure,
    calculate_priority,
    determine_changefreq,
    get_file_last_modified,
    get_project_root,
)

__all__ = [
    'generate_sitemap',
    'get_content_files',
    'parse_navigation_structure',
    'calculate_priority',
    'determine_changefreq',
    'get_file_last_modified',
    'get_project_root',
]
