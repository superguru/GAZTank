#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Pipeline Configuration Handler
===============================
Handles reading and providing access to pipeline.toml configuration.

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


class PipelineEnvironment:
    """
    Represents a single environment configuration from pipeline.toml.
    
    Provides property-based access to environment settings.
    """
    
    def __init__(self, name: str, config: dict):
        """
        Initialize environment configuration.
        
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
    def dir(self) -> str:
        """Directory name under publish/ where build artifacts are stored."""
        return self._config.get('dir', self._name)
    
    @property
    def httpd_port(self) -> int:
        """Default port for the development server."""
        return self._config.get('httpd_port', 7190)
    
    @property
    def ftpd_port(self) -> int:
        """Default port for the FTP simulation server."""
        return self._config.get('ftpd_port', 2190)
    
    @property
    def description(self) -> str:
        """Human-readable description of the environment."""
        return self._config.get('description', '')
    
    @property
    def directory_path(self) -> Path:
        """
        Full path to the environment directory.
        
        Returns:
            Path to publish/{dir}/ directory
        """
        project_root = _find_project_root()
        return project_root / 'publish' / self.dir
    
    def __repr__(self) -> str:
        return f"PipelineEnvironment(name='{self.name}', dir='{self.dir}', httpd_port={self.httpd_port}, ftpd_port={self.ftpd_port})"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.dir})"


class PipelineConfig:
    """
    Pipeline configuration manager.
    
    Provides access to all environments and their configurations.
    """
    
    def __init__(self, config_dict: dict):
        """
        Initialize pipeline configuration.
        
        Args:
            config_dict: Raw configuration dictionary from pipeline.toml
        """
        self._config = config_dict
        self._environments = {}
        
        # Parse environments
        if 'environments' in config_dict:
            for env_name, env_config in config_dict['environments'].items():
                self._environments[env_name] = PipelineEnvironment(env_name, env_config)
    
    def get_environment(self, name: str) -> PipelineEnvironment:
        """
        Get configuration for a specific environment.
        
        Args:
            name: Environment name (e.g., 'dev', 'staging', 'prod')
        
        Returns:
            PipelineEnvironment object
        
        Raises:
            ValueError: If environment is not defined
        """
        if name not in self._environments:
            available = ', '.join(self._environments.keys())
            raise ValueError(
                f"Environment '{name}' is not defined in pipeline.toml. "
                f"Available environments: {available}"
            )
        
        return self._environments[name]
    
    @property
    def environments(self) -> dict[str, PipelineEnvironment]:
        """Dictionary of all available environments."""
        return self._environments.copy()
    
    @property
    def environment_names(self) -> list[str]:
        """List of all available environment names."""
        return list(self._environments.keys())
    
    def __repr__(self) -> str:
        env_list = ', '.join(self._environments.keys())
        return f"PipelineConfig(environments=[{env_list}])"


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
    
    # Navigate up from utils/gzconfig/pipeline.py to project root
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


def _load_pipeline_toml() -> dict:
    """
    Load and parse pipeline.toml configuration file.
    
    Returns:
        Dictionary containing pipeline configuration
    
    Raises:
        FileNotFoundError: If pipeline.toml is not found
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
    config_path = project_root / 'config' / 'pipeline.toml'
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Pipeline configuration not found: {config_path}\n"
            f"Expected location: config/pipeline.toml in project root"
        )
    
    try:
        with open(config_path, 'rb') as f:
            config = tomllib.load(f)
    except Exception as e:
        raise ValueError(f"Failed to parse pipeline.toml: {e}")
    
    # Validate required structure
    if 'environments' not in config:
        raise ValueError(
            "Invalid pipeline.toml: missing 'environments' section"
        )
    
    if not config['environments']:
        raise ValueError(
            "Invalid pipeline.toml: 'environments' section is empty"
        )
    
    return config


# Cached configuration instance
_cached_config: Optional[PipelineConfig] = None


def get_pipeline_config(environment: Optional[str] = None, reload: bool = False) -> PipelineConfig | PipelineEnvironment:
    """
    Get pipeline configuration.
    
    This is the main entry point for accessing pipeline configuration.
    Configuration is cached after first load for performance.
    
    Args:
        environment: If provided, returns PipelineEnvironment for this environment.
                    If None, returns full PipelineConfig object.
        reload: If True, force reload configuration from file
    
    Returns:
        PipelineConfig object if environment is None,
        PipelineEnvironment object if environment is specified
    
    Raises:
        ValueError: If environment is specified but not defined
        FileNotFoundError: If pipeline.toml is not found
        ImportError: If toml library is not available
    
    Examples:
        # Get full configuration
        config = get_pipeline_config()
        print(config.environment_names)  # ['dev', 'staging', 'prod']
        
        # Get specific environment
        dev = get_pipeline_config('dev')
        print(dev.httpd_port)  # 7190
        print(dev.directory_path)  # Path to publish/dev/
        
        # Access via config object
        config = get_pipeline_config()
        dev = config.get_environment('dev')
        print(dev.description)
    """
    global _cached_config
    
    # Load or reload configuration if needed
    if _cached_config is None or reload:
        config_dict = _load_pipeline_toml()
        _cached_config = PipelineConfig(config_dict)
    
    # Return environment-specific or full config
    if environment is not None:
        return _cached_config.get_environment(environment)
    else:
        return _cached_config
