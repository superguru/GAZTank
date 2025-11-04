#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Markdown to HTML Converter
==========================
Converts markdown files to HTML with normalization support.
Provides the MarkdownConverter class and utility functions for use by the
generator.py orchestrator.

Authors: superguru, gazorper
License: GPL v3.0
"""

import sys
from pathlib import Path
import mistune
from mistune import HTMLRenderer
from bs4 import BeautifulSoup

# Constants
SOURCE_NOTE_TEMPLATE = '<div>\n<br><br>\n<p><em>This content was automatically generated from <code>{}</code></em></p>\n</div>'


# Custom Mermaid Plugin for Mistune
def plugin_mermaid(md):
    """
    Plugin to handle mermaid code blocks.
    
    Converts ```mermaid code blocks to <pre class="mermaid"> for client-side rendering.
    """
    original_code_block = md.renderer.block_code
    
    def mermaid_code_block(code, info=None):
        """Render code block with special handling for mermaid"""
        if info and info.strip().lower() == 'mermaid':
            # Return mermaid code wrapped in proper HTML structure
            return f'<pre class="mermaid">\n{code}\n</pre>\n'
        # For other code blocks, use the original renderer
        return original_code_block(code, info)
    
    md.renderer.block_code = mermaid_code_block


class MarkdownConverter:
    """
    Markdown to HTML converter with configuration options.
    
    Encapsulates conversion parameters and provides a clean interface
    for converting markdown files to HTML.
    """
    
    def __init__(self, dry_run: bool = False, force: bool = False):
        """
        Initialize the converter with configuration options.
        
        Args:
            dry_run: If True, only show what would be done
            force: If True, convert even if output is newer than input
        """
        self.dry_run = dry_run
        self.force = force
    
    def fix_image_paths(self, html_content: str) -> str:
        """
        Fix image paths that reference src/ directory.
        
        Since the generated HTML files are placed in src/content/, references to
        src/images/ won't work. This method removes the 'src/' prefix from image paths.
        
        Args:
            html_content: HTML string to process
            
        Returns:
            str: HTML with fixed image paths
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        fixed_count = 0
        
        # Find all img tags
        for img in soup.find_all('img'):
            src = img.get('src')
            # Handle case where src might be a list or string
            if src and isinstance(src, str) and src.startswith('src/'):
                # Remove 'src/' prefix - the HTML file is already in src/content/
                # so '../images/file.png' will work instead of 'src/images/file.png'
                new_src = '../' + src[4:]  # Skip 'src/' and add '../'
                img['src'] = new_src
                fixed_count += 1
                print(f"    → Fixed image path: {src} -> {new_src}")
        
        if fixed_count > 0:
            print(f"    ✓ Fixed {fixed_count} image path(s)")
        
        return str(soup)
    
    def convert(self, input_path, output_path):
        """
        Convert a markdown file to HTML.
        
        Args:
            input_path: Path to input markdown file
            output_path: Path to output HTML file
        
        Returns:
            str: Status - 'success', 'skipped', or 'failed'
        """
        if not input_path.exists():
            print(f"  ERROR: Input file not found: {input_path}")
            return 'failed'
        
        if self.dry_run:
            print(f"  [DRY RUN] Would convert: {input_path}")
            print(f"  [DRY RUN] Output to:     {output_path}")
            return 'success'
        
        try:
            # Check if output file exists and is newer than input
            if not self.force and output_path.exists():
                input_mtime = input_path.stat().st_mtime
                output_mtime = output_path.stat().st_mtime
                
                if output_mtime >= input_mtime:
                    print(f"  ⏭️  Skipped (up-to-date):  {input_path.name}")
                    return 'skipped'
            
            # Read markdown file
            with open(input_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert to HTML with hard line breaks enabled
            # The 'url' plugin enables better URL handling
            # The 'table' plugin enables table support
            # The 'mermaid' plugin handles mermaid diagrams
            # The hard_wrap option converts line breaks to <br> tags
            markdown = mistune.create_markdown(plugins=['url', 'table', plugin_mermaid], hard_wrap=True, escape=False)
            html_result = markdown(md_content)
            
            # Ensure we have a string result
            if not isinstance(html_result, str):
                raise ValueError(f"Markdown conversion did not return string: {type(html_result)}")
            
            # Fix image paths that reference src/ directory
            html_content = self.fix_image_paths(html_result)
            
            # Add a note at the bottom indicating the source file
            source_note = SOURCE_NOTE_TEMPLATE.format(input_path.name)
            html_content += source_note
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"  ✅ Converted to HTML: {input_path.name} -> {output_path}")
            return 'success'
            
        except Exception as e:
            error_msg = f"Failed to convert {input_path}: {e}"
            print(f"  ❌ ERROR: {error_msg}")
            return 'failed'

