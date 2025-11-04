#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Deploy Module
=============
Handles deploying packaged websites to FTP/FTPS servers.

This module provides functions for uploading site packages to remote servers,
with support for both FTP and FTPS protocols, progress tracking, and
automated subdirectory creation.

Authors: superguru, gazorper
License: GPL v3.0
"""

from .deployer import main

__all__ = ['main']
