#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Table of Contents Generator - Entry Point
==========================================
Entry point for running the TOC generator as a module.

Usage:
    python -m utils.toc -e dev
    python -m utils.toc -e staging --strip
    python -m utils.toc -e prod --dry-run

Authors: superguru, gazorper
License: GPL v3.0
"""

from .toc import main

if __name__ == "__main__":
    import sys
    sys.exit(main())
