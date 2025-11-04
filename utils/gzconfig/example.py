#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Simple example of using GZConfig
=================================
A minimal example showing how to use gzconfig in your applications.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import gzconfig
sys.path.insert(0, str(Path(__file__).parent.parent))

from gzconfig import get_pipeline_config, PipelineConfig, PipelineEnvironment


def main():
    """Simple configuration example."""
    
    print("=" * 60)
    print("GZConfig Pipeline Configuration Example")
    print("=" * 60)
    print()
    
    # Example 1: Get full configuration
    print("Example 1: Get full pipeline configuration")
    print("-" * 60)
    config: PipelineConfig = get_pipeline_config()  # type: ignore
    print(f"Available environments: {config.environment_names}")
    print()
    
    # Example 2: Access all environments
    print("Example 2: Iterate through all environments")
    print("-" * 60)
    for env_name, env in config.environments.items():
        print(f"  {env_name}:")
        print(f"    Directory: {env.dir}")
        print(f"    Port: {env.port}")
        print(f"    Path: {env.directory_path}")
        print(f"    Description: {env.description}")
        print()
    
    # Example 3: Get specific environment directly
    print("Example 3: Get specific environment")
    print("-" * 60)
    dev: PipelineEnvironment = get_pipeline_config('dev')  # type: ignore
    print(f"Environment: {dev.name}")
    print(f"Directory: {dev.dir}")
    print(f"Port: {dev.port}")
    print(f"Full path: {dev.directory_path}")
    print(f"Description: {dev.description}")
    print()
    
    # Example 4: Use in application
    print("Example 4: Typical application usage")
    print("-" * 60)
    environment_name = 'staging'
    env: PipelineEnvironment = get_pipeline_config(environment_name)  # type: ignore
    print(f"Starting server for {env.name} environment")
    print(f"Serving from: {env.directory_path}")
    print(f"Server will listen on port: {env.port}")
    print()
    
    print("=" * 60)
    print("✓ All examples completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
