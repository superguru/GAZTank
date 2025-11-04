#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
File Tracker
============
Track modified files during setup and copy them to environment directories.

Authors: superguru, gazorper
License: GPL v3.0
"""

import shutil
from pathlib import Path
from typing import Set, List, Optional, Callable
from datetime import datetime

from . import ui_helpers

print_info = ui_helpers.print_info
print_success = ui_helpers.print_success
print_warning = ui_helpers.print_warning
print_error = ui_helpers.print_error


class ModifiedFileTracker:
    """Track files modified during setup process"""
    
    def __init__(self):
        """Initialize the tracker with an empty set of modified files"""
        self._modified_files: Set[Path] = set()
    
    def track(self, file_path: str | Path) -> None:
        """Add a file to the tracked modified files
        
        Args:
            file_path: Path to the file that was modified (relative or absolute)
        """
        path = Path(file_path)
        # Store as relative path from project root for consistency
        if path.is_absolute():
            try:
                path = path.relative_to(Path.cwd())
            except ValueError:
                # If path is not relative to cwd, store as-is
                pass
        self._modified_files.add(path)
    
    def get_modified_files(self) -> List[Path]:
        """Get list of all tracked modified files
        
        Returns:
            Sorted list of modified file paths
        """
        return sorted(self._modified_files)
    
    def clear(self) -> None:
        """Clear all tracked files"""
        self._modified_files.clear()
    
    def __len__(self) -> int:
        """Get count of tracked files"""
        return len(self._modified_files)


# Global tracker instance
_tracker = ModifiedFileTracker()


def track_modified_file(file_path: str | Path) -> None:
    """Track a file as modified
    
    Args:
        file_path: Path to the file that was modified
    """
    _tracker.track(file_path)


def get_modified_files() -> List[Path]:
    """Get list of all modified files
    
    Returns:
        List of modified file paths
    """
    return _tracker.get_modified_files()


def clear_tracked_files() -> None:
    """Clear all tracked files"""
    _tracker.clear()


def copy_files_with_tracking(
    files: List[Path],
    target_dir: Path,
    force: bool = False,
    path_transformer: Optional[Callable[[Path], Path]] = None,
    description: str = "file"
) -> tuple[List[tuple[Path, Path, datetime]], List[tuple[Path, Path, datetime]], List[str]]:
    """Helper function to copy files with timestamp checking and error tracking
    
    Args:
        files: List of source file paths to copy
        target_dir: Base target directory
        force: If True, copy all files regardless of timestamp
        path_transformer: Optional function to transform source path to relative target path
        description: Description for log messages (e.g., "file", "image")
    
    Returns:
        Tuple of (copied_files, skipped_files, errors)
    """
    copied_files: List[tuple[Path, Path, datetime]] = []
    skipped_files: List[tuple[Path, Path, datetime]] = []
    errors: List[str] = []
    
    for src_file in files:
        # Determine target path
        if path_transformer:
            try:
                relative_path = path_transformer(src_file)
                target_path = target_dir / relative_path
            except Exception as e:
                error_msg = f"Failed to determine target path for {src_file}: {e}"
                print_error(error_msg)
                errors.append(error_msg)
                continue
        else:
            target_path = target_dir / src_file.name
        
        # Check if source exists
        if not src_file.exists():
            error_msg = f"{description.capitalize()} not found: {src_file}"
            print_warning(error_msg)
            errors.append(error_msg)
            continue
        
        # Get file modification time
        try:
            file_mtime = datetime.fromtimestamp(src_file.stat().st_mtime)
        except Exception as e:
            error_msg = f"Failed to get modification time for {src_file}: {e}"
            print_error(error_msg)
            errors.append(error_msg)
            continue
        
        # Check if we should copy (timestamp comparison unless force=True)
        should_copy = force
        if not force and target_path.exists():
            src_mtime = src_file.stat().st_mtime
            target_mtime = target_path.stat().st_mtime
            should_copy = src_mtime > target_mtime
        elif not force:
            # Target doesn't exist, so we need to copy
            should_copy = True
        
        if not should_copy:
            skipped_files.append((src_file, target_path, file_mtime))
            continue
        
        # Create target directory if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        try:
            shutil.copy2(src_file, target_path)
            copied_files.append((src_file, target_path, file_mtime))
            print_success(f"  ✓ Copied {description}: {src_file.name}")
        except Exception as e:
            error_msg = f"Failed to copy {description} {src_file}: {e}"
            print_error(f"  ✗ {error_msg}")
            errors.append(error_msg)
    
    return (copied_files, skipped_files, errors)


def generate_manifest_file(
    environment: str, 
    generated_copied: List[tuple[Path, Path, datetime]], 
    generated_skipped: List[tuple[Path, Path, datetime]],
    static_copied: List[tuple[Path, Path, datetime]], 
    static_skipped: List[tuple[Path, Path, datetime]],
    image_copied: List[tuple[Path, Path, datetime]], 
    image_skipped: List[tuple[Path, Path, datetime]],
    errors: Optional[List[str]] = None
) -> Optional[Path]:
    """Generate a manifest markdown file listing all copied and skipped files by category
    
    Creates a temporary manifest file that will only be included in the backup zip.
    The file is not kept in the backups directory.
    
    Files are categorized into three groups:
    - Generated/Modified Files: Files created or modified by setup (CSS variables, updated HTML, etc.)
    - Static Files: Files copied as-is without modification (robots.txt, humans.txt, etc.)
    - Image Files: Logo and favicon files
    
    Args:
        environment: Environment name (dev, staging, prod, etc.)
        generated_copied: Generated/modified files that were copied
        generated_skipped: Generated/modified files that were skipped (up-to-date)
        static_copied: Static files that were copied
        static_skipped: Static files that were skipped (up-to-date)
        image_copied: Image files that were copied
        image_skipped: Image files that were skipped (up-to-date)
        errors: Optional list of error messages to include in the manifest
    
    Returns:
        Path to the generated manifest file, or None if generation failed
    """
    # Check if we have any files to report
    if not any([generated_copied, generated_skipped, static_copied, static_skipped, image_copied, image_skipped]):
        return None
        return None
    
    try:
        # Find project root
        current_file = Path(__file__).resolve()
        if current_file.parent.name == 'setup' and current_file.parent.parent.name == 'utils':
            project_root = current_file.parent.parent.parent
        else:
            project_root = Path.cwd()
        
        # Create manifest in a temporary location (will be added to zip then deleted)
        import tempfile
        import os
        temp_dir = Path(tempfile.gettempdir())
        
        # Generate timestamp
        timestamp = datetime.now()
        manifest_filename = f"setup_manifest.md"
        manifest_path = temp_dir / manifest_filename
        
        # Normalize all paths to absolute before processing
        def normalize_to_absolute(file_list: List[tuple[Path, Path, datetime]]) -> List[tuple[Path, Path, datetime]]:
            """Convert all paths to absolute paths for consistent processing"""
            normalized = []
            for src, dest, time in file_list:
                src_abs = src.resolve() if not src.is_absolute() else src
                dest_abs = dest.resolve() if not dest.is_absolute() else dest
                normalized.append((src_abs, dest_abs, time))
            return normalized
        
        # Find common root paths from absolute paths
        def find_common_root(file_list: List[tuple[Path, Path, datetime]]) -> tuple[Path, Path]:
            """Find common root for source and destination paths using absolute paths"""
            if not file_list:
                return Path('.'), Path('.')
            
            src_paths = [src for src, _, _ in file_list]
            dest_paths = [dest for _, dest, _ in file_list]
            
            # Find common source root
            if src_paths:
                src_parts_list = [list(p.parts) for p in src_paths]
                src_common = []
                if src_parts_list:
                    for parts in zip(*src_parts_list):
                        if len(set(parts)) == 1:
                            src_common.append(parts[0])
                        else:
                            break
                src_root = Path(*src_common) if src_common else Path('.')
            else:
                src_root = Path('.')
            
            # Find common destination root
            if dest_paths:
                dest_parts_list = [list(p.parts) for p in dest_paths]
                dest_common = []
                if dest_parts_list:
                    for parts in zip(*dest_parts_list):
                        if len(set(parts)) == 1:
                            dest_common.append(parts[0])
                        else:
                            break
                dest_root = Path(*dest_common) if dest_common else Path('.')
            else:
                dest_root = Path('.')
            
            return src_root, dest_root
        
        # Smart path sorting: files in parent directory come before subdirectories
        def sort_key(file_tuple, src_root):
            """Generate sort key for smart path sorting based on relative paths
            
            Ensures files in a directory come before subdirectories:
            - Root files come before root/css/ subdirectory
            - css/file.css comes before css/subdir/ subdirectory
            
            The key is the path depth (number of parts), then alphabetical within same depth.
            """
            src_path = file_tuple[0]
            # Calculate relative path from root for sorting
            try:
                src_rel = src_path.relative_to(src_root)
            except ValueError:
                src_rel = src_path
            
            path_parts = list(src_rel.parts)
            
            # Sort by: (depth, alphabetical_path)
            # Files at same depth will sort alphabetically
            return (len(path_parts), path_parts)
        
        # Helper function to generate a file table section
        def generate_file_table(title: str, copied: List[tuple[Path, Path, datetime]], skipped: List[tuple[Path, Path, datetime]]) -> List[str]:
            """Generate markdown table for a category of files"""
            table_lines = []
            
            if not copied and not skipped:
                return table_lines
            
            table_lines.append(f"## {title}")
            table_lines.append("")
            
            # Process copied files
            if copied:
                # Normalize all paths to absolute first
                copied_abs = normalize_to_absolute(copied)
                
                # Find common roots from absolute paths
                src_root, dest_root = find_common_root(copied_abs)
                
                table_lines.extend([
                    f"### Copied",
                    f"",
                    f"**Total:** {len(copied_abs)} file(s)",
                    f"**Source Root:** `{src_root}`",
                    f"**Destination Root:** `{dest_root}`",
                    f"",
                    f"| Source Path | Filename | Destination Path | Size | Modified |",
                    f"|-------------|----------|------------------|-----:|----------|",
                ])
                
                # Sort by source path with smart sorting (using lambda to pass src_root)
                sorted_copied = sorted(copied_abs, key=lambda f: sort_key(f, src_root))
                
                for src_path, target_path, file_time in sorted_copied:
                    # Get relative paths
                    try:
                        src_rel = src_path.relative_to(src_root)
                    except ValueError:
                        src_rel = src_path
                    
                    try:
                        dest_rel = target_path.relative_to(dest_root)
                    except ValueError:
                        dest_rel = target_path
                    
                    # Add path separator in front of relative paths
                    import os
                    sep = os.sep
                    src_rel_display = sep + str(src_rel)
                    dest_rel_display = sep + str(dest_rel)
                    
                    # Get file size
                    try:
                        size_bytes = src_path.stat().st_size
                        if size_bytes < 1024:
                            size_str = f"{size_bytes} B"
                        elif size_bytes < 1024 * 1024:
                            size_str = f"{size_bytes / 1024:.1f} KB"
                        else:
                            size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
                    except:
                        size_str = "N/A"
                    
                    filename = src_path.name
                    time_str = file_time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    table_lines.append(f"| `{src_rel_display}` | `{filename}` | `{dest_rel_display}` | {size_str} | {time_str} |")
                
                table_lines.append("")
            
            # Process skipped files
            if skipped:
                # Normalize all paths to absolute first
                skipped_abs = normalize_to_absolute(skipped)
                
                # Find common roots from absolute paths
                src_root_skip, dest_root_skip = find_common_root(skipped_abs)
                
                table_lines.extend([
                    f"### Skipped (Up-to-date)",
                    f"",
                    f"**Total:** {len(skipped_abs)} file(s)",
                    f"**Source Root:** `{src_root_skip}`",
                    f"**Destination Root:** `{dest_root_skip}`",
                    f"",
                    f"| Source Path | Filename | Destination Path | Size | Modified |",
                    f"|-------------|----------|------------------|-----:|----------|",
                ])
                
                # Sort by source path with smart sorting (using lambda to pass src_root)
                sorted_skipped = sorted(skipped_abs, key=lambda f: sort_key(f, src_root_skip))
                
                for src_path, target_path, file_time in sorted_skipped:
                    # Get relative paths
                    try:
                        src_rel = src_path.relative_to(src_root_skip)
                    except ValueError:
                        src_rel = src_path
                    
                    try:
                        dest_rel = target_path.relative_to(dest_root_skip)
                    except ValueError:
                        dest_rel = target_path
                    
                    # Add path separator in front of relative paths
                    import os
                    sep = os.sep
                    src_rel_display = sep + str(src_rel)
                    dest_rel_display = sep + str(dest_rel)
                    
                    # Get file size
                    try:
                        size_bytes = src_path.stat().st_size
                        if size_bytes < 1024:
                            size_str = f"{size_bytes} B"
                        elif size_bytes < 1024 * 1024:
                            size_str = f"{size_bytes / 1024:.1f} KB"
                        else:
                            size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
                    except:
                        size_str = "N/A"
                    
                    filename = src_path.name
                    time_str = file_time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    table_lines.append(f"| `{src_rel_display}` | `{filename}` | `{dest_rel_display}` | {size_str} | {time_str} |")
                
                table_lines.append("")
            
            return table_lines
        
        # Generate manifest content
        lines = [
            f"# Setup Manifest - {environment}",
            f"",
            f"**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Environment:** {environment}",
            f"",
        ]
        
        # Add errors section if there are any errors
        if errors and len(errors) > 0:
            lines.extend([
                f"## ⚠️ Errors and Warnings",
                f"",
                f"**Total:** {len(errors)} issue(s)",
                f"",
            ])
            for error in errors:
                lines.append(f"- {error}")
            lines.append("")
        
        # Add each category of files
        lines.extend(generate_file_table("Generated/Modified Files", generated_copied, generated_skipped))
        lines.extend(generate_file_table("Static Files", static_copied, static_skipped))
        lines.extend(generate_file_table("Image Files", image_copied, image_skipped))
        
        lines.extend([
            "---",
            "*Generated by setup.py*",
            ""
        ])
        
        # Write manifest file
        manifest_path.write_text('\n'.join(lines), encoding='utf-8')
        return manifest_path
        
    except Exception as e:
        print_error(f"Failed to generate manifest: {e}")
        return None


def copy_modified_files_to_environment(
    environment: str, 
    force: bool = False, 
    additional_copied: Optional[List[tuple[Path, Path, datetime]]] = None, 
    additional_skipped: Optional[List[tuple[Path, Path, datetime]]] = None,
    additional_errors: Optional[List[str]] = None
) -> Optional[Path]:
    """Copy all tracked modified files to the environment directory
    
    Reads environment directory from config/environments.toml and copies files
    from src/ directory to the configured environment directory.
    Preserves directory structure. Generates a manifest file listing all copies.
    
    Args:
        environment: Environment name (dev, staging, prod, etc.)
        force: If True, copy all files regardless of timestamp. If False, only copy if source is newer.
        additional_copied: Additional files to include in manifest (e.g., image files)
        additional_skipped: Additional skipped files to include in manifest
        additional_errors: Additional errors to include in manifest (e.g., from image copying)
    
    Returns:
        Path to generated manifest file, or None if no files were copied
    """
    modified_files = get_modified_files()
    
    if not modified_files:
        print_warning("No files were modified during setup")
        return None
    
    # Filter to only src/ files, excluding src/components/ (composition source files)
    src_files = [f for f in modified_files 
                 if (str(f).startswith('src' + str(Path('/')) ) or str(f).startswith('src\\'))
                 and not (str(f).startswith('src' + str(Path('/')) + 'components' + str(Path('/'))) 
                          or str(f).startswith('src\\components\\'))]
    
    # Debug: show what was filtered
    components_files = [f for f in modified_files if 'components' in str(f)]
    if components_files:
        print_info(f"Filtered out {len(components_files)} components file(s)")
    
    if not src_files:
        print_warning(f"No src/ files found among {len(modified_files)} modified files")
        return None
    
    # Get environment directory from pipeline config
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from utils.gzconfig import get_pipeline_config, PipelineEnvironment
        env: PipelineEnvironment = get_pipeline_config(environment)  # type: ignore
        env_dir = env.directory_path
    except (FileNotFoundError, ValueError) as e:
        print_error(f"Configuration error: {e}")
        return None
    
    if not env_dir.exists():
        print_error(f"Environment directory not found: {env_dir}")
        print_info(f"Please create the directory or run a build for environment '{environment}'")
        return None
    
    copy_mode = "all files (--force)" if force else "newer files only"
    print_info(f"Copying {len(src_files)} modified file(s) to {env_dir} ({copy_mode})...")
    
    # Define path transformer for src/ files (removes 'src/' prefix)
    def src_path_transformer(src_path: Path) -> Path:
        return Path(*src_path.parts[1:])  # Remove 'src/' prefix
    
    # Use helper function to copy files
    copied_files, skipped_files, errors = copy_files_with_tracking(
        src_files,
        env_dir,
        force=force,
        path_transformer=src_path_transformer,
        description="file"
    )
    
    # Report results
    copied_count = len(copied_files)
    skipped_count = len(skipped_files)
    
    if skipped_count > 0:
        print_info(f"Skipped {skipped_count} up-to-date file(s)")
    
    if copied_count == len(src_files):
        print_success(f"All {copied_count} file(s) copied successfully to {environment} environment")
    elif copied_count > 0:
        print_warning(f"Copied {copied_count}/{len(src_files)} file(s) to {environment} environment")
    else:
        print_info("No files needed to be copied (all up-to-date)")
    
    # Categorize files into generated/modified vs static
    # Generated/modified files are those in the tracker (they were updated by setup)
    # Static files are those not in the tracker (just copied as-is)
    tracked_files_set = set(modified_files)
    
    generated_copied = [f for f in copied_files if f[0] in tracked_files_set]
    static_copied = [f for f in copied_files if f[0] not in tracked_files_set]
    
    generated_skipped = [f for f in skipped_files if f[0] in tracked_files_set]
    static_skipped = [f for f in skipped_files if f[0] not in tracked_files_set]
    
    # Image files are passed separately
    image_copied = additional_copied if additional_copied else []
    image_skipped = additional_skipped if additional_skipped else []
    
    # Combine all errors
    all_errors = errors.copy()
    if additional_errors:
        all_errors.extend(additional_errors)
    
    # Generate manifest file with categorized files and errors
    manifest_path = generate_manifest_file(
        environment, 
        generated_copied, generated_skipped,
        static_copied, static_skipped,
        image_copied, image_skipped,
        all_errors if all_errors else None
    )
    if manifest_path:
        print_success(f"Generated manifest file")
    
    return manifest_path


def copy_image_files_to_environment(environment: str, config_data: dict, force: bool = False) -> tuple[List[tuple[Path, Path, datetime]], List[tuple[Path, Path, datetime]], List[str]]:
    """Copy favicon and logo image files to environment directory
    
    Copies favicon_32, favicon_16, logo_512, logo_256, logo_128, logo_75, logo_50
    from src/images/ to the environment's images/ directory.
    Only copies if source is newer than destination (unless force=True).
    
    Args:
        environment: Environment name (dev, staging, prod, etc.)
        config_data: Configuration dictionary with image filenames
        force: If True, copy all files regardless of timestamp
    
    Returns:
        Tuple of (copied_files, skipped_files, errors) for manifest tracking
    """
    try:
        # Find project root
        current_file = Path(__file__).resolve()
        if current_file.parent.name == 'setup' and current_file.parent.parent.name == 'utils':
            project_root = current_file.parent.parent.parent
        else:
            project_root = Path.cwd()
        
        src_images_dir = project_root / 'src' / 'images'
        
        # Get environment directory from pipeline config
        try:
            import sys
            sys.path.insert(0, str(current_file.parent.parent.parent))
            from utils.gzconfig import get_pipeline_config, PipelineEnvironment
            env: PipelineEnvironment = get_pipeline_config(environment)  # type: ignore
            env_dir = env.directory_path
        except (FileNotFoundError, ValueError) as e:
            print_error(f"Configuration error: {e}")
            return ([], [], [f"Configuration error: {e}"])
        
        if not env_dir.exists():
            print_error(f"Environment directory not found: {env_dir}")
            return ([], [], [f"Environment directory not found: {env_dir}"])
        
        env_images_dir = env_dir / 'images'
        env_images_dir.mkdir(parents=True, exist_ok=True)
        
        # List of image config keys to copy
        image_keys = ['favicon_32', 'favicon_16', 'logo_512', 'logo_256', 'logo_128', 'logo_75', 'logo_50']
        
        # Build list of image files to copy
        image_files = []
        for key in image_keys:
            filename = config_data.get(key)
            if filename:
                image_files.append(src_images_dir / filename)
        
        # Use helper function to copy image files
        copied_files, skipped_files, errors = copy_files_with_tracking(
            image_files,
            env_images_dir,
            force=force,
            path_transformer=None,  # Images go directly into images/ dir
            description="image"
        )
        
        # Report results
        copied_count = len(copied_files)
        skipped_count = len(skipped_files)
        
        if copied_count > 0:
            print_success(f"Copied {copied_count} image file(s) to {environment} environment")
        if skipped_count > 0:
            print_info(f"Skipped {skipped_count} up-to-date image file(s)")
        
        return (copied_files, skipped_files, errors)
        
    except Exception as e:
        print_error(f"Error copying image files: {e}")
        return ([], [], [f"Error copying image files: {e}"])


def clean_environment(environment: str, force: bool = False) -> bool:
    """Delete all files in the environment directory
    
    Args:
        environment: Environment name (dev, staging, prod, etc.)
        force: If True, skip confirmation prompt
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get environment directory from pipeline config
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from utils.gzconfig import get_pipeline_config, PipelineEnvironment
            env: PipelineEnvironment = get_pipeline_config(environment)  # type: ignore
            env_dir = env.directory_path
        except (FileNotFoundError, ValueError) as e:
            print_error(f"Configuration error: {e}")
            return False
        
        if not env_dir.exists():
            print_warning(f"Environment directory does not exist: {env_dir}")
            return True  # Nothing to clean
        
        # Count files and directories
        file_count = 0
        dir_count = 0
        for item in env_dir.rglob('*'):
            if item.is_file():
                file_count += 1
            elif item.is_dir():
                dir_count += 1
        
        if file_count == 0 and dir_count == 0:
            print_info(f"Environment directory is already empty: {env_dir}")
            return True
        
        # Prompt for confirmation unless force is specified
        if not force:
            print(f"\n{ui_helpers.Colors.YELLOW}WARNING: This will delete all files in the {environment} environment!{ui_helpers.Colors.ENDC}")
            print_info(f"Directory: {env_dir}")
            print_info(f"Files: {file_count}")
            print_info(f"Directories: {dir_count}")
            print()
            
            response = input(f"Type 'yes' to confirm deletion: ").strip().lower()
            if response != 'yes':
                print_info("Clean operation cancelled")
                return False
        
        # Delete all contents
        print_info(f"Cleaning {environment} environment...")
        deleted_files = 0
        deleted_dirs = 0
        
        # Delete files first
        for item in env_dir.rglob('*'):
            if item.is_file():
                try:
                    item.unlink()
                    deleted_files += 1
                except Exception as e:
                    print_error(f"Failed to delete file {item}: {e}")
        
        # Delete directories (in reverse order to handle nested dirs)
        for item in sorted(env_dir.rglob('*'), reverse=True):
            if item.is_dir():
                try:
                    item.rmdir()
                    deleted_dirs += 1
                except Exception as e:
                    # Directory might not be empty if some files failed to delete
                    print_warning(f"Failed to delete directory {item}: {e}")
        
        print_success(f"Deleted {deleted_files} file(s) and {deleted_dirs} directory(ies)")
        return True
        
    except Exception as e:
        print_error(f"Error cleaning environment: {e}")
        return False
