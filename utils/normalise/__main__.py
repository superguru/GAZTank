#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Markdown Normaliser Entry Point
===============================
Entry point for the markdown normaliser when run as a module.

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
from .normaliser import main

if __name__ == "__main__":
    sys.exit(main())
