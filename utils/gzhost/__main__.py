#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
FTP Host Server - Module Entry Point
=====================================
Entry point for running the gzhost module with: python -m utils.gzhost

Usage:
    python -m utils.gzhost -e <environment> [-p <port>]

Examples:
    python -m utils.gzhost -e dev                 # Serve dev environment on configured port
    python -m utils.gzhost -e staging -p 2190     # Serve staging on port 2190
    python -m utils.gzhost -e prod                # Serve production environment

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
from .host import main

if __name__ == '__main__':
    sys.exit(main())
