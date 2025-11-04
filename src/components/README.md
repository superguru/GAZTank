# HTML Source Components

This directory contains source components used to compose HTML output files.

**Do not edit files in** `src/` **directly** - edit these component files instead, then run the compose module to generate the output files.

## Files

- **`index-base.html`** - Main HTML structure with composition markers
- **`sidebar.md`** - Navigation sidebar in markdown format

## Composition Markers

Markers in base HTML files indicate where components should be injected:

```html
<!-- COMPOSE:COMPONENT_KEY:config_flag -->
```

Example:
```html
<!-- COMPOSE:SIDEBAR:enable_sidebar_toggle -->
```

If `site.toml` has `[features] enable_sidebar_toggle = true`, the sidebar component will be injected at this location.

## Workflow

1. Edit component files in `src/components/`
2. Run: `python -m utils.compose -e dev`
3. Output generated to `src/index.html` (gitignored)
4. Continue with normal pipeline: `setup`, `generate`, etc.

## Adding New Components

1. Create component file (HTML or markdown)
2. Add composition marker to base HTML
3. Define component in `config/compose.toml`
4. Add feature flag to `config/site.toml` (if conditional)

---

**Note:** Generated files like `src/index.html` are gitignored. Only source components in this directory are tracked in version control.
