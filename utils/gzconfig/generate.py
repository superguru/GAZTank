#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Generate Configuration Handler
===============================
Handles reading and providing access to generate.toml configuration.

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

# Import pipeline config for environment directory access
from .pipeline import get_pipeline_config


class GenerateGroup:
    """
    Represents a single group configuration from generate.toml.
    
    Provides property-based access to group settings.
    """
    
    def __init__(self, config: dict, project_root: Path, environment: Optional[str] = None):
        """
        Initialize group configuration.
        
        Args:
            config: Configuration dictionary for this group
            project_root: Project root directory path
            environment: Target environment (dev/staging/prod) for output path resolution
        """
        self._config = config
        self._project_root = project_root
        self._environment = environment
    
    @property
    def name(self) -> str:
        """Group name for identification."""
        return self._config.get('name', 'unnamed')
    
    @property
    def enabled(self) -> bool:
        """Whether this group is enabled for processing (default: False)."""
        return self._config.get('enabled', False)
    
    @property
    def path_transform(self) -> str:
        """
        Path transformation mode for output files (default: 'flatten').
        
        Options:
            - 'flatten': Use only the filename (e.g., utils/clean/README.md -> README.html)
            - 'preserve_parent': Keep immediate parent directory (e.g., utils/clean/README.md -> clean/README.html)
            - 'preserve_all': Keep full relative path (e.g., utils/clean/README.md -> utils/clean/README.html)
            - 'strip_prefix': Remove strip_path_prefix then use remaining path (e.g., utils/clean/README.md -> clean/README.html with strip_path_prefix="utils/")
        """
        transform = self._config.get('path_transform', 'flatten')
        if transform not in ['flatten', 'preserve_parent', 'preserve_all', 'strip_prefix']:
            raise ValueError(
                f"Invalid path_transform value '{transform}'. "
                f"Must be one of: 'flatten', 'preserve_parent', 'preserve_all', 'strip_prefix'"
            )
        return transform
    
    @property
    def strip_path_prefix(self) -> str:
        """
        Path prefix to strip when path_transform is 'strip_prefix' (default: '').
        
        Example:
            - strip_path_prefix = "utils/" removes "utils/" from all paths
            - Input: utils/clean/README.md -> Output: clean/README.html
            - Input: utils/README.md -> Output: README.html
        """
        return self._config.get('strip_path_prefix', '')
    
    @property
    def input_type(self) -> str:
        """Input type (e.g., 'markdown')."""
        return self._config.get('input_type', '')
    
    @property
    def output_dir(self) -> str:
        """Directory path relative to src/content where HTML files will be saved."""
        return self._config.get('output_dir', '')
    
    @property
    def files(self) -> list[str]:
        """List of input files relative to project root."""
        return self._config.get('files', [])
    
    @property
    def output_path(self) -> Path:
        """
        Full path to the output directory.
        
        If environment is set, returns path to {env_dir}/content/{output_dir}/.
        Otherwise, returns path to src/content/{output_dir}/ (legacy behavior).
        
        Returns:
            Path to output directory
        """
        if self._environment:
            # Get environment directory from pipeline config
            try:
                from .pipeline import PipelineEnvironment
                env_config: PipelineEnvironment = get_pipeline_config(self._environment)  # type: ignore
                # env_config is PipelineEnvironment with directory_path property
                return env_config.directory_path / 'content' / self.output_dir
            except (FileNotFoundError, ValueError, ImportError):
                # Fallback to src if pipeline config unavailable
                return self._project_root / 'src' / 'content' / self.output_dir
        else:
            # Legacy: output to src/content
            return self._project_root / 'src' / 'content' / self.output_dir
    
    def __repr__(self) -> str:
        return f"GenerateGroup(name='{self.name}', input_type='{self.input_type}', files={len(self.files)})"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.input_type})"


class GenerateConfig:
    """
    Generate configuration manager.
    
    Provides access to all groups and their configurations.
    """
    
    def __init__(self, config_dict: dict, project_root: Path, environment: Optional[str] = None):
        """
        Initialize generate configuration.
        
        Args:
            config_dict: Raw configuration dictionary from generate.toml
            project_root: Project root directory path
            environment: Target environment (dev/staging/prod) for output path resolution
        """
        self._config = config_dict
        self._project_root = project_root
        self._environment = environment
        self._groups = []
        
        # Parse groups
        if 'group' in config_dict:
            for group_config in config_dict['group']:
                self._groups.append(GenerateGroup(group_config, project_root, environment))
    
    @property
    def groups(self) -> list[GenerateGroup]:
        """List of all configured groups."""
        return self._groups.copy()
    
    @property
    def group_count(self) -> int:
        """Number of configured groups."""
        return len(self._groups)
    
    def __repr__(self) -> str:
        return f"GenerateConfig(groups={len(self._groups)})"


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
    
    # Navigate up from utils/gzconfig/generate.py to project root
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


def _load_generate_toml() -> tuple[dict, Path]:
    """
    Load and parse generate.toml configuration file.
    
    Returns:
        Tuple of (configuration dictionary, project root path)
    
    Raises:
        FileNotFoundError: If generate.toml is not found
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
    config_path = project_root / 'config' / 'generate.toml'
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Generate configuration not found: {config_path}\n"
            f"Expected location: config/generate.toml in project root"
        )
    
    try:
        with open(config_path, 'rb') as f:
            config = tomllib.load(f)
    except Exception as e:
        raise ValueError(f"Failed to parse generate.toml: {e}")
    
    # Validate required structure
    if 'group' not in config:
        raise ValueError(
            "Invalid generate.toml: missing 'group' array"
        )
    
    if not config['group']:
        raise ValueError(
            "Invalid generate.toml: 'group' array is empty"
        )
    
    return config, project_root


# Cached configuration instance
_cached_config: Optional[GenerateConfig] = None


def get_generate_config(environment: Optional[str] = None, reload: bool = False) -> GenerateConfig:
    """
    Get generate configuration.
    
    This is the main entry point for accessing generate configuration.
    Configuration is cached after first load for performance.
    
    Args:
        environment: Target environment (dev/staging/prod) for output path resolution
        reload: If True, force reload configuration from file
    
    Returns:
        GenerateConfig object containing all groups
    
    Raises:
        ValueError: If configuration is invalid
        FileNotFoundError: If generate.toml is not found
        ImportError: If toml library is not available
    
    Examples:
        # Get configuration for dev environment
        config = get_generate_config('dev')
        print(f"Found {config.group_count} groups")
        
        # Iterate through groups
        for group in config.groups:
            print(f"Group: {group.name}")
            print(f"  Type: {group.input_type}")
            print(f"  Output: {group.output_path}")
            print(f"  Files: {len(group.files)}")
    """
    global _cached_config
    
    # Load or reload configuration if needed
    # Note: We always reload if environment changes since output paths depend on it
    if _cached_config is None or reload or (environment and _cached_config._environment != environment):
        config_dict, project_root = _load_generate_toml()
        _cached_config = GenerateConfig(config_dict, project_root, environment)
    
    return _cached_config
