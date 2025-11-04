#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
GZHost - FTP Host Server Module
================================
Simulates remote FTP deployment hosts for local testing using pyftpdlib.

This module provides a simple FTP server that serves files from environment-specific
directories (dev/staging/prod) under publish/ with user authentication.

Usage:
    python -m utils.gzhost -e <environment> [-p <port>]

Examples:
    python -m utils.gzhost -e dev                 # Serve dev environment on configured port
    python -m utils.gzhost -e staging -p 2190     # Serve staging on port 2190
    python -m utils.gzhost -e prod                # Serve production environment

Configuration:
    - Environments: config/pipeline.toml
    - FTP Users: config/ftp_users.toml

Authors: superguru, gazorper
License: GPL v3.0
"""

from .host import start_ftp_server, main

__all__ = ['start_ftp_server', 'main']

__version__ = '1.0.0'
