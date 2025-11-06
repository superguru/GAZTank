#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
GZConfig - Configuration Management Module
===========================================
Provides clean, abstracted access to project configuration files.

Currently supports:
- Pipeline configuration (pipeline.toml)
- Generate configuration (generate.toml)
- Tools configuration (tools.toml)
- FTP Users configuration (ftp_users.toml)

Future support planned for:
- Site configuration (site.toml)
- Other project configuration files

Authors: superguru, gazorper
License: GPL v3.0
"""

from .pipeline import get_pipeline_config, PipelineEnvironment, PipelineConfig
from .generate import get_generate_config, GenerateGroup, GenerateConfig
from .tools import get_tools_config, ToolsEnvironment, ToolsConfig
from .ftp_users import get_ftp_users_config, FTPUserEnvironment, FTPUsersConfig
from .deploy import get_deploy_config, DeployConfig
from .site import get_site_config
from .compose import get_compose_config
from .package import get_package_config, PackageConfig, PackageExclusions

__all__ = [
    'get_pipeline_config',
    'PipelineEnvironment',
    'PipelineConfig',
    'get_generate_config',
    'GenerateGroup',
    'GenerateConfig',
    'get_tools_config',
    'ToolsEnvironment',
    'ToolsConfig',
    'get_ftp_users_config',
    'FTPUserEnvironment',
    'FTPUsersConfig',
    'get_deploy_config',
    'DeployConfig',
    'get_site_config',
    'get_compose_config',
    'get_package_config',
    'PackageConfig',
    'PackageExclusions',
]

__version__ = '1.0.0'
