#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tools Configuration Handler
============================
Handles reading and providing access to tools.toml configuration.

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


class ToolsEnvironment:
    """
    Represents a single environment configuration from tools.toml.
    
    Provides property-based access to environment settings and tool-specific overrides.
    """
    
    def __init__(self, name: str, config: dict, global_config: dict):
        """
        Initialize environment configuration.
        
        Args:
            name: Environment name (e.g., 'dev', 'staging', 'prod')
            config: Configuration dictionary for this environment
            global_config: Full tools.toml configuration (for tool-specific overrides)
        """
        self._name = name
        self._config = config
        self._global_config = global_config
    
    @property
    def name(self) -> str:
        """Environment name (e.g., 'dev', 'staging', 'prod')."""
        return self._name
    
    @property
    def log_dir(self) -> str:
        """Directory path relative to logs/ where tool logs are stored."""
        return self._config.get('log_dir', self._name)
    
    @property
    def description(self) -> str:
        """Human-readable description of the environment."""
        return self._config.get('description', '')
    
    @property
    def log_directory_path(self) -> Path:
        """
        Full path to the log directory for this environment.
        
        Returns:
            Path to logs/{log_dir}/ directory
        """
        project_root = _find_project_root()
        return project_root / 'logs' / self.log_dir
    
    def get_tool_rotation_settings(self, tool_name: str) -> tuple[bool, int]:
        """
        Get rotation settings for a specific tool (with overrides).
        
        Checks for tool-specific overrides in [tools.toolname] section,
        otherwise returns global defaults from gzlogrotate.toml or built-in defaults.
        
        Args:
            tool_name: Tool name to check for overrides
            
        Returns:
            Tuple of (compress: bool, rotation_count: int)
        """
        # Start with global defaults from gzlogrotate.toml
        compress = True
        rotation_count = 30
        
        # Try to load gzlogrotate.toml for global defaults
        try:
            project_root = _find_project_root()
            rotation_config_path = project_root / 'config' / 'gzlogrotate.toml'
            
            if rotation_config_path.exists() and tomllib is not None:
                with open(rotation_config_path, 'rb') as f:
                    rotation_config = tomllib.load(f)
                
                if 'rotation' in rotation_config:
                    compress = rotation_config['rotation'].get('compress', True)
                    rotation_count = rotation_config['rotation'].get('rotation_count', 30)
        except Exception:
            # If we can't load gzlogrotate.toml, just use built-in defaults
            pass
        
        # Check for tool-specific overrides in tools.toml
        if 'tools' in self._global_config and tool_name in self._global_config['tools']:
            tool_config = self._global_config['tools'][tool_name]
            compress = tool_config.get('compress', compress)
            rotation_count = tool_config.get('rotation_count', rotation_count)
        
        return compress, rotation_count
    
    def __repr__(self) -> str:
        return f"ToolsEnvironment(name='{self.name}', log_dir='{self.log_dir}')"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.log_dir})"


class ToolsConfig:
    """
    Tools configuration manager.
    
    Provides access to all environments and their configurations.
    """
    
    def __init__(self, config_dict: dict):
        """
        Initialize tools configuration.
        
        Args:
            config_dict: Raw configuration dictionary from tools.toml
        """
        self._config = config_dict
        self._environments = {}
        
        # Parse environments
        if 'environments' in config_dict:
            for env_name, env_config in config_dict['environments'].items():
                self._environments[env_name] = ToolsEnvironment(env_name, env_config, config_dict)
    
    def get_environment(self, name: str) -> ToolsEnvironment:
        """
        Get configuration for a specific environment.
        
        Args:
            name: Environment name (e.g., 'dev', 'staging', 'prod')
        
        Returns:
            ToolsEnvironment object
        
        Raises:
            ValueError: If environment is not defined
        """
        if name not in self._environments:
            available = ', '.join(self._environments.keys())
            raise ValueError(
                f"Environment '{name}' is not defined in tools.toml. "
                f"Available environments: {available}"
            )
        
        return self._environments[name]
    
    @property
    def environments(self) -> dict[str, ToolsEnvironment]:
        """Dictionary of all available environments."""
        return self._environments.copy()
    
    @property
    def environment_names(self) -> list[str]:
        """List of all available environment names."""
        return list(self._environments.keys())
    
    def __repr__(self) -> str:
        env_list = ', '.join(self._environments.keys())
        return f"ToolsConfig(environments=[{env_list}])"


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
    
    # Navigate up from utils/gzconfig/tools.py to project root
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


def _load_tools_toml() -> dict:
    """
    Load and parse tools.toml configuration file.
    
    Returns:
        Dictionary containing tools configuration
    
    Raises:
        FileNotFoundError: If tools.toml is not found
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
    config_path = project_root / 'config' / 'tools.toml'
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Tools configuration not found: {config_path}\n"
            f"Expected location: config/tools.toml in project root"
        )
    
    try:
        with open(config_path, 'rb') as f:
            config = tomllib.load(f)
    except Exception as e:
        raise ValueError(f"Failed to parse tools.toml: {e}")
    
    # Validate required structure
    if 'environments' not in config:
        raise ValueError(
            "Invalid tools.toml: missing 'environments' section"
        )
    
    if not config['environments']:
        raise ValueError(
            "Invalid tools.toml: 'environments' section is empty"
        )
    
    return config


# Cached configuration instance
_cached_config: Optional[ToolsConfig] = None


def get_tools_config(environment: Optional[str] = None, reload: bool = False) -> ToolsConfig | ToolsEnvironment:
    """
    Get tools configuration.
    
    This is the main entry point for accessing tools configuration.
    Configuration is cached after first load for performance.
    
    Args:
        environment: If provided, returns ToolsEnvironment for this environment.
                    If None, returns full ToolsConfig object.
        reload: If True, force reload configuration from file
    
    Returns:
        ToolsConfig object if environment is None,
        ToolsEnvironment object if environment is specified
    
    Raises:
        ValueError: If environment is specified but not defined
        FileNotFoundError: If tools.toml is not found
        ImportError: If toml library is not available
    
    Examples:
        # Get full configuration
        config = get_tools_config()
        print(config.environment_names)  # ['dev', 'staging', 'prod']
        
        # Get specific environment
        dev = get_tools_config('dev')
        print(dev.log_dir)  # 'dev'
        print(dev.log_directory_path)  # Path to logs/dev/
        
        # Get tool-specific rotation settings
        compress, count = dev.get_tool_rotation_settings('server')
        print(f"Compress: {compress}, Count: {count}")
    """
    global _cached_config
    
    # Load or reload configuration if needed
    if _cached_config is None or reload:
        config_dict = _load_tools_toml()
        _cached_config = ToolsConfig(config_dict)
    
    # Return environment-specific or full config
    if environment is not None:
        return _cached_config.get_environment(environment)
    else:
        return _cached_config
