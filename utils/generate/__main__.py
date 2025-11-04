#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Generate Module Entry Point
============================
Allows running the generate module as: python -m utils.generate

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
from .generator import main

if __name__ == '__main__':
    sys.exit(main())
