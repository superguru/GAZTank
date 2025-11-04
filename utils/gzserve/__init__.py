#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Development Web Server Module
==============================
A simple, no-cache, multi-threaded development web server for local testing.

This module provides a development HTTP server with:
- No-cache headers for development
- Multi-threaded request handling
- Interactive admin console for graceful shutdown
- Custom port configuration
- Automatic src/ directory serving

Usage as a module:
    from utils.serve import start_server
    start_server(port=7190)

Usage from command line:
    python -m utils.serve [port]
    python utils/serve/server.py [port]

Authors: superguru, gazorper
License: GPL v3.0
Version: 1.0.0
"""

from .server import (
    start_server,
    NoCacheHTTPRequestHandler,
    ReusableTCPServer,
    DEFAULT_PORT
)

__version__ = '1.0.0'
__all__ = [
    'start_server',
    'NoCacheHTTPRequestHandler',
    'ReusableTCPServer',
    'DEFAULT_PORT'
]
