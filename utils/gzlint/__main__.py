#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
GZLint Module Entry Point
==========================
Allows the gzlint module to be run as: python -m gzlint

Authors: superguru, gazorper
License: GPL v3.0
"""

from .gzlinter import main

if __name__ == "__main__":
    import sys
    sys.exit(main())
