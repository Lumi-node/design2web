"""Test suite for HTML and CSS generation module.

Tests verify:
1. HTML structure generation with correct div hierarchy
2. CSS generation with flexbox properties
3. Color and contrast calculations
4. Dimension calculations (vh/vw conversions)
5. Edge cases (no regions, single region, etc.)
"""

import pytest
import re
import sys
from pathlib import Path
from html.parser import HTMLParser

# Import types and html_generator modules
import project_types
HTMLGenerationError = project_types.HTMLGenerationError

# Import html_generator
from html_generator import generate_html_structure, generate_css


class HTMLStructureParser(HTMLParser):
    """Parser to extract div structure from HTML."""

    def __init__(self):
        super().__init__()
        self.divs = []
        self.div_stack = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            attrs_dict = dict(attrs)
            class_name = attrs_dict.get('class', '')
            self.divs.append(class_name)
            self.div_stack.append(class_name)

    def handle_endtag(self, tag):
        if tag == 'div' and self.div_stack:
            self.div_stack.pop()


def extract_divs(html: str) -> list:
    """Extract list of div classes from HTML."""
    parser = HTMLStructureParser()
    parser.feed(html)
    return parser.divs


def extract_css_declaration(css: str, selector: str) -> dict:
    """Extract CSS declarations for a specific selector."""
    # Find the selector block
    pattern = rf'{re.escape(selector)}\s*\{{([^}}]*)\}}'
    match = re.search(pattern, css)
    if not match:
        return {}

    declarations = {}
    content = match.group(1)
    for line in content.split(';'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            declarations[key.strip()] = value.strip()
    return declarations


def parse_color_value(color_str: str) -> tuple:
    """Parse rgb(r, g, b) or #hex color to (r, g, b) tuple."""
    if color_str.startswith('rgb('):
        # Parse rgb(r, g, b)
        match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str)
        if match:
            return tuple(int(x) for x in match.groups())
    elif color_str.startswith('#'):
        # Parse hex color
        hex_str = color_str[1:]
        if len(hex_str) == 6:
            return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return None


def calculate_luminance(r: int, g: int, b: int) -> float:
    """Calculate luminance using the exact formula from architecture."""
    return 0.299 * r + 0.587 * g + 0.114 * b


class TestGenerateHTMLStructure:
    """Test HTML generation functionality."""

    def test_generate_html_four_region_layout(self):
        """Test HTML generation for a complete 4-region layout."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 120},
            'sidebar': {'x': 0, 'y': 120, 'width': 200, 'height': 480},
            'content': {'x': 200, 'y': 120, 'width': 600, 'height': 480},
            'footer': {'x': 0, 'y': 600, 'width': 800, 'height': 100},
        }

        html = generate_html_structure(regions)

        # Verify it's valid HTML5
        parser = HTMLParser()
        parser.feed(html)  # Should not raise

        # Verify structure
        assert '<!DOCTYPE html>' in html
        assert '<html>' in html
        assert '<head>' in html
        assert '<meta charset="UTF-8">' in html
        assert '<meta name="viewport"' in html
        assert '<title>Design to HTML</title>' in html
        assert '<body>' in html
        assert '<div class="container">' in html

        # Verify all divs present
        divs = extract_divs(html)
        assert 'container' in divs
        assert 'header' in divs
        assert 'main' in divs
        assert 'sidebar' in divs
        assert 'content' in divs
        assert 'footer' in divs

    def test_generate_html_no_sidebar(self):
        """Test HTML generation without sidebar (only header, content, footer)."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 100},
            'sidebar': None,
            'content': {'x': 0, 'y': 100, 'width': 800, 'height': 600},
            'footer': {'x': 0, 'y': 700, 'width': 800, 'height': 100},
        }

        html = generate_html_structure(regions)

        # Verify parser doesn't fail
        parser = HTMLParser()
        parser.feed(html)

        # Verify divs
        divs = extract_divs(html)
        assert 'container' in divs
        assert 'header' in divs
        assert 'main' in divs
        assert 'content' in divs
        assert 'footer' in divs
        assert 'sidebar' not in divs

    def test_generate_html_header_only(self):
        """Test HTML generation with only header region."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 200},
            'sidebar': None,
            'content': None,
            'footer': None,
        }

        html = generate_html_structure(regions)

        # Verify parser doesn't fail
        parser = HTMLParser()
        parser.feed(html)

        # Verify structure is minimal
        divs = extract_divs(html)
        assert 'container' in divs
        assert 'header' in divs
        assert 'main' not in divs
        assert 'sidebar' not in divs
        assert 'content' not in divs
        assert 'footer' not in divs

    def test_generate_html_no_regions(self):
        """Test HTML generation with no regions detected."""
        regions = {
            'header': None,
            'sidebar': None,
            'content': None,
            'footer': None,
        }

        html = generate_html_structure(regions)

        # Verify parser doesn't fail
        parser = HTMLParser()
        parser.feed(html)

        # Verify only container exists
        divs = extract_divs(html)
        assert 'container' in divs
        assert 'header' not in divs
        assert 'main' not in divs
        assert 'footer' not in divs

    def test_generate_html_only_content(self):
        """Test HTML generation with only content region."""
        regions = {
            'header': None,
            'sidebar': None,
            'content': {'x': 0, 'y': 0, 'width': 800, 'height': 600},
            'footer': None,
        }

        html = generate_html_structure(regions)

        # Verify parser doesn't fail
        parser = HTMLParser()
        parser.feed(html)

        # Verify structure
        divs = extract_divs(html)
        assert 'container' in divs
        assert 'main' in divs
        assert 'content' in divs
        assert 'header' not in divs
        assert 'sidebar' not in divs
        assert 'footer' not in divs

    def test_generate_html_invalid_regions_not_dict(self):
        """Test that invalid regions (not dict) raise HTMLGenerationError."""
        with pytest.raises(HTMLGenerationError):
            generate_html_structure("not a dict")

    def test_generate_html_missing_region_keys(self):
        """Test that missing region keys raise HTMLGenerationError."""
        invalid_regions = {'header': None, 'sidebar': None}  # Missing 'content' and 'footer'
        with pytest.raises(HTMLGenerationError):
            generate_html_structure(invalid_regions)


class TestGenerateCSS:
    """Test CSS generation functionality."""

    def test_generate_css_four_region_layout(self):
        """Test CSS generation for a complete 4-region layout."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 120},
            'sidebar': {'x': 0, 'y': 120, 'width': 200, 'height': 480},
            'content': {'x': 200, 'y': 120, 'width': 600, 'height': 480},
            'footer': {'x': 0, 'y': 600, 'width': 800, 'height': 100},
        }

        colors = {
            'header': [(245, 200, 150), (200, 150, 100), (100, 75, 50)],
            'sidebar': [(100, 100, 100), (75, 75, 75), (50, 50, 50)],
            'content': [(200, 200, 200), (150, 150, 150), (100, 100, 100)],
            'footer': [(50, 50, 200), (25, 25, 150), (10, 10, 100)],
        }

        image_width = 800
        image_height = 800

        css = generate_css(regions, colors, image_width, image_height)

        # Verify flexbox properties
        assert 'display: flex' in css
        assert 'flex-direction: column' in css  # Container
        assert 'flex-direction: row' in css  # Main with sidebar

        # Verify global styles
        assert '* {' in css
        assert 'margin: 0' in css
        assert 'padding: 0' in css
        assert 'box-sizing: border-box' in css

        # Verify body styles
        assert 'body {' in css
        assert 'width: 100vw' in css
        assert 'height: 100vh' in css
        assert 'overflow: hidden' in css

        # Verify container styles
        container_decl = extract_css_declaration(css, '.container')
        assert 'display' in container_decl
        assert container_decl['display'] == 'flex'
        assert 'flex-direction' in container_decl
        assert container_decl['flex-direction'] == 'column'

    def test_generate_css_color_declarations(self):
        """Test that CSS includes correct color declarations for each region."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 100},
            'sidebar': {'x': 0, 'y': 100, 'width': 200, 'height': 600},
            'content': {'x': 200, 'y': 100, 'width': 600, 'height': 600},
            'footer': {'x': 0, 'y': 700, 'width': 800, 'height': 100},
        }

        colors = {
            'header': [(245, 200, 150), (0, 0, 0), (0, 0, 0)],
            'sidebar': [(100, 100, 100), (0, 0, 0), (0, 0, 0)],
            'content': [(200, 200, 200), (0, 0, 0), (0, 0, 0)],
            'footer': [(50, 50, 200), (0, 0, 0), (0, 0, 0)],
        }

        css = generate_css(regions, colors, 800, 800)

        # Extract and verify header
        header_decl = extract_css_declaration(css, '.header')
        assert 'background-color' in header_decl
        assert 'rgb(245, 200, 150)' in header_decl['background-color']

        # Extract and verify sidebar
        sidebar_decl = extract_css_declaration(css, '.sidebar')
        assert 'background-color' in sidebar_decl
        assert 'rgb(100, 100, 100)' in sidebar_decl['background-color']

        # Extract and verify content
        content_decl = extract_css_declaration(css, '.content')
        assert 'background-color' in content_decl
        assert 'rgb(200, 200, 200)' in content_decl['background-color']

        # Extract and verify footer
        footer_decl = extract_css_declaration(css, '.footer')
        assert 'background-color' in footer_decl
        assert 'rgb(50, 50, 200)' in footer_decl['background-color']

    def test_generate_css_text_color_contrast(self):
        """Test that text color matches luminance formula."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 100},
            'footer': {'x': 0, 'y': 700, 'width': 800, 'height': 100},
        }

        # Light background (should get black text)
        light_color = (200, 200, 200)
        light_lum = calculate_luminance(*light_color)

        # Dark background (should get white text)
        dark_color = (50, 50, 100)
        dark_lum = calculate_luminance(*dark_color)

        colors = {
            'header': [light_color, (0, 0, 0), (0, 0, 0)],
            'footer': [dark_color, (0, 0, 0), (0, 0, 0)],
        }

        css = generate_css(regions, colors, 800, 800)

        # Extract text colors
        header_decl = extract_css_declaration(css, '.header')
        footer_decl = extract_css_declaration(css, '.footer')

        # Verify text colors based on luminance
        if light_lum >= 128:
            assert header_decl['color'] == '#000000'
        else:
            assert header_decl['color'] == '#ffffff'

        if dark_lum >= 128:
            assert footer_decl['color'] == '#000000'
        else:
            assert footer_decl['color'] == '#ffffff'

    def test_generate_css_luminance_calculation(self):
        """Test luminance calculation with known RGB values."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 100},
        }

        # Test with white (should get black text, luminance = 255)
        white = (255, 255, 255)
        colors_white = {
            'header': [white, (0, 0, 0), (0, 0, 0)],
        }

        css_white = generate_css(regions, colors_white, 800, 800)
        header_decl = extract_css_declaration(css_white, '.header')
        lum_white = calculate_luminance(*white)
        if lum_white >= 128:
            assert header_decl['color'] == '#000000'

        # Test with black (should get white text, luminance = 0)
        black = (0, 0, 0)
        colors_black = {
            'header': [black, (0, 0, 0), (0, 0, 0)],
        }

        css_black = generate_css(regions, colors_black, 800, 800)
        header_decl = extract_css_declaration(css_black, '.header')
        lum_black = calculate_luminance(*black)
        if lum_black < 128:
            assert header_decl['color'] == '#ffffff'

    def test_generate_css_viewport_dimensions_header(self):
        """Test that header height is correctly calculated in vh."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 120},
            'sidebar': None,
            'content': None,
            'footer': None,
        }

        colors = {
            'header': [(100, 100, 100), (0, 0, 0), (0, 0, 0)],
        }

        image_width = 800
        image_height = 600

        css = generate_css(regions, colors, image_width, image_height)

        # Calculate expected height: (120 / 600) * 100 = 20.0 vh
        expected_height = round((120 / 600) * 100, 2)

        header_decl = extract_css_declaration(css, '.header')
        assert 'height' in header_decl
        height_str = header_decl['height']
        # Extract number from "20.0vh"
        height_value = float(height_str.replace('vh', ''))
        # Should be within ±2 of expected
        assert abs(height_value - expected_height) <= 2

    def test_generate_css_viewport_dimensions_footer(self):
        """Test that footer height is correctly calculated in vh."""
        regions = {
            'header': None,
            'sidebar': None,
            'content': None,
            'footer': {'x': 0, 'y': 500, 'width': 800, 'height': 100},
        }

        colors = {
            'footer': [(100, 100, 100), (0, 0, 0), (0, 0, 0)],
        }

        image_width = 800
        image_height = 600

        css = generate_css(regions, colors, image_width, image_height)

        # Calculate expected height: (100 / 600) * 100 = 16.67 vh
        expected_height = round((100 / 600) * 100, 2)

        footer_decl = extract_css_declaration(css, '.footer')
        assert 'height' in footer_decl
        height_str = footer_decl['height']
        height_value = float(height_str.replace('vh', ''))
        assert abs(height_value - expected_height) <= 2

    def test_generate_css_viewport_dimensions_sidebar(self):
        """Test that sidebar width is correctly calculated in vw."""
        regions = {
            'header': None,
            'sidebar': {'x': 0, 'y': 0, 'width': 200, 'height': 600},
            'content': {'x': 200, 'y': 0, 'width': 600, 'height': 600},
            'footer': None,
        }

        colors = {
            'sidebar': [(100, 100, 100), (0, 0, 0), (0, 0, 0)],
            'content': [(200, 200, 200), (0, 0, 0), (0, 0, 0)],
        }

        image_width = 800
        image_height = 600

        css = generate_css(regions, colors, image_width, image_height)

        # Calculate expected width: (200 / 800) * 100 = 25.0 vw
        expected_width = round((200 / 800) * 100, 2)

        sidebar_decl = extract_css_declaration(css, '.sidebar')
        assert 'width' in sidebar_decl
        width_str = sidebar_decl['width']
        width_value = float(width_str.replace('vw', ''))
        assert abs(width_value - expected_width) <= 2

    def test_generate_css_no_sidebar_flex_direction(self):
        """Test that main flex-direction is column when no sidebar."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 100},
            'sidebar': None,
            'content': {'x': 0, 'y': 100, 'width': 800, 'height': 600},
            'footer': None,
        }

        colors = {
            'header': [(100, 100, 100), (0, 0, 0), (0, 0, 0)],
            'content': [(200, 200, 200), (0, 0, 0), (0, 0, 0)],
        }

        css = generate_css(regions, colors, 800, 800)

        main_decl = extract_css_declaration(css, '.main')
        assert 'flex-direction' in main_decl
        assert main_decl['flex-direction'] == 'column'

    def test_generate_css_with_sidebar_flex_direction(self):
        """Test that main flex-direction is row when sidebar present."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 100},
            'sidebar': {'x': 0, 'y': 100, 'width': 200, 'height': 500},
            'content': {'x': 200, 'y': 100, 'width': 600, 'height': 500},
            'footer': None,
        }

        colors = {
            'header': [(100, 100, 100), (0, 0, 0), (0, 0, 0)],
            'sidebar': [(100, 100, 100), (0, 0, 0), (0, 0, 0)],
            'content': [(200, 200, 200), (0, 0, 0), (0, 0, 0)],
        }

        css = generate_css(regions, colors, 800, 800)

        main_decl = extract_css_declaration(css, '.main')
        assert 'flex-direction' in main_decl
        assert main_decl['flex-direction'] == 'row'

    def test_generate_css_padding(self):
        """Test that all regions have padding: 10px."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 100},
            'sidebar': {'x': 0, 'y': 100, 'width': 200, 'height': 500},
            'content': {'x': 200, 'y': 100, 'width': 600, 'height': 500},
            'footer': {'x': 0, 'y': 600, 'width': 800, 'height': 100},
        }

        colors = {
            'header': [(100, 100, 100), (0, 0, 0), (0, 0, 0)],
            'sidebar': [(100, 100, 100), (0, 0, 0), (0, 0, 0)],
            'content': [(200, 200, 200), (0, 0, 0), (0, 0, 0)],
            'footer': [(100, 100, 100), (0, 0, 0), (0, 0, 0)],
        }

        css = generate_css(regions, colors, 800, 800)

        for region in ['header', 'sidebar', 'content', 'footer']:
            decl = extract_css_declaration(css, f'.{region}')
            assert 'padding' in decl
            assert decl['padding'] == '10px'

    def test_generate_css_invalid_regions_not_dict(self):
        """Test that invalid regions raise HTMLGenerationError."""
        colors = {'header': [(100, 100, 100), (0, 0, 0), (0, 0, 0)]}
        with pytest.raises(HTMLGenerationError):
            generate_css("not a dict", colors, 800, 800)

    def test_generate_css_invalid_colors_not_dict(self):
        """Test that invalid colors raise HTMLGenerationError."""
        regions = {'header': {'x': 0, 'y': 0, 'width': 800, 'height': 100},
                   'sidebar': None, 'content': None, 'footer': None}
        with pytest.raises(HTMLGenerationError):
            generate_css(regions, "not a dict", 800, 800)

    def test_generate_css_invalid_image_width(self):
        """Test that invalid image_width raises HTMLGenerationError."""
        regions = {'header': {'x': 0, 'y': 0, 'width': 800, 'height': 100},
                   'sidebar': None, 'content': None, 'footer': None}
        colors = {'header': [(100, 100, 100), (0, 0, 0), (0, 0, 0)]}
        with pytest.raises(HTMLGenerationError):
            generate_css(regions, colors, -100, 800)

    def test_generate_css_invalid_image_height(self):
        """Test that invalid image_height raises HTMLGenerationError."""
        regions = {'header': {'x': 0, 'y': 0, 'width': 800, 'height': 100},
                   'sidebar': None, 'content': None, 'footer': None}
        colors = {'header': [(100, 100, 100), (0, 0, 0), (0, 0, 0)]}
        with pytest.raises(HTMLGenerationError):
            generate_css(regions, colors, 800, 0)

    def test_generate_css_no_regions_detected(self):
        """Test CSS generation when no regions are detected."""
        regions = {
            'header': None,
            'sidebar': None,
            'content': None,
            'footer': None,
        }

        colors = {}

        css = generate_css(regions, colors, 800, 800)

        # Should still include global and container styles
        assert '* {' in css
        assert 'body {' in css
        assert '.container {' in css
        assert 'display: flex' in css

    def test_generate_css_contains_display_flex(self):
        """Test that generated CSS includes display: flex declarations."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 100},
            'sidebar': None,
            'content': {'x': 0, 'y': 100, 'width': 800, 'height': 700},
            'footer': None,
        }

        colors = {
            'header': [(100, 100, 100), (0, 0, 0), (0, 0, 0)],
            'content': [(200, 200, 200), (0, 0, 0), (0, 0, 0)],
        }

        css = generate_css(regions, colors, 800, 800)

        # Count occurrences of display: flex
        flex_count = css.count('display: flex')
        assert flex_count >= 3  # At least container, header, content


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_rounding_to_two_decimals(self):
        """Test that viewport dimensions are rounded to 2 decimal places."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 133},
            'sidebar': None,
            'content': None,
            'footer': None,
        }

        colors = {
            'header': [(100, 100, 100), (0, 0, 0), (0, 0, 0)],
        }

        css = generate_css(regions, colors, 800, 600)

        # Expected: (133 / 600) * 100 = 22.16666...
        # Rounded: 22.17
        expected = round((133 / 600) * 100, 2)

        header_decl = extract_css_declaration(css, '.header')
        height_str = header_decl['height']
        height_value = float(height_str.replace('vh', ''))
        assert height_value == expected

    def test_single_region_only_content(self):
        """Test CSS generation with only content region."""
        regions = {
            'header': None,
            'sidebar': None,
            'content': {'x': 0, 'y': 0, 'width': 800, 'height': 600},
            'footer': None,
        }

        colors = {
            'content': [(200, 200, 200), (0, 0, 0), (0, 0, 0)],
        }

        css = generate_css(regions, colors, 800, 600)

        # Should include content styling
        content_decl = extract_css_declaration(css, '.content')
        assert 'background-color' in content_decl
        assert 'rgb(200, 200, 200)' in content_decl['background-color']

    def test_missing_colors_uses_default(self):
        """Test that missing colors use default (gray) color."""
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 800, 'height': 100},
            'sidebar': None,
            'content': None,
            'footer': None,
        }

        colors = {}  # Empty colors dict

        css = generate_css(regions, colors, 800, 800)

        # Should use default gray color
        header_decl = extract_css_declaration(css, '.header')
        assert 'background-color' in header_decl
        assert 'rgb(128, 128, 128)' in header_decl['background-color']
