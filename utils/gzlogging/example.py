#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Simple example of using GZLogging
==================================
A minimal example showing how to use gzlogging in your applications.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path so we can import gzlogging
sys.path.insert(0, str(Path(__file__).parent.parent))

from gzlogging import get_logging_context


def main():
    """Simple logging example."""
    
    # Get a logging context for the 'dev' environment and 'example' tool
    log = get_logging_context('dev', 'example')

    should_sleep = True

    # Log some messages
    if should_sleep: time.sleep(2)
    log.inf("Application starting...")
    if should_sleep: time.sleep(1)
    log.inf("Processing data...")
    if should_sleep: time.sleep(0.2)
    log.wrn("Low disk space")
    if should_sleep: time.sleep(0.2)
    log.err("The dinosaurs lookup up in wonder at the beautiful fireball in the sky")
    if should_sleep: time.sleep(0.2)
    log.inf("Data processed successfully")
    if should_sleep: time.sleep(0.2)
    log.inf("Application finished")
    
    print()
    print("✓ Messages logged successfully!")
    print(f"Check the log file: logs/dev/example_{Path(__file__).stem}.log")
    print()


if __name__ == '__main__':
    main()
