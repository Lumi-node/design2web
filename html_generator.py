"""HTML and CSS generation module for design-to-HTML converter.

This module generates semantic HTML5 and CSS flexbox layouts from detected
region information and extracted colors.
"""

# Import types module - use project_types to avoid conflict with stdlib types
import sys
from pathlib import Path

# Ensure project_types is available
if 'project_types' not in sys.modules:
    import importlib.util
    project_root = Path(__file__).parent
    types_path = project_root / "types.py"
    spec = importlib.util.spec_from_file_location("project_types", str(types_path))
    project_types = importlib.util.module_from_spec(spec)
    sys.modules['project_types'] = project_types
    spec.loader.exec_module(project_types)

import project_types
HTMLGenerationError = project_types.HTMLGenerationError


def generate_html_structure(regions: dict) -> str:
    """Generate semantic HTML5 structure with region divs.

    Args:
        regions: Dict with keys 'header', 'sidebar', 'content', 'footer'
                Each value is None or {'x', 'y', 'width', 'height'}

    Returns:
        Valid HTML string (without <style> tag) with structure:

        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Design to HTML</title>
        </head>
        <body>
            <div class="container">
                <!-- region divs -->
            </div>
        </body>
        </html>

    Region Hierarchy (within .container):
    - If header detected: <div class="header"></div>
    - <div class="main"> (always present if any of sidebar/content detected)
        - If sidebar detected: <div class="sidebar"></div>
        - If content detected: <div class="content"></div>
    - If footer detected: <div class="footer"></div>

    Raises:
        HTMLGenerationError: If layout is invalid
    """
    try:
        # Validate input
        if not isinstance(regions, dict):
            raise HTMLGenerationError("regions must be a dictionary")

        required_keys = {'header', 'sidebar', 'content', 'footer'}
        if not all(key in regions for key in required_keys):
            raise HTMLGenerationError(f"regions must contain keys: {required_keys}")

        # Extract region data
        header = regions.get('header')
        sidebar = regions.get('sidebar')
        content = regions.get('content')
        footer = regions.get('footer')

        # Check if main should be present
        has_main = sidebar is not None or content is not None

        # Build HTML structure
        html_lines = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '    <title>Design to HTML</title>',
            '</head>',
            '<body>',
            '    <div class="container">',
        ]

        # Header div (if detected)
        if header is not None:
            html_lines.append('        <div class="header"></div>')

        # Main div (contains sidebar and content)
        if has_main:
            html_lines.append('        <div class="main">')

            # Sidebar div (if detected)
            if sidebar is not None:
                html_lines.append('            <div class="sidebar"></div>')

            # Content div (if detected)
            if content is not None:
                html_lines.append('            <div class="content"></div>')

            html_lines.append('        </div>')

        # Footer div (if detected)
        if footer is not None:
            html_lines.append('        <div class="footer"></div>')

        html_lines.extend([
            '    </div>',
            '</body>',
            '</html>',
        ])

        return '\n'.join(html_lines)

    except HTMLGenerationError:
        raise
    except Exception as e:
        raise HTMLGenerationError(f"Failed to generate HTML structure: {str(e)}")


def generate_css(regions: dict, colors: dict, image_width: int, image_height: int) -> str:
    """Generate inline CSS for layout and colors.

    Args:
        regions: Dict with keys 'header', 'sidebar', 'content', 'footer'
                Each value is None or {'x': int, 'y': int, 'width': int, 'height': int}
        colors: Dict mapping region names to lists of 3 RGB tuples
               Example: {'header': [(245, 200, 150), ...], ...}
        image_width: Original image width in pixels (from loaded image)
        image_height: Original image height in pixels (from loaded image)

    Returns:
        CSS string suitable for embedding in <style> tag.

    Raises:
        HTMLGenerationError: If data is invalid
    """
    try:
        # Validate input
        if not isinstance(regions, dict):
            raise HTMLGenerationError("regions must be a dictionary")
        if not isinstance(colors, dict):
            raise HTMLGenerationError("colors must be a dictionary")
        if not isinstance(image_width, int) or image_width <= 0:
            raise HTMLGenerationError("image_width must be a positive integer")
        if not isinstance(image_height, int) or image_height <= 0:
            raise HTMLGenerationError("image_height must be a positive integer")

        # Extract region data
        header = regions.get('header')
        sidebar = regions.get('sidebar')
        content = regions.get('content')
        footer = regions.get('footer')

        # Check if main should be present
        has_sidebar = sidebar is not None

        # Helper function to calculate luminance and determine text color
        def get_text_color(r: int, g: int, b: int) -> str:
            """Calculate luminance and return appropriate text color.

            Luminance = 0.299*R + 0.587*G + 0.114*B
            If luminance < 128: return white (#ffffff)
            If luminance >= 128: return black (#000000)
            """
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            return '#ffffff' if luminance < 128 else '#000000'

        # Helper function to get background color
        def get_background_color(region_name: str) -> str:
            """Get the dominant color for a region as rgb(r,g,b)."""
            if region_name in colors and colors[region_name]:
                r, g, b = colors[region_name][0]
                return f'rgb({r}, {g}, {b})'
            return 'rgb(128, 128, 128)'

        # Helper function to get text color for a region
        def get_region_text_color(region_name: str) -> str:
            """Get the text color for a region based on its background."""
            if region_name in colors and colors[region_name]:
                r, g, b = colors[region_name][0]
                return get_text_color(r, g, b)
            return '#ffffff'

        # Build CSS
        css_lines = [
            '* {',
            '    margin: 0;',
            '    padding: 0;',
            '    box-sizing: border-box;',
            '}',
            '',
            'body {',
            '    margin: 0;',
            '    padding: 0;',
            '    width: 100vw;',
            '    height: 100vh;',
            '    overflow: hidden;',
            '}',
            '',
            '.container {',
            '    display: flex;',
            '    flex-direction: column;',
            '    width: 100vw;',
            '    height: 100vh;',
            '}',
        ]

        # Header styles (if detected)
        if header is not None:
            header_height_vh = round((header['height'] / image_height) * 100, 2)
            bg_color = get_background_color('header')
            text_color = get_region_text_color('header')
            css_lines.extend([
                '',
                '.header {',
                '    display: flex;',
                '    align-items: center;',
                '    justify-content: center;',
                f'    background-color: {bg_color};',
                f'    color: {text_color};',
                f'    height: {header_height_vh}vh;',
                '    width: 100vw;',
                '    padding: 10px;',
                '}',
            ])

        # Main styles (if it exists)
        if sidebar is not None or content is not None:
            flex_direction = 'row' if has_sidebar else 'column'
            css_lines.extend([
                '',
                '.main {',
                '    display: flex;',
                f'    flex-direction: {flex_direction};',
                '    flex: 1;',
                '    width: 100vw;',
                '}',
            ])

        # Sidebar styles (if detected)
        if sidebar is not None:
            sidebar_width_vw = round((sidebar['width'] / image_width) * 100, 2)
            bg_color = get_background_color('sidebar')
            text_color = get_region_text_color('sidebar')
            css_lines.extend([
                '',
                '.sidebar {',
                '    display: flex;',
                '    align-items: center;',
                '    justify-content: center;',
                f'    background-color: {bg_color};',
                f'    color: {text_color};',
                f'    width: {sidebar_width_vw}vw;',
                '    height: 100%;',
                '    padding: 10px;',
                '}',
            ])

        # Content styles (if detected)
        if content is not None:
            bg_color = get_background_color('content')
            text_color = get_region_text_color('content')
            css_lines.extend([
                '',
                '.content {',
                '    display: flex;',
                '    align-items: center;',
                '    justify-content: center;',
                f'    background-color: {bg_color};',
                f'    color: {text_color};',
                '    flex: 1;',
                '    height: 100%;',
                '    padding: 10px;',
                '}',
            ])

        # Footer styles (if detected)
        if footer is not None:
            footer_height_vh = round((footer['height'] / image_height) * 100, 2)
            bg_color = get_background_color('footer')
            text_color = get_region_text_color('footer')
            css_lines.extend([
                '',
                '.footer {',
                '    display: flex;',
                '    align-items: center;',
                '    justify-content: center;',
                f'    background-color: {bg_color};',
                f'    color: {text_color};',
                f'    height: {footer_height_vh}vh;',
                '    width: 100vw;',
                '    padding: 10px;',
                '}',
            ])

        return '\n'.join(css_lines)

    except HTMLGenerationError:
        raise
    except Exception as e:
        raise HTMLGenerationError(f"Failed to generate CSS: {str(e)}")
