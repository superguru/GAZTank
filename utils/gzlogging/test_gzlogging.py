#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Test script for GZLogging module
=================================
Demonstrates usage of the gzlogging module with various scenarios.

Usage:
    python test_gzlogging.py [environment] [tool_name]
    
    environment: dev, staging, or prod (default: dev)
    tool_name: Name of the tool (default: test)

Examples:
    python test_gzlogging.py
    python test_gzlogging.py staging
    python test_gzlogging.py prod myapp
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import gzlogging
sys.path.insert(0, str(Path(__file__).parent.parent))

from gzlogging import get_logging_context


def test_basic_logging(environment: str, tool_name: str):
    """Test basic logging functionality."""
    print("=" * 70)
    print("GZLogging Test Script")
    print("=" * 70)
    print(f"Environment: {environment}")
    print(f"Tool Name: {tool_name}")
    print()
    
    # Get logging context
    print("Creating logging context...")
    try:
        ctx = get_logging_context(environment, tool_name)
        print(f"✓ Logging context created successfully")
        print(f"  Environment (read-only): {ctx.environment}")
        print(f"  Tool Name: {ctx.tool_name}")
        print()
    except Exception as e:
        print(f"✗ Failed to create logging context: {e}")
        return
    
    # Test different log levels
    print("Writing log messages...")
    print()
    
    print("1. Testing INF level:")
    ctx.inf("This is an informational message")
    print("   ✓ INF message logged")
    
    print("2. Testing WRN level:")
    ctx.wrn("This is a warning message")
    print("   ✓ WRN message logged")
    
    print("3. Testing ERR level:")
    ctx.err("This is an error message")
    print("   ✓ ERR message logged")
    
    print("4. Testing DBG level:")
    ctx.dbg("This is a debug message")
    print("   ✓ DBG message logged")
    
    print()
    print("5. Testing multi-line message:")
    ctx.inf("Starting complex operation...")
    ctx.inf("Step 1: Initialize")
    ctx.inf("Step 2: Process")
    ctx.inf("Step 3: Finalize")
    ctx.inf("Complex operation completed")
    print("   ✓ Multi-line messages logged")
    
    print()
    print("6. Testing Unicode characters:")
    ctx.inf("Testing Unicode: ✓ ✗ → ← ↑ ↓ © ® ™ € £ ¥")
    ctx.inf("Testing emoji: 🚀 ✨ 🎉 💡 ⚙️ 📝 🔧")
    print("   ✓ Unicode messages logged")
    
    print()
    print("=" * 70)
    print("Test completed successfully!")
    print("=" * 70)
    print()
    print("Log file location:")
    print(f"  {Path.cwd() / 'logs' / environment / f'{tool_name}_{Path(__file__).stem}.log'}")
    print()
    
    # Show that environment is read-only
    print("Verifying environment is read-only...")
    try:
        ctx.environment = "test"  # type: ignore
        print("   ✗ ERROR: Environment should be read-only!")
    except AttributeError:
        print("   ✓ Environment property is read-only (as expected)")
    
    print()


def test_multiple_contexts():
    """Test creating multiple logging contexts."""
    print("=" * 70)
    print("Testing Multiple Logging Contexts")
    print("=" * 70)
    print()
    
    # Create contexts for different tools in same environment
    print("Creating multiple contexts for 'dev' environment...")
    ctx1 = get_logging_context('dev', 'tool1')
    ctx2 = get_logging_context('dev', 'tool2')
    
    print("✓ Created context for tool1")
    print("✓ Created context for tool2")
    print()
    
    print("Writing messages from different tools...")
    ctx1.inf("Message from tool1")
    ctx2.inf("Message from tool2")
    ctx1.wrn("Another message from tool1")
    ctx2.err("Error from tool2")
    
    print("✓ Messages written from both tools")
    print()
    
    # Create contexts for different environments
    print("Creating contexts for different environments...")
    try:
        dev_ctx = get_logging_context('dev', 'multitest')
        staging_ctx = get_logging_context('staging', 'multitest')
        prod_ctx = get_logging_context('prod', 'multitest')
        
        print("✓ Created context for dev")
        print("✓ Created context for staging")
        print("✓ Created context for prod")
        print()
        
        print("Writing messages to different environments...")
        dev_ctx.inf("Development environment message")
        staging_ctx.inf("Staging environment message")
        prod_ctx.inf("Production environment message")
        
        print("✓ Messages written to all environments")
        print()
        
    except Exception as e:
        print(f"Note: Some environments may not be configured: {e}")
        print()
    
    print("=" * 70)
    print()


def test_error_handling():
    """Test error handling."""
    print("=" * 70)
    print("Testing Error Handling")
    print("=" * 70)
    print()
    
    # Test invalid environment
    print("1. Testing invalid environment name...")
    try:
        ctx = get_logging_context('invalid_env', 'test')
        print("   ✗ Should have raised an error!")
    except ValueError as e:
        print(f"   ✓ Caught expected error: {e}")
    
    print()
    print("=" * 70)
    print()


def show_usage():
    """Show usage information."""
    print(__doc__)


def main():
    """Main test function."""
    # Parse arguments
    environment = 'dev'
    tool_name = 'test'
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            show_usage()
            return
        environment = sys.argv[1]
    
    if len(sys.argv) > 2:
        tool_name = sys.argv[2]
    
    # Run tests
    test_basic_logging(environment, tool_name)
    test_multiple_contexts()
    test_error_handling()
    
    print("All tests completed!")
    print()
    print("Check the logs directory for output files:")
    print(f"  {Path.cwd() / 'logs' / environment}/")
    print()


if __name__ == '__main__':
    main()
