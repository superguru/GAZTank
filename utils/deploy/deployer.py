#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""Deployment Utility - FTP deployment for website packages"""

import os
import sys
import argparse
import zipfile
import string
import random
from pathlib import Path
from datetime import datetime
from ftplib import FTP, FTP_TLS, error_perm, error_temp, error_proto
from typing import Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.gzlogging import get_logging_context, LoggingContext
from utils.gzconfig import (
    get_pipeline_config,
    get_deploy_config,
    PipelineEnvironment,
    DeployConfig
)

log: Optional[LoggingContext] = None


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent


def get_latest_package(environment: str) -> Optional[Path]:
    """
    Find the latest package file for the specified environment.
    
    Args:
        environment: Environment name (dev/staging/prod)
        
    Returns:
        Path to latest package zip file, or None if not found
    """
    packages_dir = get_project_root() / "publish" / "packages"
    
    if not packages_dir.exists():
        return None
    
    # Look for package files matching pattern: package_{env}_*.zip
    pattern = f"package_{environment}_*.zip"
    package_files = list(packages_dir.glob(pattern))
    
    if not package_files:
        return None
    
    # Sort by modification time, newest first
    package_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return package_files[0]


def generate_random_string(length: int) -> str:
    """
    Generate a random alphanumeric string.
    
    Args:
        length: Length of string to generate (1-10)
        
    Returns:
        Random alphanumeric string
    """
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def create_upload_subdir_name(deploy_config: DeployConfig) -> str:
    """
    Create upload subdirectory name based on configuration.
    
    Args:
        deploy_config: Deploy configuration
        
    Returns:
        Subdirectory name with dot prefix (e.g., ".20251023_143052_296_a3f9k")
    """
    if not deploy_config.upload_subdir_fmt:
        # Empty format means no subdirectory
        return ""
    
    # Format timestamp
    timestamp = datetime.now().strftime(deploy_config.upload_subdir_fmt)
    
    # Add random postfix
    postfix = generate_random_string(deploy_config.upload_subdir_postfix_len)
    
    return f".{timestamp}_{postfix}"


def connect_ftp(deploy_config: DeployConfig) -> FTP:
    """
    Connect to FTP server.
    
    Args:
        deploy_config: Deploy configuration
        
    Returns:
        Connected FTP object
        
    Raises:
        ConnectionError: If connection fails
    """
    global log
    assert log is not None
    
    try:
        # Create FTP or FTP_TLS connection
        if deploy_config.use_ftps:
            log.inf(f"Connecting to FTPS server {deploy_config.server}:{deploy_config.port}")
            ftp = FTP_TLS()
        else:
            log.inf(f"Connecting to FTP server {deploy_config.server}:{deploy_config.port}")
            ftp = FTP()
        
        # Connect to server (with 10 second timeout)
        ftp.connect(deploy_config.server, deploy_config.port, timeout=10)
        
        # Login
        log.inf(f"Logging in as {deploy_config.username}")
        ftp.login(deploy_config.username, deploy_config.password)
        
        # Upgrade to secure connection if using FTPS
        if deploy_config.use_ftps and isinstance(ftp, FTP_TLS):
            ftp.prot_p()  # Protect data channel
            log.inf("Upgraded to secure FTPS connection")
        
        log.inf("✅ Connected to FTP server")
        return ftp
        
    except (error_perm, error_temp, error_proto) as e:
        log.err(f"FTP error: {e}")
        raise ConnectionError(f"FTP connection failed: {e}")
    except OSError as e:
        log.err(f"Network error: {e}")
        raise ConnectionError(f"Network error: {e}")
    except Exception as e:
        log.err(f"Unexpected error: {e}")
        raise ConnectionError(f"Connection failed: {e}")


def write_deployment_history(package_path: Path, environment: str, remote_path: str) -> None:
    """
    Write deployment history to a text file.
    
    Args:
        package_path: Path to the deployed package file
        environment: Environment name (dev/staging/prod)
        remote_path: Remote directory where package was deployed
    """
    global log
    assert log is not None
    
    from datetime import datetime
    
    # Generate history filename from package name (remove .zip extension)
    package_name_base = package_path.stem  # filename without extension
    history_filename = f"{package_name_base}.deploy_history.txt"
    history_path = package_path.parent / history_filename
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create history entry
    history_entry = f'Deployed {package_path.name} to "{environment}" at {timestamp} to dir {remote_path}\n'
    
    try:
        # Append to file (creates if doesn't exist)
        with open(history_path, 'a', encoding='utf-8') as f:
            f.write(history_entry)
        
        log.inf(f"Updated deployment history: {history_filename}")
    except OSError as e:
        log.wrn(f"Could not write deployment history: {e}")
        # Don't fail deployment if history file can't be written


def upload_file(ftp: FTP, local_path: Path, remote_name: str) -> None:
    """
    Upload a file to FTP server.
    
    Args:
        ftp: Connected FTP object
        local_path: Path to local file
        remote_name: Name for file on remote server
        
    Raises:
        OSError: If upload fails
    """
    global log
    assert log is not None
    
    file_size = local_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    
    log.inf(f"Uploading {local_path.name} ({file_size_mb:.2f} MB)")
    
    try:
        with open(local_path, 'rb') as f:
            ftp.storbinary(f'STOR {remote_name}', f)
        
        log.inf(f"✅ Upload complete: {remote_name}")
        print(f"✅ Uploaded: {local_path.name} → {remote_name}")
        
    except (error_perm, error_temp) as e:
        log.err(f"FTP upload error: {e}")
        raise OSError(f"Upload failed: {e}")
    except OSError as e:
        log.err(f"File read error: {e}")
        raise OSError(f"Upload failed: {e}")


def deploy_package(environment: str, dry_run: bool = False, force: bool = False) -> int:
    """
    Deploy package to FTP server.
    
    Args:
        environment: Environment name (dev/staging/prod)
        dry_run: If True, show what would be done without doing it
        force: Not used in this function (kept for compatibility)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    global log
    assert log is not None
    
    # Load configurations
    try:
        env_config: PipelineEnvironment = get_pipeline_config(environment)  # type: ignore
        deploy_config: DeployConfig = get_deploy_config(environment)  # type: ignore
    except (FileNotFoundError, ValueError) as e:
        log.err(f"Configuration error: {e}")
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Find latest package
    log.inf(f"Looking for latest package for {environment}")
    package_path = get_latest_package(environment)
    
    if not package_path:
        log.err(f"No package found for environment '{environment}'")
        print(f"❌ No package found for environment '{environment}'")
        print(f"   Run: python -m utils.package -e {environment}")
        return 1
    
    log.inf(f"Found package: {package_path.name}")
    print(f"📦 Package: {package_path.name}")
    
    # Generate upload subdirectory name
    upload_subdir = create_upload_subdir_name(deploy_config)
    
    # Build full remote path
    if upload_subdir:
        remote_path = f"{deploy_config.target_dir.rstrip('/')}/{upload_subdir}"
        log.inf(f"Upload subdirectory: {upload_subdir}")
        print(f"📁 Upload directory: {remote_path}")
    else:
        remote_path = deploy_config.target_dir
        log.inf(f"Upload directory: {remote_path}")
        print(f"📁 Upload directory: {remote_path}")
    
    # Show deployment details
    print(f"🌐 FTP Server: {deploy_config.server}:{deploy_config.port}")
    print(f"👤 Username: {deploy_config.username}")
    print(f"🔒 Security: {'FTPS (secure)' if deploy_config.use_ftps else 'FTP (insecure)'}")
    
    if dry_run:
        print("\n✅ [DRY RUN] Would deploy:")
        print(f"   Local file: {package_path}")
        print(f"   Remote path: {remote_path.rstrip('/')}/{package_path.name}")
        log.inf("[DRY RUN] Would deploy package")
        return 0
    
    # Connect to FTP server
    print(f"\n🔌 Connecting to FTP server...")
    try:
        ftp = connect_ftp(deploy_config)
        print(f"✅ Connected successfully")
    except ConnectionError as e:
        print(f"❌ {e}")
        return 1
    
    try:
        # Change to target directory
        log.inf(f"Changing to directory: {deploy_config.target_dir}")
        try:
            ftp.cwd(deploy_config.target_dir)
        except error_perm as e:
            log.err(f"Cannot access target directory '{deploy_config.target_dir}': {e}")
            print(f"❌ Cannot access target directory '{deploy_config.target_dir}': {e}")
            return 1
        
        # Create upload subdirectory if specified
        if upload_subdir:
            log.inf(f"Creating subdirectory: {upload_subdir}")
            try:
                ftp.mkd(upload_subdir)
                log.inf(f"Created directory: {upload_subdir}")
            except error_perm as e:
                log.wrn(f"Could not create directory (may already exist): {e}")
            
            # Change to subdirectory
            try:
                ftp.cwd(upload_subdir)
                log.inf(f"Changed to directory: {upload_subdir}")
            except error_perm as e:
                log.err(f"Cannot access subdirectory '{upload_subdir}': {e}")
                print(f"❌ Cannot access subdirectory '{upload_subdir}': {e}")
                return 1
        
        # Upload package
        print(f"\n🚀 Uploading package...")
        upload_file(ftp, package_path, package_path.name)
        
        # Write deployment history
        write_deployment_history(package_path, environment, remote_path)
        
        print(f"\n✅ Deployment complete!")
        print(f"   File: {package_path.name}")
        print(f"   Location: {remote_path.rstrip('/')}/{package_path.name}")
        log.inf(f"Deployment complete: {package_path.name} → {remote_path}")
        
        return 0
        
    except OSError as e:
        print(f"❌ Deployment failed: {e}")
        return 1
        
    finally:
        # Always close FTP connection
        try:
            ftp.quit()
            log.inf("Closed FTP connection")
        except Exception:
            pass  # Connection may already be closed


def main():
    """Main entry point for deployment tool"""
    global log
    
    parser = argparse.ArgumentParser(description='Deploy website packages via FTP')
    parser.add_argument('-e', '--environment', required=True, 
                       choices=['dev', 'staging', 'prod'],
                       help='Target environment (dev/staging/prod)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deployed without deploying')
    parser.add_argument('--force', action='store_true',
                       help='Force deployment without confirmation')
    parser.add_argument('--deploy', action='store_true',
                       help='Enable deployment (required unless --force is used)')
    
    # Use parse_known_args to ignore unknown arguments from pipeline
    args, unknown = parser.parse_known_args()
    
    # Initialize logging
    log = get_logging_context(args.environment, 'deploy')
    
    log.inf(f'🚀 Deploy starting for environment: {args.environment}')
    
    # Check if deployment is allowed (unless dry-run)
    if not args.dry_run and not args.force and not args.deploy:
        print("❌ Deployment not enabled")
        print("   Use --force or --deploy to enable deployment")
        log.inf("Deployment skipped: neither --force nor --deploy specified")
        return 0
    
    # Deploy package
    exit_code = deploy_package(args.environment, args.dry_run, args.force)
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
