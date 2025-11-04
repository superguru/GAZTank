#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
GZLogging - Logging Module for GAZ Tank
========================================
Provides environment-aware logging functionality with automatic configuration
from tools.toml.

Authors: superguru, gazorper
License: GPL v3.0
"""

from .gzlogging import get_logging_context, LoggingContext

__all__ = ['get_logging_context', 'LoggingContext']
