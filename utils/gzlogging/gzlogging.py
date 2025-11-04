#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
GZLogging - Core Logging Implementation
========================================
Environment-aware logging with automatic configuration from tools.toml.

Authors: superguru, gazorper
License: GPL v3.0
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import zipfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.gzconfig import get_tools_config, ToolsEnvironment


class LoggingContext:
    """
    Logging context for a specific environment and tool.
    
    This class provides the interface for client code to perform logging.
    It maintains the environment name and tool name, and uses internal
    state managed by the module to determine log file locations.
    """
    
    def __init__(self, environment: str, tool_name: str, log_dir: Path, logger: logging.Logger):
        """
        Initialize logging context.
        
        Args:
            environment: Environment name (dev, staging, prod, etc.)
            tool_name: Short name for the tool using this logger
            log_dir: Directory where logs will be written
            logger: Configured logger instance
        """
        self._environment = environment
        self._tool_name = tool_name
        self._log_dir = log_dir
        self._logger = logger
    
    @property
    def environment(self) -> str:
        """Get the environment name (read-only)."""
        return self._environment
    
    @property
    def tool_name(self) -> str:
        """Get the tool name (read-only)."""
        return self._tool_name
    
    def _log(self, message: str, level: str) -> None:
        """
        Internal log method - not for direct client use.
        
        Log a message with automatic timestamp and environment prefix.
        The logged message will be formatted as:
        [YYYY-MM-DD HH:MM:SS] [environment] [LEVEL] message
        
        Args:
            message: The message to log
            level: Log level (must be valid logging level)
        """
        # Get the appropriate logging method
        log_methods = {
            'DBG': self._logger.debug,
            'INF': self._logger.info,
            'WRN': self._logger.warning,
            'ERR': self._logger.error,
        }
        
        log_method = log_methods.get(level, self._logger.info)
        
        # Format: timestamp and level are added by logger, we just pass the message
        # The environment is added via the formatter
        log_method(message)
    
    def dbg(self, message: str) -> None:
        """Log a debug message (DBG level)."""
        self._log(message, 'DBG')
    
    def inf(self, message: str) -> None:
        """Log an informational message (INF level)."""
        self._log(message, 'INF')
    
    def wrn(self, message: str) -> None:
        """Log a warning message (WRN level)."""
        self._log(message, 'WRN')
    
    def err(self, message: str) -> None:
        """Log an error message (ERR level)."""
        self._log(message, 'ERR')


class _LoggingManager:
    """
    Internal singleton manager for logging configuration.
    
    This class maintains internal state about log directories for each
    environment and creates/manages logger instances.
    """
    
    def __init__(self):
        self._env_cache: dict[str, ToolsEnvironment] = {}
        self._loggers: dict[str, logging.Logger] = {}
    
    def _get_environment(self, environment: str) -> ToolsEnvironment:
        """
        Get tools environment configuration from gzconfig.
        
        Args:
            environment: Environment name
            
        Returns:
            ToolsEnvironment instance
        """
        # Check cache
        if environment in self._env_cache:
            return self._env_cache[environment]
        
        # Load from gzconfig (returns ToolsEnvironment when environment is specified)
        env: ToolsEnvironment = get_tools_config(environment)  # type: ignore
        
        # Cache and return
        self._env_cache[environment] = env
        return env
    
    def _get_rotation_settings(self, environment: str, tool_name: str) -> tuple[bool, int]:
        """
        Get rotation settings for a tool (global defaults or tool-specific overrides).
        
        Args:
            environment: Environment name
            tool_name: Tool name to check for overrides
            
        Returns:
            Tuple of (compress: bool, rotation_count: int)
        """
        env = self._get_environment(environment)
        return env.get_tool_rotation_settings(tool_name)
    
    def _rotate_old_logs(self, log_dir: Path, environment: str, tool_name: str) -> None:
        """
        Rotate old log files for a tool.
        
        This function:
        1. Finds old log files (not today's active log)
        2. Moves them to logs/00rotated (compressing if configured)
        3. Deletes oldest rotated files if count exceeds rotation_count
        
        Args:
            log_dir: Directory containing active log files
            environment: Environment name
            tool_name: Tool name (used to identify log files)
        """
        # Get rotation settings
        compress, rotation_count = self._get_rotation_settings(environment, tool_name)
        
        # Get rotated directory (parent of log_dir is logs/, then go to 00rotated)
        rotated_dir = log_dir.parent / '00rotated'
        rotated_dir.mkdir(parents=True, exist_ok=True)
        
        # Current date string (today's log is NOT rotated)
        today_str = datetime.now().strftime('%Y%m%d')
        today_log = f"{tool_name}_{today_str}.log"
        
        # Find all old log files for this tool in the active log directory
        old_logs = []
        for log_file in log_dir.glob(f"{tool_name}_*.log"):
            if log_file.name != today_log:
                old_logs.append(log_file)
        
        # Rotate old log files
        for old_log in old_logs:
            try:
                if compress:
                    # Compress to .zip
                    zip_name = old_log.stem + '.zip'
                    zip_path = rotated_dir / zip_name
                    
                    # Only compress if not already in rotated dir
                    if not zip_path.exists():
                        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                            zf.write(old_log, arcname=old_log.name)
                    
                    # Remove original log file
                    old_log.unlink()
                else:
                    # Move without compression
                    target_path = rotated_dir / old_log.name
                    if not target_path.exists():
                        shutil.move(str(old_log), str(target_path))
            except Exception:
                # Silently ignore rotation errors - don't break logging
                pass
        
        # Clean up old rotated files if count exceeds limit
        self._cleanup_rotated_logs(rotated_dir, tool_name, rotation_count)
    
    def _cleanup_rotated_logs(self, rotated_dir: Path, tool_name: str, max_count: int) -> None:
        """
        Delete oldest rotated log files if count exceeds max_count.
        
        Args:
            rotated_dir: Directory containing rotated logs
            tool_name: Tool name (used to identify log files)
            max_count: Maximum number of rotated files to keep
        """
        # Find all rotated files for this tool (both .log and .zip)
        rotated_files = []
        
        for ext in ['*.log', '*.zip']:
            for log_file in rotated_dir.glob(f"{tool_name}_*{ext}"):
                rotated_files.append(log_file)
        
        # If count doesn't exceed limit, nothing to do
        if len(rotated_files) <= max_count:
            return
        
        # Sort by modification time (oldest first)
        rotated_files.sort(key=lambda f: f.stat().st_mtime)
        
        # Delete oldest files until we're at the limit
        files_to_delete = len(rotated_files) - max_count
        for i in range(files_to_delete):
            try:
                rotated_files[i].unlink()
            except Exception:
                # Silently ignore deletion errors
                pass
    
    def _get_log_dir(self, environment: str) -> Path:
        """
        Get the log directory for a specific environment.
        
        Args:
            environment: Environment name
            
        Returns:
            Absolute path to the log directory
        """
        # Get environment configuration from gzconfig
        env = self._get_environment(environment)
        
        # Get log directory path
        log_dir = env.log_directory_path
        
        # Create directory if it doesn't exist
        log_dir.mkdir(parents=True, exist_ok=True)
        
        return log_dir
    
    def _create_logger(self, environment: str, tool_name: str, console: bool = False) -> logging.Logger:
        """
        Create and configure a logger for a specific environment and tool.
        
        Args:
            environment: Environment name
            tool_name: Tool name
            console: If True, also output to console/stdout
            
        Returns:
            Configured logger instance
        """
        # Create unique logger name
        logger_name = f"gzlogging.{environment}.{tool_name}"
        
        # Check if logger already exists
        if logger_name in self._loggers:
            return self._loggers[logger_name]
        
        # Create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)  # Capture all levels
        
        # Prevent duplicate handlers if logger already configured
        if logger.handlers:
            return logger
        
        # Get log directory
        log_dir = self._get_log_dir(environment)
        
        # Perform log rotation (hidden from users, happens automatically)
        self._rotate_old_logs(log_dir, environment, tool_name)
        
        # Create log filename with current date
        date_str = datetime.now().strftime('%Y%m%d')
        log_filename = f"{tool_name}_{date_str}.log"
        log_filepath = log_dir / log_filename
        
        # Create file handler with UTF-8 encoding
        file_handler = logging.FileHandler(
            log_filepath,
            mode='a',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Create custom formatter with environment and custom level names
        # Format: [YYYY-MM-DD HH:MM:SS] [environment] [LEVEL] message
        class EnvironmentFormatter(logging.Formatter):
            # Map Python logging levels to our custom short names
            LEVEL_MAP = {
                'DEBUG': 'DBG',
                'INFO': 'INF',
                'WARNING': 'WRN',
                'ERROR': 'ERR',
            }
            
            def __init__(self, env, fmt, datefmt):
                super().__init__(fmt, datefmt)
                self.env = env
            
            def format(self, record):
                # Add environment to the record
                record.environment = self.env
                # Replace levelname with our custom short name
                record.levelname = self.LEVEL_MAP.get(record.levelname, record.levelname)
                return super().format(record)
        
        formatter = EnvironmentFormatter(
            environment,
            '[%(asctime)s] [%(environment)s] [%(levelname)s] %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        # Add console handler if requested
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Cache logger
        self._loggers[logger_name] = logger
        
        return logger
    
    def get_context(self, environment: str, tool_name: str, console: bool = False) -> LoggingContext:
        """
        Get a logging context for a specific environment and tool.
        
        Args:
            environment: Environment name (dev, staging, prod, etc.)
            tool_name: Short name for the tool using this logger
            console: If True, also output logs to console/stdout
            
        Returns:
            LoggingContext instance
        """
        log_dir = self._get_log_dir(environment)
        logger = self._create_logger(environment, tool_name, console)
        
        return LoggingContext(environment, tool_name, log_dir, logger)


# Global singleton instance
_manager = _LoggingManager()


def get_logging_context(environment: str, tool_name: str, console: bool = False) -> LoggingContext:
    """
    Get a logging context for a specific environment and tool.
    
    This is the main entry point for client code to use gzlogging.
    
    Example:
        from gzlogging import get_logging_context
        
        ctx = get_logging_context('dev', 'setup')
        ctx.inf("Starting setup process")
        ctx.wrn("Configuration file is old")
        ctx.err("Failed to copy file")
        
        # With console output
        ctx = get_logging_context('dev', 'server', console=True)
        ctx.inf("Server started on port 8080")  # Logs to file AND console
    
    Args:
        environment: Environment name (dev, staging, prod, etc.)
                    Must match an environment defined in config/tools.toml
        tool_name: Short name for the tool (e.g., 'setup', 'deploy', 'server')
                  Used in log messages and log filenames
        console: If True, also output logs to console/stdout (default: False)
    
    Returns:
        LoggingContext instance ready for logging
        
    Raises:
        FileNotFoundError: If tools.toml is not found
        ValueError: If environment is not defined in tools.toml
        ImportError: If TOML library is not available
    """
    return _manager.get_context(environment, tool_name, console)
