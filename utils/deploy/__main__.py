#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Deploy Module Entry Point
==========================
Allows the deploy module to be run as: python -m deploy

Authors: superguru, gazorper
License: GPL v3.0
"""

from .deployer import main

if __name__ == "__main__":
    main()
