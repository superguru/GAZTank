#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Package Module Entry Point
===========================
Entry point for the package module when run as a module.

Usage:
    python -m package -e <environment> [--force] [--dry-run]

Examples:
    python -m package -e dev
    python -m package -e staging --force
    python -m package -e prod --dry-run

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
from .packager import main

if __name__ == "__main__":
    sys.exit(main())
