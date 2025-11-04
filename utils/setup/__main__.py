#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Setup Module Entry Point
========================
Allows running the setup module with: python -m setup

Authors: superguru, gazorper
License: GPL v3.0
"""

from .setup import main

if __name__ == "__main__":
    import sys
    sys.exit(main())
