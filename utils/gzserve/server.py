#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Development Web Server - Core Implementation
=============================================
A simple, no-cache, multi-threaded development web server with environment support.

Serves files from environment-specific directories (dev/staging/prod) under publish/
and provides an interactive admin console for shutting down the server gracefully.

Authors: superguru, gazorper
License: GPL v3.0
"""

import http.server
import socketserver
import sys
import os
import threading
import signal
import argparse
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.gzlogging import get_logging_context
from utils.gzconfig import get_pipeline_config

# Default port GZ = 71,90. If you know, you know.
DEFAULT_PORT = 7190

# Global variable for clean shutdown
shutdown_requested = False

# Global variable for current environment and logging context
current_environment = None
log_context = None


class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with no-cache headers for development"""

    def end_headers(self):
        # Disable all caching for development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, format, *args):
        # Log HTTP requests using gzlogging if available
        global log_context
        message = format % args
        
        if log_context:
            # Determine log level based on status code
            # Extract status code if present (usually second arg)
            status_code = args[1] if len(args) > 1 and isinstance(args[1], (int, str)) else None
            
            if status_code:
                try:
                    status_int = int(status_code) if isinstance(status_code, str) else status_code
                    if status_int >= 400:
                        log_context.err(message)
                    elif status_int >= 300:
                        log_context.wrn(message)
                    else:
                        log_context.inf(message)
                except (ValueError, TypeError):
                    log_context.inf(message)
            else:
                log_context.inf(message)
        else:
            # Fallback to print if logging not initialized
            env_prefix = f"[{current_environment}] " if current_environment else ""
            print(f"{env_prefix}[{self.log_date_time_string()}] {message}")


class ReusableTCPServer(socketserver.TCPServer):
    """TCP server with address reuse enabled for development"""
    allow_reuse_address = True


def admin_command_listener(httpd: socketserver.TCPServer) -> None:
    """
    Listen for admin commands in the terminal.

    Args:
        httpd: The HTTP server instance to control
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
                print("\nShutting down server...")
                shutdown_requested = True
                httpd.shutdown()
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
            shutdown_requested = True
            httpd.shutdown()
            break
        except KeyboardInterrupt:
            # Handle Ctrl+C in the admin thread
            print("\nReceived interrupt signal, shutting down...")
            shutdown_requested = True
            httpd.shutdown()
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
    shutdown_requested = True


def find_src_directory() -> Path:
    """
    Find the src directory relative to the project root.

    DEPRECATED: This function is kept for backward compatibility.
    New code should use get_environment_directory() instead.

    Returns:
        Path to the src directory, or current directory if not found
    """
    # Try to find src directory from multiple possible locations
    current_file = Path(__file__).resolve()

    # Case 1: Running from utils/serve/server.py
    if current_file.parent.name == 'serve' and current_file.parent.parent.name == 'utils':
        project_root = current_file.parent.parent.parent
    # Case 2: Running from utils/serve.py (legacy)
    elif current_file.parent.name == 'utils':
        project_root = current_file.parent.parent
    # Case 3: Running from project root
    else:
        project_root = Path.cwd()

    src_dir = project_root / 'src'

    if src_dir.exists() and src_dir.is_dir():
        return src_dir
    else:
        return Path.cwd()


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path to the project root
    """
    current_file = Path(__file__).resolve()

    # Case 1: Running from utils/serve/server.py
    if current_file.parent.name == 'serve' and current_file.parent.parent.name == 'utils':
        return current_file.parent.parent.parent
    # Case 2: Running from utils/serve.py (legacy)
    elif current_file.parent.name == 'utils':
        return current_file.parent.parent
    # Case 3: Running from project root
    else:
        return Path.cwd()


def start_server(port: Optional[int] = None, serve_dir: Optional[Path] = None, environment: Optional[str] = None) -> int:
    """
    Start the development web server.

    Args:
        port: Port number to listen on (overrides config if provided)
        serve_dir: Directory to serve files from (overrides environment if provided)
        environment: Environment name to serve (dev/staging/prod)

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
            log_context = get_logging_context(environment, 'server', console=True)
            log_context.inf("=" * 60)
            log_context.inf("Initializing development web server")
        except Exception as e:
            print(f"✗ Logging Error: {e}")
            print("  Continuing without logging...")
            log_context = None

    # Load environment configuration if specified
    env_config: Optional['PipelineEnvironment'] = None
    if environment is not None:
        try:
            from utils.gzconfig import PipelineEnvironment
            env_config = get_pipeline_config(environment)  # type: ignore
            if log_context:
                log_context.dbg("Configuration loaded successfully")
        except (FileNotFoundError, ValueError, ImportError) as e:
            if log_context:
                log_context.err(f"Configuration Error: {e}")
            else:
                print(f"✗ Configuration Error: {e}")
            return 1

    # Determine serve directory
    if serve_dir is None:
        if env_config is not None:
            serve_dir = env_config.directory_path
            if log_context:
                log_context.dbg(f"Serve directory: {serve_dir}")
            
            if not serve_dir.exists():
                error_msg = f"Environment directory not found: {serve_dir}\nPlease create the directory or run a build for environment '{environment}'"
                if log_context:
                    log_context.err(error_msg)
                else:
                    print(f"✗ Error: {error_msg}")
                return 1
        else:
            # Environment is required - no fallback
            error_msg = "Environment parameter is required"
            if log_context:
                log_context.err(error_msg)
                log_context.inf("Usage: python -m utils.serve -e <environment>")
                log_context.inf("Available environments: dev, staging, prod")
            else:
                print(f"✗ Error: {error_msg}")
                print("  Usage: python -m utils.serve -e <environment>")
                print("  Available environments: dev, staging, prod")
            return 1

    # Determine port
    if port is None:
        if env_config is not None:
            port = env_config.httpd_port
        else:
            port = DEFAULT_PORT
    
    # Ensure port is always an integer (type narrowing for Pylance)
    assert port is not None, "Port should never be None at this point"
    if not isinstance(port, int):
        port = int(port)
    
    # Type assertion: port is now guaranteed to be int
    final_port: int = port

    # Change to serving directory
    os.chdir(serve_dir)

    # Display server information
    print("=" * 60)
    print("DEVELOPMENT WEB SERVER")
    print("=" * 60)
    if env_config:
        print(f"Environment: {env_config.name}")
        if env_config.description:
            print(f"Description: {env_config.description}")
    print(f"Port: {final_port}")
    print(f"URL: http://localhost:{final_port}")
    print(f"Directory: {serve_dir.absolute()}")
    
    # Log server configuration
    if log_context:
        log_context.inf(f"Server configuration:")
        if env_config:
            log_context.inf(f"  Environment: {env_config.name}")
            if env_config.description:
                log_context.inf(f"  Description: {env_config.description}")
        log_context.inf(f"  Port: {final_port}")
        log_context.inf(f"  URL: http://localhost:{final_port}")
        log_context.inf(f"  Directory: {serve_dir.absolute()}")

    try:
        httpd = ReusableTCPServer(('', final_port), NoCacheHTTPRequestHandler)
        
        if log_context:
            log_context.inf("TCP server created successfully")

        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start admin command listener in a separate thread (not daemon)
        admin_thread = threading.Thread(target=admin_command_listener, args=(httpd,))
        admin_thread.start()
        
        if log_context:
            log_context.inf("Admin command listener started")

        # Start the server
        print("\nServer is running...")
        print("Press Ctrl+C to stop the server or type 'quit' in the admin prompt.\n")
        
        if log_context:
            log_context.inf("Server is now running and accepting connections")
            log_context.inf("=" * 60)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt...")
            if log_context:
                log_context.inf("Received keyboard interrupt signal")
            shutdown_requested = True
        finally:
            print("Shutting down server...")
            if log_context:
                log_context.inf("Shutting down server...")
            shutdown_requested = True
            httpd.shutdown()
            httpd.server_close()
            admin_thread.join(timeout=2)  # Give admin thread time to clean up
            if log_context:
                log_context.inf("Server shutdown complete")

        print("\n" + "=" * 60)
        print("Server stopped")
        print("=" * 60)
        
        if log_context:
            log_context.inf("=" * 60)
            log_context.inf("Server stopped normally")
            log_context.inf("=" * 60)

        return 0

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Server stopped by user (Ctrl+C)")
        print("=" * 60)
        if log_context:
            log_context.inf("Server stopped by user (Ctrl+C)")
        return 0
    except OSError as e:
        if e.errno == 10048 or e.errno == 48:  # Windows/Unix port already in use
            error_msg = f"Port {final_port} is already in use"
            if log_context:
                log_context.err(error_msg)
                log_context.inf(f"Try a different port: python -m utils.serve -e {environment} -p <port>")
            else:
                print(f"\n✗ Error: {error_msg}")
                print(f"  Try a different port: python -m utils.serve -e {environment} -p <port>")
        else:
            if log_context:
                log_context.err(f"Error starting server: {e}")
            else:
                print(f"\n✗ Error starting server: {e}")
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
        description='Development web server with environment support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m utils.serve -e dev                 # Serve dev environment on configured port
  python -m utils.serve -e staging -p 7190     # Serve staging on port 7190
  python -m utils.serve -e prod                # Serve production environment

Environments are configured in config/environments.toml
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
    
    return start_server(
        port=args.port,
        environment=args.environment
    )


if __name__ == '__main__':
    sys.exit(main())
