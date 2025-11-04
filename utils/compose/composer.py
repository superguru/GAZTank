"""
HTML Composition Engine
=======================

Assembles HTML files from source components based on compose.toml configuration.

This module:
1. Reads composition definitions from config/compose.toml
2. Loads base HTML templates with composition markers
3. Processes markers based on site.toml feature flags
4. Transforms component sources (e.g., markdown → navigation HTML)
5. Injects or removes components based on configuration
6. Writes composed output files

Composition Marker Format:
    <!-- COMPOSE:COMPONENT_KEY:config_flag -->

Example:
    <!-- COMPOSE:SIDEBAR:enable_sidebar_toggle -->
    
    If site.toml has [features] enable_sidebar_toggle = true,
    the sidebar component will be injected at this location.

Author: superguru
Version: 1.0
Last Updated: November 4, 2025
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

from bs4 import BeautifulSoup, Comment
import mistune

# Import utils modules - use absolute imports
from utils.gzconfig import get_site_config, get_compose_config
from utils.gzlogging import get_logging_context


class ComponentTransformer:
    """Transforms component sources into HTML suitable for injection"""
    
    def __init__(self, log):
        self.log = log
    
    def transform(self, content: str, transform_type: str, component_key: str) -> str:
        """
        Transform component content based on type
        
        Args:
            content: Source content to transform
            transform_type: Type of transformation (e.g., 'navigation', 'raw')
            component_key: Component key for error messages
            
        Returns:
            Transformed HTML string
        """
        if transform_type == "navigation":
            return self._transform_navigation(content, component_key)
        elif transform_type == "raw":
            return content
        else:
            if self.log:
                self.log.war(f"Unknown transform type '{transform_type}' for {component_key}, using raw")
            return content
    
    def _transform_navigation(self, markdown_content: str, component_key: str) -> str:
        """
        Transform markdown list to navigation HTML structure
        
        Converts:
            - [Label](#target)
            - [Parent](#parent)
              - [Child](#child)
        
        To:
            <nav id="sidebar">
              <ul class="nav-level-1">
                <li><a data-content="target" href="#">Label</a></li>
                <li class="has-children">
                  <div class="nav-item-wrapper">
                    <a data-content="parent" href="#">Parent</a>
                    <button aria-label="Toggle submenu" class="nav-toggle">▼</button>
                  </div>
                  <ul class="nav-level-2">
                    <li><a data-content="child" href="#">Child</a></li>
                  </ul>
                </li>
              </ul>
            </nav>
        """
        # Convert markdown to HTML
        html_content = mistune.html(markdown_content)
        # mistune.html() always returns str, but type checker doesn't know this
        assert isinstance(html_content, str), "mistune.html() should return str"
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the main <ul> element
        main_ul = soup.find('ul')
        if not main_ul:
            if self.log:
                self.log.war(f"No list found in markdown for {component_key}")
            return ""
        
        # Build navigation HTML
        nav_parts = [
            '<nav id="sidebar">',
            '<button aria-label="Toggle sidebar" class="sidebar-toggle" id="sidebar-toggle">◀</button>',
            '<ul class="nav-level-1">'
        ]
        
        for li in main_ul.find_all('li', recursive=False):
            nav_parts.append(self._process_nav_item(li, level=1))
        
        nav_parts.extend(['</ul>', '</nav>'])
        return '\n'.join(nav_parts)
    
    def _process_nav_item(self, li, level: int = 1) -> str:
        """
        Process a single navigation item recursively
        
        Args:
            li: BeautifulSoup li element
            level: Nesting level (1-based)
            
        Returns:
            HTML string for this nav item and its children
        """
        # Check for nested children
        nested_ul = li.find('ul')
        has_children = nested_ul is not None
        
        result_parts = []
        li_attrs = ' class="has-children"' if has_children else ''
        result_parts.append(f'<li{li_attrs}>')
        
        # Get the link
        link = li.find('a', recursive=False)
        if link:
            # Extract href (remove leading #) and text
            href = link.get('href', '#').lstrip('#')
            text = link.get_text(strip=True)
            
            if has_children:
                result_parts.append('<div class="nav-item-wrapper">')
            
            result_parts.append(f'<a data-content="{href}" href="#">{text}</a>')
            
            if has_children:
                result_parts.append('<button aria-label="Toggle submenu" class="nav-toggle">▼</button>')
                result_parts.append('</div>')
                result_parts.append(f'<ul class="nav-level-{level + 1}">')
                
                # Process children
                for child_li in nested_ul.find_all('li', recursive=False):
                    result_parts.append(self._process_nav_item(child_li, level + 1))
                
                result_parts.append('</ul>')
        
        result_parts.append('</li>')
        return '\n'.join(result_parts)


class HTMLComposer:
    """Composes HTML files from source components"""
    
    def __init__(self, site_config, compose_config, environment: str, log, force: bool = False):
        """
        Initialize HTML composer
        
        Args:
            site_config: Site configuration object from gzconfig
            compose_config: Composition configuration object from gzconfig
            environment: Target environment (dev/staging/prod)
            log: Logging context from gzlogging (or None)
            force: Force recomposition even if files up-to-date
        """
        self.site_config = site_config
        self.compose_config = compose_config
        self.environment = environment
        self.log = log
        self.force = force
        self.transformer = ComponentTransformer(log)
    
    def compose_all(self) -> int:
        """
        Execute all compositions defined in compose.toml
        
        Returns:
            0 on success, non-zero on error
        """
        compositions = self.compose_config.get('compositions', [])
        
        if not compositions:
            if self.log:
                self.log.war("No compositions defined in compose.toml")
            print("⚠ No compositions defined in compose.toml")
            return 0
        
        if self.log:
            self.log.inf(f"Processing {len(compositions)} composition(s)")
        print(f"\n🔨 Processing {len(compositions)} composition(s)...")
        
        success_count = 0
        for idx, composition in enumerate(compositions, 1):
            output = composition.get('output')
            description = composition.get('description', output)
            
            if self.log:
                self.log.inf(f"Composition {idx}/{len(compositions)}: {description}")
            print(f"\n[{idx}/{len(compositions)}] {description}")
            
            if self._compose_single(composition):
                success_count += 1
            else:
                if self.log:
                    self.log.err(f"Composition failed: {output}")
                print(f"❌ Composition failed: {output}")
                return 1  # Stop on first error
        
        if self.log:
            self.log.inf(f"Successfully composed {success_count}/{len(compositions)} file(s)")
        print(f"\n✅ Successfully composed {success_count}/{len(compositions)} file(s)")
        return 0
    
    def _compose_single(self, composition: Dict) -> bool:
        """
        Execute a single composition
        
        Args:
            composition: Composition definition dict
            
        Returns:
            True on success, False on error
        """
        output_path = Path(composition.get('output', ''))
        base_path = Path(composition.get('base', ''))
        components = composition.get('components', [])
        
        # Validate paths
        if not output_path:
            if self.log:
                self.log.err("No output path specified in composition")
            print("❌ No output path specified")
            return False
        
        if not base_path or not base_path.exists():
            if self.log:
                self.log.err(f"Base HTML not found: {base_path}")
            print(f"❌ Base HTML not found: {base_path}")
            return False
        
        # Read base HTML
        try:
            base_html = base_path.read_text(encoding='utf-8')
        except Exception as e:
            if self.log:
                self.log.err(f"Failed to read base HTML: {e}")
            print(f"❌ Failed to read base HTML: {e}")
            return False
        
        # Replace template variables from site.toml
        base_html = self._replace_template_variables(base_html)
        
        # Parse HTML
        soup = BeautifulSoup(base_html, 'html.parser')
        
        # Process composition markers
        markers_processed = self._process_composition_markers(soup, components)
        
        # Write composed output
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Use str(soup) instead of prettify() to avoid excessive whitespace
            # formatter='html' preserves character encoding properly
            output_path.write_text(str(soup), encoding='utf-8')
            if self.log:
                self.log.inf(f"Wrote composed HTML: {output_path}")
            print(f"  ✓ Wrote: {output_path}")
            if markers_processed > 0:
                print(f"  ✓ Processed {markers_processed} composition marker(s)")
            return True
        except Exception as e:
            if self.log:
                self.log.err(f"Failed to write output: {e}")
            print(f"❌ Failed to write output: {e}")
            return False
    
    def _replace_template_variables(self, html: str) -> str:
        """
        Replace {{VARIABLE}} placeholders with values from site.toml
        
        Args:
            html: HTML content with template variables
            
        Returns:
            HTML with variables replaced
        """
        # Get site configuration - returns the full TOML structure
        config = get_site_config()
        
        # Extract values from sections
        site = config.get('site', {})
        seo = config.get('seo', {})
        images = config.get('images', {})
        
        # Build author list
        author = site.get('author', '')
        author_secondary = site.get('author_secondary', '')
        authors_list = [a for a in [author, author_secondary] if a]
        authors_text = ', '.join(authors_list)
        
        # Build replacement dictionary
        replacements = {
            'SITE_NAME': site.get('name', 'GAZ Tank'),
            'SITE_TAGLINE': site.get('tagline', 'Gaming Content, Mods & Campaign Runs'),
            'SITE_DESCRIPTION': site.get('description', 'Welcome to GAZ Tank'),
            'SITE_URL': seo.get('canonical_base', 'https://mygaztank.com/'),
            'SITE_KEYWORDS': seo.get('keywords', ''),
            'SITE_AUTHORS': authors_text,
            'LOGO_512': images.get('logo_512', 'gaztank_logo_512x512.webp'),
            'LOGO_256': images.get('logo_256', 'gaztank_logo_256x256.webp'),
            'LOGO_128': images.get('logo_128', 'gaztank_logo_128x128.webp'),
            'LOGO_75': images.get('logo_75', 'gaztank_logo_75x75.webp'),
            'LOGO_50': images.get('logo_50', 'gaztank_logo_50x50.webp'),
            'FAVICON_32': images.get('favicon_32', 'gaztank_favicon_32x32.webp'),
            'FAVICON_16': images.get('favicon_16', 'gaztank_favicon_16x16.webp'),
        }
        
        # Replace all template variables
        for key, value in replacements.items():
            html = html.replace(f'{{{{{key}}}}}', value)
        
        return html
    
    def _process_composition_markers(self, soup: BeautifulSoup, components: List[Dict]) -> int:
        """
        Process <!-- COMPOSE:KEY:config_flag --> markers in HTML
        
        Args:
            soup: BeautifulSoup object of HTML
            components: List of component definitions
            
        Returns:
            Number of markers processed
        """
        markers_processed = 0
        
        # Build component lookup by key
        component_map = {comp.get('key'): comp for comp in components if comp.get('key')}
        
        # Find all HTML comments
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        
        for comment in comments:
            comment_text = comment.strip()
            
            # Check if it's a composition marker
            match = re.match(r'COMPOSE:(\w+):(\w+)', comment_text)
            if not match:
                continue
            
            component_key = match.group(1)
            config_flag = match.group(2)
            
            # Check if component exists
            if component_key not in component_map:
                if self.log:
                    self.log.war(f"Component '{component_key}' not defined in compose.toml")
                print(f"  ⚠ Component '{component_key}' not defined")
                continue
            
            # Check feature flag
            features = self.site_config.get('features', {})
            enabled = features.get(config_flag, True)
            
            if self.log:
                self.log.inf(f"Marker {component_key} (flag: {config_flag} = {enabled})")
            
            if enabled:
                # Generate component HTML
                component = component_map[component_key]
                component_html = self._generate_component(component)
                
                if component_html:
                    # Replace marker with component
                    new_tag = BeautifulSoup(component_html, 'html.parser')
                    comment.replace_with(new_tag)
                    print(f"  ✓ Injected: {component_key}")
                    markers_processed += 1
                else:
                    # Failed to generate - remove marker
                    comment.extract()
            else:
                # Feature disabled - remove marker and add CSS class
                comment.extract()
                print(f"  ✓ Skipped: {component_key} (disabled)")
                markers_processed += 1
                
                # Add no-{component_key} class to main-container
                main_container = soup.find('div', class_='main-container')
                if main_container and component_key:
                    # Get existing classes - can be str, list, or None
                    existing_classes = main_container.get('class')
                    if existing_classes is None:
                        classes_list: List[str] = []
                    elif isinstance(existing_classes, str):
                        classes_list = [existing_classes]
                    else:
                        classes_list = list(existing_classes)
                    
                    no_class = f'no-{component_key.lower()}'
                    if no_class not in classes_list:
                        classes_list.append(no_class)
                    # BeautifulSoup accepts list[str] for class attribute
                    main_container['class'] = classes_list  # type: ignore[assignment]
        
        return markers_processed
    
    def _generate_component(self, component: Dict) -> Optional[str]:
        """
        Generate HTML for a component
        
        Args:
            component: Component definition dict
            
        Returns:
            HTML string or None on error
        """
        source_path = Path(component.get('source', ''))
        component_type = component.get('type', 'raw')
        transform_type = component.get('transform', 'raw')
        component_key = component.get('key', 'unknown')
        
        if not source_path or not source_path.exists():
            if self.log:
                self.log.err(f"Component source not found: {source_path}")
            print(f"❌ Component source not found: {source_path}")
            return None
        
        try:
            content = source_path.read_text(encoding='utf-8')
        except Exception as e:
            if self.log:
                self.log.err(f"Failed to read component: {e}")
            print(f"❌ Failed to read component: {e}")
            return None
        
        # Transform based on type
        if component_type == 'markdown':
            html = self.transformer.transform(content, transform_type, component_key)
        else:
            html = content
        
        return html


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Compose HTML files from source components',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m utils.compose -e dev
  python -m utils.compose -e staging --force
  scripts\\compose.cmd -e prod

Description:
  Reads compose.toml to determine which HTML files to compose from
  source components. Processes composition markers in base HTML files
  to conditionally include components based on site.toml feature flags.
  
  Composition markers: <!-- COMPOSE:KEY:config_flag -->
  
  For each marker:
    - Looks up component by KEY in compose.toml
    - Checks site.toml [features] section for config_flag
    - If enabled: transforms and injects component
    - If disabled: removes marker, adds no-KEY class
        """
    )
    
    parser.add_argument(
        '-e', '--environment',
        required=True,
        choices=['dev', 'staging', 'prod'],
        help='Target environment (dev/staging/prod)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force recomposition even if files are up-to-date'
    )
    
    # Use parse_known_args to ignore unknown arguments from pipeline
    args, unknown = parser.parse_known_args()
    
    # Initialize logger
    try:
        log = get_logging_context(args.environment, 'compose', console=False)
        log.inf("=" * 60)
        log.inf("HTML Composition started")
        log.inf(f"Environment: {args.environment}")
        log.inf(f"Force: {args.force}")
    except Exception as e:
        print(f"WARNING: Logging initialization failed: {e}")
        print("Continuing without logging...")
        log = None
    
    print("\n" + "=" * 60)
    print("🔨 HTML Composition")
    print("=" * 60)
    print(f"Environment: {args.environment}")
    print(f"Force: {args.force}")
    
    # Load configurations
    try:
        site_config = get_site_config()
        compose_config = get_compose_config()
    except Exception as e:
        if log:
            log.err(f"Failed to load configuration: {e}")
        print(f"\n❌ Failed to load configuration: {e}")
        return 1
    
    # Create composer and execute
    composer = HTMLComposer(
        site_config=site_config,
        compose_config=compose_config,
        environment=args.environment,
        log=log,
        force=args.force
    )
    
    result = composer.compose_all()
    
    if result == 0:
        if log:
            log.inf("HTML Composition completed successfully")
        print("\n✅ Composition completed successfully")
    else:
        if log:
            log.err("HTML Composition failed")
        print("\n❌ Composition failed")
    
    if log:
        log.inf("=" * 60)
    print("=" * 60 + "\n")
    
    return result


if __name__ == '__main__':
    sys.exit(main())
