#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
FTP Users Configuration Handler
================================
Handles reading and providing access to ftp_users.toml configuration.

Authors: superguru, gazorper
License: GPL v3.0
"""

from pathlib import Path
from typing import Optional

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore # Fallback for Python < 3.11
    except ModuleNotFoundError:
        tomllib = None  # type: ignore


class FTPUserEnvironment:
    """
    Represents FTP user credentials and permissions for a single environment.
    
    Provides property-based access to FTP user settings.
    """
    
    def __init__(self, name: str, config: dict):
        """
        Initialize FTP user configuration.
        
        Args:
            name: Environment name (e.g., 'dev', 'staging', 'prod')
            config: Configuration dictionary for this environment
        """
        self._name = name
        self._config = config
    
    @property
    def name(self) -> str:
        """Environment name (e.g., 'dev', 'staging', 'prod')."""
        return self._name
    
    @property
    def username(self) -> str:
        """FTP login username."""
        return self._config.get('username', f'{self._name}_user')
    
    @property
    def password(self) -> str:
        """FTP login password (plain text, local development only)."""
        return self._config.get('password', f'{self._name}_pass')
    
    @property
    def permissions(self) -> str:
        """
        Permission string for pyftpdlib authorizer.
        
        Common values:
        - 'elr' = Read-only access
        - 'elradfmwMT' = Full access (read, write, delete, create)
        - 'elrw' = Read and write, no delete
        """
        return self._config.get('permissions', 'elr')
    
    def __repr__(self) -> str:
        return f"FTPUserEnvironment(name='{self.name}', username='{self.username}', permissions='{self.permissions}')"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.username})"


class FTPUsersConfig:
    """
    FTP users configuration manager.
    
    Provides access to all FTP user configurations by environment.
    """
    
    def __init__(self, config_dict: dict):
        """
        Initialize FTP users configuration.
        
        Args:
            config_dict: Raw configuration dictionary from ftp_users.toml
        """
        self._config = config_dict
        self._environments = {}
        
        # Parse environments
        if 'environments' in config_dict:
            for env_name, env_config in config_dict['environments'].items():
                self._environments[env_name] = FTPUserEnvironment(env_name, env_config)
    
    def get_environment(self, name: str) -> FTPUserEnvironment:
        """
        Get FTP user configuration for a specific environment.
        
        Args:
            name: Environment name (e.g., 'dev', 'staging', 'prod')
        
        Returns:
            FTPUserEnvironment object
        
        Raises:
            ValueError: If environment is not defined
        """
        if name not in self._environments:
            available = ', '.join(self._environments.keys())
            raise ValueError(
                f"Environment '{name}' is not defined in ftp_users.toml. "
                f"Available environments: {available}"
            )
        
        return self._environments[name]
    
    @property
    def environments(self) -> dict[str, FTPUserEnvironment]:
        """Dictionary of all available FTP user environments."""
        return self._environments.copy()
    
    @property
    def environment_names(self) -> list[str]:
        """List of all available environment names."""
        return list(self._environments.keys())
    
    def __repr__(self) -> str:
        env_list = ', '.join(self._environments.keys())
        return f"FTPUsersConfig(environments=[{env_list}])"


def _find_project_root() -> Path:
    """
    Find the project root directory.
    
    Starts from this file and navigates upward until it finds the project root
    (identified by the presence of config/ directory).
    
    Returns:
        Path to the project root directory
    
    Raises:
        FileNotFoundError: If project root cannot be determined
    """
    current_file = Path(__file__).resolve()
    
    # Navigate up from utils/gzconfig/ftp_users.py to project root
    if current_file.parent.name == 'gzconfig' and current_file.parent.parent.name == 'utils':
        project_root = current_file.parent.parent.parent
    else:
        # Fallback: search upward for config directory
        current_dir = current_file.parent
        while current_dir.parent != current_dir:  # Stop at filesystem root
            if (current_dir / 'config').exists() and (current_dir / 'config').is_dir():
                project_root = current_dir
                break
            current_dir = current_dir.parent
        else:
            raise FileNotFoundError(
                "Could not find project root (no config/ directory found). "
                f"Searching from: {current_file}"
            )
    
    return project_root


def _load_ftp_users_toml() -> dict:
    """
    Load and parse ftp_users.toml configuration file.
    
    Returns:
        Dictionary containing FTP users configuration
    
    Raises:
        FileNotFoundError: If ftp_users.toml is not found
        ValueError: If configuration is invalid or cannot be parsed
        ImportError: If toml library is not available
    """
    if tomllib is None:
        raise ImportError(
            "No TOML library available. Please install Python 3.11+ or install tomli: "
            "pip install tomli"
        )
    
    # Find and load config file
    project_root = _find_project_root()
    config_path = project_root / 'config' / 'ftp_users.toml'
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"FTP users configuration not found: {config_path}\n"
            f"Expected location: config/ftp_users.toml in project root"
        )
    
    try:
        with open(config_path, 'rb') as f:
            config = tomllib.load(f)
    except Exception as e:
        raise ValueError(f"Failed to parse ftp_users.toml: {e}")
    
    # Validate required structure
    if 'environments' not in config:
        raise ValueError(
            "Invalid ftp_users.toml: missing 'environments' section"
        )
    
    if not config['environments']:
        raise ValueError(
            "Invalid ftp_users.toml: 'environments' section is empty"
        )
    
    return config


# Cached configuration instance and file timestamp
_cached_config: Optional[FTPUsersConfig] = None
_cached_timestamp: Optional[float] = None


def get_ftp_users_config(environment: Optional[str] = None, reload: bool = False) -> FTPUsersConfig | FTPUserEnvironment:
    """
    Get FTP users configuration.
    
    This is the main entry point for accessing FTP users configuration.
    Configuration is cached after first load for performance.
    
    Args:
        environment: If provided, returns FTPUserEnvironment for this environment.
                    If None, returns full FTPUsersConfig object.
        reload: If True, force reload configuration from file
    
    Returns:
        FTPUsersConfig object if environment is None,
        FTPUserEnvironment object if environment is specified
    
    Raises:
        ValueError: If environment is specified but not defined
        FileNotFoundError: If ftp_users.toml is not found
        ImportError: If toml library is not available
    
    Examples:
        # Get full configuration
        config = get_ftp_users_config()
        print(config.environment_names)  # ['dev', 'staging', 'prod']
        
        # Get specific environment
        dev = get_ftp_users_config('dev')
        print(dev.username)    # 'dev_user'
        print(dev.password)    # 'dev_pass'
        print(dev.permissions) # 'elradfmwMT'
        
        # Access via config object
        config = get_ftp_users_config()
        dev = config.get_environment('dev')
        print(dev.username)
    """
    global _cached_config, _cached_timestamp
    
    # Check if config file has been modified
    project_root = _find_project_root()
    config_path = project_root / 'config' / 'ftp_users.toml'
    
    if config_path.exists():
        current_timestamp = config_path.stat().st_mtime
        
        # Reload if file has changed or cache is empty
        if (_cached_config is None or 
            _cached_timestamp is None or 
            current_timestamp != _cached_timestamp or 
            reload):
            config_dict = _load_ftp_users_toml()
            _cached_config = FTPUsersConfig(config_dict)
            _cached_timestamp = current_timestamp
    else:
        # File doesn't exist, will be handled by _load_ftp_users_toml
        if _cached_config is None or reload:
            config_dict = _load_ftp_users_toml()
            _cached_config = FTPUsersConfig(config_dict)
            _cached_timestamp = None
    
    # Return environment-specific or full config
    if environment is not None:
        return _cached_config.get_environment(environment)
    else:
        return _cached_config
