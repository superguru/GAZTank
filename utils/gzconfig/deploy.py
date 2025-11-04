#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Deploy Configuration Module
============================
Handles loading and parsing of deploy.toml configuration file.

Provides access to FTP/FTPS deployment settings including:
- Server connection details
- Upload subdirectory formatting
- Security settings (FTPS)

Authors: superguru, gazorper
License: GPL v3.0
"""

import tomllib
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class DeployConfig:
    """Deploy configuration from deploy.toml"""
    
    server: str
    username: str
    password: str
    target_dir: str
    port: int = 21
    use_ftps: bool = True
    upload_subdir_fmt: str = "%Y%m%d_%H%M%S_%j"
    upload_subdir_postfix_len: int = 5
    
    def __post_init__(self):
        """Validate configuration values"""
        if not self.server:
            raise ValueError("FTP server must be specified")
        if not self.username:
            raise ValueError("FTP username must be specified")
        if not self.password:
            raise ValueError("FTP password must be specified")
        if not self.target_dir:
            raise ValueError("FTP target directory must be specified")
        
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port number: {self.port}")
        
        if self.upload_subdir_postfix_len < 1 or self.upload_subdir_postfix_len > 10:
            raise ValueError(
                f"upload_subdir_postfix_len must be between 1 and 10, "
                f"got {self.upload_subdir_postfix_len}"
            )
    
    def __repr__(self) -> str:
        """String representation (masks password)"""
        return (
            f"DeployConfig(server='{self.server}', port={self.port}, "
            f"use_ftps={self.use_ftps}, username='{self.username}', "
            f"password='***', target_dir='{self.target_dir}', "
            f"upload_subdir_fmt='{self.upload_subdir_fmt}', "
            f"upload_subdir_postfix_len={self.upload_subdir_postfix_len})"
        )


# Module-level cache
_cached_config: Optional[DeployConfig] = None


def get_deploy_config() -> DeployConfig:
    """
    Load and parse deploy.toml configuration file.
    
    Returns:
        DeployConfig object with FTP deployment settings
        
    Raises:
        FileNotFoundError: If deploy.toml doesn't exist
        ValueError: If required fields are missing or invalid
        
    Note:
        Results are cached after first load. The config file is only
        read once per process.
    """
    global _cached_config
    
    if _cached_config is not None:
        return _cached_config
    
    # Find config file
    config_path = Path(__file__).parent.parent.parent / "config" / "deploy.toml"
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Deploy configuration not found: {config_path}\n"
            f"Copy config/deploy.example.toml to config/deploy.toml and fill in your FTP details"
        )
    
    # Load and parse TOML
    with open(config_path, "rb") as f:
        data = tomllib.load(f)
    
    # Validate structure
    if "ftp" not in data:
        raise ValueError("deploy.toml must contain [ftp] section")
    
    ftp_data = data["ftp"]
    
    # Check required fields
    required_fields = ["server", "username", "password", "target_dir"]
    missing = [field for field in required_fields if field not in ftp_data]
    if missing:
        raise ValueError(
            f"Missing required fields in [ftp] section: {', '.join(missing)}"
        )
    
    # Create config object with defaults
    _cached_config = DeployConfig(
        server=ftp_data["server"],
        username=ftp_data["username"],
        password=ftp_data["password"],
        target_dir=ftp_data["target_dir"],
        port=ftp_data.get("port", 21),
        use_ftps=ftp_data.get("use_ftps", True),
        upload_subdir_fmt=ftp_data.get("upload_subdir_fmt", "%Y%m%d_%H%M%S_%j"),
        upload_subdir_postfix_len=ftp_data.get("upload_subdir_postfix_len", 5),
    )
    
    return _cached_config
