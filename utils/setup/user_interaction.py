#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
User Interaction
================
Functions for getting user input during interactive setup wizard.

Authors: superguru, gazorper
License: GPL v3.0
"""

from . import ui_helpers
from . import validators

# Re-export for convenience
Colors = ui_helpers.Colors
print_section = ui_helpers.print_section
print_info = ui_helpers.print_info
print_warning = ui_helpers.print_warning
print_error = ui_helpers.print_error
get_color = validators.get_color


def get_input(prompt, default=None, required=True):
    """Get user input with optional default value
    
    Args:
        prompt: The prompt text to display
        default: Default value if user presses Enter
        required: Whether a value is required
        
    Returns:
        User input string or default value
    """
    if default:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "
    
    while True:
        value = input(prompt_text).strip()
        
        if not value and default:
            return default
        elif not value and not required:
            return ""
        elif not value and required:
            print_error("This field is required. Please enter a value.")
            continue
        else:
            return value


def get_yes_no(prompt, default=True):
    """Get yes/no input from user
    
    Args:
        prompt: The prompt text to display
        default: Default boolean value if user presses Enter
        
    Returns:
        Boolean value based on user input
    """
    default_text = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_text}]: ").strip().lower()
    
    if not response:
        return default
    return response in ['y', 'yes', 'true', '1']


def interactive_setup(existing_config):
    """Interactive setup wizard with user prompts
    
    Args:
        existing_config: Dictionary with existing configuration values
        
    Returns:
        Dictionary with user-provided configuration or 0 if cancelled
    """
    config_data = {}
    
    # ========================================
    # Basic Site Information
    # ========================================
    print_section("1. Basic Site Information")
    
    config_data['site_name'] = get_input(
        "Site name",
        default=existing_config['site_name']
    )
    
    config_data['tagline'] = get_input(
        "Site tagline/subtitle",
        default=existing_config['tagline']
    )
    
    config_data['short_name'] = get_input(
        "Short/alternate name (used in schema.org structured data)",
        default=config_data['site_name'][:20]
    )
    
    config_data['domain'] = get_input(
        "Domain name (without https://)",
        default=existing_config['domain']
    )
    
    # Immediately update canonical_base based on the domain
    config_data['canonical_base'] = f"https://{config_data['domain']}/"
    
    config_data['description'] = get_input(
        "Site description (for SEO)",
        default=existing_config['description']
    )
    
    config_data['author'] = get_input(
        "Primary author/owner name",
        default=existing_config['author']
    )
    
    config_data['author_secondary'] = get_input(
        "Secondary author name (optional, leave blank if none)",
        default=existing_config.get('author_secondary', ''),
        required=False
    )
    
    # ========================================
    # Theme Colors
    # ========================================
    print_section("2. Theme Colors")
    
    # Header Colors
    print_info("Header colors for site navigation and branding")
    config_data['header_text_color'] = get_color(
        "Header text color",
        default=existing_config['header_text_color'],
        get_input_fn=get_input
    )
    config_data['header_background_color'] = get_color(
        "Header background color",
        default=existing_config['header_background_color'],
        get_input_fn=get_input
    )
    
    # Footer Colors
    print_info("Footer colors for site footer area")
    config_data['footer_text_color'] = get_color(
        "Footer text color",
        default=existing_config['footer_text_color'],
        get_input_fn=get_input
    )
    config_data['footer_background_color'] = get_color(
        "Footer background color",
        default=existing_config['footer_background_color'],
        get_input_fn=get_input
    )
    config_data['footer_link_text_color'] = get_color(
        "Footer link text color",
        default=existing_config['footer_link_text_color'],
        get_input_fn=get_input
    )
    config_data['footer_link_hover_text_color'] = get_color(
        "Footer hover link text color",
        default=existing_config['footer_link_hover_text_color'],
        get_input_fn=get_input
    )
    
    # Sidebar Colors
    print_info("Sidebar colors for navigation menu")
    config_data['sidebar_background_color'] = get_color(
        "Sidebar background color",
        default=existing_config['sidebar_background_color'],
        get_input_fn=get_input
    )
    config_data['sidebar_highlight_background_color'] = get_color(
        "Sidebar highlight/active background color",
        default=existing_config['sidebar_highlight_background_color'],
        get_input_fn=get_input
    )
    config_data['sidebar_hover_background_color'] = get_color(
        "Sidebar hover background color",
        default=existing_config['sidebar_hover_background_color'],
        get_input_fn=get_input
    )
    config_data['sidebar_toggle_button_background_color'] = get_color(
        "Sidebar toggle button background color",
        default=existing_config['sidebar_toggle_button_background_color'],
        get_input_fn=get_input
    )
    
    # Content Colors
    print_info("Content colors for main content area")
    config_data['content_text_color'] = get_color(
        "Content text color",
        default=existing_config['content_text_color'],
        get_input_fn=get_input
    )
    config_data['content_background_color'] = get_color(
        "Content background color",
        default=existing_config['content_background_color'],
        get_input_fn=get_input
    )
    
    # Breadcrumb Colors
    print_info("Breadcrumb colors for navigation path")
    config_data['breadcrumb_text_color'] = get_color(
        "Breadcrumb text color",
        default=existing_config['breadcrumb_text_color'],
        get_input_fn=get_input
    )
    
    # TOC Colors
    print_info("Table of Contents colors")
    config_data['toc_background_color'] = get_color(
        "TOC background color",
        default=existing_config['toc_background_color'],
        get_input_fn=get_input
    )
    config_data['toc_heading_text_color'] = get_color(
        "TOC heading text color",
        default=existing_config['toc_heading_text_color'],
        get_input_fn=get_input
    )
    config_data['toc_link_text_color'] = get_color(
        "TOC link text color",
        default=existing_config['toc_link_text_color'],
        get_input_fn=get_input
    )
    config_data['toc_link_hover_text_color'] = get_color(
        "TOC hover link text color",
        default=existing_config['toc_link_hover_text_color'],
        get_input_fn=get_input
    )
    
    # Hashtag Colors
    print_info("Hashtag colors for tag elements")
    config_data['hashtag_text_color'] = get_color(
        "Hashtag text color",
        default=existing_config['hashtag_text_color'],
        get_input_fn=get_input
    )
    config_data['hashtag_background_color'] = get_color(
        "Hashtag background color",
        default=existing_config['hashtag_background_color'],
        get_input_fn=get_input
    )
    
    # Link Colors
    print_info("Link colors for all hyperlinks")
    config_data['link_text_color'] = get_color(
        "Link text color",
        default=existing_config['link_text_color'],
        get_input_fn=get_input
    )
    config_data['link_visited_text_color'] = get_color(
        "Visited link color",
        default=existing_config['link_visited_text_color'],
        get_input_fn=get_input
    )
    config_data['link_hover_text_color'] = get_color(
        "Link hover color",
        default=existing_config['link_hover_text_color'],
        get_input_fn=get_input
    )
    
    # General Colors (page and brand)
    if get_yes_no("Customize general page and brand colors?", default=False):
        config_data['body_text_color'] = get_color(
            "General body text color",
            default=existing_config['body_text_color'],
            get_input_fn=get_input
        )
        config_data['muted_text_color'] = get_color(
            "Muted/secondary text color",
            default=existing_config['muted_text_color'],
            get_input_fn=get_input
        )

    # ========================================
    # Images
    # ========================================
    print_section("3. Images & Branding")
    
    print_info("Place your logo images in the src/images/ directory")
    print_info("Recommended sizes: 512x512, 256x256 (desktop), 128x128, 75x75 (mobile), 50x50 (small)")
    
    config_data['logo_512'] = get_input(
        "Logo filename (512x512)",
        default=existing_config.get('logo_512', 'gaztank_logo_512x512.webp'),
        required=False
    )
    
    config_data['logo_256'] = get_input(
        "Logo filename (256x256)",
        default=existing_config['logo_256'],
        required=False
    )
    
    config_data['logo_128'] = get_input(
        "Logo filename (128x128)",
        default=existing_config.get('logo_128', 'gaztank_logo_128x128.webp'),
        required=False
    )
    
    config_data['logo_75'] = get_input(
        "Logo filename (75x75)",
        default=existing_config['logo_75'],
        required=False
    )
    
    config_data['logo_50'] = get_input(
        "Logo filename (50x50)",
        default=existing_config.get('logo_50', 'gaztank_logo_50x50.webp'),
        required=False
    )
    
    config_data['favicon_32'] = get_input(
        "Favicon filename (32x32)",
        default=existing_config['favicon_32'],
        required=False
    )
    
    config_data['favicon_16'] = get_input(
        "Favicon filename (16x16)",
        default=existing_config['favicon_16'],
        required=False
    )
    
    config_data['logo_alt_text'] = get_input(
        "Logo alt text (for accessibility)",
        default=existing_config.get('logo_alt_text', f"{config_data['site_name']} Logo"),
        required=False
    )
    
    # ========================================
    # Features
    # ========================================
    print_section("4. Features")
    
    config_data['enable_breadcrumbs'] = get_yes_no(
        "Enable breadcrumb navigation?",
        default=True
    )
    
    config_data['enable_toc'] = get_yes_no(
        "Enable table of contents?",
        default=True
    )
    
    config_data['enable_sidebar_toggle'] = get_yes_no(
        "Enable sidebar toggle button?",
        default=True
    )
    
    config_data['enable_syntax_highlighting'] = get_yes_no(
        "Enable syntax highlighting (Prism.js)?",
        default=True
    )
    
    # ========================================
    # SEO & Analytics
    # ========================================
    print_section("5. SEO & Analytics (Optional)")
    
    if get_yes_no("Configure SEO and analytics?", default=False):
        config_data['google_site_verification'] = get_input(
            "Google site verification code",
            default="",
            required=False
        )
        
        config_data['plausible_domain'] = get_input(
            "Plausible Analytics domain",
            default="",
            required=False
        )
        
        config_data['google_analytics_id'] = get_input(
            "Google Analytics ID (GA4)",
            default="",
            required=False
        )
    
    # ========================================
    # Summary & Confirmation
    # ========================================
    print_section("6. Configuration Summary")
    
    print(f"\n{Colors.BOLD}Site Configuration:{Colors.ENDC}")
    print(f"  Name: {config_data['site_name']}")
    print(f"  Domain: {config_data['domain']}")
    print(f"  Header Colors: {config_data.get('header_text_color', 'default')} / {config_data.get('header_background_color', 'default')}")
    print(f"  Content Colors: {config_data.get('content_text_color', 'default')} / {config_data.get('content_background_color', 'default')}")
    print(f"  Link Color: {config_data.get('link_text_color', 'default')}")
    print(f"  Author: {config_data['author']}")
    if config_data.get('author_secondary'):
        print(f"  Secondary Author: {config_data['author_secondary']}")
    print()
    
    if not get_yes_no("Save this configuration?", default=True):
        print_warning("Configuration cancelled. No changes made.")
        return 0
    
    return config_data
