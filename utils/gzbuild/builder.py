#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
GAZTank Build Pipeline
======================
Complete pipeline execution that orchestrates all build steps in order.

This module runs the complete GAZTank build pipeline:
1. Clean orphaned files
2. Generate content files
3. Compose HTML from components
4. Apply site configuration
5. Run linting checks
6. Normalize markdown structure
7. Generate sitemap
8. Generate table of contents
9. Package site files
10. Deploy to target environment

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
import time
from pathlib import Path
from typing import Tuple, Optional, Callable
from dataclasses import dataclass, field

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.gzlogging import get_logging_context, LoggingContext
from utils.gzconfig import get_pipeline_config

# Import all the modules we'll orchestrate
from utils.compose.composer import main as compose_main
from utils.clean.cleaner import main as clean_main
from utils.setup.setup import main as setup_main
from utils.gzlint.gzlinter import main as lint_main
from utils.normalise.batch import main as normalise_main
from utils.generate.generator import main as generate_main
from utils.sitemap.sitemapper import main as sitemap_main
from utils.toc.toc import main as toc_main
from utils.package.packager import main as package_main
from utils.deploy.deployer import main as deploy_main

# Global logging context
log: Optional[LoggingContext] = None


@dataclass
class PipelineStep:
    """
    Represents a single step in the build pipeline.
    
    Each step encapsulates its configuration, execution logic, and timing data.
    """
    
    icon: str
    module_name: str
    main_func: Callable
    description: str
    extra_args: list = field(default_factory=list)
    display_timing: bool = False
    time_ms: int = field(default=0, init=False)
    step_num: int = field(default=0, init=False)
    full_description: str = field(init=False)
    
    def __post_init__(self):
        """Calculate the full description (icon + description) once on initialization."""
        self.full_description = f"{self.icon} {self.description}"
    
    def get_summary_line(self, max_desc_len: int) -> str:
        """
        Get formatted summary line for this step.
        
        Args:
            max_desc_len: Maximum description length for alignment
            
        Returns:
            Formatted string with icon, description, and timing
        """
        timing = format_time(self.time_ms)
        padding = max_desc_len - len(self.full_description)
        return f"    - {self.full_description}{' ' * padding}  ⏱️  {timing}"
    
    def execute(self, step_num: int, total_steps: int, pass_through_args: list) -> bool:
        """
        Execute this pipeline step.
        
        Args:
            step_num: Current step number (1-based)
            total_steps: Total number of steps in pipeline
            pass_through_args: Arguments to pass through to the module
            
        Returns:
            True if step succeeded, False otherwise
        """
        global log
        assert log is not None
        
        self.step_num = step_num
        step_start = time.time()
        
        print(f"{self.icon} [{step_num}/{total_steps}] {self.description}...")
        log.inf(f"Step {step_num}/{total_steps}: {self.description}")
        
        # Build command arguments
        original_argv = sys.argv.copy()
        sys.argv = [self.module_name] + self.extra_args + pass_through_args
        
        try:
            self.main_func()
            success = True
        except SystemExit as e:
            if e.code != 0:
                log.err(f"Step {step_num}/{total_steps} failed: {self.description}")
                success = False
            else:
                success = True
        finally:
            sys.argv = original_argv
        
        # Record timing
        self.time_ms = int((time.time() - step_start) * 1000)
        log.inf(f"Step {step_num}/{total_steps} completed in {format_time(self.time_ms)}")
        
        # Log deployment completion if this step should display timing
        if self.display_timing:
            log.inf(f"Deployment completed in {format_time(self.time_ms)}")
        
        print("")
        return success


class Pipeline:
    """
    Manages a collection of pipeline steps and their execution.
    """
    
    def __init__(self):
        """Initialize an empty pipeline."""
        self.steps: list[PipelineStep] = []
        self.max_desc_len: int = 0
    
    def add(self, step: PipelineStep) -> None:
        """
        Add a step to the pipeline.
        
        Args:
            step: PipelineStep to add
        """
        self.steps.append(step)
        # Update max description length
        self.max_desc_len = max(self.max_desc_len, len(step.full_description))
    
    def execute_all(self, pass_through_args: list) -> bool:
        """
        Execute all pipeline steps in sequence.
        
        Args:
            pass_through_args: Arguments to pass through to each step
            
        Returns:
            True if all steps succeeded, False otherwise
        """
        total_steps = len(self.steps)
        
        for step_num, step in enumerate(self.steps, start=1):
            success = step.execute(step_num, total_steps, pass_through_args)
            if not success:
                return False
        
        return True
    
    def get_deploy_time(self) -> int:
        """
        Get the deployment time from steps marked with display_timing.
        
        Returns:
            Deployment time in milliseconds
        """
        return next((step.time_ms for step in self.steps if step.display_timing), 0)
    
    def print_summary(self, total_time: int) -> None:
        """
        Print the pipeline execution summary.
        
        Args:
            total_time: Total execution time in milliseconds
        """
        print("")
        print("=" * 60)
        print("  ✅ Pipeline Complete!")
        print("=" * 60)
        print("  All pipeline stages executed successfully.")
        print("  Your site has been:")
        
        for step in self.steps:
            print(step.get_summary_line(self.max_desc_len))
        
        print("")
        print(f"  ⏱️  Total time: {format_time(total_time)}")
        print("=" * 60)
        print("")


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent


def format_time(milliseconds: int) -> str:
    """
    Format milliseconds into appropriate time format.
    
    Args:
        milliseconds: Total milliseconds
        
    Returns:
        Formatted time string like "2m 15.234s" or "1.234s" or "123ms"
    """
    if milliseconds < 1000:
        return f"{milliseconds}ms"
    
    total_seconds = milliseconds / 1000.0
    
    if total_seconds >= 60:
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}m {seconds:.3f}s"
    else:
        return f"{total_seconds:.3f}s"


def run_pipeline(pass_through_args: list) -> Tuple[bool, int, int, int]:
    """
    Run the complete build pipeline.
    
    Args:
        pass_through_args: All arguments to pass to each module
        
    Returns:
        Tuple of (success, build_time, deploy_time, total_time) in milliseconds
    """
    global log
    assert log is not None
    
    start_time = time.time()
    
    print("")
    print("=" * 60)
    print("  🏗️  GAZ Tank - Complete Pipeline Execution")
    print("=" * 60)
    print("")
    
    # Create pipeline and add steps
    pipeline = Pipeline()
    pipeline.add(PipelineStep("🧹", "clean", clean_main, "Cleaning orphaned files"))
    pipeline.add(PipelineStep("🪄", "generate", generate_main, "Generating content"))
    pipeline.add(PipelineStep("🔨", "compose", compose_main, "Composing HTML from components"))
    pipeline.add(PipelineStep("⚙️", "setup_site", setup_main, "Applying site configuration", extra_args=["--force"]))
    pipeline.add(PipelineStep("🔍", "gzlint", lint_main, "Running lint checks"))
    pipeline.add(PipelineStep("⚖️", "normalise", normalise_main, "Normalizing markdown structure"))
    pipeline.add(PipelineStep("🗺️", "sitemap", sitemap_main, "Generating sitemap"))
    pipeline.add(PipelineStep("📑", "toc", toc_main, "Generating table of contents"))
    pipeline.add(PipelineStep("📦", "package", package_main, "Packaging site files"))
    pipeline.add(PipelineStep("🚀", "deploy", deploy_main, "Deploying to environment", display_timing=True))
    
    # Execute all pipeline steps
    success = pipeline.execute_all(pass_through_args)
    if not success:
        return False, 0, 0, 0
    
    # Calculate timing metrics
    end_time = time.time()
    total_time = int((end_time - start_time) * 1000)
    
    deploy_time = pipeline.get_deploy_time()
    build_time = total_time - deploy_time
    log.inf(f"Build steps completed in {format_time(build_time)}")
    
    # Print success summary
    pipeline.print_summary(total_time)
    
    return True, build_time, deploy_time, total_time


def main() -> None:
    """Main entry point for the build pipeline"""
    global log
    
    # Parse arguments - only validate -h and -e, pass everything else through
    if '-h' in sys.argv or '--help' in sys.argv:
        print("GAZ Tank - Complete Build Pipeline")
        print("")
        print("Usage: gzbuild -e ENVIRONMENT [OPTIONS...]")
        print("")
        print("Required arguments:")
        print("  -e ENVIRONMENT    Target environment (dev, staging, prod)")
        print("")
        print("Optional arguments:")
        print("  -h, --help        Show this help message and exit")
        print("  --force           Force operations even if validation fails")
        print("  --clean-all       Clean all generated files and exit")
        print("  --dry-run         Preview operations without making changes")
        print("")
        print("Pipeline stages:")
        print("  1. Clean orphaned files")
        print("  2. Generate content")
        print("  3. Compose HTML from components")
        print("  4. Apply site configuration")
        print("  5. Run lint checks")
        print("  6. Normalize markdown structure")
        print("  7. Generate sitemap")
        print("  8. Generate table of contents")
        print("  9. Package site files")
        print(" 10. Deploy to environment")
        sys.exit(0)
    
    # Extract environment argument
    environment = None
    try:
        env_index = sys.argv.index('-e')
        if env_index + 1 < len(sys.argv):
            environment = sys.argv[env_index + 1]
    except ValueError:
        pass
    
    if not environment:
        print("Error: -e ENVIRONMENT is required")
        print("Use -h for help")
        sys.exit(1)
    
    if environment not in ['dev', 'staging', 'prod']:
        print(f"Error: Invalid environment '{environment}'. Must be dev, staging, or prod")
        sys.exit(1)
    
    # Build pass-through args (include -e and all other args)
    pass_through_args = []
    i = 1  # Skip program name
    while i < len(sys.argv):
        pass_through_args.append(sys.argv[i])
        i += 1
    
    # Initialize logging
    log = get_logging_context(environment, 'gzbuild')
    project_root = get_project_root()
    
    # Handle --clean-all mode: run clean and exit
    if '--clean-all' in pass_through_args:
        log.inf("GAZTank Build Pipeline started in CLEAN-ALL mode")
        log.inf(f"Project root: {project_root}")
        log.inf(f"Target environment: {environment}")
        print("")
        print("=" * 60)
        print("  🧹 GAZ Tank - Clean All Mode")
        print("=" * 60)
        print("")
        
        # Save original sys.argv to restore later
        original_argv = sys.argv.copy()
        
        # Build clean command arguments - pass through all args
        sys.argv = ['clean'] + pass_through_args
        
        try:
            from utils.clean.cleaner import main as clean_main
            clean_main()
            sys.exit(0)
        except SystemExit as e:
            sys.exit(e.code)
        finally:
            sys.argv = original_argv
    
    # Normal pipeline mode
    log.inf("GAZTank Build Pipeline started")
    log.inf(f"Project root: {project_root}")
    log.inf(f"Target environment: {environment}")
    
    # Run the pipeline
    success, build_time, deploy_time, total_time = run_pipeline(pass_through_args)
    
    if success:
        log.inf(f"Build time: {format_time(build_time)}, Deployment time: {format_time(deploy_time)}, Total time: {format_time(total_time)}")
        log.inf("GAZTank Build Pipeline completed successfully")
        sys.exit(0)
    else:
        log.err("GAZTank Build Pipeline failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
