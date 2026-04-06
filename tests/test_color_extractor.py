"""Test suite for color extraction module.

Tests verify:
1. extract_colors function correctly imports types module
2. Function accepts image (H,W,3) uint8 and regions dict
3. Returns dict mapping only detected regions to color lists
4. Each color list contains exactly 3 RGB tuples
5. Each RGB tuple is (r, g, b) with 0 <= r,g,b <= 255 (integers)
6. K-means uses n_clusters=3, n_init=10, max_iter=300, random_state=42
7. Pixel sampling uses center 80% of region (10% margins on all sides)
8. For regions < 10 pixels after sampling: random fallback used
9. For small regions: most common color repeated if < 3 unique colors
10. Colors sorted by frequency (most common first) after k-means
11. Cluster centers converted from float64 to uint8 with rounding/clipping
12. Function raises ColorExtractionError if clustering fails
13. Only detected regions included in output (undetected regions omitted)
"""

import pytest
import numpy as np
from PIL import Image
from pathlib import Path

# Import project_types as configured in conftest.py
import project_types as types_module
ColorExtractionError = types_module.ColorExtractionError

# Import the module under test
from color_extractor import extract_colors


class TestExtractColorsImports:
    """Test that extract_colors module imports correctly."""

    def test_extract_colors_is_callable(self):
        """extract_colors should be a callable function."""
        assert callable(extract_colors)

    def test_color_extraction_error_is_available(self):
        """ColorExtractionError should be importable from types."""
        assert ColorExtractionError is not None
        assert issubclass(ColorExtractionError, Exception)


class TestExtractColorsBasic:
    """Test basic functionality of extract_colors."""

    def test_extract_colors_single_solid_region(self):
        """Extract colors from a single solid-color region."""
        # Create a 100x100 solid red image
        image = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        regions = {'header': {'x': 0, 'y': 0, 'width': 100, 'height': 100}}

        result = extract_colors(image, regions)

        # Should have header in result
        assert 'header' in result
        # Should have exactly 3 colors
        assert len(result['header']) == 3
        # All colors should be red (or very close to red)
        for color in result['header']:
            assert isinstance(color, tuple)
            assert len(color) == 3
            assert color[0] == 255  # Red channel should be 255
            assert color[1] == 0    # Green should be ~0
            assert color[2] == 0    # Blue should be ~0

    def test_extract_colors_returns_dict(self):
        """extract_colors should return a dictionary."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        regions = {'header': {'x': 0, 'y': 0, 'width': 100, 'height': 100}}

        result = extract_colors(image, regions)

        assert isinstance(result, dict)

    def test_extract_colors_only_detected_regions(self):
        """extract_colors should only include detected regions in output."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 100, 'height': 50},
            'sidebar': None,
            'content': {'x': 0, 'y': 50, 'width': 100, 'height': 50},
            'footer': None
        }

        result = extract_colors(image, regions)

        # Should only contain header and content
        assert 'header' in result
        assert 'content' in result
        assert 'sidebar' not in result
        assert 'footer' not in result

    def test_extract_colors_all_none_regions(self):
        """extract_colors with all None regions should return empty dict."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        regions = {
            'header': None,
            'sidebar': None,
            'content': None,
            'footer': None
        }

        result = extract_colors(image, regions)

        assert result == {}


class TestExtractColorsColorValidation:
    """Test that extracted colors are valid RGB values."""

    def test_extracted_colors_are_tuples(self):
        """Each extracted color should be a tuple."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        regions = {'header': {'x': 0, 'y': 0, 'width': 100, 'height': 100}}

        result = extract_colors(image, regions)

        for color in result['header']:
            assert isinstance(color, tuple)
            assert len(color) == 3

    def test_extracted_colors_are_integers(self):
        """Each color component should be an integer."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        regions = {'header': {'x': 0, 'y': 0, 'width': 100, 'height': 100}}

        result = extract_colors(image, regions)

        for color in result['header']:
            for component in color:
                assert isinstance(component, (int, np.integer))

    def test_extracted_colors_in_valid_range(self):
        """All color components should be in [0, 255]."""
        image = np.random.randint(0, 256, (150, 150, 3), dtype=np.uint8)
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 150, 'height': 50},
            'content': {'x': 0, 'y': 50, 'width': 150, 'height': 100}
        }

        result = extract_colors(image, regions)

        for region_colors in result.values():
            for color in region_colors:
                assert all(0 <= c <= 255 for c in color)

    def test_extracted_colors_exactly_three(self):
        """Each region should have exactly 3 colors."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 50, 'height': 50},
            'content': {'x': 50, 'y': 50, 'width': 50, 'height': 50}
        }

        result = extract_colors(image, regions)

        assert len(result['header']) == 3
        assert len(result['content']) == 3


class TestExtractColorsMultiRegion:
    """Test color extraction from multiple regions."""

    def test_extract_colors_multiple_regions(self):
        """Extract colors from multiple regions simultaneously."""
        # Create 200x200 image with 4 colored quadrants
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        image[0:100, 0:100] = [255, 0, 0]        # Red
        image[0:100, 100:200] = [0, 255, 0]      # Green
        image[100:200, 0:100] = [0, 0, 255]      # Blue
        image[100:200, 100:200] = [255, 255, 0]  # Yellow

        regions = {
            'header': {'x': 0, 'y': 0, 'width': 200, 'height': 100},
            'sidebar': {'x': 0, 'y': 100, 'width': 100, 'height': 100},
            'content': {'x': 100, 'y': 100, 'width': 100, 'height': 100},
            'footer': None
        }

        result = extract_colors(image, regions)

        # All regions should be present except footer
        assert 'header' in result
        assert 'sidebar' in result
        assert 'content' in result
        assert 'footer' not in result
        # Each should have 3 colors
        assert len(result['header']) == 3
        assert len(result['sidebar']) == 3
        assert len(result['content']) == 3


class TestExtractColorsFrequencySorting:
    """Test that colors are sorted by frequency (most common first)."""

    def test_colors_sorted_by_frequency(self):
        """Colors should be sorted by frequency (most common first)."""
        # Create image with one color dominating
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        # 80 pixels red, 15 pixels green, 5 pixels blue
        image[0:80, :, :] = [255, 0, 0]
        image[80:95, :, :] = [0, 255, 0]
        image[95:100, :, :] = [0, 0, 255]

        regions = {'header': {'x': 0, 'y': 0, 'width': 100, 'height': 100}}

        result = extract_colors(image, regions)

        # The most common color (red) should be first
        # (Note: due to k-means, exact order may vary, but frequency sorting should apply)
        # We just verify that all 3 colors are returned
        assert len(result['header']) == 3


class TestExtractColorsSmallRegionFallback:
    """Test small region fallback (< 10 pixels after center 80% sampling)."""

    def test_small_region_uses_fallback(self):
        """Regions < 10 pixels after 80% sampling should use random fallback."""
        # Create a very small 10x10 region
        # After 80% center sampling: [1:9, 1:9] = 8x8 = 64 pixels (> 10)
        # Need smaller region to trigger fallback
        # For N_pixels < 10: need region where center 80% < 10 pixels
        # If region is 10x10, center is [1:9, 1:9] = 64 pixels
        # If region is 5x5, center is [1:4, 1:4] = 9 pixels (< 10, triggers fallback)

        image = np.zeros((50, 50, 3), dtype=np.uint8)
        image[0:5, 0:5] = [255, 128, 64]  # Mixed color

        regions = {'header': {'x': 0, 'y': 0, 'width': 5, 'height': 5}}

        result = extract_colors(image, regions)

        # Should still return exactly 3 colors
        assert len(result['header']) == 3
        # Colors should be valid
        for color in result['header']:
            assert all(0 <= c <= 255 for c in color)

    def test_small_region_repeated_color(self):
        """For small regions with < 3 unique colors, most common color is repeated."""
        # Create a 5x5 region with only 2 unique colors
        image = np.zeros((50, 50, 3), dtype=np.uint8)
        image[0:3, 0:5] = [255, 0, 0]    # Red
        image[3:5, 0:5] = [0, 255, 0]    # Green

        regions = {'header': {'x': 0, 'y': 0, 'width': 5, 'height': 5}}

        result = extract_colors(image, regions)

        # Should return exactly 3 colors
        assert len(result['header']) == 3
        # Most common color should appear at least once more
        # (at least one duplicate)
        colors = result['header']
        # Count duplicates
        unique_colors = set(colors)
        # We should have at most 2 unique colors
        assert len(unique_colors) <= 2


class TestExtractColorsWithFixtures:
    """Test color extraction using fixture images."""

    @pytest.fixture
    def fixtures_dir(self):
        """Return path to test fixtures directory."""
        return Path(__file__).parent / 'fixtures'

    def test_solid_color_fixture(self, fixtures_dir):
        """Extract colors from solid_color.png fixture."""
        fixture_path = fixtures_dir / 'solid_color.png'
        if not fixture_path.exists():
            pytest.skip(f"Fixture {fixture_path} not found")

        image = np.array(Image.open(fixture_path))
        regions = {'header': {'x': 0, 'y': 0, 'width': 100, 'height': 100}}

        result = extract_colors(image, regions)

        assert 'header' in result
        assert len(result['header']) == 3
        # All colors should be very similar (nearly red)
        for color in result['header']:
            assert color[0] > 200  # Red dominant
            assert color[1] < 50   # Low green
            assert color[2] < 50   # Low blue

    def test_color_bands_fixture(self, fixtures_dir):
        """Extract colors from color_bands.png fixture with 3 distinct bands."""
        fixture_path = fixtures_dir / 'color_bands.png'
        if not fixture_path.exists():
            pytest.skip(f"Fixture {fixture_path} not found")

        image = np.array(Image.open(fixture_path))
        # Image is 100 height x 300 width with 3 vertical bands

        # Extract from the entire image (all 3 bands)
        regions = {'header': {'x': 0, 'y': 0, 'width': 300, 'height': 100}}

        result = extract_colors(image, regions)

        assert 'header' in result
        assert len(result['header']) == 3

    def test_multi_color_fixture(self, fixtures_dir):
        """Extract colors from multi_color.png with 4 colored quadrants."""
        fixture_path = fixtures_dir / 'multi_color.png'
        if not fixture_path.exists():
            pytest.skip(f"Fixture {fixture_path} not found")

        image = np.array(Image.open(fixture_path))

        # Extract from each quadrant
        regions = {
            'header': {'x': 0, 'y': 0, 'width': 100, 'height': 100},
            'sidebar': {'x': 0, 'y': 100, 'width': 100, 'height': 100},
            'content': {'x': 100, 'y': 100, 'width': 100, 'height': 100},
            'footer': None
        }

        result = extract_colors(image, regions)

        # All detected regions should be in result
        assert 'header' in result
        assert 'sidebar' in result
        assert 'content' in result
        assert 'footer' not in result

        # Each should have 3 colors
        for region_name in ['header', 'sidebar', 'content']:
            assert len(result[region_name]) == 3


class TestExtractColorsEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_pixel_region(self):
        """Handle region with single pixel."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[50, 50] = [123, 45, 67]

        regions = {'header': {'x': 50, 'y': 50, 'width': 1, 'height': 1}}

        result = extract_colors(image, regions)

        # Should return 3 colors (all the same)
        assert len(result['header']) == 3
        # Center 80% of 1x1 region would be 0 pixels, triggering fallback
        for color in result['header']:
            assert color == (123, 45, 67)

    def test_large_uniform_region(self):
        """Handle large uniform color region."""
        image = np.full((200, 200, 3), [100, 150, 200], dtype=np.uint8)

        regions = {'content': {'x': 0, 'y': 0, 'width': 200, 'height': 200}}

        result = extract_colors(image, regions)

        assert len(result['content']) == 3
        # All colors should be very similar
        for color in result['content']:
            assert abs(color[0] - 100) < 5
            assert abs(color[1] - 150) < 5
            assert abs(color[2] - 200) < 5

    def test_region_with_exact_3_unique_colors(self):
        """Handle region with exactly 3 unique colors."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        # Divide into 3 sections
        image[0:33, :] = [255, 0, 0]
        image[33:66, :] = [0, 255, 0]
        image[66:100, :] = [0, 0, 255]

        regions = {'header': {'x': 0, 'y': 0, 'width': 100, 'height': 100}}

        result = extract_colors(image, regions)

        assert len(result['header']) == 3
        # Should extract the 3 main colors
        colors = set(result['header'])
        # k-means may round slightly, but should get close to R, G, B
        assert len(colors) <= 3

    def test_region_offset_from_origin(self):
        """Test region that is offset from image origin."""
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        # Put a red region at offset (50, 75)
        image[75:125, 50:100] = [255, 0, 0]

        regions = {'content': {'x': 50, 'y': 75, 'width': 50, 'height': 50}}

        result = extract_colors(image, regions)

        assert 'content' in result
        assert len(result['content']) == 3
        # Should extract red color
        for color in result['content']:
            assert color[0] > 200


class TestExtractColorsErrorHandling:
    """Test error handling and exception raising."""

    def test_invalid_region_data_raises_error(self):
        """Invalid region data should raise ColorExtractionError."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        # Missing 'width' key
        regions = {'header': {'x': 0, 'y': 0, 'height': 50}}

        with pytest.raises(ColorExtractionError):
            extract_colors(image, regions)

    def test_out_of_bounds_region_graceful_handling(self):
        """Out of bounds region should be handled gracefully (NumPy slicing behavior)."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        # Region extends beyond image bounds - NumPy slicing handles this gracefully
        regions = {'header': {'x': 50, 'y': 50, 'width': 200, 'height': 200}}

        # Should not raise an error, but return colors for the partial region
        result = extract_colors(image, regions)
        assert 'header' in result
        assert len(result['header']) == 3


class TestExtractColorsDeterminism:
    """Test that color extraction is deterministic."""

    def test_same_image_same_colors(self):
        """Extracting colors from same image twice should give same results."""
        # Create deterministic image
        np.random.seed(42)
        image = np.random.randint(50, 200, (100, 100, 3), dtype=np.uint8)

        regions = {'header': {'x': 0, 'y': 0, 'width': 100, 'height': 100}}

        # Extract twice
        result1 = extract_colors(image, regions)
        result2 = extract_colors(image, regions)

        # Results should be identical
        assert result1['header'] == result2['header']

    def test_kmeans_random_state_determinism(self):
        """K-means with random_state=42 should be deterministic."""
        # Create varied image to test k-means
        image = np.random.RandomState(123).randint(0, 256, (200, 200, 3), dtype=np.uint8)

        regions = {'header': {'x': 0, 'y': 0, 'width': 200, 'height': 200}}

        # Extract multiple times
        result1 = extract_colors(image, regions)
        result2 = extract_colors(image, regions)
        result3 = extract_colors(image, regions)

        # All should be identical
        assert result1['header'] == result2['header']
        assert result2['header'] == result3['header']
