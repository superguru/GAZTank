#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Sitemap Module Entry Point
===========================
Entry point for the sitemap module when run as a module.

Usage:
    python -m sitemap

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
from .sitemapper import main

if __name__ == "__main__":
    sys.exit(main())
