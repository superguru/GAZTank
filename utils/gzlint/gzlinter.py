#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
GZLint - HTML & JavaScript Linter
=================================
Scans HTML and JavaScript files for common issues and best practice violations.

This linter checks for things like multiple <h1> tags, incorrect heading order,
and the presence of `console.log` statements.

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from html.parser import HTMLParser

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.gzlogging import get_logging_context

# Global logging context
log = None


class HTMLValidator(HTMLParser):
    """HTML parser to detect malformed tags and basic validation issues"""
    
    def __init__(self):
        super().__init__()
        self.errors = []
        self.tag_stack = []  # Stack to track open tags
        self.line_number = 1
        
    def handle_starttag(self, tag, attrs):
        # Track opening tags for heading elements
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.tag_stack.append((tag, self.line_number))
    
    def handle_endtag(self, tag):
        # Check for mismatched closing tags for heading elements
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if not self.tag_stack:
                self.errors.append((
                    self.line_number,
                    f"Closing tag </{tag}> found without matching opening tag"
                ))
            else:
                opening_tag, opening_line = self.tag_stack.pop()
                if opening_tag != tag:
                    self.errors.append((
                        opening_line,
                        f"Mismatched tags: <{opening_tag}> opened on line {opening_line} but closed with </{tag}>"
                    ))
    
    def handle_data(self, data):
        # Count newlines to track line numbers
        self.line_number += data.count('\n')
    
    def feed(self, data):
        """Override feed to reset state"""
        self.line_number = 1
        self.tag_stack = []
        self.errors = []
        super().feed(data)
    
    def get_unclosed_tags(self):
        """Get any tags that were opened but never closed"""
        return self.tag_stack


class HeadingParser(HTMLParser):
    """Custom HTML parser to track heading tags"""
    
    def __init__(self):
        super().__init__()
        self.headings = []  # List of tuples: (tag, line_number, text_content)
        self.current_tag = None
        self.current_text = []
        self.line_number = 1
        self.data_line = 1
        
    def handle_starttag(self, tag, attrs):
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.current_tag = tag
            self.current_text = []
            self.data_line = self.line_number
    
    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] and self.current_tag == tag:
            text = ''.join(self.current_text).strip()
            self.headings.append((tag, self.data_line, text))
            self.current_tag = None
            self.current_text = []
    
    def handle_data(self, data):
        if self.current_tag:
            self.current_text.append(data)
        # Count newlines to track line numbers
        self.line_number += data.count('\n')
    
    def feed(self, data):
        """Override feed to reset line counter"""
        self.line_number = 1
        super().feed(data)


class LintIssue:
    """Represents a single linting issue"""
    
    SEVERITY_ERROR = '❌'
    SEVERITY_WARNING = '⚠️'
    SEVERITY_INFO = 'ℹ️'
    
    def __init__(self, file_path, severity, rule, message, line=None, suggestion=None):
        self.file_path = file_path
        self.severity = severity
        self.rule = rule
        self.message = message
        self.line = line
        self.suggestion = suggestion
    
    def __str__(self):
        result = f"{self.severity} [{self.rule}] {self.file_path}"
        if self.line:
            result += f" (line {self.line})"
        result += f"\n   {self.message}"
        if self.suggestion:
            result += f"\n   💡 Suggestion: {self.suggestion}"
        return result


class JSLinter:
    """Linter for JavaScript files"""
    
    def __init__(self):
        self.issues = []
    
    def lint_file(self, file_path, report_path=None):
        """Lint a single JavaScript file
        
        Args:
            file_path: Absolute path to the file to read
            report_path: Path to display in reports (defaults to file_path)
        """
        if report_path is None:
            report_path = file_path
        
        if log:
            log.inf(f"Linting JavaScript file: {report_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Run checks
            self.check_console_log(report_path, lines)
            
        except Exception as e:
            if log:
                log.err(f"Failed to parse {report_path}: {str(e)}")
            self.issues.append(LintIssue(
                report_path,
                LintIssue.SEVERITY_ERROR,
                'PARSE_ERROR',
                f"Failed to parse file: {str(e)}"
            ))
    
    def check_console_log(self, file_path, lines):
        """Check for console.log statements (error in production)"""
        for i, line in enumerate(lines, start=1):
            # Skip lines that are comments
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            
            # Check for console.log (not in block comments)
            if 'console.log' in line:
                # Simple check - doesn't handle multi-line comments perfectly
                # but good enough for most cases
                if log:
                    log.wrn(f"console.log found in {file_path} line {i}")
                self.issues.append(LintIssue(
                    file_path,
                    LintIssue.SEVERITY_ERROR,
                    'CONSOLE_LOG',
                    "console.log() statement found. Remove console.log() before production.",
                    line=i,
                    suggestion="Remove this console.log() or use console.error()/console.warn() for intentional logging."
                ))


class HTMLLinter:
    """Linter for HTML files"""
    
    def __init__(self):
        self.issues = []
    
    def lint_file(self, file_path, report_path=None):
        """Lint a single HTML file
        
        Args:
            file_path: Absolute path to the file to read
            report_path: Path to display in reports (defaults to file_path)
        """
        if report_path is None:
            report_path = file_path
        
        if log:
            log.inf(f"Linting HTML file: {report_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # First, validate HTML structure
            validator = HTMLValidator()
            validator.feed(content)
            
            # Check for validation errors (stop processing if found)
            if validator.errors:
                for line, error_msg in validator.errors:
                    if log:
                        log.err(f"HTML validation error in {report_path} line {line}: {error_msg}")
                    self.issues.append(LintIssue(
                        report_path,
                        LintIssue.SEVERITY_ERROR,
                        'HTML_INVALID',
                        error_msg,
                        line=line,
                        suggestion="Fix the malformed HTML tags before other checks can run."
                    ))
                # Stop processing this file if HTML is invalid
                return
            
            # Check for unclosed tags
            unclosed = validator.get_unclosed_tags()
            if unclosed:
                for tag, line in unclosed:
                    if log:
                        log.err(f"Unclosed tag in {report_path} line {line}: <{tag}>")
                    self.issues.append(LintIssue(
                        report_path,
                        LintIssue.SEVERITY_ERROR,
                        'HTML_INVALID',
                        f"Unclosed tag: <{tag}> opened on line {line} but never closed",
                        line=line,
                        suggestion=f"Add closing tag </{tag}> before end of file."
                    ))
                # Stop processing this file if HTML is invalid
                return
            
            # Parse headings (only if HTML is valid)
            parser = HeadingParser()
            parser.feed(content)
            
            # Run checks
            self.check_h1_count(report_path, parser.headings)
            self.check_h1_before_other_headings(report_path, parser.headings)
            
        except Exception as e:
            if log:
                log.err(f"Failed to parse {report_path}: {str(e)}")
            self.issues.append(LintIssue(
                report_path,
                LintIssue.SEVERITY_ERROR,
                'PARSE_ERROR',
                f"Failed to parse file: {str(e)}"
            ))
    
    def check_h1_count(self, file_path, headings):
        """Check that there is exactly one h1 per file"""
        h1_headings = [h for h in headings if h[0] == 'h1']
        
        if len(h1_headings) == 0:
            if log:
                log.wrn(f"No <h1> tag in {file_path}")
            self.issues.append(LintIssue(
                file_path,
                LintIssue.SEVERITY_WARNING,
                'H1_MISSING',
                "No <h1> tag found. Pages should have exactly one <h1> for SEO.",
                suggestion="Add an <h1> tag as the main heading for this page."
            ))
        elif len(h1_headings) > 1:
            lines = [str(h[1]) for h in h1_headings]
            if log:
                log.err(f"Multiple <h1> tags in {file_path} on lines: {', '.join(lines)}")
            self.issues.append(LintIssue(
                file_path,
                LintIssue.SEVERITY_ERROR,
                'H1_MULTIPLE',
                f"Found {len(h1_headings)} <h1> tags (lines: {', '.join(lines)}). Pages should have exactly one <h1>.",
                line=h1_headings[0][1],
                suggestion="Keep only one <h1> tag and change others to <h2> or appropriate levels."
            ))
    
    def check_h1_before_other_headings(self, file_path, headings):
        """Check that h1 appears before h2, h3, etc."""
        if not headings:
            return
        
        # Find first h1
        first_h1_index = None
        for i, (tag, line, text) in enumerate(headings):
            if tag == 'h1':
                first_h1_index = i
                break
        
        # If no h1, skip this check (already caught by check_h1_count)
        if first_h1_index is None:
            return
        
        # Check if any h2, h3, etc. appear before the first h1
        for i in range(first_h1_index):
            tag, line, text = headings[i]
            if tag in ['h2', 'h3', 'h4', 'h5', 'h6']:
                if log:
                    log.err(f"<{tag}> appears before <h1> in {file_path} line {line}")
                self.issues.append(LintIssue(
                    file_path,
                    LintIssue.SEVERITY_ERROR,
                    'H1_ORDER',
                    f"<{tag}> appears before <h1> (line {line}). The <h1> should be the first heading.",
                    line=line,
                    suggestion=f"Move the <h1> tag before this <{tag}> tag, or change the <{tag}> to <h1>."
                ))
                break  # Only report the first violation


class ConfigLinter:
    """Linter for TOML configuration files"""
    
    def __init__(self):
        self.issues = []
    
    def lint_generate_config(self, config_path: Path, report_path=None):
        """
        Lint the generate.toml configuration file
        
        Args:
            config_path: Absolute path to the config file
            report_path: Path to display in reports (defaults to config_path)
        """
        if report_path is None:
            report_path = config_path
        
        if log:
            log.inf(f"Linting config file: {report_path}")
        
        # Check if tomllib is available
        if tomllib is None:
            if log:
                log.err(f"Cannot validate {report_path}: tomllib/tomli not available")
            self.issues.append(LintIssue(
                str(report_path),
                LintIssue.SEVERITY_ERROR,
                'CONFIG_DEPENDENCY',
                "Cannot validate config: tomllib/tomli not available",
                suggestion="Install tomli package: pip install tomli"
            ))
            return
        
        # Try to parse the TOML file
        try:
            with open(config_path, 'rb') as f:
                config_data = tomllib.load(f)
        except Exception as e:
            if log:
                log.err(f"Failed to parse {report_path}: {str(e)}")
            self.issues.append(LintIssue(
                str(report_path),
                LintIssue.SEVERITY_ERROR,
                'CONFIG_PARSE',
                f"Failed to parse TOML file: {str(e)}",
                suggestion="Check TOML syntax is valid"
            ))
            return
        
        # Validate each group
        groups = config_data.get('group', [])
        if not groups:
            self.issues.append(LintIssue(
                str(report_path),
                LintIssue.SEVERITY_WARNING,
                'CONFIG_EMPTY',
                "No [[group]] sections found in config",
                suggestion="Add at least one [[group]] section with files to process"
            ))
            return
        
        for i, group in enumerate(groups):
            group_name = group.get('name', f'group_{i}')
            
            # Check for required input_type attribute
            if 'input_type' not in group:
                if log:
                    log.err(f"Group '{group_name}' in {report_path} missing input_type attribute")
                self.issues.append(LintIssue(
                    str(report_path),
                    LintIssue.SEVERITY_ERROR,
                    'CONFIG_MISSING_INPUT_TYPE',
                    f"Group '{group_name}' is missing required 'input_type' attribute",
                    suggestion="Add input_type attribute (e.g., input_type = \"markdown\")"
                ))
            
            # Check for output_dir attribute
            if 'output_dir' not in group:
                if log:
                    log.err(f"Group '{group_name}' in {report_path} missing output_dir attribute")
                self.issues.append(LintIssue(
                    str(report_path),
                    LintIssue.SEVERITY_ERROR,
                    'CONFIG_MISSING_OUTPUT_DIR',
                    f"Group '{group_name}' is missing required 'output_dir' attribute",
                    suggestion="Add output_dir attribute specifying where to save generated files"
                ))
            
            # Check for files array
            if 'files' not in group:
                if log:
                    log.err(f"Group '{group_name}' in {report_path} missing files attribute")
                self.issues.append(LintIssue(
                    str(report_path),
                    LintIssue.SEVERITY_ERROR,
                    'CONFIG_MISSING_FILES',
                    f"Group '{group_name}' is missing required 'files' attribute",
                    suggestion="Add files array with list of files to process"
                ))
            elif not group['files']:
                if log:
                    log.wrn(f"Group '{group_name}' in {report_path} has empty files array")
                self.issues.append(LintIssue(
                    str(report_path),
                    LintIssue.SEVERITY_WARNING,
                    'CONFIG_EMPTY_FILES',
                    f"Group '{group_name}' has an empty files array",
                    suggestion="Add files to process or remove this group"
                ))
    
    def lint_tools_config(self, config_path: Path, report_path=None):
        """
        Lint the tools.toml configuration file
        
        Args:
            config_path: Absolute path to the config file
            report_path: Path to display in reports (defaults to config_path)
        """
        if report_path is None:
            report_path = config_path
        
        # Check if tomllib is available
        if tomllib is None:
            self.issues.append(LintIssue(
                str(report_path),
                LintIssue.SEVERITY_ERROR,
                'CONFIG_DEPENDENCY',
                "Cannot validate config: tomllib/tomli not available",
                suggestion="Install tomli package: pip install tomli"
            ))
            return
        
        # Try to parse the TOML file
        try:
            with open(config_path, 'rb') as f:
                config_data = tomllib.load(f)
        except Exception as e:
            self.issues.append(LintIssue(
                str(report_path),
                LintIssue.SEVERITY_ERROR,
                'CONFIG_PARSE',
                f"Failed to parse TOML file: {str(e)}",
                suggestion="Check TOML syntax is valid"
            ))
            return
        
        # Check for environments section
        if 'environments' not in config_data:
            self.issues.append(LintIssue(
                str(report_path),
                LintIssue.SEVERITY_ERROR,
                'CONFIG_MISSING_ENVIRONMENTS',
                "Missing [environments] section in tools.toml",
                suggestion="Add [environments] section with at least one environment"
            ))
            return
        
        environments = config_data['environments']
        if not environments:
            self.issues.append(LintIssue(
                str(report_path),
                LintIssue.SEVERITY_WARNING,
                'CONFIG_EMPTY_ENVIRONMENTS',
                "No environments defined in [environments] section",
                suggestion="Add at least one environment (e.g., [environments.dev])"
            ))
            return
        
        # Validate each environment
        for env_name, env_config in environments.items():
            if not isinstance(env_config, dict):
                self.issues.append(LintIssue(
                    str(report_path),
                    LintIssue.SEVERITY_ERROR,
                    'CONFIG_INVALID_ENVIRONMENT',
                    f"Environment '{env_name}' is not properly configured",
                    suggestion="Each environment should be a table: [environments.{env_name}]"
                ))
                continue
            
            # Check for required log_dir attribute
            if 'log_dir' not in env_config:
                self.issues.append(LintIssue(
                    str(report_path),
                    LintIssue.SEVERITY_ERROR,
                    'CONFIG_MISSING_LOG_DIR',
                    f"Environment '{env_name}' is missing required 'log_dir' attribute",
                    suggestion="Add log_dir attribute (e.g., log_dir = \"dev\")"
                ))
            
            # Check for description attribute (warning if missing)
            if 'description' not in env_config:
                self.issues.append(LintIssue(
                    str(report_path),
                    LintIssue.SEVERITY_WARNING,
                    'CONFIG_MISSING_DESCRIPTION',
                    f"Environment '{env_name}' is missing 'description' attribute",
                    suggestion="Add description for documentation purposes"
                ))
    
    def lint_ftp_users_config(self, config_path: Path, report_path=None):
        """
        Lint the ftp_users.toml configuration file
        
        Args:
            config_path: Absolute path to the config file
            report_path: Path to display in reports (defaults to config_path)
        """
        if report_path is None:
            report_path = config_path
        
        # Check if tomllib is available
        if tomllib is None:
            self.issues.append(LintIssue(
                str(report_path),
                LintIssue.SEVERITY_ERROR,
                'CONFIG_DEPENDENCY',
                "Cannot validate config: tomllib/tomli not available",
                suggestion="Install tomli package: pip install tomli"
            ))
            return
        
        # Try to parse the TOML file
        try:
            with open(config_path, 'rb') as f:
                config_data = tomllib.load(f)
        except Exception as e:
            self.issues.append(LintIssue(
                str(report_path),
                LintIssue.SEVERITY_ERROR,
                'CONFIG_PARSE',
                f"Failed to parse TOML file: {str(e)}",
                suggestion="Check TOML syntax is valid"
            ))
            return
        
        # Check for environments section
        if 'environments' not in config_data:
            self.issues.append(LintIssue(
                str(report_path),
                LintIssue.SEVERITY_ERROR,
                'CONFIG_MISSING_ENVIRONMENTS',
                "Missing [environments] section in ftp_users.toml",
                suggestion="Add [environments] section with at least one environment"
            ))
            return
        
        environments = config_data['environments']
        if not environments:
            self.issues.append(LintIssue(
                str(report_path),
                LintIssue.SEVERITY_WARNING,
                'CONFIG_EMPTY_ENVIRONMENTS',
                "No environments defined in [environments] section",
                suggestion="Add at least one environment (e.g., [environments.dev])"
            ))
            return
        
        # Validate each environment
        for env_name, env_config in environments.items():
            if not isinstance(env_config, dict):
                self.issues.append(LintIssue(
                    str(report_path),
                    LintIssue.SEVERITY_ERROR,
                    'CONFIG_INVALID_ENVIRONMENT',
                    f"Environment '{env_name}' is not properly configured",
                    suggestion="Each environment should be a table: [environments.{env_name}]"
                ))
                continue
            
            # Check for required username attribute
            if 'username' not in env_config:
                self.issues.append(LintIssue(
                    str(report_path),
                    LintIssue.SEVERITY_ERROR,
                    'CONFIG_MISSING_USERNAME',
                    f"Environment '{env_name}' is missing required 'username' attribute",
                    suggestion="Add username attribute (e.g., username = \"dev_user\")"
                ))
            
            # Check for required password attribute
            if 'password' not in env_config:
                self.issues.append(LintIssue(
                    str(report_path),
                    LintIssue.SEVERITY_ERROR,
                    'CONFIG_MISSING_PASSWORD',
                    f"Environment '{env_name}' is missing required 'password' attribute",
                    suggestion="Add password attribute (e.g., password = \"dev_pass\")"
                ))
            
            # Check for required permissions attribute
            if 'permissions' not in env_config:
                self.issues.append(LintIssue(
                    str(report_path),
                    LintIssue.SEVERITY_ERROR,
                    'CONFIG_MISSING_PERMISSIONS',
                    f"Environment '{env_name}' is missing required 'permissions' attribute",
                    suggestion="Add permissions attribute (e.g., permissions = \"elradfmwMT\")"
                ))
    
    def lint_config_consistency(self, project_root: Path):
        """
        Check that pipeline.toml, tools.toml, and ftp_users.toml have matching environment sections.
        
        Args:
            project_root: Project root directory path
        """
        config_dir = project_root / 'config'
        pipeline_toml = config_dir / 'pipeline.toml'
        tools_toml = config_dir / 'tools.toml'
        ftp_users_toml = config_dir / 'ftp_users.toml'
        
        # Check if pipeline.toml exists (required for comparison)
        if not pipeline_toml.exists():
            return  # Individual file checks will catch missing files
        
        # Check if tomllib is available
        if tomllib is None:
            return  # Already reported in individual file checks
        
        # Parse pipeline.toml (source of truth)
        try:
            with open(pipeline_toml, 'rb') as f:
                pipeline_config = tomllib.load(f)
        except Exception:
            return  # Parse error already caught in individual file check
        
        # Check for environments section in pipeline.toml
        if 'environments' not in pipeline_config:
            return  # Missing section already caught in individual file checks
        
        pipeline_envs = set(pipeline_config['environments'].keys())
        
        # Check tools.toml if it exists
        if tools_toml.exists():
            try:
                with open(tools_toml, 'rb') as f:
                    tools_config = tomllib.load(f)
                
                if 'environments' in tools_config:
                    tools_envs = set(tools_config['environments'].keys())
                    
                    if pipeline_envs != tools_envs:
                        # Find differences
                        missing_in_tools = pipeline_envs - tools_envs
                        extra_in_tools = tools_envs - pipeline_envs
                        
                        report_path = f"{tools_toml.relative_to(project_root)} vs {pipeline_toml.relative_to(project_root)}"
                        error_msg = "Environment sections do not match between pipeline.toml and tools.toml"
                        
                        details = []
                        if missing_in_tools:
                            details.append(f"Missing in tools.toml: {', '.join(sorted(missing_in_tools))}")
                        if extra_in_tools:
                            details.append(f"Extra in tools.toml (not in pipeline.toml): {', '.join(sorted(extra_in_tools))}")
                        
                        if details:
                            error_msg += "\n   " + "\n   ".join(details)
                        
                        self.issues.append(LintIssue(
                            report_path,
                            LintIssue.SEVERITY_ERROR,
                            'CONFIG_MISMATCH',
                            error_msg,
                            suggestion="Ensure both files define the same environment names (dev, staging, prod, etc.)"
                        ))
            except Exception:
                pass  # Parse error already caught in individual file check
        
        # Check ftp_users.toml if it exists
        if ftp_users_toml.exists():
            try:
                with open(ftp_users_toml, 'rb') as f:
                    ftp_users_config = tomllib.load(f)
                
                if 'environments' in ftp_users_config:
                    ftp_users_envs = set(ftp_users_config['environments'].keys())
                    
                    if pipeline_envs != ftp_users_envs:
                        # Find differences
                        missing_in_ftp_users = pipeline_envs - ftp_users_envs
                        extra_in_ftp_users = ftp_users_envs - pipeline_envs
                        
                        report_path = f"{ftp_users_toml.relative_to(project_root)} vs {pipeline_toml.relative_to(project_root)}"
                        error_msg = "Environment sections do not match between pipeline.toml and ftp_users.toml"
                        
                        details = []
                        if missing_in_ftp_users:
                            details.append(f"Missing in ftp_users.toml: {', '.join(sorted(missing_in_ftp_users))}")
                        if extra_in_ftp_users:
                            details.append(f"Extra in ftp_users.toml (not in pipeline.toml): {', '.join(sorted(extra_in_ftp_users))}")
                        
                        if details:
                            error_msg += "\n   " + "\n   ".join(details)
                        
                        self.issues.append(LintIssue(
                            report_path,
                            LintIssue.SEVERITY_ERROR,
                            'CONFIG_MISMATCH',
                            error_msg,
                            suggestion="Ensure both files define the same environment names (dev, staging, prod, etc.)"
                        ))
            except Exception:
                pass  # Parse error already caught in individual file check


class GZLinter:
    """Main linter class"""
    
    def __init__(self, src_dir, project_root=None):
        self.src_dir = Path(src_dir)
        self.project_root = Path(project_root) if project_root else self.src_dir.parent
        self.html_linter = HTMLLinter()
        self.js_linter = JSLinter()
        self.config_linter = ConfigLinter()
        self.files_scanned = 0
        self.files_with_issues = 0
    
    def scan(self):
        """Scan all HTML and JavaScript files in src directory"""
        print(f"Scanning: {self.src_dir}")
        print()
        
        # Check configuration files
        print("Checking configuration files...")
        generate_config = self.project_root / 'config' / 'generate.toml'
        if generate_config.exists():
            print(f"  {generate_config.relative_to(self.project_root)}")
            self.config_linter.lint_generate_config(
                generate_config,
                generate_config.relative_to(self.project_root)
            )
            self.files_scanned += 1
        
        tools_config = self.project_root / 'config' / 'tools.toml'
        if tools_config.exists():
            print(f"  {tools_config.relative_to(self.project_root)}")
            self.config_linter.lint_tools_config(
                tools_config,
                tools_config.relative_to(self.project_root)
            )
            self.files_scanned += 1
        
        ftp_users_config = self.project_root / 'config' / 'ftp_users.toml'
        if ftp_users_config.exists():
            print(f"  {ftp_users_config.relative_to(self.project_root)}")
            self.config_linter.lint_ftp_users_config(
                ftp_users_config,
                ftp_users_config.relative_to(self.project_root)
            )
            self.files_scanned += 1
        
        # Check consistency between config files
        self.config_linter.lint_config_consistency(self.project_root)
        print()
        
        # Find all HTML and JS files (recursively including subdirectories)
        html_files = list(self.src_dir.rglob('*.html'))
        js_files = list(self.src_dir.rglob('*.js'))
        
        if not html_files and not js_files:
            print("⚠️  No HTML or JavaScript files found")
            return
        
        if html_files:
            print(f"Found {len(html_files)} HTML file(s) (including subdirectories)")
        if js_files:
            print(f"Found {len(js_files)} JavaScript file(s) (including subdirectories)")
        print()
        
        # Lint HTML files
        if html_files:
            print("Checking HTML files (including subdirectories)...")
            for html_file in sorted(html_files):
                relative_path = html_file.relative_to(self.src_dir.parent)
                print(f"  {relative_path}")
                # Pass absolute path for reading, relative path for reporting
                self.html_linter.lint_file(html_file, relative_path)
                self.files_scanned += 1
            print()
        
        # Lint JavaScript files
        if js_files:
            print("Checking JavaScript files (including subdirectories)...")
            for js_file in sorted(js_files):
                relative_path = js_file.relative_to(self.src_dir.parent)
                print(f"  {relative_path}")
                # Pass absolute path for reading, relative path for reporting
                self.js_linter.lint_file(js_file, relative_path)
                self.files_scanned += 1
            print()
        
        # Count files with issues
        files_with_issues = set()
        for issue in self.html_linter.issues + self.js_linter.issues + self.config_linter.issues:
            files_with_issues.add(issue.file_path)
        self.files_with_issues = len(files_with_issues)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate the lint report"""
        print("=" * 60)
        print("GENERATING REPORT")
        print("=" * 60)
        
        # Combine all issues
        all_issues = self.html_linter.issues + self.js_linter.issues + self.config_linter.issues
        
        # Group issues by severity
        errors = [i for i in all_issues if i.severity == LintIssue.SEVERITY_ERROR]
        warnings = [i for i in all_issues if i.severity == LintIssue.SEVERITY_WARNING]
        info = [i for i in all_issues if i.severity == LintIssue.SEVERITY_INFO]
        
        # Build report
        lines = []
        lines.append("=" * 80)
        lines.append("GZLINT REPORT - GAZ TANK HTML LINTER")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Scanned: {self.files_scanned} file(s)")
        lines.append(f"Files with issues: {self.files_with_issues}")
        lines.append("")
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"  ❌ Errors:   {len(errors)}")
        lines.append(f"  ⚠️  Warnings: {len(warnings)}")
        lines.append(f"  ℹ️  Info:     {len(info)}")
        lines.append("")
        
        if not all_issues:
            lines.append("✅ NO ISSUES FOUND - ALL CHECKS PASSED!")
            lines.append("")
        else:
            # Report errors
            if errors:
                lines.append("=" * 80)
                lines.append("ERRORS")
                lines.append("=" * 80)
                lines.append("")
                for issue in errors:
                    lines.append(str(issue))
                    lines.append("")
            
            # Report warnings
            if warnings:
                lines.append("=" * 80)
                lines.append("WARNINGS")
                lines.append("=" * 80)
                lines.append("")
                for issue in warnings:
                    lines.append(str(issue))
                    lines.append("")
            
            # Report info
            if info:
                lines.append("=" * 80)
                lines.append("INFO")
                lines.append("=" * 80)
                lines.append("")
                for issue in info:
                    lines.append(str(issue))
                    lines.append("")
        
        # Print report to console
        print('\n'.join(lines))
        print()
        print("SUMMARY")
        print(f"  Files scanned: {self.files_scanned}")
        print(f"  Files with issues: {self.files_with_issues}")
        print(f"  ❌ Errors: {len(errors)}")
        print(f"  ⚠️  Warnings: {len(warnings)}")
        print(f"  ℹ️  Info: {len(info)}")
        
        all_issues = self.html_linter.issues + self.js_linter.issues + self.config_linter.issues
        if not all_issues:
            print()
            print("✅ ALL CHECKS PASSED!")


def main():
    """Main function"""
    global log
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='GZLint - HTML, JavaScript & Config Linter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python -m gzlint              # Lint all files in src/
  python -m gzlint --help       # Show this help message

Exit codes:
  0 - No errors found (warnings are OK)
  1 - Errors found that must be fixed
        '''
    )
    
    # Add arguments accepted but ignored for compatibility with build scripts
    parser.add_argument(
        '-e', '--environment',
        choices=['dev', 'staging', 'prod'],
        help='Ignored (accepted for compatibility with other modules)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Ignored (accepted for compatibility with other modules)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Ignored (accepted for compatibility with other modules)'
    )
    
    # Use parse_known_args to ignore unknown arguments from pipeline
    args, unknown = parser.parse_known_args()
    
    # Initialize logging (using 'dev' environment, with console output)
    try:
        log = get_logging_context('dev', 'gzlint', console=True)
        log.inf("GZLint - HTML, JavaScript & Config Linter started")
    except Exception as e:
        print(f"Warning: Logging initialization failed: {e}")
        print("Continuing without logging...")
        log = None
    
    # Console banner (not logged to file)
    print("=" * 60)
    print("GZLINT - HTML, JAVASCRIPT & CONFIG LINTER")
    print("=" * 60)
    
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    src_dir = project_root / 'src'
    
    # Validate src directory exists
    if not src_dir.exists():
        print(f"❌ ERROR: Source directory not found: {src_dir}")
        if log:
            log.err(f"Source directory not found: {src_dir}")
        return 1
    
    # Run linter
    linter = GZLinter(src_dir, project_root)
    linter.scan()
    
    print()
    print("=" * 60)
    
    # Return exit code based on issues found
    all_issues = linter.html_linter.issues + linter.js_linter.issues + linter.config_linter.issues
    if all_issues:
        errors = [i for i in all_issues if i.severity == LintIssue.SEVERITY_ERROR]
        if errors:
            print("❌ LINTING FAILED - Errors found")
            print("=" * 60)
            if log:
                log.err(f"Linting failed - {len(errors)} error(s) found")
            return 1
        else:
            print("⚠️  LINTING PASSED - Warnings found")
            print("=" * 60)
            if log:
                log.wrn(f"Linting passed with {len(all_issues)} warning(s)")
            return 0
    else:
        print("✅ LINTING PASSED - No issues")
        print("=" * 60)
        if log:
            log.inf("Linting passed - no issues found")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
