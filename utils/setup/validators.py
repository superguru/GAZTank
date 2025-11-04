#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Input Validators
================
Validation functions for user input (colors, domains, etc).

Authors: superguru, gazorper
License: GPL v3.0
"""

from . import ui_helpers

print_error = ui_helpers.print_error


def get_color(prompt, default, get_input_fn):
    """Get color input (hex format) from user and ensure uppercase
    
    Args:
        prompt: The prompt text to display
        default: Default color value
        get_input_fn: Function to get input from user
        
    Returns:
        Validated and uppercase hex color string
    """
    while True:
        color = get_input_fn(prompt, default, required=False)
        if not color:
            return default
        
        # Clean up color format - remove alpha channel if present
        clean_color = color.strip()
        if clean_color.startswith('#') and len(clean_color) == 9:  # 8-digit hex with alpha
            clean_color = clean_color[:7].upper()  # Keep only RGB part and make uppercase
        elif clean_color.endswith('ff') and len(clean_color) == 8:  # 8-digit without #
            clean_color = f"#{clean_color[:6].upper()}"
        
        # Validate hex color format and ensure uppercase
        if clean_color.startswith('#') and len(clean_color) in [4, 7]:
            return clean_color.upper()
        elif len(clean_color) in [3, 6]:
            return f"#{clean_color.upper()}"
        else:
            print_error("Invalid color format. Please use hex format (e.g., #E58822)")


def hex_to_rgba(hex_color, alpha):
    """Convert hex color to rgba with specified alpha
    
    Args:
        hex_color: Hex color string (with or without #)
        alpha: Alpha value as string (e.g., '0.15')
        
    Returns:
        RGBA color string
    """
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Convert hex to RGB
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    except (ValueError, IndexError):
        # Fallback to default color if hex is invalid
        return f"rgba(255, 215, 0, {alpha})"
