#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
GZLint Module
=============
HTML & JavaScript linter for the GAZTank project.

This module provides functions for scanning and validating HTML and JavaScript
files for common issues and best practice violations.

Authors: superguru, gazorper
License: GPL v3.0
"""

from .gzlinter import (
    GZLinter,
    HTMLLinter,
    JSLinter,
    LintIssue,
    HeadingParser,
    HTMLValidator
)

__all__ = [
    'GZLinter',
    'HTMLLinter',
    'JSLinter',
    'LintIssue',
    'HeadingParser',
    'HTMLValidator'
]
