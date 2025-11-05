#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Configuration I/O
=================
Functions for loading and saving site configuration (TOML format).

Note: This file uses tomlkit which provides dict-like objects (Item, Container)
that support .get(), __getitem__, __setitem__, and 'in' operator at runtime,
but Pylance doesn't recognize these methods in the type stubs.

Authors: superguru, gazorper
License: GPL v3.0
"""

import shutil
from pathlib import Path
from datetime import datetime

try:
    import tomlkit
except ImportError:
    print("Error: tomlkit library not found.")
    print("Please install it with: pip install tomlkit")
    print("Note: tomlkit preserves comments and formatting in TOML files")
    import sys
    sys.exit(1)

from . import ui_helpers
from . import backup_manager

# Re-export for convenience
print_warning = ui_helpers.print_warning
print_success = ui_helpers.print_success
print_info = ui_helpers.print_info
format_setup_date = ui_helpers.format_setup_date
create_backup = backup_manager.create_backup


def backup_all_config_files(environment='unknown'):
    """Backup all configuration files in the config directory
    
    This creates a single timestamped zip file containing all config files
    (excluding backup files and example files). Files are automatically
    discovered, so new config files are included without code changes.
    
    Args:
        environment: Environment name to include in zip filename (dev, staging, production, etc.)
    
    Returns:
        String path to the backup zip file, or None if no files were backed up
    """
    config_dir = Path("config")
    if not config_dir.exists():
        print_warning("Config directory not found, skipping backup")
        return None
    
    # Get all files in config directory (excluding backups and examples)
    config_files = [
        f for f in config_dir.iterdir()
        if f.is_file() 
        and '.backup.' not in f.name 
        and '.example.' not in f.name
    ]
    
    if not config_files:
        print_warning("No config files found to backup")
        return None
    
    # Backup each file (they'll all go into the same zip due to timestamp)
    backup_path = None
    for config_file in config_files:
        result = create_backup(str(config_file), environment)
        if result:
            backup_path = result
    
    return backup_path


def get_fallback_defaults():
    """Get fallback default configuration values
    
    Returns:
        Dictionary with default configuration values
    """
    return {
        'site_name': 'My New Site',
        'tagline': 'Your Content Hub',
        'short_name': 'My Site',
        'domain': 'example.com',
        'description': 'Welcome to my site. Explore our content and resources.',
        'author': 'Your Name',
        'author_secondary': '',
        # Header Colors
        'header_text_color': '#212529',
        'header_background_color': '#F8F9FA',
        # Footer Colors
        'footer_text_color': '#6C757D',
        'footer_background_color': '#E9ECEF',
        'footer_link_text_color': '#0066CC',
        'footer_link_hover_text_color': '#0052A3',
        # Sidebar Colors
        'sidebar_background_color': '#F1F3F4',
        'sidebar_highlight_background_color': '#0066CC',
        'sidebar_hover_background_color': '#E9ECEF',
        'sidebar_toggle_button_background_color': '#0066CC',
        'sidebar_left_accent_color': '#FF0000',
        'sidebar_submenu_overlay_color': '#000000',
        # Content Colors
        'content_text_color': '#212529',
        'content_background_color': '#FFFFFF',
        'image_loading_background_color': '#E58822',
        # Breadcrumb Colors
        'breadcrumb_text_color': '#6C757D',
        # TOC Colors
        'toc_background_color': '#F1F3F4',
        'toc_heading_text_color': '#FFFFFF',
        'toc_link_text_color': '#0066CC',
        'toc_link_hover_text_color': '#0052A3',
        # Hashtag Colors
        'hashtag_text_color': '#0066CC',
        'hashtag_background_color': '#F8F9FA',
        # Link Colors
        'link_text_color': '#0066CC',
        'link_visited_text_color': '#6F42C1',
        'link_hover_text_color': '#0052A3',
        # Text Colors
        'body_text_color': '#212529',
        'muted_text_color': '#6C757D',
        # Keyboard Navigation Colors
        'keyboard_focus_outline_color': '#FFD700',
        'keyboard_focus_background_color': '#FFD700',
        'keyboard_hover_background_color': '#D47A1A',
        # Layout dimensions
        'header_height': '70px',
        'header_logo_size': '50px',
        'sidebar_width': '240px',
        'sidebar_collapsed_width': '30px',
        # Typography
        'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, sans-serif',
        'font_size_base': '16px',
        'font_size_small': '0.9rem',
        'font_size_large': '1.2rem',
        # Layout
        'max_content_width': 'none',
        'sidebar_default_collapsed_mobile': True,
        'toc_max_width': '640px',
        'logo_512': 'site_logo_512x512.webp',
        'logo_256': 'site_logo_256x256.webp',
        'logo_128': 'site_logo_128x128.webp',
        'logo_75': 'site_logo_75x75.webp',
        'logo_50': 'site_logo_50x50.webp',
        'favicon_32': 'site_favicon_32x32.webp',
        'favicon_16': 'site_favicon_16x16.webp',
        'logo_alt_text': 'Site Logo',
        'enable_breadcrumbs': True,
        'enable_toc': True,
        'enable_sidebar_toggle': True,
        'enable_syntax_highlighting': True,
        'google_site_verification': '',
        'plausible_domain': '',
        'google_analytics_id': '',
    }


def load_existing_config():
    """Load existing configuration values for use as defaults
    
    Returns:
        Dictionary with configuration values from site.toml or fallback defaults
    """
    config_path = Path("config/site.toml")
    fallback_defaults = get_fallback_defaults()
    
    if not config_path.exists():
        return fallback_defaults
    
    try:
        # Load TOML file
        with open(config_path, 'r') as f:
            config = tomlkit.load(f)
        
        # Extract values from TOML structure
        existing_config = {}
        
        # Site information
        if 'site' in config:
            site = config['site']  # type: ignore[index]
            existing_config.update({
                'site_name': site.get('name', fallback_defaults['site_name']),  # type: ignore[union-attr]
                'tagline': site.get('tagline', fallback_defaults['tagline']),  # type: ignore[union-attr]
                'short_name': site.get('short_name', fallback_defaults['short_name']),  # type: ignore[union-attr]
                'domain': site.get('domain', fallback_defaults['domain']),  # type: ignore[union-attr]
                'description': site.get('description', fallback_defaults['description']),  # type: ignore[union-attr]
                'author': site.get('author', fallback_defaults['author']),  # type: ignore[union-attr]
                'author_secondary': site.get('author_secondary', fallback_defaults.get('author_secondary', '')),  # type: ignore[union-attr]
            })
        
        # Theme colors - TOML handles everything cleanly, no cleaning needed!
        if 'theme' in config:
            theme = config['theme']  # type: ignore[index]
            # List of theme keys to extract
            theme_keys = [
                'header_text_color', 'header_background_color',
                'footer_text_color', 'footer_background_color',
                'footer_link_text_color', 'footer_link_hover_text_color',
                'sidebar_background_color', 'sidebar_highlight_background_color',
                'sidebar_hover_background_color', 'sidebar_toggle_button_background_color',
                'sidebar_left_accent_color', 'sidebar_submenu_overlay_color',
                'content_text_color', 'content_background_color', 'image_loading_background_color',
                'breadcrumb_text_color',
                'toc_background_color', 'toc_heading_text_color', 'toc_link_text_color', 'toc_link_hover_text_color',
                'hashtag_text_color', 'hashtag_background_color',
                'link_text_color', 'link_visited_text_color', 'link_hover_text_color',
                'body_text_color', 'muted_text_color',
                'keyboard_focus_outline_color', 'keyboard_focus_background_color', 'keyboard_hover_background_color',
                'header_height', 'header_logo_size', 'sidebar_width', 'sidebar_collapsed_width',
                'font_family', 'font_size_base', 'font_size_small', 'font_size_large'
            ]
            
            for key in theme_keys:
                if key in theme:  # type: ignore[operator]
                    value = theme[key]  # type: ignore[index]
                    # Convert 8-digit hex to 6-digit if needed
                    if isinstance(value, str) and value.startswith('#') and len(value) == 9:
                        existing_config[key] = value[:7].upper()
                    else:
                        existing_config[key] = value
                elif key in fallback_defaults:
                    # Use fallback if key not in TOML
                    existing_config[key] = fallback_defaults[key]
        
        # Images
        if 'images' in config:
            images = config['images']  # type: ignore[index]
            existing_config.update({
                'logo_512': images.get('logo_512', fallback_defaults['logo_512']),  # type: ignore[union-attr]
                'logo_256': images.get('logo_256', fallback_defaults['logo_256']),  # type: ignore[union-attr]
                'logo_128': images.get('logo_128', fallback_defaults['logo_128']),  # type: ignore[union-attr]
                'logo_75': images.get('logo_75', fallback_defaults['logo_75']),  # type: ignore[union-attr]
                'logo_50': images.get('logo_50', fallback_defaults['logo_50']),  # type: ignore[union-attr]
                'favicon_32': images.get('favicon_32', fallback_defaults['favicon_32']),  # type: ignore[union-attr]
                'favicon_16': images.get('favicon_16', fallback_defaults['favicon_16']),  # type: ignore[union-attr]
                'logo_alt_text': images.get('logo_alt_text', fallback_defaults['logo_alt_text']),  # type: ignore[union-attr]
            })
        
        # Features
        if 'features' in config:
            features = config['features']  # type: ignore[index]
            existing_config.update({
                'enable_breadcrumbs': features.get('enable_breadcrumbs', fallback_defaults['enable_breadcrumbs']),  # type: ignore[union-attr]
                'enable_toc': features.get('enable_toc', fallback_defaults['enable_toc']),  # type: ignore[union-attr]
                'enable_sidebar_toggle': features.get('enable_sidebar_toggle', fallback_defaults['enable_sidebar_toggle']),  # type: ignore[union-attr]
                'enable_syntax_highlighting': features.get('enable_syntax_highlighting', fallback_defaults['enable_syntax_highlighting']),  # type: ignore[union-attr]
            })
        
        # Analytics
        if 'analytics' in config:
            analytics = config['analytics']  # type: ignore[index]
            existing_config.update({
                'google_site_verification': analytics.get('google_site_verification', fallback_defaults['google_site_verification']),  # type: ignore[union-attr]
                'plausible_domain': analytics.get('plausible_domain', fallback_defaults['plausible_domain']),  # type: ignore[union-attr]
                'google_analytics_id': analytics.get('google_analytics_id', fallback_defaults['google_analytics_id']),  # type: ignore[union-attr]
            })
        
        # Layout
        if 'layout' in config:
            layout = config['layout']  # type: ignore[index]
            existing_config.update({
                'max_content_width': layout.get('max_content_width', fallback_defaults['max_content_width']),  # type: ignore[union-attr]
                'sidebar_default_collapsed_mobile': layout.get('sidebar_default_collapsed_mobile', fallback_defaults['sidebar_default_collapsed_mobile']),  # type: ignore[union-attr]
                'toc_max_width': layout.get('toc_max_width', fallback_defaults['toc_max_width']),  # type: ignore[union-attr]
            })
        
        # SEO
        if 'seo' in config:
            seo = config['seo']  # type: ignore[index]
            existing_config.update({
                'canonical_base': seo.get('canonical_base', f"https://{existing_config.get('domain', 'example.com')}/"),  # type: ignore[union-attr]
            })
        
        # Fill in any missing values with fallbacks
        for key, value in fallback_defaults.items():
            if key not in existing_config:
                existing_config[key] = value
                
        return existing_config
        
    except Exception as e:
        print_warning(f"Error reading existing config: {e}")
        return fallback_defaults


def update_canonical_base(domain):
    """Update canonical_base in site.toml based on domain
    
    Args:
        domain: Domain name (e.g., 'gaztank.org')
    """
    config_path = Path("config/site.toml")
    
    if not config_path.exists():
        print_warning(f"Configuration file not found: {config_path}")
        return
    
    try:
        # Load existing TOML file
        with open(config_path, 'r') as f:
            config = tomlkit.load(f)
        
        # Ensure seo section exists
        if 'seo' not in config:
            config['seo'] = {}  # type: ignore[index]
        
        # Update canonical_base
        new_canonical_base = f"https://{domain}/"
        config['seo']['canonical_base'] = new_canonical_base  # type: ignore[index]
        
        # Write back to file
        with open(config_path, 'w') as f:
            tomlkit.dump(config, f)
        
        print_info(f"Updated canonical_base to: {new_canonical_base}")
        
    except Exception as e:
        print_warning(f"Could not update canonical_base: {e}")


def is_first_time_setup():
    """Check if this is the first time setup is being run
    
    Returns:
        Tuple of (is_first_time: bool, last_setup_date: str or None)
    """
    config_path = Path("config/site.toml")
    
    if not config_path.exists():
        return True, None
    
    # Read existing config to check last_configured timestamp
    try:
        with open(config_path, 'r') as f:
            config = tomlkit.load(f)
        
        if 'setup' not in config:
            return True, None
            
        last_configured = config['setup'].get('last_configured', '')  # type: ignore[union-attr]
        
        if not last_configured:
            return True, None
            
        # Check if timestamp is before 2-Jan-2025
        try:
            dt = datetime.strptime(str(last_configured), '%Y%m%d%H%M')
            cutoff_date = datetime(2025, 1, 2, 0, 0)
            
            if dt < cutoff_date:
                return True, None
            else:
                return False, format_setup_date(str(last_configured))
        except:
            return True, None
            
    except Exception:
        return True, None


def update_config_file(config_data):
    """Update the site.toml configuration file
    
    Args:
        config_data: Dictionary containing configuration values to write
    """
    config_path = Path("config/site.toml")
    
    # Load existing TOML file
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = tomlkit.load(f)
    else:
        # Start with empty config
        config = {}
    
    # Update sections with new values (update individual keys to preserve comments)
    # Note: tomlkit objects support __setitem__ at runtime, Pylance doesn't recognize it
    if 'setup' not in config:
        config['setup'] = {}  # type: ignore[index]
    config['setup']['last_configured'] = datetime.now().strftime('%Y%m%d%H%M')  # type: ignore[index]
    config['setup']['version'] = '1.0'  # type: ignore[index]
    
    if 'site' not in config:
        config['site'] = {}  # type: ignore[index]
    config['site']['name'] = config_data['site_name']  # type: ignore[index]
    config['site']['tagline'] = config_data['tagline']  # type: ignore[index]
    config['site']['short_name'] = config_data['short_name']  # type: ignore[index]
    config['site']['domain'] = config_data['domain']  # type: ignore[index]
    config['site']['description'] = config_data['description']  # type: ignore[index]
    config['site']['author'] = config_data['author']  # type: ignore[index]
    config['site']['author_secondary'] = config_data.get('author_secondary', '')  # type: ignore[index]
    config['site']['twitter_handle'] = config_data.get('twitter_handle', '')  # type: ignore[index]
    config['site']['facebook_url'] = config_data.get('facebook_url', '')  # type: ignore[index]
    config['site']['linkedin_url'] = config_data.get('linkedin_url', '')  # type: ignore[index]
    
    if 'theme' not in config:
        config['theme'] = {}  # type: ignore[index]
    config['theme']['header_text_color'] = config_data.get('header_text_color', '#212529')  # type: ignore[index]
    config['theme']['header_background_color'] = config_data.get('header_background_color', '#F8F9FA')  # type: ignore[index]
    config['theme']['footer_text_color'] = config_data.get('footer_text_color', '#6C757D')  # type: ignore[index]
    config['theme']['footer_background_color'] = config_data.get('footer_background_color', '#E9ECEF')  # type: ignore[index]
    config['theme']['footer_link_text_color'] = config_data.get('footer_link_text_color', '#0066CC')  # type: ignore[index]
    config['theme']['footer_link_hover_text_color'] = config_data.get('footer_link_hover_text_color', '#0052A3')  # type: ignore[index]
    config['theme']['sidebar_background_color'] = config_data.get('sidebar_background_color', '#F1F3F4')  # type: ignore[index]
    config['theme']['sidebar_highlight_background_color'] = config_data.get('sidebar_highlight_background_color', '#0066CC')  # type: ignore[index]
    config['theme']['sidebar_hover_background_color'] = config_data.get('sidebar_hover_background_color', '#E9ECEF')  # type: ignore[index]
    config['theme']['sidebar_toggle_button_background_color'] = config_data.get('sidebar_toggle_button_background_color', '#0066CC')  # type: ignore[index]
    config['theme']['sidebar_left_accent_color'] = config_data.get('sidebar_left_accent_color', '#FF0000')  # type: ignore[index]
    config['theme']['sidebar_submenu_overlay_color'] = config_data.get('sidebar_submenu_overlay_color', '#000000')  # type: ignore[index]
    config['theme']['content_text_color'] = config_data.get('content_text_color', '#212529')  # type: ignore[index]
    config['theme']['content_background_color'] = config_data.get('content_background_color', '#FFFFFF')  # type: ignore[index]
    config['theme']['image_loading_background_color'] = config_data.get('image_loading_background_color', '#E58822')  # type: ignore[index]
    config['theme']['breadcrumb_text_color'] = config_data.get('breadcrumb_text_color', '#6C757D')  # type: ignore[index]
    config['theme']['toc_background_color'] = config_data.get('toc_background_color', '#F1F3F4')  # type: ignore[index]
    config['theme']['toc_heading_text_color'] = config_data.get('toc_heading_text_color', '#FFFFFF')  # type: ignore[index]
    config['theme']['toc_link_text_color'] = config_data.get('toc_link_text_color', '#0066CC')  # type: ignore[index]
    config['theme']['toc_link_hover_text_color'] = config_data.get('toc_link_hover_text_color', '#0052A3')  # type: ignore[index]
    config['theme']['hashtag_text_color'] = config_data.get('hashtag_text_color', '#0066CC')  # type: ignore[index]
    config['theme']['hashtag_background_color'] = config_data.get('hashtag_background_color', '#F8F9FA')  # type: ignore[index]
    config['theme']['link_text_color'] = config_data.get('link_text_color', '#0066CC')  # type: ignore[index]
    config['theme']['link_visited_text_color'] = config_data.get('link_visited_text_color', '#6F42C1')  # type: ignore[index]
    config['theme']['link_hover_text_color'] = config_data.get('link_hover_text_color', '#0052A3')  # type: ignore[index]
    config['theme']['body_text_color'] = config_data.get('body_text_color', '#212529')  # type: ignore[index]
    config['theme']['muted_text_color'] = config_data.get('muted_text_color', '#6C757D')  # type: ignore[index]
    config['theme']['keyboard_focus_outline_color'] = config_data.get('keyboard_focus_outline_color', '#FFD700')  # type: ignore[index]
    config['theme']['keyboard_focus_background_color'] = config_data.get('keyboard_focus_background_color', '#FFD700')  # type: ignore[index]
    config['theme']['keyboard_hover_background_color'] = config_data.get('keyboard_hover_background_color', '#D47A1A')  # type: ignore[index]
    config['theme']['header_height'] = config_data.get('header_height', '70px')  # type: ignore[index]
    config['theme']['header_logo_size'] = config_data.get('header_logo_size', '50px')  # type: ignore[index]
    config['theme']['sidebar_width'] = config_data.get('sidebar_width', '240px')  # type: ignore[index]
    config['theme']['sidebar_collapsed_width'] = config_data.get('sidebar_collapsed_width', '30px')  # type: ignore[index]
    config['theme']['font_family'] = config_data.get('font_family', '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, sans-serif')  # type: ignore[index]
    config['theme']['font_size_base'] = config_data.get('font_size_base', '16px')  # type: ignore[index]
    config['theme']['font_size_small'] = config_data.get('font_size_small', '0.9rem')  # type: ignore[index]
    config['theme']['font_size_large'] = config_data.get('font_size_large', '1.2rem')  # type: ignore[index]
    
    if 'layout' not in config:
        config['layout'] = {}  # type: ignore[index]
    config['layout']['max_content_width'] = config_data.get('max_content_width', 'none')  # type: ignore[index]
    config['layout']['sidebar_default_collapsed_mobile'] = config_data.get('sidebar_default_collapsed_mobile', True)  # type: ignore[index]
    config['layout']['toc_max_width'] = config_data.get('toc_max_width', '640px')  # type: ignore[index]
    
    if 'images' not in config:
        config['images'] = {}  # type: ignore[index]
    config['images']['logo_512'] = config_data.get('logo_512', 'site_logo_512x512.webp')  # type: ignore[index]
    config['images']['logo_256'] = config_data.get('logo_256', 'site_logo_256x256.webp')  # type: ignore[index]
    config['images']['logo_128'] = config_data.get('logo_128', 'site_logo_128x128.webp')  # type: ignore[index]
    config['images']['logo_75'] = config_data.get('logo_75', 'site_logo_75x75.webp')  # type: ignore[index]
    config['images']['logo_50'] = config_data.get('logo_50', 'site_logo_50x50.webp')  # type: ignore[index]
    config['images']['favicon_32'] = config_data.get('favicon_32', 'site_favicon_32x32.webp')  # type: ignore[index]
    config['images']['favicon_16'] = config_data.get('favicon_16', 'site_favicon_16x16.webp')  # type: ignore[index]
    config['images']['og_image'] = config_data.get('og_image', 'site_logo_256x256.webp')  # type: ignore[index]
    config['images']['logo_alt_text'] = config_data.get('logo_alt_text', 'Site Logo')  # type: ignore[index]
    
    if 'features' not in config:
        config['features'] = {}  # type: ignore[index]
    config['features']['enable_breadcrumbs'] = config_data.get('enable_breadcrumbs', True)  # type: ignore[index]
    config['features']['enable_toc'] = config_data.get('enable_toc', True)  # type: ignore[index]
    config['features']['enable_lazy_loading'] = config_data.get('enable_lazy_loading', True)  # type: ignore[index]
    config['features']['enable_sidebar_toggle'] = config_data.get('enable_sidebar_toggle', True)  # type: ignore[index]
    config['features']['enable_focus_management'] = config_data.get('enable_focus_management', True)  # type: ignore[index]
    config['features']['enable_hashtags'] = config_data.get('enable_hashtags', True)  # type: ignore[index]
    config['features']['enable_syntax_highlighting'] = config_data.get('enable_syntax_highlighting', True)  # type: ignore[index]
    
    if 'seo' not in config:
        config['seo'] = {}  # type: ignore[index]
    config['seo']['google_site_verification'] = config_data.get('google_site_verification', '')  # type: ignore[index]
    config['seo']['bing_site_verification'] = config_data.get('bing_site_verification', '')  # type: ignore[index]
    config['seo']['canonical_base'] = f"https://{config_data.get('domain', 'example.com')}/"  # type: ignore[index]
    config['seo']['site_type'] = config_data.get('site_type', 'WebSite')  # type: ignore[index]
    config['seo']['default_content_type'] = config_data.get('default_content_type', 'Article')  # type: ignore[index]
    
    if 'analytics' not in config:
        config['analytics'] = {}  # type: ignore[index]
    config['analytics']['plausible_domain'] = config_data.get('plausible_domain', '')  # type: ignore[index]
    config['analytics']['google_analytics_id'] = config_data.get('google_analytics_id', '')  # type: ignore[index]
    config['analytics']['matomo_url'] = config_data.get('matomo_url', '')  # type: ignore[index]
    config['analytics']['matomo_site_id'] = config_data.get('matomo_site_id', '')  # type: ignore[index]
    
    if 'security' not in config:
        config['security'] = {}  # type: ignore[index]
    config['security']['csp_enabled'] = config_data.get('csp_enabled', True)  # type: ignore[index]
    config['security']['hsts_enabled'] = config_data.get('hsts_enabled', False)  # type: ignore[index]
    config['security']['hsts_max_age'] = config_data.get('hsts_max_age', 31536000)  # type: ignore[index]
    
    if 'content' not in config:
        config['content'] = {}  # type: ignore[index]
    config['content']['home_page'] = config_data.get('home_page', 'home')  # type: ignore[index]
    config['content']['error_page_fallback'] = config_data.get('error_page_fallback', 'home')  # type: ignore[index]
    config['content']['default_meta_description'] = config_data.get('default_meta_description', 'Explore content and resources.')  # type: ignore[index]
    
    if 'performance' not in config:
        config['performance'] = {}  # type: ignore[index]
    config['performance']['enable_compression'] = config_data.get('enable_compression', True)  # type: ignore[index]
    config['performance']['enable_minification'] = config_data.get('enable_minification', True)  # type: ignore[index]
    config['performance']['cache_css_js_seconds'] = config_data.get('cache_css_js_seconds', 300)  # type: ignore[index]
    config['performance']['cache_images_seconds'] = config_data.get('cache_images_seconds', 3600)  # type: ignore[index]
    
    # Write TOML file
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        tomlkit.dump(config, f)
    
    print_success(f"Configuration saved to {config_path}")
