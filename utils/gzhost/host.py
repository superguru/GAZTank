#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
FTP Host Server - Core Implementation
======================================
A simple FTP server for simulating remote deployment hosts using pyftpdlib.

Serves files from environment-specific directories (dev/staging/prod) under publish/
with user authentication from ftp_users.toml configuration.

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
import argparse
import signal
import threading
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.gzlogging import get_logging_context
from utils.gzconfig import get_pipeline_config, get_ftp_users_config

try:
    from pyftpdlib.authorizers import DummyAuthorizer
    from pyftpdlib.handlers import FTPHandler
    from pyftpdlib.servers import FTPServer
except ImportError:
    print("✗ Error: pyftpdlib is not installed")
    print("  Install it with: pip install pyftpdlib")
    sys.exit(1)


# Default port for FTP
DEFAULT_PORT = 2190

# Global variable for clean shutdown
shutdown_requested = False

# Global variables for environment and logging
current_environment = None
log_context = None


def admin_command_listener(server: 'FTPServer') -> None:
    """
    Listen for admin commands in the terminal.

    Args:
        server: The FTP server instance to control
    """
    global shutdown_requested
    global current_environment

    print("\nAvailable commands:")
    print("  'stop' or 'quit' - Stop the server")
    print("  'help' - Show this help")
    print("=" * 60)
    print()

    # Build prompt with environment prefix
    env_prefix = f"[{current_environment}] " if current_environment else ""
    prompt = f"{env_prefix}admin> "

    while not shutdown_requested:
        try:
            command = input(prompt).strip().lower()

            if command in ['stop', 'quit', 'exit', 'q']:
                print("\nShutting down FTP server...")
                if log_context:
                    log_context.inf("Admin command: shutdown requested")
                shutdown_requested = True
                server.close_all()
                break
            elif command == 'help':
                print("\nAvailable commands:")
                print("  stop, quit, exit, q - Stop the server")
                print("  help - Show this help")
                print()
            elif command == '':
                continue
            else:
                print(f"Unknown command: '{command}'. Type 'help' for available commands.")
        except EOFError:
            # Handle Ctrl+D / EOF
            print("\nReceived EOF, shutting down...")
            if log_context:
                log_context.inf("Received EOF signal")
            shutdown_requested = True
            server.close_all()
            break
        except KeyboardInterrupt:
            # Handle Ctrl+C in the admin thread
            print("\nReceived interrupt signal, shutting down...")
            if log_context:
                log_context.inf("Received keyboard interrupt in admin thread")
            shutdown_requested = True
            server.close_all()
            break
        except Exception as e:
            print(f"Error: {e}")


def signal_handler(signum, frame) -> None:
    """
    Handle interrupt signals for clean shutdown.

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    global shutdown_requested
    print("\nReceived interrupt signal, shutting down...")
    if log_context:
        log_context.inf("Received interrupt signal, shutting down...")
    shutdown_requested = True


def start_ftp_server(port: Optional[int] = None, environment: Optional[str] = None) -> int:
    """
    Start the FTP simulation server.

    Args:
        port: Port number to listen on (overrides config if provided)
        environment: Environment name (dev/staging/prod)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    global shutdown_requested
    global current_environment
    global log_context
    
    # Set current environment for logging
    current_environment = environment
    
    # Initialize logging with console output
    if environment:
        try:
            log_context = get_logging_context(environment, 'gzhost', console=True)
            log_context.inf("=" * 60)
            log_context.inf("Initializing FTP host server")
        except Exception as e:
            print(f"✗ Logging Error: {e}")
            print("  Continuing without logging...")
            log_context = None

    # Load environment configuration
    try:
        from utils.gzconfig import PipelineEnvironment
        env_config: PipelineEnvironment = get_pipeline_config(environment)  # type: ignore
        if log_context:
            log_context.dbg("Pipeline configuration loaded successfully")
    except (FileNotFoundError, ValueError, ImportError) as e:
        if log_context:
            log_context.err(f"Configuration Error: {e}")
        else:
            print(f"✗ Configuration Error: {e}")
        return 1

    # Load FTP users configuration
    try:
        from utils.gzconfig import FTPUserEnvironment
        ftp_user: FTPUserEnvironment = get_ftp_users_config(environment)  # type: ignore
        if log_context:
            log_context.dbg("FTP users configuration loaded successfully")
    except (FileNotFoundError, ValueError, ImportError) as e:
        if log_context:
            log_context.err(f"FTP Users Configuration Error: {e}")
        else:
            print(f"✗ FTP Users Configuration Error: {e}")
        return 1

    # Verify environment directory exists
    home_dir = env_config.directory_path
    if not home_dir.exists():
        error_msg = f"Environment directory not found: {home_dir}\nPlease create the directory or run a build for environment '{environment}'"
        if log_context:
            log_context.err(error_msg)
        else:
            print(f"✗ Error: {error_msg}")
        return 1

    # Determine port
    if port is None:
        port = env_config.ftpd_port
    
    # Ensure port is always an integer
    assert port is not None, "Port should never be None at this point"
    if not isinstance(port, int):
        port = int(port)
    
    final_port: int = port

    # Display server information
    print("=" * 60)
    print("FTP HOST SERVER")
    print("=" * 60)
    print(f"Environment: {env_config.name}")
    if env_config.description:
        print(f"Description: {env_config.description}")
    print(f"Port: {final_port}")
    print(f"FTP URL: ftp://localhost:{final_port}")
    print(f"Home Directory: {home_dir.absolute()}")
    print(f"FTP User: {ftp_user.username}")
    print(f"Permissions: {ftp_user.permissions}")
    
    # Log server configuration
    if log_context:
        log_context.inf(f"Server configuration:")
        log_context.inf(f"  Environment: {env_config.name}")
        if env_config.description:
            log_context.inf(f"  Description: {env_config.description}")
        log_context.inf(f"  Port: {final_port}")
        log_context.inf(f"  FTP URL: ftp://localhost:{final_port}")
        log_context.inf(f"  Home Directory: {home_dir.absolute()}")
        log_context.inf(f"  FTP User: {ftp_user.username}")
        log_context.inf(f"  Permissions: {ftp_user.permissions}")

    try:
        # Create authorizer for managing permissions
        authorizer = DummyAuthorizer()
        
        # Add user with permissions
        authorizer.add_user(
            ftp_user.username,
            ftp_user.password,
            str(home_dir.absolute()),
            perm=ftp_user.permissions
        )
        
        if log_context:
            log_context.dbg(f"Added FTP user: {ftp_user.username}")

        # Create FTP handler with authorizer
        handler = FTPHandler
        handler.authorizer = authorizer
        
        # Optional: Set banner
        handler.banner = f"GAZTank FTP Host [{environment}] ready."
        
        if log_context:
            log_context.dbg("FTP handler configured successfully")

        # Create FTP server
        address = ('', final_port)
        server = FTPServer(address, handler)
        
        # Set limits
        server.max_cons = 256
        server.max_cons_per_ip = 5
        
        if log_context:
            log_context.inf("FTP server created successfully")

        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start admin command listener in a separate thread (not daemon)
        admin_thread = threading.Thread(target=admin_command_listener, args=(server,))
        admin_thread.start()
        
        if log_context:
            log_context.inf("Admin command listener started")

        # Start the server
        print("\nServer is running...")
        print("Press Ctrl+C to stop the server or type 'quit' in the admin prompt.\n")
        
        if log_context:
            log_context.inf("FTP server is now running and accepting connections")
            log_context.inf("=" * 60)

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt...")
            if log_context:
                log_context.inf("Received keyboard interrupt signal")
            shutdown_requested = True
        finally:
            print("Shutting down FTP server...")
            if log_context:
                log_context.inf("Shutting down FTP server...")
            shutdown_requested = True
            server.close_all()
            admin_thread.join(timeout=2)  # Give admin thread time to clean up
            if log_context:
                log_context.inf("FTP server shutdown complete")

        print("\n" + "=" * 60)
        print("FTP server stopped")
        print("=" * 60)
        
        if log_context:
            log_context.inf("=" * 60)
            log_context.inf("FTP server stopped normally")
            log_context.inf("=" * 60)

        return 0

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("FTP server stopped by user (Ctrl+C)")
        print("=" * 60)
        if log_context:
            log_context.inf("FTP server stopped by user (Ctrl+C)")
        return 0
    except OSError as e:
        if e.errno == 10048 or e.errno == 48:  # Windows/Unix port already in use
            error_msg = f"Port {final_port} is already in use"
            if log_context:
                log_context.err(error_msg)
                log_context.inf(f"Try a different port: python -m utils.gzhost -e {environment} -p <port>")
            else:
                print(f"\n✗ Error: {error_msg}")
                print(f"  Try a different port: python -m utils.gzhost -e {environment} -p <port>")
        else:
            if log_context:
                log_context.err(f"Error starting FTP server: {e}")
            else:
                print(f"\n✗ Error starting FTP server: {e}")
        return 1
    except Exception as e:
        if log_context:
            log_context.err(f"Unexpected error: {e}")
        else:
            print(f"\n✗ Unexpected error: {e}")
        return 1


def main() -> int:
    """
    Main entry point when run as a script or module.

    Command-line arguments:
        -e, --environment: Environment to serve (dev/staging/prod) [REQUIRED]
        -p, --port: Port number (overrides config)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description='FTP host server for simulating remote deployment targets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m utils.gzhost -e dev                 # Serve dev environment on configured port
  python -m utils.gzhost -e staging -p 2190     # Serve staging on port 2190
  python -m utils.gzhost -e prod                # Serve production environment

Environments are configured in config/pipeline.toml
FTP users are configured in config/ftp_users.toml
        """
    )
    
    parser.add_argument(
        '-e', '--environment',
        required=True,
        choices=['dev', 'staging', 'prod'],
        help='Environment to serve (dev/staging/prod)'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        help='Port number (overrides config)'
    )
    
    # Use parse_known_args to ignore unknown arguments from pipeline
    args, unknown = parser.parse_known_args()
    
    return start_ftp_server(
        port=args.port,
        environment=args.environment
    )


if __name__ == '__main__':
    sys.exit(main())
