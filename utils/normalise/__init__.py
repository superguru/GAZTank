#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Markdown Normaliser
===================
Converts standalone bold text to proper markdown headings while preserving
bold text used for emphasis within sentences and lists.

Authors: superguru, gazorper
License: GPL v3.0
"""

from .normaliser import (
    ProcessingState,
    read_file,
    write_file,
    get_stripped_standalone_bold,
    count_leading_hashes,
    get_heading_level,
    should_skip_line,
    process_line,
    process_lines,
    process_file,
    main
)
from .batch import main as batch_main

__version__ = "1.0.0"
__all__ = [
    "ProcessingState",
    "read_file",
    "write_file",
    "get_stripped_standalone_bold",
    "count_leading_hashes",
    "get_heading_level",
    "should_skip_line",
    "process_line",
    "process_lines",
    "process_file",
    "main",
    "batch_main"
]
