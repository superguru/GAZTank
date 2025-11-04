#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Development Web Server - Module Entry Point
============================================
Entry point for running the server module with: python -m utils.server

Usage:
    python -m utils.server [port]

Examples:
    python -m utils.server          # Use default port 7190
    python -m utils.server 8080     # Use custom port 8080

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
from .server import main

if __name__ == '__main__':
    sys.exit(main())
